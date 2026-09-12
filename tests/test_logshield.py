"""
LogShield Comprehensive Test Suite
====================================
Tests all three modules:
  1. LogMask (SCS Engine, factor evaluation, scoring, thresholds)
  2. SecureReveal (Vault encryption, retrieval, authorization, audit logging, TTL)
  3. SecretLineage (Keyed HMAC fingerprinting, sprawl reporting)
  4. LogShieldInterceptor end-to-end log stream processing
"""

import unittest
import os
import tempfile
import sqlite3
import shutil

from sidecar.logmask.scorer import SCSEngine
from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter
from sidecar.main import LogShieldInterceptor


class TestLogMaskSCS(unittest.TestCase):
    def setUp(self):
        self.engine = SCSEngine()

    def test_database_password_high_score(self):
        line = "DEBUG DATABASE_PASSWORD=MyP@ssw0rd123 connected to db"
        results = self.engine.extract_and_score(line)
        self.assertTrue(len(results) > 0)
        top = max(results, key=lambda r: r.score)
        self.assertGreaterEqual(top.score, 80)
        self.assertEqual(top.decision, "MASK")

    def test_order_id_low_score(self):
        line = "INFO Processed order_id=550e8400-e29b-41d4-a716-446655440000"
        results = self.engine.extract_and_score(line)
        for r in results:
            if r.token == "550e8400-e29b-41d4-a716-446655440000":
                self.assertLess(r.score, 80)

    def test_aws_key_direct_regex(self):
        line = "LOG AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLEwJalrXUtnFEMI"
        results = self.engine.extract_and_score(line)
        self.assertTrue(any(r.decision == "MASK" for r in results))


class TestSecureRevealVault(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "vault.db")
        self.key_path = os.path.join(self.temp_dir, "vault.key")
        self.vault = Vault(db_path=self.db_path, key_path=self.key_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_and_authorised_retrieve(self):
        secret = "SuperSecretPassword123"
        ref_id = self.vault.store(secret, 90, {"regex": 1.0})
        self.assertTrue(ref_id.startswith("SEC-"))

        success, val = self.vault.retrieve(ref_id, actor="admin", reason="incident investigation")
        self.assertTrue(success)
        self.assertEqual(val, secret)

    def test_unauthorised_retrieve_denied_and_audited(self):
        secret = "ConfidentialKey"
        ref_id = self.vault.store(secret, 95, {"regex": 1.0})

        success, val = self.vault.retrieve(ref_id, actor="unauthorized_user", reason="curious")
        self.assertFalse(success)
        self.assertIn("not authorised", val)

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT outcome FROM audit_log WHERE ref_id=? AND actor=?",
                (ref_id, "unauthorized_user")
            ).fetchall()
            outcomes = [r[0] for r in rows]
            self.assertIn("DENIED", outcomes)


class TestSecretLineage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "lineage.db")
        self.key_path = os.path.join(self.temp_dir, "lineage.key")
        self.fp = Fingerprinter(db_path=self.db_path, key_path=self.key_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_record_and_sprawl_report(self):
        secret = "SharedDBPassword123"
        self.fp.record(secret)
        self.fp.record(secret)

        report = self.fp.sprawl_report()
        self.assertEqual(len(report), 1)
        item = report[0]
        self.assertEqual(item["occurrences"], 2)
        self.assertEqual(item["pod_count"], 1)


class TestLogShieldInterceptor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        os.environ["VAULT_DB_PATH"] = os.path.join(self.temp_dir, "vault.db")
        os.environ["VAULT_KEY_PATH"] = os.path.join(self.temp_dir, "vault.key")
        os.environ["LINEAGE_DB_PATH"] = os.path.join(self.temp_dir, "lineage.db")
        os.environ["LINEAGE_KEY_PATH"] = os.path.join(self.temp_dir, "lineage.key")
        self.interceptor = LogShieldInterceptor()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_process_line_redaction(self):
        line = "DEBUG DATABASE_PASSWORD=MyP@ssw0rd123 connected to db"
        sanitised = self.interceptor.process_line(line)
        self.assertNotIn("MyP@ssw0rd123", sanitised)
        self.assertIn("[REDACTED:SEC-", sanitised)
        self.assertEqual(self.interceptor.stats["secrets_masked"], 1)


if __name__ == "__main__":
    unittest.main()
