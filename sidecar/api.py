import os
import json
import sqlite3
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="LogShield Enterprise API", version="1.0")

STATS_OUTPUT_PATH = os.environ.get("STATS_OUTPUT_PATH", "/data/stats.json")
VAULT_DB_PATH     = os.environ.get("VAULT_DB_PATH",     "/data/vault.db")
LINEAGE_DB_PATH   = os.environ.get("LINEAGE_DB_PATH",   "/data/lineage.db")
LINEAGE_KEY_PATH  = os.environ.get("LINEAGE_KEY_PATH",  "/data/lineage.key")
VAULT_KEY_PATH    = os.environ.get("VAULT_KEY_PATH",    "/data/vault.key")

from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter

class RetrieveRequest(BaseModel):
    ref_id: str
    actor: str
    reason: str

@app.get("/api/stats")
def get_stats():
    # Read all stats_*.json in /data/ and aggregate them
    import glob
    stats_files = glob.glob("/data/stats*.json")
    if not stats_files:
        stats_files = [STATS_OUTPUT_PATH] if os.path.exists(STATS_OUTPUT_PATH) else []
        
    if not stats_files:
        return {"error": "Stats not generated yet"}
        
    aggregated = {
        "lines_processed": 0,
        "secrets_masked": 0,
        "lines_flagged": 0,
        "lines_clean": 0,
        "timeseries": []
    }
    
    # Simple aggregation of timeseries based on time keys
    ts_map = {}
    
    for fpath in stats_files:
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
                aggregated["lines_processed"] += data.get("lines_processed", 0)
                aggregated["secrets_masked"] += data.get("secrets_masked", 0)
                aggregated["lines_flagged"] += data.get("lines_flagged", 0)
                aggregated["lines_clean"] += data.get("lines_clean", 0)
                
                for pt in data.get("timeseries", []):
                    t = pt["time"]
                    if t not in ts_map:
                        ts_map[t] = {"time": t, "lines": 0, "secrets": 0}
                    ts_map[t]["lines"] += pt["lines"]
                    ts_map[t]["secrets"] += pt["secrets"]
        except Exception:
            pass
            
    # Sort timeseries and keep last 60
    sorted_ts = sorted(list(ts_map.values()), key=lambda x: x["time"])
    aggregated["timeseries"] = sorted_ts[-60:]
    
    return aggregated

@app.get("/api/logs")
def get_recent_logs():
    import glob
    log_files = glob.glob("/data/recent_logs*.json")
    
    all_logs = []
    for fpath in log_files:
        try:
            with open(fpath, "r") as f:
                all_logs.extend(json.load(f))
        except Exception:
            pass
            
    # Keep last 500 across all services
    return all_logs[-500:]

@app.get("/api/vault")
def get_vault_entries():
    if not os.path.exists(VAULT_DB_PATH):
        return []
    try:
        with sqlite3.connect(VAULT_DB_PATH) as conn:
            rows = conn.execute(
                "SELECT ref_id, scs_score, factors_json, pod_name, namespace, created_at "
                "FROM vault ORDER BY created_at DESC"
            ).fetchall()
            return [
                {
                    "ref_id": r[0],
                    "scs_score": r[1],
                    "factors": json.loads(r[2]),
                    "pod_name": r[3],
                    "namespace": r[4],
                    "created_at": r[5]
                }
                for r in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vault/retrieve")
def retrieve_secret(req: RetrieveRequest):
    if not os.path.exists(VAULT_DB_PATH) or not os.path.exists(VAULT_KEY_PATH):
        raise HTTPException(status_code=500, detail="Vault not configured")
    
    vault = Vault(db_path=VAULT_DB_PATH, key_path=VAULT_KEY_PATH)
    ok, result = vault.retrieve(req.ref_id, req.actor, req.reason)
    if ok:
        return {"success": True, "plaintext": result}
    else:
        return {"success": False, "message": result}

@app.get("/api/audit")
def get_audit_log():
    if not os.path.exists(VAULT_DB_PATH):
        return []
    try:
        with sqlite3.connect(VAULT_DB_PATH) as conn:
            rows = conn.execute(
                "SELECT timestamp, ref_id, action, actor, reason, outcome "
                "FROM audit_log ORDER BY timestamp DESC LIMIT 50"
            ).fetchall()
            return [
                {
                    "timestamp": r[0],
                    "ref_id": r[1],
                    "action": r[2],
                    "actor": r[3],
                    "reason": r[4],
                    "outcome": r[5]
                }
                for r in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lineage")
def get_lineage():
    if not os.path.exists(LINEAGE_DB_PATH) or not os.path.exists(LINEAGE_KEY_PATH):
        return []
    try:
        fp = Fingerprinter(db_path=LINEAGE_DB_PATH, key_path=LINEAGE_KEY_PATH)
        return fp.sprawl_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
