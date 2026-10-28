"""
LogShield Novel Capabilities Verification Harness
=================================================
Automated verification for:
1. Vault Pre-seeding & Secret Lineage Exemption (Zero-sprawl pre-seeding)
2. Adaptive Evasion Defense (Token Window Fusion, Hex unescape, Base64 unnesting)
3. Transformation-Aware Secret Lineage (Canonical blind HMAC linking across representations)
4. Autonomous Containment Engine (Blast radius assessment, policy triggers, MTTC measurement)
5. FastAPI REST API Integration Endpoints
"""

import os
import sys
import tempfile
import time
import base64
import urllib.parse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sidecar.logmask.scorer import SCSEngine
from sidecar.logmask.preprocessor import LogPreprocessor
from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter
from sidecar.containment.engine import ContainmentEngine
from sidecar.main import LogShieldInterceptor
from fastapi.testclient import TestClient
from sidecar.api import app, VAULT_DB_PATH, LINEAGE_DB_PATH, CONTAINMENT_DB_PATH


def test_vault_preseed_and_exemption(tmpdir: Path):
    print("\n" + "="*70)
    print("TEST 1: Vault Pre-seeding & Secret Lineage Exemption Mechanism")
    print("="*70)

    vault_db = str(tmpdir / "vault.db")
    vault_key = str(tmpdir / "vault.key")
    lineage_db = str(tmpdir / "lineage.db")
    lineage_key = str(tmpdir / "lineage.key")

    vault = Vault(db_path=vault_db, key_path=vault_key)
    fp = Fingerprinter(db_path=lineage_db, key_path=lineage_key)

    authorized_secret = "AKIA-AUTHORIZED-PROD-KEY-9999"
    secret_label = "Production Cloud Deploy Key"

    # 1. Pre-seed secret into Vault with lineage suppression enabled
    print("[+] Pre-seeding authorized secret into SecureReveal Vault...")
    ref_id = vault.preseed(
        plaintext=authorized_secret,
        label=secret_label,
        scs_score=100,
        suppress_lineage=True,
        fingerprinter=fp,
        actor="admin"
    )
    assert ref_id.upper().startswith("SEC-"), f"Invalid ref_id: {ref_id}"
    print(f"    Secret pre-seeded successfully: ref_id={ref_id}")

    # 2. Verify vault retrieval works
    ok, retrieved = vault.retrieve(ref_id, actor="admin", reason="Verify pre-seed")
    assert ok and retrieved == authorized_secret, f"Failed to retrieve preseeded secret from vault: {retrieved}"
    print(f"    Verified vault cryptographic retrieval: {retrieved[:8]}****")

    # 3. Verify secret is listed in lineage exemptions
    assert fp.is_exempt(authorized_secret), "Secret was not recorded in lineage exemptions"
    exemptions = fp.list_exemptions()
    assert len(exemptions) == 1, f"Expected 1 exemption, found {len(exemptions)}"
    assert exemptions[0]["label"] == secret_label
    print(f"    Verified lineage exemption record: label='{exemptions[0]['label']}'")

    # 4. Process log line containing the pre-seeded secret
    # Lineage must NOT record this secret
    fp.pod_name = "payment-gateway-pod"
    fp.namespace = "production"
    fp.record(authorized_secret)

    # 5. Sprawl report must be empty (completely suppressed from sprawl graph)
    sprawl = fp.sprawl_report()
    assert len(sprawl) == 0, f"Exempt secret leaked into sprawl report! Count: {len(sprawl)}"
    print("    Verified zero-sprawl guarantee: Sprawl report returned 0 entries for exempt secret")

    # 6. Verify exemption removal
    canon_fp = exemptions[0]["fingerprint"]
    removed = fp.remove_exemption(canon_fp)
    assert removed, "Failed to remove exemption"
    assert not fp.is_exempt(authorized_secret), "Secret should no longer be exempt"
    print("    Verified exemption removal: Secret can be re-monitored if de-authorized")

    print("[PASS] Test 1: Vault Pre-seeding & Lineage Exemption verified successfully.")


def test_adaptive_evasion_defense():
    print("\n" + "="*70)
    print("TEST 2: Adaptive Evasion Defense (Token Window Fusion & Normalization)")
    print("="*70)

    engine = SCSEngine()
    preprocessor = LogPreprocessor()

    # Case A: Whitespace/Delimiter Split AWS Key
    # Adversary logs: "aws_access_key_id = AKIA IOSFODNN7EXAMPLE"
    split_log = "2026-10-21 14:02:11 [ERROR] Failed auth: access_key = AKIA IOSFODNN7EXAMPLE (access denied)"
    prep_res = preprocessor.process(split_log)
    fused_tokens = [t for t in prep_res.tokens if t.evasion_type == "delimiter_split"]
    assert len(fused_tokens) > 0, "Failed to detect delimiter-split evasion"
    print(f"    [+] Delimiter-Split Detected: raw_slice='{fused_tokens[0].raw_slice}' -> fused='{fused_tokens[0].value}'")

    results_split = engine.extract_and_score(split_log)
    assert any(r.decision == "MASK" for r in results_split), "Engine failed to MASK delimiter-split AWS key"
    matched_split = [r for r in results_split if r.token == "AKIAIOSFODNN7EXAMPLE"][0]
    assert matched_split.score >= 80, f"Expected SCS >= 80, got {matched_split.score}"
    assert matched_split.raw_slice == "AKIA IOSFODNN7EXAMPLE", f"Expected raw_slice match, got {matched_split.raw_slice}"
    print(f"    [+] Delimiter-Split Scored: Decision={matched_split.decision}, SCS={matched_split.score}, Category={matched_split.category}")

    # Case B: Hex-Escaped Secret
    # \x41\x4b\x49\x41\x49\x4f\x53\x46\x4f\x44\x4e\x4e\x37\x45\x58\x41\x4d\x50\x4c\x45 = AKIAIOSFODNN7EXAMPLE
    hex_log = r"DEBUG worker: key=\x41\x4b\x49\x41\x49\x4f\x53\x46\x4f\x44\x4e\x4e\x37\x45\x58\x41\x4d\x50\x4c\x45 status=active"
    results_hex = engine.extract_and_score(hex_log)
    assert any(r.decision == "MASK" for r in results_hex), "Engine failed to MASK hex-escaped AWS key"
    matched_hex = [r for r in results_hex if r.token == "AKIAIOSFODNN7EXAMPLE"][0]
    assert matched_hex.evasion_type == "hex_escaped", f"Expected evasion_type='hex_escaped', got {matched_hex.evasion_type}"
    print(f"    [+] Hex-Escaped Detected & Normalized: Decision={matched_hex.decision}, SCS={matched_hex.score}, Evasion={matched_hex.evasion_type}")

    # Case C: Base64 Obfuscated Token
    # AKIAIOSFODNN7EXAMPLE in Base64 is QUtJQUlPU0ZPRE5ON0VYQU1QTEU=
    b64_log = "INFO request: Authorization: Basic QUtJQUlPU0ZPRE5ON0VYQU1QTEU= auth_ok"
    results_b64 = engine.extract_and_score(b64_log)
    assert any(r.decision == "MASK" for r in results_b64), "Engine failed to MASK Base64 encoded secret"
    matched_b64 = [r for r in results_b64 if r.token == "AKIAIOSFODNN7EXAMPLE"][0]
    assert matched_b64.evasion_type == "base64_encoded"
    print(f"    [+] Base64-Encoded Secret Defused: Decision={matched_b64.decision}, SCS={matched_b64.score}")

    print("[PASS] Test 2: Adaptive Evasion Defense verified successfully.")


def test_canonical_secret_lineage(tmpdir: Path):
    print("\n" + "="*70)
    print("TEST 3: Transformation-Aware Secret Lineage (Canonical HMAC Linking)")
    print("="*70)

    lineage_db = str(tmpdir / "lineage_sprawl.db")
    lineage_key = str(tmpdir / "lineage_sprawl.key")
    fp = Fingerprinter(db_path=lineage_db, key_path=lineage_key)

    raw_secret = "ghp_99NovelSecurityEvidenceTokenForLineageTest2026"
    b64_secret = base64.b64encode(raw_secret.encode()).decode()
    url_secret = urllib.parse.quote(raw_secret)

    # 1. Canonical fingerprints must match exactly across all encodings
    c_fp_raw, fmt_raw, _ = fp.canonical_fingerprint(raw_secret)
    c_fp_b64, fmt_b64, _ = fp.canonical_fingerprint(b64_secret)
    c_fp_url, fmt_url, _ = fp.canonical_fingerprint(url_secret)

    assert c_fp_raw == c_fp_b64, f"Mismatch in canonical HMAC: raw={c_fp_raw[:12]} vs b64={c_fp_b64[:12]}"
    assert c_fp_raw == c_fp_url, f"Mismatch in canonical HMAC: raw={c_fp_raw[:12]} vs url={c_fp_url[:12]}"
    print(f"    [+] Canonical Blind HMAC Matches Across Formats:")
    print(f"        Raw:        {raw_secret[:12]}... -> {c_fp_raw[:16]}... (fmt: {fmt_raw})")
    print(f"        Base64:     {b64_secret[:12]}... -> {c_fp_b64[:16]}... (fmt: {fmt_b64})")
    print(f"        URL-Encode: {url_secret[:12]}... -> {c_fp_url[:16]}... (fmt: {fmt_url})")

    # 2. Simulate cross-service sprawl with heterogeneous representations
    fp.pod_name = "auth-service-pod-1a"
    fp.namespace = "security"
    fp.record(raw_secret)

    fp.pod_name = "payment-service-pod-8b"
    fp.namespace = "production"
    fp.record(b64_secret)

    fp.pod_name = "analytics-worker-pod-3c"
    fp.namespace = "data"
    fp.record(url_secret)

    # 3. Query Sprawl Report
    sprawl = fp.sprawl_report()
    assert len(sprawl) == 1, f"Expected 1 grouped sprawl node, found {len(sprawl)}"
    node = sprawl[0]
    assert node["canonical_fingerprint"] == c_fp_raw
    assert node["distinct_services"] == 3, f"Expected 3 distinct services, got {node['distinct_services']}"
    assert node["distinct_pods"] == 3
    assert node["is_multi_representation"] is True
    assert set(node["representations_observed"]) >= {"raw", "base64"}

    print(f"    [+] Cross-Service Sprawl Graph Successfully Unified:")
    print(f"        Canonical Hash:         {node['canonical_fingerprint'][:16]}...")
    print(f"        Distinct Services:      {node['distinct_services']} ({', '.join(node['services'])})")
    print(f"        Representations Seen:   {node['representations_observed']}")
    print(f"        Multi-Representation:   {node['is_multi_representation']}")

    print("[PASS] Test 3: Transformation-Aware Secret Lineage verified successfully.")


def test_autonomous_containment_engine(tmpdir: Path):
    print("\n" + "="*70)
    print("TEST 4: Autonomous Containment Engine (Blast Radius & Policy Triggering)")
    print("="*70)

    containment_db = str(tmpdir / "containment.db")
    lineage_db = str(tmpdir / "lineage_containment.db")
    lineage_key = str(tmpdir / "lineage_containment.key")

    fp = Fingerprinter(db_path=lineage_db, key_path=lineage_key)
    engine = ContainmentEngine(db_path=containment_db, lineage_db_path=lineage_db, mode="dry_run")

    # Seed cross-service sprawl to establish blast radius >= 3 services
    leaked_aws_key = "AKIAIOSFODNN7CRITICALKEY"
    c_fp, _, _ = fp.canonical_fingerprint(leaked_aws_key)

    for svc in ["ingress-controller-1", "payment-service-2", "backup-worker-3"]:
        fp.pod_name = svc
        fp.namespace = "prod"
        fp.record(leaked_aws_key)

    # Trigger Containment Assessment
    event = engine.assess_and_contain(
        ref_id="sec-crit-9988",
        fingerprint=c_fp,
        secret_type="aws",
        scs_score=100,
        pod_name="ingress-controller-1",
        namespace="prod"
    )

    print(f"    [+] Containment Assessment Generated:")
    print(f"        Event ID:         {event['event_id']}")
    print(f"        Severity:         {event['severity']}")
    print(f"        Policy:           {event['policy']}")
    print(f"        Action:           {event['action']}")
    print(f"        Status:           {event['status']}")
    print(f"        Blast Radius:     {event['blast_radius_services']} services, {event['blast_radius_pods']} pods")
    print(f"        MTTC Latency:     {event['mttc_ms']:.3f} ms")

    assert event["severity"] == "CRITICAL", f"Expected CRITICAL severity, got {event['severity']}"
    assert event["policy"] == "Cloud Credential Auto-Rotation"
    assert event["action"] == "TRIGGER_CREDENTIAL_ROTATION"
    assert event["status"] == "RECOMMENDED_DRY_RUN"
    assert event["blast_radius_services"] >= 3
    assert event["mttc_ms"] < 20.0, f"MTTC exceeded target: {event['mttc_ms']} ms"

    # Execute Containment Action
    exec_res = engine.execute_action(event["event_id"], actor="ciso-auto-approver")
    assert exec_res["success"] is True
    assert exec_res["status"] == "EXECUTED"
    print(f"    [+] Containment Execution Authorized: Action '{exec_res['action']}' status={exec_res['status']}")

    # Verify Metrics Aggregation
    metrics = engine.get_metrics()
    assert metrics["total_events"] >= 1
    assert metrics["executed_containments"] >= 1
    assert metrics["critical_exposures"] >= 1
    print(f"    [+] Containment Metrics Verified: Total={metrics['total_events']}, Executed={metrics['executed_containments']}, Avg MTTC={metrics['avg_mttc_ms']} ms")

    print("[PASS] Test 4: Autonomous Containment Engine verified successfully.")


def test_fastapi_rest_endpoints(tmpdir: Path):
    print("\n" + "="*70)
    print("TEST 5: FastAPI REST Endpoints Integration")
    print("="*70)

    # Point sidecar paths to temporary databases for isolated test
    os.environ["VAULT_DB_PATH"] = str(tmpdir / "api_vault.db")
    os.environ["VAULT_KEY_PATH"] = str(tmpdir / "api_vault.key")
    os.environ["LINEAGE_DB_PATH"] = str(tmpdir / "api_lineage.db")
    os.environ["LINEAGE_KEY_PATH"] = str(tmpdir / "api_lineage.key")
    os.environ["CONTAINMENT_DB_PATH"] = str(tmpdir / "api_containment.db")

    client = TestClient(app)

    # 1. Preseed Secret via REST
    resp = client.post("/api/vault/preseed", json={
        "plaintext": "ghp_ApiTestingKey998877665544",
        "label": "API Test Admin Token",
        "scs_score": 100,
        "suppress_lineage": True,
        "actor": "api-tester"
    })
    assert resp.status_code == 200, f"API failed: {resp.text}"
    body = resp.json()
    assert body["success"] is True and "ref_id" in body
    print(f"    [+] POST /api/vault/preseed -> OK (ref_id={body['ref_id']})")

    # 2. Get Exemptions
    resp = client.get("/api/lineage/exemptions")
    assert resp.status_code == 200
    exemptions = resp.json()
    assert len(exemptions) >= 1
    ex_fp = exemptions[0]["fingerprint"]
    print(f"    [+] GET /api/lineage/exemptions -> OK ({len(exemptions)} active exemptions)")

    # 3. Add explicit exemption
    resp = client.post("/api/lineage/exempt", json={
        "secret": "stripe_sk_test_51Mz99ExplicitExemptionKey",
        "label": "Stripe Dev Key Exemption",
        "created_by": "api-tester"
    })
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    print("    [+] POST /api/lineage/exempt -> OK")

    # 4. Containment Policies & Metrics
    resp_pol = client.get("/api/containment/policies")
    assert resp_pol.status_code == 200 and len(resp_pol.json()) >= 4
    print(f"    [+] GET /api/containment/policies -> OK ({len(resp_pol.json())} default policies)")

    resp_met = client.get("/api/containment/metrics")
    assert resp_met.status_code == 200
    print(f"    [+] GET /api/containment/metrics -> OK ({resp_met.json()['containment_mode']} mode)")

    print("[PASS] Test 5: FastAPI REST Endpoints verified successfully.")


if __name__ == "__main__":
    t_start = time.perf_counter()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_vault_preseed_and_exemption(tmp_path)
        test_adaptive_evasion_defense()
        test_canonical_secret_lineage(tmp_path)
        test_autonomous_containment_engine(tmp_path)
        test_fastapi_rest_endpoints(tmp_path)

    elapsed = time.perf_counter() - t_start
    print("\n" + "="*70)
    print(f"ALL 5 NOVELTY & CAPABILITY TESTS PASSED WITH EXIT CODE 0 ({elapsed:.2f}s)")
    print("="*70 + "\n")
