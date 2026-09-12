"""
SecureReveal — Encrypted Vault with Audited Retrieval
======================================================
Every value masked by LogMask is:
  1. Encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
  2. Stored in SQLite under a unique reference ID (e.g. SEC-A1B2C3D4)
  3. Retrievable ONLY via authenticated, authorised request
  4. Auto-expired after a configurable TTL (default 30 days)

CRITICAL DESIGN DECISION — AUDIT LOG BEFORE AUTHORISATION:
  The audit record is written BEFORE the authorisation check runs.
  This means a denied, unauthorised retrieval attempt is still
  permanently recorded. Most naive implementations only log
  successful accesses, silently losing the most security-relevant
  event. We record EVERYTHING.
"""

import os
import sqlite3
import time
import uuid
import json
from pathlib import Path
from cryptography.fernet import Fernet


class Vault:
    def __init__(
        self,
        db_path: str = "/data/vault.db",
        key_path: str = "/data/vault.key",
        default_ttl_days: int = 30,
    ):
        self.db_path = db_path
        self.default_ttl_days = default_ttl_days
        self._fernet = Fernet(self._load_or_create_key(key_path))
        self._init_db()

    def _load_or_create_key(self, key_path: str) -> bytes:
        path = Path(key_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return path.read_bytes()
        key = Fernet.generate_key()
        path.write_bytes(key)
        try:
            os.chmod(key_path, 0o400)
        except Exception:
            pass
        return key

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    ref_id        TEXT    PRIMARY KEY,
                    ciphertext    BLOB    NOT NULL,
                    scs_score     INTEGER,
                    factors_json  TEXT,
                    pod_name      TEXT,
                    namespace     TEXT,
                    created_at    INTEGER NOT NULL,
                    expires_at    INTEGER NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_id    TEXT    NOT NULL,
                    action    TEXT    NOT NULL,
                    actor     TEXT,
                    reason    TEXT,
                    timestamp INTEGER NOT NULL,
                    outcome   TEXT    NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ref ON audit_log(ref_id)")

    def store(self, plaintext: str, scs_score: int, factors: dict) -> str:
        ref_id     = f"SEC-{uuid.uuid4().hex[:8].upper()}"
        ciphertext = self._fernet.encrypt(plaintext.encode("utf-8"))
        now        = int(time.time())
        expires_at = now + (self.default_ttl_days * 86400)
        pod_name   = os.environ.get("POD_NAME", "unknown")
        namespace  = os.environ.get("NAMESPACE", "default")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO vault VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ref_id, ciphertext, scs_score,
                 json.dumps(factors), pod_name, namespace, now, expires_at),
            )
            conn.execute(
                "INSERT INTO audit_log (ref_id, action, actor, reason, timestamp, outcome) "
                "VALUES (?, 'STORE', 'logshield-sidecar', 'automatic_detection', ?, 'STORED')",
                (ref_id, now),
            )
        return ref_id

    def retrieve(self, ref_id: str, actor: str, reason: str) -> tuple:
        now = int(time.time())

        # Step 1: Log the attempt BEFORE any check
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_log (ref_id, action, actor, reason, timestamp, outcome) "
                "VALUES (?, 'RETRIEVE', ?, ?, ?, 'ATTEMPTED')",
                (ref_id, actor, reason, now),
            )

        # Step 2: Authorisation check
        if not self._is_authorised(actor):
            self._audit(ref_id, actor, reason, now, "DENIED")
            return False, f"Actor '{actor}' is not authorised to retrieve vault entries."

        # Step 3: Look up
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT ciphertext, expires_at FROM vault WHERE ref_id = ?",
                (ref_id,),
            ).fetchone()

        if not row:
            self._audit(ref_id, actor, reason, now, "NOT_FOUND")
            return False, f"Reference ID {ref_id} not found."

        ciphertext, expires_at = row

        # Step 4: Expiry check
        if now > expires_at:
            self._audit(ref_id, actor, reason, now, "EXPIRED")
            return False, f"Reference ID {ref_id} has expired."

        # Step 5: Decrypt
        plaintext = self._fernet.decrypt(ciphertext).decode("utf-8")
        self._audit(ref_id, actor, reason, now, "SUCCESS")
        return True, plaintext

    def expire_old_entries(self):
        now = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM vault WHERE expires_at < ?", (now,))

    def _is_authorised(self, actor: str) -> bool:
        allowed = os.environ.get("AUTHORIZED_ACTORS", "admin,security-team").split(",")
        return actor.strip() in [a.strip() for a in allowed]

    def _audit(self, ref_id: str, actor: str, reason: str, ts: int, outcome: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_log (ref_id, action, actor, reason, timestamp, outcome) "
                "VALUES (?, 'RETRIEVE', ?, ?, ?, ?)",
                (ref_id, actor, reason, ts, outcome),
            )
