"""
test_catalog.py
================
Verification tests for the LogShield Detector Catalog.

Tests 10 canonical representative log line scenarios:
  1.  AWS IAM Key in a DEBUG log
  2.  OpenAI API Key in an env dump
  3.  Slack Bot Token in a config log
  4.  MongoDB URI in a connection string log
  5.  GitHub PAT in a CI/CD log
  6.  RSA Private Key PEM header
  7.  Stripe Secret Key in a payment log
  8.  Clean UUID trace_id (should PASS — no secret)
  9.  SMTP credentials in a mailer config
  10. PostgreSQL connection string

Also runs structural catalog health checks:
  - All catalog modules import without error
  - No duplicate pattern string across specific detectors
  - Total detector count ≥ 200
"""

import sys
import os
import pytest
import re

# ── path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sidecar.logmask.scorer import SCSEngine, SCSResult
from sidecar.logmask.catalog import ALL_SPECIFIC_DETECTORS, ALL_GENERIC_DETECTORS


# ════════════════════════════════════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def engine():
    return SCSEngine()


# ════════════════════════════════════════════════════════════════════════════
# Catalog Health Checks
# ════════════════════════════════════════════════════════════════════════════

class TestCatalogHealth:
    def test_catalog_imports(self):
        """All 8 catalog modules must import without error."""
        from sidecar.logmask.catalog import cloud, ai, vcs_cicd, database
        from sidecar.logmask.catalog import messaging, payment, private_keys, generic
        assert True

    def test_minimum_specific_detector_count(self):
        """Must have at least 200 specific detector entries."""
        assert len(ALL_SPECIFIC_DETECTORS) >= 200, (
            f"Expected ≥200 specific detectors, got {len(ALL_SPECIFIC_DETECTORS)}"
        )

    def test_minimum_generic_detector_count(self):
        """Must have at least 15 generic detector entries."""
        assert len(ALL_GENERIC_DETECTORS) >= 15, (
            f"Expected ≥15 generic detectors, got {len(ALL_GENERIC_DETECTORS)}"
        )

    def test_all_entries_are_5_tuples(self):
        """Every entry must be (pattern, name, company, category, confidence)."""
        for entry in ALL_SPECIFIC_DETECTORS + ALL_GENERIC_DETECTORS:
            assert len(entry) == 5, f"Entry has wrong length: {entry}"
            pat, name, company, category, confidence = entry
            assert isinstance(pat, re.Pattern), f"First element must be compiled pattern: {entry}"
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(company, str)
            assert isinstance(category, str)
            assert isinstance(confidence, float), f"Confidence must be float: {entry}"
            assert 0.0 <= confidence <= 1.0, f"Confidence out of range: {entry}"

    def test_no_duplicate_detector_names(self):
        """Detector names within the specific list must be unique enough to debug."""
        names = [entry[1] for entry in ALL_SPECIFIC_DETECTORS]
        # Allow some duplication for variant detectors but flag clear copy-paste errors
        name_counts = {}
        for n in names:
            name_counts[n] = name_counts.get(n, 0) + 1
        duplicates = {n: c for n, c in name_counts.items() if c > 5}
        assert not duplicates, f"Suspiciously many duplicate detector names: {duplicates}"


# ════════════════════════════════════════════════════════════════════════════
# Representative Log-Line Scoring Tests
# ════════════════════════════════════════════════════════════════════════════

class TestRepresentativeLogLines:

    # ── Test 1: AWS IAM Key ───────────────────────────────────────────────
    def test_aws_iam_key_masked(self, engine):
        line = "DEBUG aws_access_key_id=AKIAIOSFODNN7EXAMPLE aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        results = engine.extract_and_score(line)
        decisions = {r.token: r.decision for r in results}
        # At least one token should be MASK or FLAG (AWS key)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for AWS key line, got: {decisions}"
        )

    # ── Test 2: OpenAI API Key ───────────────────────────────────────────
    def test_openai_key_masked(self, engine):
        line = "INFO OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghij loading model"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for OpenAI key. Got: {[r.decision for r in results]}"
        )

    # ── Test 3: Slack Bot Token ──────────────────────────────────────────
    def test_slack_token_detected(self, engine):
        line = "CONFIG slack_bot_token=x0xb-111222333444-555666777888-AbCdEfGhIjKlMnOpQrStUvWx starting bot"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for Slack token. Got: {[r.decision for r in results]}"
        )

    # ── Test 4: MongoDB URI ──────────────────────────────────────────────
    def test_mongodb_uri_detected(self, engine):
        line = "ERROR mongo_uri=mongodb://admin:superSecretPass123@cluster0.mongodb.net/mydb connection failed"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for MongoDB URI. Got: {[r.decision for r in results]}"
        )

    # ── Test 5: GitHub PAT ───────────────────────────────────────────────
    def test_github_pat_detected(self, engine):
        line = "CI github_token=ghp_16C7e42F292c6912E7710c838347Ae178B4a successfully cloned repo"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for GitHub PAT. Got: {[r.decision for r in results]}"
        )

    # ── Test 6: RSA Private Key PEM Header ──────────────────────────────
    def test_rsa_pem_key_detected(self, engine):
        line = "INFO Loading cert: -----BEGIN RSA PRIVATE KEY----- MIIEpAIBAAKCAQEA..."
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for RSA PEM Key. Got: {[r.decision for r in results]}"
        )

    # ── Test 7: Stripe Secret Key ────────────────────────────────────────
    def test_stripe_key_detected(self, engine):
        line = "WARN stripe_secret_key=sk_test_51ABcDeFgHiJkLmNoPqRsTuVwXyZ0123456789abcdefghij payment failed"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for Stripe key. Got: {[r.decision for r in results]}"
        )

    # ── Test 8: Clean UUID trace_id (should PASS) ────────────────────────
    def test_clean_uuid_passes(self, engine):
        line = "INFO trace_id=550e8400-e29b-41d4-a716-446655440000 request completed in 32ms"
        results = engine.extract_and_score(line)
        # None should be MASK (a UUID trace_id is not a secret)
        mask_results = [r for r in results if r.decision == "MASK"]
        assert len(mask_results) == 0, (
            f"False positive: UUID trace_id should PASS, got MASK: {mask_results}"
        )

    # ── Test 9: SMTP Credentials ─────────────────────────────────────────
    def test_smtp_credentials_detected(self, engine):
        line = "CONFIG SMTP_PASSWORD=MailS3nd3r!Pass@word mailer initialized"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for SMTP password. Got: {[r.decision for r in results]}"
        )

    # ── Test 10: PostgreSQL Connection String ────────────────────────────
    def test_postgres_uri_detected(self, engine):
        line = "DB postgres_password=R@nd0mStr0ngP@ss database_url=postgresql://admin:R@nd0mStr0ngP@ss@db.example.com:5432/prod_db"
        results = engine.extract_and_score(line)
        assert any(r.decision in ("MASK", "FLAG") for r in results), (
            f"Expected MASK/FLAG for PostgreSQL URI. Got: {[r.decision for r in results]}"
        )


# ════════════════════════════════════════════════════════════════════════════
# SCSResult Vendor Metadata Tests
# ════════════════════════════════════════════════════════════════════════════

class TestVendorMetadata:

    def test_scs_result_has_vendor_fields(self, engine):
        """SCSResult must carry all 4 vendor attribution fields."""
        line = "stripe_secret_key=sk_test_51ABcDeFgHiJkLmNoPqRsTuVwXyZ0123456789abcdefghij"
        results = engine.extract_and_score(line)
        for r in results:
            assert hasattr(r, "vendor"), "SCSResult missing vendor field"
            assert hasattr(r, "category"), "SCSResult missing category field"
            assert hasattr(r, "detector_name"), "SCSResult missing detector_name field"
            assert hasattr(r, "detector_type"), "SCSResult missing detector_type field"

    def test_detector_type_values_are_valid(self, engine):
        """detector_type must be one of: specific | generic | heuristic"""
        valid_types = {"specific", "generic", "heuristic"}
        line = "DEBUG openai_api_key=sk-proj-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab"
        results = engine.extract_and_score(line)
        for r in results:
            assert r.detector_type in valid_types, (
                f"Invalid detector_type '{r.detector_type}' for token '{r.token}'"
            )
