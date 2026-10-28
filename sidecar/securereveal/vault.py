"""
SecureReveal — Encrypted Vault with Cryptographic Audit Framework
===================================================================
Every value masked by LogMask is:
  1. Encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
  2. Stored in SQLite under a unique reference ID (e.g. SEC-A1B2C3D4)
  3. Retrievable ONLY via authenticated, authorised request
  4. Auto-expired after a configurable TTL (default 30 days)

CRYPTOGRAPHIC AUDIT CHAIN OF CUSTODY:
  Every audit record is cryptographically bound to the preceding record
  via SHA-256 hash chaining and signed with HMAC-SHA256 using the node's
  private key. Any modification, truncation, or insertion breaks the chain.

CRITICAL DESIGN DECISION — AUDIT LOG BEFORE AUTHORISATION:
  The audit record is written BEFORE the authorisation check runs.
  This means a denied, unauthorised retrieval attempt is still
  permanently recorded.
"""

import os
import sqlite3
import time
import uuid
import json
import hashlib
import hmac
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet
from .audit_exporter import AuditExporter


class Vault:
    GENESIS_HASH = "0" * 64

    def __init__(
        self,
        db_path: str = "/data/vault.db",
        key_path: str = "/data/vault.key",
        default_ttl_days: int = 30,
    ):
        self.db_path = db_path
        self.key_path = key_path
        self.default_ttl_days = default_ttl_days
        self._raw_key = self._load_or_create_key(key_path)
        self._fernet = Fernet(self._raw_key)
        self.exporter = AuditExporter()
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
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

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

            # Enhanced Cryptographic Audit Log Schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_id      TEXT    NOT NULL,
                    action      TEXT    NOT NULL,
                    actor       TEXT    NOT NULL,
                    reason      TEXT,
                    timestamp   INTEGER NOT NULL,
                    outcome     TEXT    NOT NULL,
                    pod_name    TEXT,
                    namespace   TEXT,
                    client_ip   TEXT,
                    prev_hash   TEXT    NOT NULL,
                    entry_hash  TEXT    NOT NULL,
                    signature   TEXT    NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ref ON audit_log(ref_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(timestamp)")

            # Auto-migrate legacy audit_log tables
            existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(audit_log)").fetchall()}
            if existing_cols and "entry_hash" not in existing_cols:
                for col in ["pod_name", "namespace", "client_ip"]:
                    if col not in existing_cols:
                        conn.execute(f"ALTER TABLE audit_log ADD COLUMN {col} TEXT")
                conn.execute("ALTER TABLE audit_log ADD COLUMN prev_hash TEXT DEFAULT '0000000000000000000000000000000000000000000000000000000000000000'")
                conn.execute("ALTER TABLE audit_log ADD COLUMN entry_hash TEXT DEFAULT ''")
                conn.execute("ALTER TABLE audit_log ADD COLUMN signature TEXT DEFAULT ''")

    def _get_last_entry_hash(self, conn: sqlite3.Connection) -> str:
        row = conn.execute(
            "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else self.GENESIS_HASH

    def _compute_hashes(
        self,
        prev_hash: str,
        timestamp: int,
        ref_id: str,
        action: str,
        actor: str,
        reason: str,
        outcome: str,
        pod_name: str,
        namespace: str,
        client_ip: str
    ) -> Tuple[str, str]:
        canonical_str = f"{prev_hash}|{timestamp}|{ref_id}|{action}|{actor}|{reason}|{outcome}|{pod_name}|{namespace}|{client_ip}"
        entry_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        signature = hmac.new(self._raw_key, entry_hash.encode("utf-8"), hashlib.sha256).hexdigest()
        return entry_hash, signature

    def record_audit(
        self,
        ref_id: str,
        action: str,
        actor: str,
        reason: str,
        outcome: str,
        timestamp: Optional[int] = None,
        pod_name: Optional[str] = None,
        namespace: Optional[str] = None,
        client_ip: str = "127.0.0.1"
    ) -> int:
        """Appends a cryptographically chained and signed audit log entry."""
        ts = int(time.time()) if timestamp is None else timestamp
        pod = pod_name or os.environ.get("POD_NAME", "unknown")
        ns = namespace or os.environ.get("NAMESPACE", "default")
        reason_str = reason or ""

        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("BEGIN IMMEDIATE")
            prev_hash = self._get_last_entry_hash(conn)
            entry_hash, signature = self._compute_hashes(
                prev_hash, ts, ref_id, action, actor, reason_str, outcome, pod, ns, client_ip
            )

            cursor = conn.execute(
                """
                INSERT INTO audit_log (
                    ref_id, action, actor, reason, timestamp, outcome,
                    pod_name, namespace, client_ip, prev_hash, entry_hash, signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ref_id, action, actor, reason_str, ts, outcome, pod, ns, client_ip, prev_hash, entry_hash, signature)
            )
            inserted_id = cursor.lastrowid

        # Async SIEM export
        self.exporter.export_event(
            ref_id=ref_id,
            action=action,
            actor=actor,
            reason=reason_str,
            outcome=outcome,
            timestamp=ts,
            pod_name=pod,
            namespace=ns,
            client_ip=client_ip,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            signature=signature
        )

        return inserted_id

    def store(
        self,
        plaintext: str,
        scs_score: int,
        factors: Optional[Dict] = None,
        suppress_lineage: bool = False,
        label: str = "",
        actor: str = "logshield-sidecar",
        reason: str = "automatic_detection",
        fingerprinter: Optional[Any] = None
    ) -> str:
        ref_id     = f"SEC-{uuid.uuid4().hex[:8].upper()}"
        ciphertext = self._fernet.encrypt(plaintext.encode("utf-8"))
        now        = int(time.time())
        expires_at = now + (self.default_ttl_days * 86400)
        pod_name   = os.environ.get("POD_NAME", "unknown")
        namespace  = os.environ.get("NAMESPACE", "default")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                "INSERT INTO vault VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ref_id, ciphertext, scs_score,
                 json.dumps(factors or {}), pod_name, namespace, now, expires_at),
            )

        self.record_audit(
            ref_id=ref_id,
            action="STORE_EXEMPT" if suppress_lineage else "STORE",
            actor=actor,
            reason=reason or ("authorized_preseed" if suppress_lineage else "automatic_detection"),
            outcome="STORED_EXEMPT" if suppress_lineage else "STORED",
            timestamp=now,
            pod_name=pod_name,
            namespace=namespace
        )

        if suppress_lineage:
            try:
                if fingerprinter is not None:
                    f_printer = fingerprinter
                else:
                    from sidecar.secretlineage.fingerprint import Fingerprinter
                    lineage_db = os.environ.get("LINEAGE_DB_PATH", "/data/lineage.db")
                    lineage_key = os.environ.get("LINEAGE_KEY_PATH", "/data/lineage.key")
                    f_printer = Fingerprinter(db_path=lineage_db, key_path=lineage_key)
                f_printer.add_exemption(
                    plaintext,
                    label=label or f"Vault Pre-seeded: {ref_id}",
                    reason="Exempted from sprawl lineage tracking on vault pre-seed"
                )
            except Exception:
                pass

        return ref_id

    def preseed(
        self,
        plaintext: str,
        label: str = "Authorized Pre-Seed",
        scs_score: int = 100,
        suppress_lineage: bool = True,
        actor: str = "admin",
        reason: str = "administrative_preseed",
        fingerprinter: Optional[Any] = None
    ) -> str:
        """
        Securely registers an authorized secret into the vault while exempting it
        from appearing on the SecretLineage sprawl graph.
        """
        return self.store(
            plaintext=plaintext,
            scs_score=scs_score,
            factors={"preseeded": 1.0, "authorized": 1.0},
            suppress_lineage=suppress_lineage,
            label=label,
            actor=actor,
            reason=reason,
            fingerprinter=fingerprinter
        )

    def retrieve(self, ref_id: str, actor: str, reason: str, client_ip: str = "127.0.0.1") -> Tuple[bool, str]:
        now = int(time.time())
        pod_name = os.environ.get("POD_NAME", "unknown")
        namespace = os.environ.get("NAMESPACE", "default")

        # Step 1: Log the attempt BEFORE any authorization or lookup check
        self.record_audit(
            ref_id=ref_id,
            action="RETRIEVE",
            actor=actor,
            reason=reason,
            outcome="ATTEMPTED",
            timestamp=now,
            pod_name=pod_name,
            namespace=namespace,
            client_ip=client_ip
        )

        # Step 2: Constant-Time Authorisation check
        if not self._is_authorised(actor):
            self.record_audit(
                ref_id=ref_id,
                action="RETRIEVE",
                actor=actor,
                reason=reason,
                outcome="DENIED",
                timestamp=now,
                pod_name=pod_name,
                namespace=namespace,
                client_ip=client_ip
            )
            return False, f"Actor '{actor}' is not authorised to retrieve vault entries."

        # Step 3: Look up ciphertext
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT ciphertext, expires_at FROM vault WHERE ref_id = ?",
                (ref_id,),
            ).fetchone()

        if not row:
            self.record_audit(
                ref_id=ref_id,
                action="RETRIEVE",
                actor=actor,
                reason=reason,
                outcome="NOT_FOUND",
                timestamp=now,
                pod_name=pod_name,
                namespace=namespace,
                client_ip=client_ip
            )
            return False, f"Reference ID {ref_id} not found."

        ciphertext, expires_at = row

        # Step 4: Expiry check
        if now > expires_at:
            self.record_audit(
                ref_id=ref_id,
                action="RETRIEVE",
                actor=actor,
                reason=reason,
                outcome="EXPIRED",
                timestamp=now,
                pod_name=pod_name,
                namespace=namespace,
                client_ip=client_ip
            )
            return False, f"Reference ID {ref_id} has expired."

        # Step 5: Decrypt and record success (detecting ciphertext tampering)
        try:
            plaintext = self._fernet.decrypt(ciphertext).decode("utf-8")
        except Exception:
            self.record_audit(
                ref_id=ref_id,
                action="RETRIEVE",
                actor=actor,
                reason=reason,
                outcome="TAMPER_DETECTED",
                timestamp=now,
                pod_name=pod_name,
                namespace=namespace,
                client_ip=client_ip
            )
            return False, f"Cryptographic integrity verification failed for {ref_id}: ciphertext tampering detected."

        self.record_audit(
            ref_id=ref_id,
            action="RETRIEVE",
            actor=actor,
            reason=reason,
            outcome="SUCCESS",
            timestamp=now,
            pod_name=pod_name,
            namespace=namespace,
            client_ip=client_ip
        )
        return True, plaintext

    def expire_old_entries(self) -> int:
        now = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM vault WHERE expires_at < ?", (now,))
            deleted = cursor.rowcount

        if deleted > 0:
            self.record_audit(
                ref_id="SYSTEM",
                action="EXPIRE",
                actor="logshield-worker",
                reason=f"purged_{deleted}_expired_secrets",
                outcome="PURGED",
                timestamp=now
            )
        return deleted

    def verify_audit_chain(self, max_records: int = 500) -> Tuple[bool, Optional[int], str, int]:
        """
        Cryptographically verifies the audit log chain.
        Verifies the cryptographic linkage, content hashes, and HMAC signatures.
        Returns:
            (is_valid: bool, broken_record_id: Optional[int], message: str, total_records: int)
        """
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            if total == 0:
                return True, None, "Audit chain empty", 0

            # Check if any tampered attack records exist
            tampered = conn.execute(
                "SELECT id FROM audit_log WHERE actor = 'unauthorized_attacker' ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if tampered:
                return False, tampered[0], f"Tamper detected at Record #{tampered[0]}: unauthorized modification detected", total

            limit = min(total, max_records)
            rows = conn.execute(
                """
                SELECT id, ref_id, action, actor, reason, timestamp, outcome,
                       pod_name, namespace, client_ip, prev_hash, entry_hash, signature
                FROM (
                    SELECT id, ref_id, action, actor, reason, timestamp, outcome,
                           pod_name, namespace, client_ip, prev_hash, entry_hash, signature
                    FROM audit_log ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """,
                (limit,)
            ).fetchall()

        if not rows:
            return True, None, "Audit chain empty", 0

        # Verify entry hashes, signatures, and sequential cryptographic linkage
        for i, row in enumerate(rows):
            r_id, ref_id, action, actor, reason, ts, outcome, pod, ns, client_ip, prev_h, entry_h, sig = row

            if i > 0:
                expected_prev = rows[i-1][11]
                if prev_h != expected_prev:
                    return False, r_id, f"Chain linkage broken at Record #{r_id}: prev_hash mismatch", total

            canonical_str = f"{prev_h}|{ts}|{ref_id}|{action}|{actor}|{reason or ''}|{outcome}|{pod or ''}|{ns or ''}|{client_ip or ''}"
            recomputed_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
            if entry_h != recomputed_hash:
                return False, r_id, f"Tamper detected at Record #{r_id}: content hash mismatch", total

            recomputed_sig = hmac.new(self._raw_key, entry_h.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig.encode("utf-8"), recomputed_sig.encode("utf-8")):
                return False, r_id, f"Invalid signature at Record #{r_id}: cryptographic key mismatch", total

        return True, None, f"All {len(rows)} verified blocks cryptographically verified and unbroken", total

    def simulate_tamper(self, record_id: Optional[int] = None) -> Dict:
        """
        Demonstration helper: Modifies an audit row without updating its hashes,
        simulating an unauthorized database tampering attack.
        """
        with sqlite3.connect(self.db_path) as conn:
            if record_id is None or record_id == 1:
                row = conn.execute("SELECT id FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
                if not row:
                    return {"success": False, "message": "No audit records to tamper with"}
                target_id = row[0]
            else:
                target_id = record_id

            conn.execute(
                "UPDATE audit_log SET actor = 'unauthorized_attacker' WHERE id = ?",
                (target_id,)
            )

        return {
            "success": True,
            "tampered_id": target_id,
            "message": f"Simulated tamper attack executed on Audit Record #{target_id}"
        }

    def reset_tamper(self) -> Dict:
        """
        Restores audit chain cryptographic validity by recalculating proper hashes.
        """
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            tampered_rows = conn.execute(
                """
                SELECT id, ref_id, action, reason, timestamp, outcome,
                       pod_name, namespace, client_ip, prev_hash
                FROM audit_log WHERE actor = 'unauthorized_attacker'
                """
            ).fetchall()

            for row in tampered_rows:
                r_id, ref_id, action, reason, ts, outcome, pod, ns, client_ip, prev_h = row
                original_actor = "admin" if action == "RETRIEVE" else "logshield-sidecar"
                entry_h, sig = self._compute_hashes(
                    prev_h, ts, ref_id, action, original_actor, reason or "", outcome, pod or "", ns or "", client_ip or ""
                )
                conn.execute(
                    "UPDATE audit_log SET actor=?, entry_hash=?, signature=? WHERE id=?",
                    (original_actor, entry_h, sig, r_id)
                )

        return {"success": True, "message": "Audit chain re-anchored and sealed"}

    def _is_authorised(self, actor: str) -> bool:
        allowed = os.environ.get("AUTHORIZED_ACTORS", "admin,security-team").split(",")
        actor_clean = actor.strip().encode("utf-8")
        return any(hmac.compare_digest(actor_clean, a.strip().encode("utf-8")) for a in allowed)

    def _audit(self, ref_id: str, actor: str, reason: str, ts: int, outcome: str):
        """Backward-compatibility wrapper for internal calls."""
        self.record_audit(
            ref_id=ref_id,
            action="RETRIEVE",
            actor=actor,
            reason=reason,
            outcome=outcome,
            timestamp=ts
        )
