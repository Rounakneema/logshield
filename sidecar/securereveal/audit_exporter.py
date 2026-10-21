"""
LogShield SecureReveal — SIEM Audit Exporter
==============================================
Exports structured audit events to /data/audit.jsonl
using Elastic Common Schema (ECS) / Splunk CIM format.
Designed for high-throughput tailing by Fluent Bit, Logstash, or Vector.
"""

import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import threading
from queue import Queue, Empty


class AuditExporter:
    def __init__(self, export_path: str = "/data/audit.jsonl"):
        self.export_path = os.environ.get("AUDIT_JSONL_PATH", export_path)
        self._queue = Queue(maxsize=10000)
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._flusher, daemon=True)
        self._worker_thread.start()

    def export_event(
        self,
        ref_id: str,
        action: str,
        actor: str,
        reason: str,
        outcome: str,
        timestamp: int,
        pod_name: str = "unknown",
        namespace: str = "default",
        client_ip: str = "127.0.0.1",
        prev_hash: str = "",
        entry_hash: str = "",
        signature: str = ""
    ):
        """Enqueue an audit event to be asynchronously written to audit.jsonl."""
        iso_ts = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        ecs_record = {
            "@timestamp": iso_ts,
            "event": {
                "action": action,
                "outcome": outcome,
                "category": ["security", "audit"],
                "type": ["access", "change"],
            },
            "user": {
                "name": actor,
            },
            "host": {
                "hostname": pod_name,
                "namespace": namespace,
            },
            "client": {
                "ip": client_ip,
            },
            "logshield": {
                "ref_id": ref_id,
                "reason": reason,
                "prev_hash": prev_hash,
                "entry_hash": entry_hash,
                "signature": signature[:16] + "..." if signature else "",
            }
        }
        try:
            self._queue.put_nowait(ecs_record)
        except Exception:
            pass  # Fail open if queue is full

    def _flusher(self):
        Path(self.export_path).parent.mkdir(parents=True, exist_ok=True)
        batch = []
        last_flush = time.time()

        while not self._stop_event.is_set():
            try:
                record = self._queue.get(timeout=1.0)
                batch.append(record)
            except Empty:
                pass

            now = time.time()
            if batch and (len(batch) >= 20 or (now - last_flush) >= 2.0):
                try:
                    with open(self.export_path, "a", encoding="utf-8") as f:
                        for item in batch:
                            f.write(json.dumps(item) + "\n")
                    batch.clear()
                    last_flush = now
                except Exception as e:
                    # Keep trying without crashing
                    pass

    def flush(self):
        """Synchronously flush any remaining events."""
        items = []
        while not self._queue.empty():
            try:
                items.append(self._queue.get_nowait())
            except Empty:
                break
        if items:
            try:
                Path(self.export_path).parent.mkdir(parents=True, exist_ok=True)
                with open(self.export_path, "a", encoding="utf-8") as f:
                    for item in items:
                        f.write(json.dumps(item) + "\n")
            except Exception:
                pass
