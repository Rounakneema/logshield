"""
LogShield Sidecar — Main Interceptor
======================================
This is the entry point for the sidecar container.
"""

import os
import sys
import time
import threading
import json
from pathlib import Path
from collections import deque

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sidecar.logmask.scorer import SCSEngine
from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter
from sidecar.containment.engine import ContainmentEngine

pod_name = os.environ.get("POD_NAME", "unknown")
LOG_INPUT_PATH    = os.environ.get("LOG_INPUT_PATH",    "/shared/app.log")
STATS_OUTPUT_PATH = os.environ.get("STATS_OUTPUT_PATH", f"/data/stats_{pod_name}.json")
VAULT_EXPIRY_INTERVAL_S = int(os.environ.get("VAULT_EXPIRY_INTERVAL", "3600"))
VAULT_DB_PATH     = os.environ.get("VAULT_DB_PATH",     "/data/vault.db")
VAULT_KEY_PATH    = os.environ.get("VAULT_KEY_PATH",    "/data/vault.key")
LINEAGE_DB_PATH   = os.environ.get("LINEAGE_DB_PATH",   "/data/lineage.db")
LINEAGE_KEY_PATH  = os.environ.get("LINEAGE_KEY_PATH",  "/data/lineage.key")
CONTAINMENT_DB_PATH = os.environ.get("CONTAINMENT_DB_PATH", "/data/containment.db")
MODE_FILE_PATH    = os.environ.get("MODE_FILE_PATH",    "/data/mode.json")


class LogShieldInterceptor:
    def __init__(self):
        self.engine        = SCSEngine()
        self.vault         = Vault(db_path=VAULT_DB_PATH, key_path=VAULT_KEY_PATH)
        self.fingerprinter = Fingerprinter(db_path=LINEAGE_DB_PATH, key_path=LINEAGE_KEY_PATH)
        self.containment   = ContainmentEngine(db_path=CONTAINMENT_DB_PATH, lineage_db_path=LINEAGE_DB_PATH)
        self.pod_name      = pod_name
        self.namespace     = os.environ.get("NAMESPACE", "default")

        self.stats = {
            "lines_processed":  0,
            "secrets_masked":   0,
            "lines_flagged":    0,
            "lines_clean":      0,
            "avg_latency_ms":   0.0,
            "p95_latency_ms":   0.0,
            "p99_latency_ms":   0.0,
            "mode":             "protected",
            "timeseries":       []
        }
        self._latency_window: deque = deque(maxlen=1000)
        self._timeseries_buffer: deque = deque(maxlen=60)
        self.recent_logs: deque = deque(maxlen=1500)
        self.recent_raw_logs: deque = deque(maxlen=1500)

        # Pre-load existing recent logs from disk if present to preserve history across restarts
        try:
            svc_name = self.pod_name
            for s in ["auth", "payment", "inventory", "user", "notification"]:
                if s in self.pod_name:
                    svc_name = s
                    break
            init_logs_path = os.environ.get("RECENT_LOGS_PATH", f"/data/recent_logs_{svc_name}.json")
            if os.path.exists(init_logs_path):
                with open(init_logs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.recent_logs.extend(data[-1000:])
        except Exception:
            pass

    def get_current_mode(self) -> str:
        if os.path.exists(MODE_FILE_PATH):
            try:
                with open(MODE_FILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f).get("mode", "protected")
            except Exception:
                pass
        return "protected"

    def process_line(self, raw_line: str) -> str:
        t_start = time.perf_counter()
        self.stats["lines_processed"] += 1

        current_mode = self.get_current_mode()
        self.stats["mode"] = current_mode

        if not hasattr(self, "_last_mode"):
            self._last_mode = current_mode
        elif self._last_mode != current_mode:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            marker = f"[{ts}] === SHIELD MODE CHANGED: {self._last_mode.upper()} ➔ {current_mode.upper()} ==="
            self.recent_logs.append(marker)
            self._last_mode = current_mode

        # BYPASS MODE: When shield is disabled, pass through raw line completely unredacted!
        if current_mode == "bypass":
            self.stats["lines_clean"] += 1
            elapsed_ms = (time.perf_counter() - t_start) * 1000
            self._latency_window.append(elapsed_ms)
            if self.stats["lines_processed"] % 10 == 0:
                self._update_latency_stats()
            self.recent_raw_logs.append(raw_line)
            self.recent_logs.append(f"[BYPASS] {raw_line}")
            return raw_line

        sanitised = raw_line
        had_secret = False

        results = self.engine.extract_and_score(raw_line)

        for result in results:
            replace_target = result.raw_slice if (result.raw_slice and result.raw_slice in sanitised) else result.token

            if result.decision == "MASK":
                ref_id = self.vault.store(
                    result.token, result.score, result.factors
                )
                self.fingerprinter.record(result.token)
                canon_fp, _, _ = self.fingerprinter.canonical_fingerprint(result.token)
                
                # Autonomous Containment Assessment
                self.containment.assess_and_contain(
                    ref_id=ref_id,
                    fingerprint=canon_fp,
                    secret_type=result.category,
                    scs_score=result.score,
                    pod_name=self.pod_name,
                    namespace=self.namespace,
                    evasion_type=result.evasion_type
                )

                sanitised = sanitised.replace(
                    replace_target,
                    f"[REDACTED:{ref_id}:SCS={result.score}]",
                )
                self.stats["secrets_masked"] += 1
                had_secret = True

            elif result.decision == "FLAG":
                ref_id = self.vault.store(
                    result.token, result.score, result.factors
                )
                self.fingerprinter.record(result.token)
                sanitised = sanitised.replace(
                    replace_target,
                    f"[FLAGGED:{ref_id}:SCS={result.score}]",
                )
                self.stats["lines_flagged"] += 1
                had_secret = True

        if not had_secret:
            self.stats["lines_clean"] += 1

        elapsed_ms = (time.perf_counter() - t_start) * 1000
        self._latency_window.append(elapsed_ms)
        
        if self.stats["lines_processed"] % 10 == 0:
            self._update_latency_stats()
            
        self.recent_raw_logs.append(raw_line)
        self.recent_logs.append(sanitised)

        return sanitised

    def _update_latency_stats(self):
        if not self._latency_window:
            return
        w = sorted(self._latency_window)
        n = len(w)
        self.stats["avg_latency_ms"] = round(sum(w) / n, 3)
        self.stats["p95_latency_ms"] = round(w[int(n * 0.95) - 1], 3)
        self.stats["p99_latency_ms"] = round(w[int(n * 0.99) - 1], 3)

    def _vault_expiry_worker(self):
        while True:
            time.sleep(VAULT_EXPIRY_INTERVAL_S)
            self.vault.expire_old_entries()

    def _stats_writer(self):
        while True:
            try:
                now_str = time.strftime("%H:%M:%S")
                current_mode = self.get_current_mode()
                self.stats["mode"] = current_mode

                if not hasattr(self, "_last_mode"):
                    self._last_mode = current_mode
                elif self._last_mode != current_mode:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S")
                    marker = f"[{ts}] === SHIELD MODE CHANGED: {self._last_mode.upper()} ➔ {current_mode.upper()} ==="
                    self.recent_logs.append(marker)
                    self._last_mode = current_mode

                self._timeseries_buffer.append({
                    "time": now_str,
                    "lines": self.stats["lines_processed"],
                    "secrets": self.stats["secrets_masked"] + self.stats["lines_flagged"]
                })
                self.stats["timeseries"] = list(self._timeseries_buffer)
                
                Path(STATS_OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
                with open(STATS_OUTPUT_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.stats, f, indent=2)
                    
                def _clean_svc(p: str) -> str:
                    for s in ["auth", "payment", "inventory", "user", "notification"]:
                        if s in p:
                            return s
                    return p

                svc_name = _clean_svc(pod_name)
                recent_logs_path = os.environ.get("RECENT_LOGS_PATH", f"/data/recent_logs_{svc_name}.json")
                with open(recent_logs_path, "w", encoding="utf-8") as f:
                    json.dump(list(self.recent_logs), f, indent=2)

                recent_raw_logs_path = os.environ.get("RECENT_RAW_LOGS_PATH", f"/data/recent_raw_logs_{svc_name}.json")
                with open(recent_raw_logs_path, "w", encoding="utf-8") as f:
                    json.dump(list(self.recent_raw_logs), f, indent=2)
            except Exception as e:
                print(f"[StatsWriter] Error: {e}", file=sys.stderr)
            time.sleep(0.75)

    def _api_worker(self):
        import uvicorn
        port = int(os.environ.get("PORT", "8000"))
        uvicorn.run("sidecar.api:app", host="0.0.0.0", port=port, log_level="warning")

    def run(self):
        # Start API, stats, and vault workers immediately so endpoints are always responsive
        threading.Thread(target=self._vault_expiry_worker, daemon=True).start()
        threading.Thread(target=self._stats_writer, daemon=True).start()
        threading.Thread(target=self._api_worker, daemon=True).start()

        print("[LogShield] Waiting for log file...", flush=True)
        while not Path(LOG_INPUT_PATH).exists():
            time.sleep(0.5)
        print(f"[LogShield] Tailing {LOG_INPUT_PATH}", flush=True)

        with open(LOG_INPUT_PATH, "r", encoding="utf-8", errors="replace") as fh:
            fh.seek(0, 2)
            while True:
                line = fh.readline()
                if line:
                    sanitised = self.process_line(line.rstrip("\n"))
                    print(sanitised, flush=True)
                else:
                    time.sleep(0.01)


if __name__ == "__main__":
    interceptor = LogShieldInterceptor()
    interceptor.run()
