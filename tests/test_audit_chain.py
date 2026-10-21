import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import tempfile
import sqlite3
import shutil
import gc
from sidecar.securereveal.vault import Vault


def test_audit_hash_chain_creation_and_verification():
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, "vault.db")
        key_path = os.path.join(tmpdir, "vault.key")
        vault = Vault(db_path=db_path, key_path=key_path)

        # Store two secrets
        ref1 = vault.store("secret_1_value", 95, {"regex": 1.0})
        ref2 = vault.store("secret_2_value", 88, {"regex": 0.85})

        # Retrieve one secret
        vault.retrieve(ref1, "admin", "testing_incident_123")
        # Attempt unauthorized retrieval
        vault.retrieve(ref2, "unauthorized_user", "malicious_attempt")

        # Verify the audit chain
        is_valid, broken_id, message, total = vault.verify_audit_chain()
        assert is_valid is True
        assert broken_id is None
        assert total >= 4
        assert "cryptographically verified" in message
    finally:
        gc.collect()
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_audit_tamper_detection():
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, "vault.db")
        key_path = os.path.join(tmpdir, "vault.key")
        vault = Vault(db_path=db_path, key_path=key_path)

        vault.store("secret_data_abc", 90, {"regex": 1.0})
        vault.store("secret_data_xyz", 85, {"regex": 0.9})

        # Chain initially valid
        is_valid, _, _, total = vault.verify_audit_chain()
        assert is_valid is True
        assert total == 2

        # Simulate tamper attack
        tamper_res = vault.simulate_tamper(record_id=1)
        assert tamper_res["success"] is True

        # Verification must now catch the tamper!
        is_valid, broken_id, msg, _ = vault.verify_audit_chain()
        assert is_valid is False
        assert broken_id == 1
        assert "Tamper detected" in msg

        # Reset tamper and verify recovery
        reset_res = vault.reset_tamper()
        assert reset_res["success"] is True
        is_valid, _, _, _ = vault.verify_audit_chain()
        assert is_valid is True
    finally:
        gc.collect()
        shutil.rmtree(tmpdir, ignore_errors=True)
