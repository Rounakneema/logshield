#!/usr/bin/env python3
"""
LogShield SecureReveal — Vault Admin Utility
=============================================
Designed to be run via:
  kubectl exec -n logshield-protected <pod> -c logshield-sidecar -- python /app/vault_admin.py

Usage:
  Provides interactive access to the LogShield Vault, Audit Log, and Lineage Tracking.
"""

import sys, os

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


def cmd_audit():
    banner("IMMUTABLE AUDIT LOG", YELLOW)
    with sqlite3.connect(os.environ["VAULT_DB_PATH"]) as conn:
        audit_rows = conn.execute(
            "SELECT timestamp, ref_id, action, actor, reason, outcome "
            "FROM audit_log ORDER BY timestamp DESC LIMIT 50"
        ).fetchall()

    if not audit_rows:
        print("  No audit events found.")
        return

    print(f"  {'Timestamp':<20} {'Ref ID':<22} {'Action':<10} {'Actor':<15} {'Outcome'}")
    print(f"  {'-'*20} {'-'*22} {'-'*10} {'-'*15} {'-'*10}")
    for ts, ref_id, action, actor, reason, outcome in audit_rows:
        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        color = GREEN if outcome == "SUCCESS" else RED if outcome in ("DENIED",) else YELLOW
        print(f"  {dt}  {ref_id:<22} {action:<10} {actor:<15} {color}{outcome}{RESET}")


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
    sub.add_parser("audit", help="View recent audit logs")

    # sprawl
    sub.add_parser("sprawl", help="View secret lineage sprawl report")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list()
    elif args.cmd == "retrieve":
        cmd_retrieve(args.ref_id, args.actor, args.reason)
    elif args.cmd == "audit":
        cmd_audit()
    elif args.cmd == "sprawl":
        cmd_sprawl()


if __name__ == "__main__":
    main()
