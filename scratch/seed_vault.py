import sqlite3
import json
import time
import os

VAULT_DB = "d:/LOGSHEILD/data/vault.db"
os.makedirs("d:/LOGSHEILD/data", exist_ok=True)

with sqlite3.connect(VAULT_DB) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vault (
            ref_id TEXT PRIMARY KEY,
            ciphertext BLOB,
            iv BLOB,
            scs_score REAL,
            factors_json TEXT,
            pod_name TEXT,
            namespace TEXT,
            pod_uid TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("DELETE FROM vault")
    
    entries = [
        ("SEC-A1B2C3D4", b"dummy", b"iv", 99.5, json.dumps(["keyword", "entropy"]), "target-app-1", "logshield", "uid-1234", "2026-09-12 10:00:00"),
        ("SEC-E5F6G7H8", b"dummy", b"iv", 85.0, json.dumps(["regex"]), "target-app-2", "logshield", "uid-5678", "2026-09-12 10:05:00"),
    ]
    conn.executemany("INSERT INTO vault (ref_id, ciphertext, iv, scs_score, factors_json, pod_name, namespace, pod_uid, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", entries)

print("Fake vault data seeded.")
