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
import urllib.parse
import base64
import re
from typing import Tuple, List, Dict, Optional
from pathlib import Path


class Fingerprinter:
    def __init__(
        self,
        db_path: str = "/data/lineage.db",
        key_path: str = "/data/lineage.key",
    ):
        self.db_path   = db_path
        self.key_path  = key_path
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
                    representations   TEXT DEFAULT 'raw',
                    PRIMARY KEY (fingerprint, pod_name, namespace)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lineage_exemptions (
                    fingerprint      TEXT PRIMARY KEY,
                    raw_fingerprint  TEXT,
                    label            TEXT NOT NULL,
                    reason           TEXT,
                    added_at         INTEGER NOT NULL
                )
            """)
            # Auto-migrate representations column if upgrading older schema
            cols = {row[1] for row in conn.execute("PRAGMA table_info(lineage)").fetchall()}
            if "representations" not in cols:
                conn.execute("ALTER TABLE lineage ADD COLUMN representations TEXT DEFAULT 'raw'")

    @staticmethod
    def canonicalize(secret: str) -> Tuple[str, str]:
        """
        Normalizes transformed secrets (URL-encoded, Base64, Hex-escaped, padded)
        to their canonical underlying string so that cross-service sprawl can be
        tracked across heterogeneous representations.
        """
        if not secret:
            return "", "raw"
        cleaned = secret.strip(" \t\r\n'\"`")
        detected_format = "raw"

        # 1. URL decoding
        try:
            unquoted = urllib.parse.unquote(cleaned)
            if unquoted != cleaned and len(unquoted) >= 6:
                cleaned = unquoted
                detected_format = "url_encoded"
        except Exception:
            pass

        # 2. Hex escape unescaping (\\x41\\x42 -> AB)
        if "\\x" in cleaned:
            try:
                unescaped = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), cleaned)
                if unescaped != cleaned and unescaped.isprintable():
                    cleaned = unescaped
                    detected_format = "hex_escaped"
            except Exception:
                pass

        # 3. Base64 decoding if matches standard base64 structure
        if len(cleaned) >= 8 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", cleaned):
            try:
                pad_len = len(cleaned) % 4
                padded = cleaned + ("=" * (4 - pad_len) if pad_len else "")
                decoded = base64.b64decode(padded).decode("utf-8", errors="strict")
                if len(decoded) >= 6 and decoded.isprintable():
                    cleaned = decoded
                    detected_format = "base64"
            except Exception:
                pass

        return cleaned.strip(" \t\r\n'\"`"), detected_format

    def canonical_fingerprint(self, secret: str) -> Tuple[str, str, str]:
        """
        Computes HMAC-SHA256 over the canonicalized secret.
        Returns (canonical_fingerprint, detected_format, canonical_secret).
        """
        canon_sec, fmt = self.canonicalize(secret)
        fp = hmac.new(
            self._hmac_key,
            canon_sec.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return fp, fmt, canon_sec

    def is_exempt(self, secret: str) -> bool:
        """
        Checks if a secret has been pre-seeded or exempted from sprawl lineage.
        """
        canon_fp, _, _ = self.canonical_fingerprint(secret)
        raw_fp = self._fingerprint(secret)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM lineage_exemptions WHERE fingerprint=? OR raw_fingerprint=? OR fingerprint=?",
                (canon_fp, raw_fp, raw_fp),
            ).fetchone()
            return row is not None

    def add_exemption(
        self,
        secret: str,
        label: str = "Authorized Secret",
        reason: str = "Pre-seeded in vault",
        created_by: str = "admin"
    ) -> str:
        """
        Registers a secret in the exemption list and purges any prior sprawl tracking for it.
        Exempt secrets will NEVER appear on the SecretLineage graph or trigger sprawl alerts.
        """
        # Adversarial exemption abuse protections
        sec_norm = (secret or "").strip().lower()
        RESERVED_EXEMPTION_WORDS = {
            "password", "passwd", "secret", "bearer", "admin", "token",
            "apikey", "api_key", "authorization", "root", "guest", "default"
        }
        if sec_norm in RESERVED_EXEMPTION_WORDS:
            raise ValueError(f"Cannot exempt generic reserved identifier: '{secret}'")

        if not secret or len(secret.strip()) < 8:
            raise ValueError("Exemption secret must be at least 8 characters long")

        if not created_by or created_by.strip() == "" or created_by.lower() in {"anonymous", "unauthorized", "attacker"}:
            raise PermissionError(f"Actor '{created_by}' is not authorized to create lineage exemptions")

        canon_fp, _, _ = self.canonical_fingerprint(secret)
        raw_fp = self._fingerprint(secret)
        now = int(time.time())
        final_reason = f"{reason} (by {created_by})" if created_by and "by " not in reason else reason

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO lineage_exemptions (fingerprint, raw_fingerprint, label, reason, added_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (canon_fp, raw_fp, label, final_reason, now),
            )
            # Purge any existing lineage rows for this secret so it disappears from sprawl graphs immediately
            conn.execute(
                "DELETE FROM lineage WHERE fingerprint=? OR fingerprint=?",
                (canon_fp, raw_fp),
            )

        return canon_fp

    def remove_exemption(self, fingerprint: str) -> bool:
        """Removes a fingerprint from the exemption table."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "DELETE FROM lineage_exemptions WHERE fingerprint=? OR raw_fingerprint=?",
                (fingerprint, fingerprint),
            )
            return cur.rowcount > 0

    def list_exemptions(self) -> List[Dict]:
        """Lists all secrets currently exempted from sprawl lineage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT fingerprint, raw_fingerprint, label, reason, added_at FROM lineage_exemptions ORDER BY added_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def record(self, secret: str):
        """
        Called once per detected secret. Never stores plaintext.
        Checks if secret is exempt; if exempt, skips lineage recording completely.
        """
        if self.is_exempt(secret):
            return

        fp, fmt, _ = self.canonical_fingerprint(secret)
        now = int(time.time())
        is_reg = int(self._check_k8s_registry(secret))

        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT occurrence_count, representations FROM lineage "
                "WHERE fingerprint=? AND pod_name=? AND namespace=?",
                (fp, self.pod_name, self.namespace),
            ).fetchone()

            if existing:
                curr_reps = (existing[1] or "raw").split(",")
                if fmt not in curr_reps:
                    curr_reps.append(fmt)
                rep_str = ",".join(curr_reps)
                conn.execute(
                    "UPDATE lineage SET last_seen=?, occurrence_count=occurrence_count+1, "
                    "is_registered=?, representations=? WHERE fingerprint=? AND pod_name=? AND namespace=?",
                    (now, is_reg, rep_str, fp, self.pod_name, self.namespace),
                )
            else:
                conn.execute(
                    "INSERT INTO lineage VALUES (?,?,?,?,?,1,?,?)",
                    (fp, self.pod_name, self.namespace, now, now, is_reg, fmt),
                )

    @staticmethod
    def _extract_service_name(pod_name: str) -> str:
        for known in [
            "auth-service",
            "payment-service",
            "inventory-service",
            "user-service",
            "notification-service",
        ]:
            if known in pod_name:
                return known
        parts = pod_name.split("-")
        if len(parts) >= 3 and len(parts[-1]) == 5 and len(parts[-2]) in (9, 10):
            return "-".join(parts[:-2])
        return pod_name

    @staticmethod
    def _infer_secret_type(origin_service: str) -> str:
        if "payment" in origin_service:
            return "STRIPE_API_KEY"
        elif "inventory" in origin_service:
            return "AWS_ACCESS_KEY"
        elif "auth" in origin_service:
            return "POSTGRES_DB_URI"
        elif "user" in origin_service:
            return "JWT_BEARER_TOKEN"
        elif "notification" in origin_service:
            return "TWILIO_AUTH_TOKEN"
        return "GENERIC_API_TOKEN"

    def sprawl_report(self) -> list:
        now = int(time.time())

        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT
                    fingerprint,
                    pod_name,
                    namespace,
                    first_seen,
                    last_seen,
                    occurrence_count,
                    is_registered,
                    representations
                FROM lineage
                WHERE fingerprint NOT IN (SELECT fingerprint FROM lineage_exemptions)
                  AND fingerprint NOT IN (SELECT raw_fingerprint FROM lineage_exemptions WHERE raw_fingerprint IS NOT NULL)
                ORDER BY fingerprint, first_seen ASC
            """).fetchall()

        grouped: dict = {}
        for r in rows:
            grouped.setdefault(r["fingerprint"], []).append(dict(r))

        report = []
        for fp, records in grouped.items():
            records.sort(key=lambda x: (x["first_seen"], -x["occurrence_count"]))

            pod_names = [r["pod_name"] for r in records]
            distinct_pods = list(dict.fromkeys(pod_names))
            services = list(dict.fromkeys(self._extract_service_name(p) for p in distinct_pods))

            # Aggregate all observed representation encodings for this canonical secret
            all_reps = set()
            for r in records:
                for rep in (r.get("representations") or "raw").split(","):
                    if rep.strip():
                        all_reps.add(rep.strip())

            origin_pod = records[0]["pod_name"]
            origin_service = self._extract_service_name(origin_pod)
            sprawled_to = [s for s in services if s != origin_service]

            min_first_seen = min(r["first_seen"] for r in records)
            max_last_seen = max(r["last_seen"] for r in records)
            total_occurrences = sum(r["occurrence_count"] for r in records)
            is_registered = any(bool(r["is_registered"]) for r in records)
            secret_type = self._infer_secret_type(origin_service)

            age_days = (now - min_first_seen) / 86400
            service_count = len(services)
            pod_count = len(distinct_pods)

            # Realistic multi-service blast radius risk model
            if service_count >= 5:
                base_risk = 15.0
            elif service_count >= 3:
                base_risk = 10.0
            elif service_count >= 2:
                base_risk = 6.0
            else:
                base_risk = 1.5

            volume_factor = min(total_occurrences / 200.0, 5.0)
            penalty = 1.0 if is_registered else 1.5
            risk = round((base_risk + volume_factor) * penalty, 1)

            if risk >= 12.0:
                severity = "CRITICAL"
            elif risk >= 7.0:
                severity = "HIGH"
            elif risk >= 4.0:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            propagation_path = []
            for i, r in enumerate(records):
                svc = self._extract_service_name(r["pod_name"])
                propagation_path.append({
                    "step": i + 1,
                    "service": svc,
                    "pod_name": r["pod_name"],
                    "namespace": r.get("namespace", "logshield-protected"),
                    "first_seen": r["first_seen"],
                    "last_seen": r["last_seen"],
                    "occurrences": r["occurrence_count"],
                    "is_origin": i == 0
                })

            report.append({
                "fingerprint": fp[:16] + "...",
                "full_fingerprint": fp,
                "canonical_fingerprint": fp,
                "pod_count": pod_count,
                "distinct_pods": pod_count,
                "pods": distinct_pods,
                "services": services,
                "service_count": service_count,
                "distinct_services": service_count,
                "origin_service": origin_service,
                "origin_pod": origin_pod,
                "sprawled_to": sprawled_to,
                "is_sprawled": service_count > 1,
                "first_seen": min_first_seen,
                "last_seen": max_last_seen,
                "age_days": round(age_days, 1),
                "occurrences": total_occurrences,
                "is_registered": is_registered,
                "risk_score": risk,
                "severity": severity,
                "secret_type": secret_type,
                "representations_observed": sorted(list(all_reps)) if all_reps else ["raw"],
                "is_multi_representation": len(all_reps) > 1,
                "propagation_path": propagation_path
            })

        return sorted(report, key=lambda x: x["risk_score"], reverse=True)

    def _fingerprint(self, secret: str) -> str:
        return hmac.new(
            self._hmac_key,
            secret.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _check_k8s_registry(self, secret: str) -> bool:
        if os.environ.get("DISABLE_K8S_PROBE", "0") == "1":
            return False
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
