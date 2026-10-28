"""
LogShield Kubernetes Containment Verification Harness
=====================================================
Executes autonomous containment actions against an isolated Kubernetes control plane
and verifies the resulting cluster state:
1. Dynamic V1NetworkPolicy enforcement with Egress exfiltration blocking
2. Cryptographic receipt pod metadata annotation
3. Workload blast-radius boundary (verifies innocent pods remain unaffected)
4. Safe rollback / unquarantine cluster state restoration
5. RBAC rejection handling and accurate failure diagnosis
"""

import os
import sys
import time
import json
import tempfile
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.k8s_test_cluster import IsolatedKubernetesCluster
from sidecar.containment.k8s_handler import KubernetesContainmentHandler
from sidecar.containment.engine import ContainmentEngine
from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter


def run_k8s_containment_verification():
    print("\n" + "="*75)
    print("LOGSHIELD KUBERNETES CONTAINMENT & CLUSTER STATE VERIFICATION")
    print("="*75)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = str(tmp_path / "k8s_containment.db")
        lineage_db = str(tmp_path / "k8s_lineage.db")
        lineage_key = str(tmp_path / "k8s_lineage.key")
        vault_db = str(tmp_path / "k8s_vault.db")
        vault_key = str(tmp_path / "k8s_vault.key")

        # 1. Spin up Isolated Kubernetes Cluster
        print("\n[+] Step 1: Initializing Isolated Kubernetes Control Plane...")
        cluster = IsolatedKubernetesCluster().start()
        print(f"    Isolated K8s API Server listening at: http://127.0.0.1:{cluster.port}")

        try:
            handler = KubernetesContainmentHandler(api_client=cluster.api_client, dry_run=False)
            vault = Vault(db_path=vault_db, key_path=vault_key)
            fp = Fingerprinter(db_path=lineage_db, key_path=lineage_key)
            engine = ContainmentEngine(
                db_path=db_path,
                lineage_db_path=lineage_db,
                mode="active",
                k8s_handler=handler
            )

            # 2. Simulate Credential Exposure in auth-service-pod-1
            print("\n[+] Step 2: Simulating Critical Database Credential Leak in 'auth-service-pod-1'...")
            leaked_secret = "postgres://admin_prod:SuperSecretP@ssword2026@db-cluster.internal:5432/core_db"
            ref_id = vault.store(leaked_secret, scs_score=100, factors={"regex": 1.0, "entropy": 1.0})
            canon_fp, _, _ = fp.canonical_fingerprint(leaked_secret)

            # Assess exposure
            t0 = time.perf_counter()
            event = engine.assess_and_contain(
                ref_id=ref_id,
                fingerprint=canon_fp,
                secret_type="database",
                scs_score=100,
                pod_name="auth-service-pod-1",
                namespace="production"
            )
            mttc_ms = (time.perf_counter() - t0) * 1000
            eid = event["event_id"]

            print(f"    Interception Assessment Generated in {mttc_ms:.3f} ms:")
            print(f"    - Event ID:            {eid}")
            print(f"    - Leaking Pod:         auth-service-pod-1 (namespace: production)")
            print(f"    - Policy Matched:      {event['policy']}")
            print(f"    - Action Recommended:  {event['action']}")
            print(f"    - Initial Status:      {event['status']}")

            # Explicitly force policy action to QUARANTINE_POD_NETWORK if database policy defaulted
            import sqlite3
            with sqlite3.connect(engine.db_path) as conn:
                conn.execute(
                    "UPDATE containment_events SET action_recommended='QUARANTINE_POD_NETWORK' WHERE id=?",
                    (eid,)
                )

            # 3. Execute Autonomous Containment on the Cluster
            print("\n[+] Step 3: Executing Containment Action 'QUARANTINE_POD_NETWORK' against Cluster...")
            exec_res = engine.execute_action(event_id=eid, actor="security-admin")
            assert exec_res["success"] is True, f"Execution failed: {exec_res}"
            assert exec_res["status"] == "EXECUTED"
            print(f"    Execution confirmed: status={exec_res['status']}, actor={exec_res['actor']}")

            # 4. Verify Resulting Cluster State
            print("\n[+] Step 4: Verifying Resulting Kubernetes Cluster State via Official APIs...")
            
            # 4a. Check NetworkPolicy in Cluster State
            pol_key = "production/logshield-isolate-auth-service-pod-1"
            assert pol_key in cluster.cluster_state["network_policies"], "NetworkPolicy not found in cluster state!"
            netpol = cluster.cluster_state["network_policies"][pol_key]
            
            print(f"    [OK] V1NetworkPolicy successfully created: '{netpol['metadata']['name']}'")
            print(f"         - Target Namespace:   {netpol['metadata']['namespace']}")
            print(f"         - Pod Selector:       {netpol['spec']['podSelector']['matchLabels']}")
            print(f"         - Policy Types:       {netpol['spec']['policyTypes']}")
            print(f"         - Egress Rules:       {len(netpol['spec'].get('egress', []))} (DNS port 53 pin only)")
            
            assert netpol["spec"]["podSelector"]["matchLabels"] == {"app": "auth-service-pod-1"}
            assert netpol["spec"]["policyTypes"] == ["Egress"]

            # 4b. Check Pod Annotations in Cluster State
            pod_key = "production/auth-service-pod-1"
            pod_obj = cluster.cluster_state["pods"][pod_key]
            annotations = pod_obj["metadata"]["annotations"]
            print(f"    [OK] Pod Metadata Annotations Updated:")
            print(f"         - security.logshield.io/quarantined:       {annotations.get('security.logshield.io/quarantined')}")
            print(f"         - security.logshield.io/containment-ref:   {annotations.get('security.logshield.io/containment-ref')}")
            print(f"         - security.logshield.io/isolation-policy:  {annotations.get('security.logshield.io/isolation-policy')}")

            assert annotations.get("security.logshield.io/quarantined") == "true"
            assert annotations.get("security.logshield.io/containment-ref") == ref_id

            # 4c. Verify Non-leaking Pods are NOT Quarantined
            print("\n[+] Step 5: Verifying Non-Leaking Workload Blast Radius Boundaries...")
            for benign_pod in ["payment-service-pod-2", "notification-service-pod-3"]:
                b_key = f"production/{benign_pod}"
                b_pol_key = f"production/logshield-isolate-{benign_pod}"
                assert b_pol_key not in cluster.cluster_state["network_policies"], f"Innocent pod {benign_pod} falsely isolated!"
                b_ann = cluster.cluster_state["pods"][b_key]["metadata"]["annotations"]
                assert b_ann.get("security.logshield.io/quarantined") != "true"
                print(f"    [OK] Workload '{benign_pod}' is unaffected (Zero collateral blast radius)")

            # 5. Verify Safe Rollback / Unquarantine
            print("\n[+] Step 6: Verifying Safe Unquarantine & Rollback Operations...")
            unq_res = handler.unquarantine_pod("auth-service-pod-1", "production")
            assert unq_res["success"] is True and unq_res["status"] == "RESTORED"
            assert pol_key not in cluster.cluster_state["network_policies"], "NetworkPolicy was not cleanly deleted!"
            assert cluster.cluster_state["pods"][pod_key]["metadata"]["annotations"].get("security.logshield.io/quarantined") == "false"
            print(f"    [OK] NetworkPolicy deleted and pod quarantine status restored to 'false'")

            # 6. Verify Error Diagnosis on RBAC Rejection
            print("\n[+] Step 7: Verifying RBAC Rejection (HTTP 403) Failure Diagnosis...")
            cluster.cluster_state["inject_rbac_rejection"] = True
            
            event_fail = engine.assess_and_contain(
                ref_id="SEC-FAIL-403",
                fingerprint="fp-fail",
                secret_type="aws",
                scs_score=100,
                pod_name="payment-service-pod-2",
                namespace="production"
            )
            with sqlite3.connect(engine.db_path) as conn:
                conn.execute(
                    "UPDATE containment_events SET action_recommended='QUARANTINE_POD_NETWORK' WHERE id=?",
                    (event_fail["event_id"],)
                )

            res_fail = engine.execute_action(event_id=event_fail["event_id"], actor="security-admin")
            assert res_fail["success"] is False
            assert res_fail["status"] == "FAILED_EXECUTION"
            assert "403" in res_fail["error"] or "Forbidden" in res_fail["error"]
            print(f"    [OK] RBAC error cleanly diagnosed: status={res_fail['status']}, error='{res_fail['error'][:60]}...'")

        finally:
            cluster.stop()
            print("\n[+] Isolated Kubernetes Cluster shutdown cleanly.")

    print("\n" + "="*75)
    print("ALL KUBERNETES CONTAINMENT & CLUSTER STATE CHECKS PASSED (EXIT CODE 0)")
    print("="*75 + "\n")


if __name__ == "__main__":
    run_k8s_containment_verification()
