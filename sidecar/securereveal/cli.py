"""
SecureReveal CLI
=================
The panel demo's Act 3 uses this script to show:
  (a) a legitimate, authorised retrieval of a masked value
  (b) an UNAUTHORISED retrieval attempt being blocked AND recorded

Usage:
  python cli.py retrieve SEC-A1B2C3D4 --actor admin --reason "incident-2026-001"
  python cli.py retrieve SEC-A1B2C3D4 --actor hacker --reason "just curious"
  python cli.py sprawl-report
  python cli.py audit-log --ref-id SEC-A1B2C3D4
"""

import argparse
import sqlite3
import sys
import os
from datetime import datetime

# Adjust Python path so sidecar modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sidecar.securereveal.vault import Vault
from sidecar.secretlineage.fingerprint import Fingerprinter


def cmd_retrieve(args):
    db_path = os.environ.get("VAULT_DB_PATH", "/data/vault.db")
    key_path = os.environ.get("VAULT_KEY_PATH", "/data/vault.key")
    vault = Vault(db_path=db_path, key_path=key_path)
    print(f"\n[SecureReveal] Retrieving {args.ref_id}")
    print(f"  Actor  : {args.actor}")
    print(f"  Reason : {args.reason}")
    print()

    success, result = vault.retrieve(args.ref_id, args.actor, args.reason)
    if success:
        print(f"  [SUCCESS] RETRIEVED VALUE: {result}")
    else:
        print(f"  [DENIED] {result}")
        sys.exit(1)


def cmd_sprawl_report(_args):
    db_path = os.environ.get("LINEAGE_DB_PATH", "/data/lineage.db")
    key_path = os.environ.get("LINEAGE_KEY_PATH", "/data/lineage.key")
    fp = Fingerprinter(db_path=db_path, key_path=key_path)
    report = fp.sprawl_report()

    print("\n" + "=" * 60)
    print("  SECRET SPRAWL REPORT")
    print("=" * 60)

    if not report:
        print("  No secrets detected yet.")
        return

    for item in report:
        reg_str = "YES (Registered in K8s Secrets)" if item["is_registered"] else "NO (NOT in K8s Secrets - Orphaned)"
        print(f"\n  [{item['severity']}] Fingerprint: {item['fingerprint']}")
        print(f"      Pods seen:    {item['pod_count']}")
        print(f"      Age:          {item['age_days']} days")
        print(f"      Occurrences:  {item['occurrences']}")
        print(f"      K8s Registry: {reg_str}")
        print(f"      Risk Score:   {item['risk_score']}")

    print("\n" + "=" * 60)


def cmd_audit_log(args):
    db_path = os.environ.get("VAULT_DB_PATH", "/data/vault.db")
    if not os.path.exists(db_path):
        print(f"Audit log DB not found at {db_path}")
        return

    with sqlite3.connect(db_path) as conn:
        if args.ref_id:
            rows = conn.execute(
                "SELECT timestamp, action, actor, reason, outcome "
                "FROM audit_log WHERE ref_id=? ORDER BY timestamp",
                (args.ref_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT timestamp, ref_id, action, actor, reason, outcome "
                "FROM audit_log ORDER BY timestamp DESC LIMIT 50"
            ).fetchall()

    print("\n" + "=" * 70)
    print("  AUDIT LOG" + (f" for {args.ref_id}" if args.ref_id else " (last 50 entries)"))
    print("=" * 70)
    for row in rows:
        ts = datetime.fromtimestamp(row[0]).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {ts}  {'  '.join(str(x) for x in row[1:])}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="SecureReveal CLI — retrieve masked log values with full audit trail"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # retrieve
    p_ret = sub.add_parser("retrieve", help="Retrieve a masked value by reference ID")
    p_ret.add_argument("ref_id", help="e.g. SEC-A1B2C3D4")
    p_ret.add_argument("--actor",  required=True, help="Your identity (goes into audit log)")
    p_ret.add_argument("--reason", required=True, help="Why you need this (goes into audit log)")

    # sprawl-report
    sub.add_parser("sprawl-report", help="Print the Secret Sprawl Report")

    # audit-log
    p_aud = sub.add_parser("audit-log", help="Print audit log entries")
    p_aud.add_argument("--ref-id", default=None, help="Filter by reference ID")

    args = parser.parse_args()

    if args.cmd == "retrieve":
        cmd_retrieve(args)
    elif args.cmd == "sprawl-report":
        cmd_sprawl_report(args)
    elif args.cmd == "audit-log":
        cmd_audit_log(args)


if __name__ == "__main__":
    main()
