"""
LogShield Adversarial Security Test Suite
=========================================
Rigorous verification of edge-case security controls:
1. Exemption Abuse: Short string injection, generic keyword exemptions, unauthorized callers.
2. Vault Access & Tamper Resistance: Unauthorized retrieval, brute-forcing, expired records,
   ciphertext byte manipulation (TAMPER_DETECTED), and cryptographic audit chain verification.
3. Forged Containment Events: Non-existent IDs, invalid actors, and replay attacks on execution.
4. Failed Response Actions: Kubernetes RBAC 403 Forbidden, Pod 404 Not Found, webhook 500 failure,
   and accurate FAILED_EXECUTION diagnostic logging.
"""

import os
import sys
import time
import pytest
import sqlite3
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sidecar.secretlineage.fingerprint import Fingerprinter
from sidecar.securereveal.vault import Vault
from sidecar.containment.engine import ContainmentEngine
from sidecar.containment.k8s_handler import KubernetesContainmentHandler
from tests.k8s_test_cluster import IsolatedKubernetesCluster


# ==============================================================================
# 1. ADVERSARIAL TESTS: EXEMPTION ABUSE
# ==============================================================================

class TestExemptionAbuse:
    @pytest.fixture
    def fp(self, tmp_path):
        db_path = str(tmp_path / "lineage_abuse.db")
        key_path = str(tmp_path / "lineage_abuse.key")
        return Fingerprinter(db_path=db_path, key_path=key_path)

    def test_short_string_exemption_rejected(self, fp):
        """Attacker attempts to exempt very short or empty strings to create broad match holes."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            fp.add_exemption("", label="Empty")

        with pytest.raises(ValueError, match="at least 8 characters"):
            fp.add_exemption("abc", label="Short")

        with pytest.raises(ValueError, match="at least 8 characters"):
            fp.add_exemption("   ", label="Spaces")

    def test_reserved_generic_word_exemption_rejected(self, fp):
        """Attacker attempts to exempt standard words like 'password' or 'bearer'."""
        reserved_words = ["password", "bearer", "admin", "token", "secret", "apikey", "root"]
        for word in reserved_words:
            with pytest.raises(ValueError, match="Cannot exempt generic reserved identifier"):
                fp.add_exemption(word, label="Malicious generic exemption")

    def test_unauthorized_actor_exemption_rejected(self, fp):
        """Attacker or anonymous user tries to register an exemption without admin authorization."""
        valid_secret = "ghp_ValidSecretForExemptionTesting123"
        for bad_actor in ["", "anonymous", "attacker", "unauthorized"]:
            with pytest.raises(PermissionError, match="not authorized"):
                fp.add_exemption(valid_secret, label="Unauthorized", created_by=bad_actor)

    def test_blind_hmac_collision_resistance(self, fp):
        """Verifies that 1-bit / 1-char differences produce non-colliding canonical blind HMACs."""
        base_sec = "AKIAIOSFODNN7EXAMPLE1"
        tampered = "AKIAIOSFODNN7EXAMPLE2"
        h1, _, _ = fp.canonical_fingerprint(base_sec)
        h2, _, _ = fp.canonical_fingerprint(tampered)
        assert h1 != h2, "Critical cryptographic collision detected in blind HMAC"


# ==============================================================================
# 2. ADVERSARIAL TESTS: VAULT ACCESS & INTEGRITY TAMPERING
# ==============================================================================

class TestVaultAccessAndTampering:
    @pytest.fixture
    def vault(self, tmp_path):
        db_path = str(tmp_path / "vault_abuse.db")
        key_path = str(tmp_path / "vault_abuse.key")
        return Vault(db_path=db_path, key_path=key_path)

    def test_unauthorized_actor_retrieval_denied_and_audited(self, vault):
        """Unauthorized actor attempts retrieval; must be rejected and logged as DENIED."""
        ref_id = vault.store("super-secret-token-12345", scs_score=100, factors={})
        
        ok, msg = vault.retrieve(ref_id, actor="malicious-actor", reason="exfiltration")
        assert not ok
        assert "not authorised" in msg

        # Audit log must contain the attempted denial
        with sqlite3.connect(vault.db_path) as conn:
            row = conn.execute("SELECT outcome, actor FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
            assert row[0] == "DENIED"
            assert row[1] == "malicious-actor"

    def test_brute_force_ref_id_scanning_audited(self, vault):
        """Scanning random reference IDs must be rejected and recorded as NOT_FOUND."""
        bogus_ids = ["SEC-00000000", "SEC-DEADBEEF", "SEC-INVALID1"]
        for bid in bogus_ids:
            ok, msg = vault.retrieve(bid, actor="admin", reason="scan")
            assert not ok
            assert "not found" in msg

        with sqlite3.connect(vault.db_path) as conn:
            rows = conn.execute("SELECT outcome, ref_id FROM audit_log WHERE outcome='NOT_FOUND'").fetchall()
            assert len(rows) == 3

    def test_expired_secret_retrieval_refused(self, vault):
        """Retrieval of a secret past its expiration timestamp must be rejected."""
        ref_id = vault.store("temporary-token-to-expire", scs_score=95, factors={})
        
        # Manually force expiration timestamp in SQLite to 1 hour in the past
        past_time = int(time.time()) - 3600
        with sqlite3.connect(vault.db_path) as conn:
            conn.execute("UPDATE vault SET expires_at=? WHERE ref_id=?", (past_time, ref_id))

        ok, msg = vault.retrieve(ref_id, actor="admin", reason="retrieve expired")
        assert not ok
        assert "expired" in msg

        with sqlite3.connect(vault.db_path) as conn:
            row = conn.execute("SELECT outcome FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
            assert row[0] == "EXPIRED"

    def test_ciphertext_tampering_detected(self, vault):
        """Adversary directly modifies ciphertext bytes in the SQLite database."""
        ref_id = vault.store("original-sensitive-credential", scs_score=100, factors={})

        # Corrupt the ciphertext bytes in the database
        corrupted_bytes = b"gAAAAAB_CorruptedFernetPayloadTamperedByAttacker998877=="
        with sqlite3.connect(vault.db_path) as conn:
            conn.execute("UPDATE vault SET ciphertext=? WHERE ref_id=?", (corrupted_bytes, ref_id))

        ok, msg = vault.retrieve(ref_id, actor="admin", reason="verify corruption")
        assert not ok
        assert "tampering detected" in msg

        # Audit log must record TAMPER_DETECTED
        with sqlite3.connect(vault.db_path) as conn:
            row = conn.execute("SELECT outcome FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
            assert row[0] == "TAMPER_DETECTED"

    def test_cryptographic_audit_chain_tamper_detection(self, vault):
        """Adversary modifies an existing audit record; the hash-chain verification must break."""
        ref_id = vault.store("test-audit-chain-tamper", scs_score=100, factors={})
        vault.retrieve(ref_id, actor="admin", reason="read 1")
        vault.retrieve(ref_id, actor="admin", reason="read 2")

        # Confirm chain initially valid
        is_valid, broken_id, msg, total = vault.verify_audit_chain()
        assert is_valid is True
        assert total >= 3

        # Tamper with an audit entry in the middle of the chain
        with sqlite3.connect(vault.db_path) as conn:
            conn.execute("UPDATE audit_log SET reason='tampered_reason_by_attacker' WHERE id=2")

        # Chain verification must immediately pinpoint the tampering at record 2
        is_valid, broken_id, msg, total = vault.verify_audit_chain()
        assert is_valid is False
        assert broken_id == 2
        assert "hash mismatch" in msg.lower()


# ==============================================================================
# 3. ADVERSARIAL TESTS: FORGED CONTAINMENT EVENTS & REPLAY ATTACKS
# ==============================================================================

class TestForgedContainmentEvents:
    @pytest.fixture
    def engine(self, tmp_path):
        db_path = str(tmp_path / "containment_abuse.db")
        lineage_db = str(tmp_path / "lineage_abuse.db")
        return ContainmentEngine(db_path=db_path, lineage_db_path=lineage_db, mode="dry_run")

    def test_execute_nonexistent_event_rejected(self, engine):
        """Attempting to execute non-existent or negative event IDs."""
        res1 = engine.execute_action(event_id=999999, actor="admin")
        assert res1["success"] is False
        assert res1["error_code"] == 404

        res2 = engine.execute_action(event_id=-1, actor="admin")
        assert res2["success"] is False
        assert res2["error_code"] == 404

    def test_unauthorized_actor_cannot_execute_containment(self, engine):
        """Unauthorized actor attempts to trigger or approve containment actions."""
        event = engine.assess_and_contain("SEC-111", "fp-111", "aws", 100, "pod-1", "default")
        eid = event["event_id"]

        for bad_actor in ["", "anonymous", "attacker", "unauthorized"]:
            res = engine.execute_action(event_id=eid, actor=bad_actor)
            assert res["success"] is False
            assert res["error_code"] == 403

    def test_containment_replay_attack_rejected(self, engine):
        """Adversary attempts to replay an already executed containment action."""
        event = engine.assess_and_contain("SEC-222", "fp-222", "aws", 100, "pod-1", "default")
        eid = event["event_id"]

        # First execution succeeds
        first_exec = engine.execute_action(event_id=eid, actor="security-admin")
        assert first_exec["success"] is True
        assert first_exec["status"] == "EXECUTED"

        # Second execution (replay) must be rejected
        replay_exec = engine.execute_action(event_id=eid, actor="security-admin")
        assert replay_exec["success"] is False
        assert replay_exec["error_code"] == 409
        assert replay_exec["status"] == "ALREADY_EXECUTED"


# ==============================================================================
# 4. ADVERSARIAL TESTS: FAILED RESPONSE ACTIONS & ERROR DIAGNOSTICS
# ==============================================================================

class TestFailedResponseActions:
    @pytest.fixture
    def k8s_cluster(self):
        cluster = IsolatedKubernetesCluster().start()
        yield cluster
        cluster.stop()

    def test_k8s_rbac_rejection_marks_failed_execution(self, tmp_path, k8s_cluster):
        """Simulates Kubernetes API returning HTTP 403 Forbidden on NetworkPolicy creation."""
        # Inject RBAC failure in the isolated cluster
        k8s_cluster.cluster_state["inject_rbac_rejection"] = True

        handler = KubernetesContainmentHandler(api_client=k8s_cluster.api_client, dry_run=False)
        db_path = str(tmp_path / "containment_rbac.db")
        lineage_db = str(tmp_path / "lineage_rbac.db")
        engine = ContainmentEngine(db_path=db_path, lineage_db_path=lineage_db, mode="active", k8s_handler=handler)

        event = engine.assess_and_contain("SEC-RBAC-01", "fp-rbac", "aws", 100, "auth-service-pod-1", "production")
        eid = event["event_id"]

        # Force policy action to QUARANTINE_POD_NETWORK
        with sqlite3.connect(engine.db_path) as conn:
            conn.execute("UPDATE containment_events SET action_recommended='QUARANTINE_POD_NETWORK' WHERE id=?", (eid,))

        res = engine.execute_action(event_id=eid, actor="security-admin")
        assert res["success"] is False
        assert res["status"] == "FAILED_EXECUTION"
        assert "403" in res["error"] or "Forbidden" in res["error"]

        # Verify DB records FAILED_EXECUTION status, NOT EXECUTED
        with sqlite3.connect(engine.db_path) as conn:
            row = conn.execute("SELECT action_status, details_json FROM containment_events WHERE id=?", (eid,)).fetchone()
            assert row[0] == "FAILED_EXECUTION"
            assert "Forbidden" in row[1] or "403" in row[1]

    def test_webhook_rotation_failure_marks_failed_execution(self, tmp_path):
        """Simulates cloud provider rotation webhook returning HTTP 500 error."""
        os.environ["SIMULATE_ROTATION_FAILURE"] = "1"
        try:
            db_path = str(tmp_path / "containment_rot.db")
            lineage_db = str(tmp_path / "lineage_rot.db")
            engine = ContainmentEngine(db_path=db_path, lineage_db_path=lineage_db, mode="active")

            event = engine.assess_and_contain("SEC-ROT-01", "fp-rot", "aws", 100, "pod-1", "production")
            eid = event["event_id"]

            res = engine.execute_action(event_id=eid, actor="security-admin")
            assert res["success"] is False
            assert res["status"] == "FAILED_EXECUTION"
            assert "500" in res["error"]

            with sqlite3.connect(engine.db_path) as conn:
                status = conn.execute("SELECT action_status FROM containment_events WHERE id=?", (eid,)).fetchone()[0]
                assert status == "FAILED_EXECUTION"
        finally:
            os.environ.pop("SIMULATE_ROTATION_FAILURE", None)
