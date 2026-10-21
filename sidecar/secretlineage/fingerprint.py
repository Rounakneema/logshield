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

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT
                    fingerprint,
                    pod_name,
                    namespace,
                    first_seen,
                    last_seen,
                    occurrence_count,
                    is_registered
                FROM lineage
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
                "pod_count": pod_count,
                "pods": distinct_pods,
                "services": services,
                "service_count": service_count,
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
