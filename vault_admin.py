#!/usr/bin/env python3
"""
LogShield SecureReveal — Vault Admin Utility
=============================================
Designed to be run via:
  kubectl exec -n logshield-protected <pod> -c logshield-sidecar -- python /app/vault_admin.py

Usage:
  Provides interactive access to the LogShield Vault, Audit Log, and Lineage Tracking.
"""

import sys, os, json, time

sys.path.insert(0, "/app")
os.environ.setdefault("VAULT_DB_PATH",    "/data/vault.db")
os.environ.setdefault("VAULT_KEY_PATH",   "/data/vault.key")
os.environ.setdefault("LINEAGE_DB_PATH",  "/data/lineage.db")
os.environ.setdefault("LINEAGE_KEY_PATH", "/data/lineage.key")
os.environ.setdefault("AUTHORIZED_ACTORS","admin,security-team")

from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter
import sqlite3
from datetime import datetime
import argparse

RESET  = "\033[0m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"

def banner(text, color=CYAN):
    print(f"\n{color}{BOLD}{'='*64}{RESET}")
    print(f"{color}{BOLD}  {text}{RESET}")
    print(f"{color}{BOLD}{'='*64}{RESET}\n")

vault = Vault(
    db_path=os.environ["VAULT_DB_PATH"],
    key_path=os.environ["VAULT_KEY_PATH"],
)
fp = Fingerprinter(
    db_path=os.environ["LINEAGE_DB_PATH"],
    key_path=os.environ["LINEAGE_KEY_PATH"],
)

def cmd_list():
    banner("VAULT CONTENTS (encrypted at rest)", CYAN)
    with sqlite3.connect(os.environ["VAULT_DB_PATH"]) as conn:
        rows = conn.execute(
            "SELECT ref_id, scs_score, factors_json, pod_name, namespace, created_at "
            "FROM vault ORDER BY created_at DESC"
        ).fetchall()

    if not rows:
        print(f"{YELLOW}  ⚠ No secrets in vault currently.{RESET}")
        return

    print(f"  {'Ref ID':<22} {'SCS':>5}  {'Pod':<28}  {'Detected At'}")
    print(f"  {'-'*22} {'---':>5}  {'-'*28}  {'-'*19}")
    for ref_id, score, _, pod, ns, ts in rows:
        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        severity = f"{RED}MASK{RESET}" if score >= 80 else f"{YELLOW}FLAG{RESET}"
        print(f"  {ref_id:<22} [{severity}] SCS={score:3d}  pod={pod:<20}  {dt}")


def cmd_retrieve(ref_id, actor, reason):
    banner("SECURE REVEAL", GREEN)
    print(f"  Retrieving: {BOLD}{ref_id}{RESET}")
    print(f"  Actor     : {GREEN}{actor}{RESET}")
    print(f"  Reason    : {reason}\n")

    ok, result = vault.retrieve(ref_id, actor, reason)
    if ok:
        print(f"  {GREEN}✅ SUCCESS — PLAINTEXT RECOVERED:{RESET}")
        print(f"     {BOLD}{result}{RESET}")
    else:
        print(f"  {RED}🚫 DENIED — {result}{RESET}")
        print(f"  {YELLOW}  ↳ This failed attempt is permanently recorded in the audit log.{RESET}")


def cmd_audit(verify=False, actor=None, outcome=None, export=None):
    if verify:
        banner("CRYPTOGRAPHIC AUDIT CHAIN VERIFICATION", CYAN)
        is_valid, broken_id, message, total = vault.verify_audit_chain()
        if is_valid:
            print(f"  {GREEN}[+] AUDIT CHAIN VALID -- {message}{RESET}")
            print(f"     Total Blocks: {BOLD}{total}{RESET} | Genesis to Tip: Cryptographically Sealed")
        else:
            print(f"  {RED}[!] INTEGRITY VIOLATION DETECTED!{RESET}")
            print(f"     Broken Record ID: {BOLD}#{broken_id}{RESET}")
            print(f"     Details         : {RED}{message}{RESET}")
        return

    banner("IMMUTABLE AUDIT LOG", YELLOW)
    with sqlite3.connect(os.environ["VAULT_DB_PATH"]) as conn:
        query = "SELECT timestamp, ref_id, action, actor, reason, outcome FROM audit_log WHERE 1=1"
        params = []
        if actor:
            query += " AND actor LIKE ?"
            params.append(f"%{actor}%")
        if outcome:
            query += " AND outcome = ?"
            params.append(outcome)
        query += " ORDER BY id DESC LIMIT 50"
        audit_rows = conn.execute(query, params).fetchall()

    if not audit_rows:
        print("  No matching audit events found.")
        return

    if export:
        import json
        with open(export, "w", encoding="utf-8") as f:
            records = [{"timestamp": r[0], "ref_id": r[1], "action": r[2], "actor": r[3], "reason": r[4], "outcome": r[5]} for r in audit_rows]
            json.dump(records, f, indent=2)
        print(f"  {GREEN}Exported {len(records)} audit records to {export}{RESET}")
        return

    print(f"  {'Timestamp':<20} {'Ref ID':<22} {'Action':<10} {'Actor':<15} {'Outcome'}")
    print(f"  {'-'*20} {'-'*22} {'-'*10} {'-'*15} {'-'*10}")
    for ts, ref_id, action, act, reason, outc in audit_rows:
        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        color = GREEN if outc == "SUCCESS" else RED if outc in ("DENIED",) else YELLOW
        print(f"  {dt}  {ref_id:<22} {action:<10} {act:<15} {color}{outc}{RESET}")


def cmd_sprawl():
    banner("SECRET SPRAWL REPORT (lineage tracking)", CYAN)
    report = fp.sprawl_report()
    if not report:
        print(f"  {YELLOW}No lineage data yet.{RESET}")
    else:
        for item in report:
            sev_color = RED if item["severity"] == "CRITICAL" else YELLOW if item["severity"] == "HIGH" else GREEN
            reg_str = f"{GREEN}YES (K8s Registered){RESET}" if item["is_registered"] else f"{RED}NO  (Orphaned Secret){RESET}"
            print(f"  [{sev_color}{item['severity']:<8}{RESET}]  Fingerprint: {item['fingerprint']}")
            print(f"             Pods: {item['pod_count']}   Age: {item['age_days']}d   "
                  f"Occurrences: {item['occurrences']}   Risk: {item['risk_score']}")
            print(f"             K8s Registry: {reg_str}")
            print()


def cmd_mode(set_mode=None):
    mode_file = os.environ.get("MODE_FILE_PATH", "/data/mode.json")
    if set_mode:
        if set_mode not in ["protected", "bypass"]:
            print(f"{RED}Error: Mode must be 'protected' or 'bypass'{RESET}")
            sys.exit(1)
        os.makedirs(os.path.dirname(mode_file) or ".", exist_ok=True)
        import time
        with open(mode_file, "w", encoding="utf-8") as f:
            json.dump({"mode": set_mode, "timestamp": time.time()}, f)

        banner(f"SHIELD MODE SWITCHED: {set_mode.upper()}", RED if set_mode == "bypass" else GREEN)
        if set_mode == "bypass":
            print(f"  {RED}[!] LOGSHIELD SHIELD DEACTIVATED (BYPASS MODE){RESET}")
            print(f"  -> Incoming logs will PASS THROUGH UNMASKED directly.")
            print(f"  -> Web Dashboard will reflect BYPASSED state in real-time.")
        else:
            print(f"  {GREEN}[+] LOGSHIELD SHIELD ACTIVATED (PROTECTED MODE){RESET}")
            print(f"  -> Real-time multi-stage secret sanitization (LogMask SCS) is ACTIVE.")
            print(f"  -> Web Dashboard will reflect PROTECTED state in real-time.")
        return

    current = "protected"
    if os.path.exists(mode_file):
        try:
            with open(mode_file, "r", encoding="utf-8") as f:
                current = json.load(f).get("mode", "protected")
        except Exception:
            pass
    color = GREEN if current == "protected" else RED
    banner("CURRENT LOGSHIELD PROTECTION STATUS", color)
    print(f"  Current Mode: {BOLD}{color}{current.upper()}{RESET}")
    status_msg = "All secrets sanitized & vaulted in real time." if current == "protected" else "SHIELD BYPASSED: Raw logs pass through unredacted!"
    print(f"  Status      : {status_msg}")


def main():
    parser = argparse.ArgumentParser(description="LogShield Vault Administration CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list
    sub.add_parser("list", help="List all secrets in the vault")

    # retrieve
    p_ret = sub.add_parser("retrieve", help="Retrieve a plaintext secret")
    p_ret.add_argument("ref_id", help="Vault Reference ID")
    p_ret.add_argument("--actor", required=True, help="Your username/ID")
    p_ret.add_argument("--reason", required=True, help="Reason for retrieval")

    # audit
    p_aud = sub.add_parser("audit", help="View recent audit logs or verify chain")
    p_aud.add_argument("--verify", action="store_true", help="Run cryptographic chain verification")
    p_aud.add_argument("--actor", help="Filter by actor name")
    p_aud.add_argument("--outcome", help="Filter by outcome")
    p_aud.add_argument("--export", help="Export matching audit logs to a JSON file")

    # sprawl
    sub.add_parser("sprawl", help="View secret lineage sprawl report")

    # mode
    p_mode = sub.add_parser("mode", help="Query or switch LogShield protection mode (protected / bypass)")
    p_mode.add_argument("--set", choices=["protected", "bypass"], help="Switch mode to protected or bypass")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list()
    elif args.cmd == "retrieve":
        cmd_retrieve(args.ref_id, args.actor, args.reason)
    elif args.cmd == "audit":
        cmd_audit(verify=args.verify, actor=args.actor, outcome=args.outcome, export=args.export)
    elif args.cmd == "sprawl":
        cmd_sprawl()
    elif args.cmd == "mode":
        cmd_mode(set_mode=args.set)


if __name__ == "__main__":
    main()
