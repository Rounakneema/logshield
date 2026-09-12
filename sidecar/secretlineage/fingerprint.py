"""
SecretLineage — Privacy-Preserving Secret Reuse Tracker
=========================================================
Every secret detected by LogMask gets fingerprinted and compared
across pods/namespaces to answer:

  "Is this secret supposed to be here, and how widespread is it?"

WHY KEYED HMAC INSTEAD OF PLAIN SHA-256:
  Many real secrets — especially passwords — don't have enough
  entropy to resist an offline dictionary attack against a plain hash.
  An attacker with access to the lineage SQLite file could hash
  common passwords and compare them against stored fingerprints.

  A KEYED HMAC (HMAC-SHA256 with a 256-bit secret key held only
  in /data/lineage.key) defeats this entirely. Without the key,
  the fingerprint database is computationally irreversible.
"""

import hmac
import hashlib
import os
import sqlite3
import time
from pathlib import Path


class Fingerprinter:
    def __init__(
        self,
        db_path: str = "/data/lineage.db",
        key_path: str = "/data/lineage.key",
    ):
        self.db_path   = db_path
        self._hmac_key = self._load_or_create_key(key_path)
        self.pod_name  = os.environ.get("POD_NAME", "unknown")
        self.namespace = os.environ.get("NAMESPACE", "default")
        self._init_db()

    def _load_or_create_key(self, key_path: str) -> bytes:
        path = Path(key_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return path.read_bytes()
        key = os.urandom(32)   # 256-bit key
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
                CREATE TABLE IF NOT EXISTS lineage (
                    fingerprint       TEXT NOT NULL,
                    pod_name          TEXT NOT NULL,
                    namespace         TEXT NOT NULL,
                    first_seen        INTEGER NOT NULL,
                    last_seen         INTEGER NOT NULL,
                    occurrence_count  INTEGER DEFAULT 1,
                    is_registered     INTEGER DEFAULT 0,
                    PRIMARY KEY (fingerprint, pod_name, namespace)
                )
            """)

    def record(self, secret: str):
        """
        Called once per detected secret. Never stores plaintext.
        """
        fp = self._fingerprint(secret)
        now = int(time.time())
        is_reg = int(self._check_k8s_registry(secret))

        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT occurrence_count FROM lineage "
                "WHERE fingerprint=? AND pod_name=? AND namespace=?",
                (fp, self.pod_name, self.namespace),
            ).fetchone()

            if existing:
                conn.execute(
                    "UPDATE lineage SET last_seen=?, occurrence_count=occurrence_count+1, "
                    "is_registered=? WHERE fingerprint=? AND pod_name=? AND namespace=?",
                    (now, is_reg, fp, self.pod_name, self.namespace),
                )
            else:
                conn.execute(
                    "INSERT INTO lineage VALUES (?,?,?,?,?,1,?)",
                    (fp, self.pod_name, self.namespace, now, now, is_reg),
                )

    def sprawl_report(self) -> list:
        now = int(time.time())

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT
                    fingerprint,
                    COUNT(DISTINCT pod_name)       AS pod_count,
                    MIN(first_seen)                AS first_seen,
                    SUM(occurrence_count)          AS occurrences,
                    MAX(is_registered)             AS is_registered
                FROM lineage
                GROUP BY fingerprint
            """).fetchall()

        report = []
        for fp, pod_count, first_seen, occurrences, is_registered in rows:
            age_days   = (now - first_seen) / 86400
            age_factor = min(age_days / 30, 10)
            penalty    = 1.0 if is_registered else 2.0
            risk       = round(pod_count * age_factor * penalty, 2)

            if risk >= 10:
                severity = "CRITICAL"
            elif risk >= 5:
                severity = "HIGH"
            elif risk >= 2:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            report.append({
                "fingerprint":   fp[:16] + "...",
                "pod_count":     pod_count,
                "age_days":      round(age_days, 1),
                "occurrences":   occurrences,
                "is_registered": bool(is_registered),
                "risk_score":    risk,
                "severity":      severity,
            })

        return sorted(report, key=lambda x: x["risk_score"], reverse=True)

    def _fingerprint(self, secret: str) -> str:
        return hmac.new(
            self._hmac_key,
            secret.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _check_k8s_registry(self, secret: str) -> bool:
        try:
            from kubernetes import client, config
            try:
                config.load_incluster_config()
            except Exception:
                config.load_kube_config()

            v1 = client.CoreV1Api()
            k8s_secrets = v1.list_namespaced_secret(self.namespace)

            import base64
            for ks in k8s_secrets.items:
                if not ks.data:
                    continue
                for _key, encoded in ks.data.items():
                    try:
                        decoded = base64.b64decode(encoded).decode("utf-8", errors="ignore")
                        if decoded == secret:
                            return True
                    except Exception:
                        pass
            return False
        except Exception:
            return False   # fail open
