"""
LogShield — Model & SCS Engine Live Inspector
================================================
Interactive & Batch Log Testing CLI to inspect LogShield engine performance,
feature scores, ML-derived SCS weights, decisions, and Vault redactions.

Usage:
  python scripts/inspect_logs.py --demo         # Run curated sample logs (with & without secrets)
  python scripts/inspect_logs.py --interactive  # Type/paste any log line live
  python scripts/inspect_logs.py --file <path>   # Process a log file line-by-line
"""

import sys
import os
import argparse
import time
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sidecar.logmask.scorer import SCSEngine
from sidecar.main import LogShieldInterceptor


DEMO_LOGS = [
    # ── LOGS WITH SECRETS (True Positives Expected) ──────────────────────────
    {
        "category": "WITH SECRETS",
        "description": "Postgres Database Password in Debug Output",
        "line": "DEBUG 2026-09-10 12:00:01 [db_pool] Connecting host=10.0.0.4 DATABASE_PASSWORD=MySuperS3cretP@ssw0rd! user=admin status=init"
    },
    {
        "category": "WITH SECRETS",
        "description": "AWS Secret Access Key",
        "line": "INFO 2026-09-10 12:00:02 [aws_s3] Config loaded AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY region=us-east-1"
    },
    {
        "category": "WITH SECRETS",
        "description": "Stripe Live API Key",
        "line": "ERROR 2026-09-10 12:00:03 [payment_gate] Payment failed stripe_secret=sk_test_51Nxabc1234567890abcdefghijklmnopqrstuvwxyz"
    },
    {
        "category": "WITH SECRETS",
        "description": "GitHub Personal Access Token (PAT)",
        "line": "INFO 2026-09-10 12:00:04 [ci_runner] Fetching repo api_key=ghp_1234567890abcdefghijklmnopqrstuvwxyz"
    },
    {
        "category": "WITH SECRETS",
        "description": "JWT Bearer Authorization Token",
        "line": "DEBUG 2026-09-10 12:00:05 [auth_middleware] Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    },

    # ── LOGS WITHOUT SECRETS (Clean Lines / False Positive Prevention) ───────
    {
        "category": "WITHOUT SECRETS (CLEAN)",
        "description": "UUID Order ID (High entropy non-secret)",
        "line": "INFO 2026-09-10 12:00:10 [checkout] Processed order order_id=550e8400-e29b-41d4-a716-446655440000 status=COMPLETED duration=45ms"
    },
    {
        "category": "WITHOUT SECRETS (CLEAN)",
        "description": "Distributed Tracing Trace ID",
        "line": "DEBUG 2026-09-10 12:00:11 [http_in] trace_id=c0a80101-4096-11ec-81d3-0242ac130003 span_id=00f067aa0ba902b7 path=/api/v1/health"
    },
    {
        "category": "WITHOUT SECRETS (CLEAN)",
        "description": "Standard HTTP Web Server Access Log",
        "line": "INFO 2026-09-10 12:00:12 [nginx] 192.168.1.50 - - GET /users/profile?tab=settings HTTP/1.1 200 1420 12ms"
    },
    {
        "category": "WITHOUT SECRETS (CLEAN)",
        "description": "Database Connection Timeout Error (No Credentials)",
        "line": "ERROR 2026-09-10 12:00:13 [db_pool] Connection timeout to host=db-replica-2.prod.internal port=5432 retry=3 error='Connection reset by peer'"
    },
    {
        "category": "WITHOUT SECRETS (CLEAN)",
        "description": "Base64 Image Metadata Header",
        "line": "INFO 2026-09-10 12:00:14 [avatar_service] Uploaded asset data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
]


def inspect_single_line(interceptor: LogShieldInterceptor, raw_line: str, category: str = "", description: str = ""):
    print("\n" + "=" * 90)
    if category or description:
        print(f"  [{category}] {description}")
        print("-" * 90)
    print(f"  RAW INPUT LOG:")
    print(f"    {raw_line}")
    print()

    # Detailed extraction and SCS score breakdown
    t0 = time.perf_counter()
    results = interceptor.engine.extract_and_score(raw_line)
    processing_ms = (time.perf_counter() - t0) * 1000

    # Process through full interceptor (vault + fingerprinter + sanitization)
    sanitized_line = interceptor.process_line(raw_line)

    print(f"  SANITIZED OUTPUT LOG:")
    print(f"    {sanitized_line}")
    print()

    if not results:
        print("  SCS ENGINE ANALYSIS: [NO SECRET CANDIDATES TRIGGERED / CLEAN LINE]")
        print(f"    • Decision: PASS")
        print(f"    • Engine Latency: {processing_ms:.3f} ms")
    else:
        print(f"  SCS ENGINE ANALYSIS ({len(results)} candidate(s) evaluated in {processing_ms:.3f} ms):")
        for i, res in enumerate(results, 1):
            print(f"    Candidate #{i}: '{res.token}'")
            print(f"      • Final SCS Score : {res.score} / 100")
            print(f"      • Engine Decision : [{res.decision}]")
            print(f"      • Detector Match  : {res.detector_name} (Category: {res.category}, Type: {res.detector_type})")
            print(f"      • 6-Factor Breakdown:")
            for factor_name, score in res.factors.items():
                weight = interceptor.engine.WEIGHTS.get(factor_name, 0)
                weighted_val = score * weight
                print(f"         - {factor_name:<13}: Raw Score = {score:.2f} | Weight = {weight:>2} | Weighted = {weighted_val:>6.2f}")


def run_demo():
    print("\n" + "=" * 90)
    print("  LOGSHIELD MODEL & SCS ENGINE INSPECTOR — DEMO SUITE")
    print("  Evaluating performance across real-world logs with secrets and clean non-secrets")
    print("=" * 90)

    interceptor = LogShieldInterceptor()
    # Print current active SCS weights (ML derived)
    print("\nActive SCS Weights (Loaded from optimal_weights.json):")
    for k, v in interceptor.engine.WEIGHTS.items():
        print(f"  • {k:<15}: {v}")

    for item in DEMO_LOGS:
        inspect_single_line(interceptor, item["line"], item["category"], item["description"])

    print("\n" + "=" * 90)
    print("  PERFORMANCE SUMMARY")
    print("=" * 90)
    print(f"  Total Lines Processed : {interceptor.stats['total_lines']}")
    print(f"  Secrets Redacted/Masked: {interceptor.stats['secrets_masked']}")
    print(f"  Secrets Flagged        : {interceptor.stats['secrets_flagged']}")
    print(f"  Clean Lines Passed     : {interceptor.stats['lines_clean']}")
    print(f"  Average Engine Latency : {interceptor.stats['avg_latency_ms']} ms")
    print("=" * 90 + "\n")


def run_interactive():
    print("\n" + "=" * 90)
    print("  LOGSHIELD INTERACTIVE LOG TESTER")
    print("  Type or paste any log line below to test model & SCS engine live.")
    print("  Type 'exit' or press Ctrl+C to quit.")
    print("=" * 90 + "\n")

    interceptor = LogShieldInterceptor()

    while True:
        try:
            user_input = input("LogShield> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                break
            inspect_single_line(interceptor, user_input, "INTERACTIVE INPUT", "Custom Log Line")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting interactive mode.")
            break


def run_file(file_path: str, max_lines: int = 5000, verbose: bool = False):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"\n" + "=" * 90)
    print(f"  LOGSHIELD BATCH FILE PROCESSOR")
    print(f"  Target File : {file_path} ({file_size_mb:.2f} MB)")
    if max_lines > 0:
        print(f"  Limit       : Processing up to {max_lines:,} lines (use --max-lines 0 for full file)")
    else:
        print(f"  Limit       : Processing ALL lines")
    print("=" * 90 + "\n")

    interceptor = LogShieldInterceptor()
    t_start = time.perf_counter()
    detected_secrets = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            if max_lines > 0 and line_num > max_lines:
                print(f"\n[Limit reached ({max_lines:,} lines). Stopping processing.]")
                break

            line = line.rstrip("\r\n")
            if not line:
                continue

            results = interceptor.engine.extract_and_score(line)
            sanitized = interceptor.process_line(line)

            if results:
                for r in results:
                    if r.decision in ("MASK", "FLAG"):
                        detected_secrets.append((line_num, line, sanitized, r))

            if verbose:
                print(f"[{line_num:06d}] {sanitized}")
            elif line_num % 10000 == 0:
                elapsed = time.perf_counter() - t_start
                lps = line_num / elapsed if elapsed > 0 else 0
                print(f"  Processed {line_num:,} lines... ({lps:,.0f} lines/sec | Secrets Masked: {interceptor.stats['secrets_masked']})")

    t_total = time.perf_counter() - t_start
    total_processed = interceptor.stats['total_lines']
    avg_lps = total_processed / t_total if t_total > 0 else 0

    print("\n" + "=" * 90)
    print("  FILE PROCESSING SUMMARY")
    print("=" * 90)
    print(f"  Total Lines Processed : {total_processed:,}")
    print(f"  Total Secrets Masked  : {interceptor.stats['secrets_masked']:,}")
    print(f"  Total Secrets Flagged : {interceptor.stats['secrets_flagged']:,}")
    print(f"  Clean Lines Passed    : {interceptor.stats['lines_clean']:,}")
    print(f"  Total Processing Time : {t_total:.2f} seconds ({avg_lps:,.0f} lines/sec)")
    print(f"  Average Engine Latency: {interceptor.stats['avg_latency_ms']} ms/line")

    if detected_secrets:
        print("\n" + "-" * 90)
        print(f"  SAMPLE DETECTED SECRETS / FLAGS ({len(detected_secrets)} hit(s)):")
        print("-" * 90)
        for line_num, raw, san, res in detected_secrets[:10]:  # Show up to 10
            print(f"  [Line #{line_num}] Decision: [{res.decision}] | SCS Score: {res.score}/100 | Detector: {res.detector_name}")
            print(f"    Raw      : {raw[:120]}")
            print(f"    Sanitized: {san[:120]}")
            print()
    else:
        print("\n  Result: 100% CLEAN — No secrets or credential leaks detected in processed log lines.")

    print("=" * 90 + "\n")


def main():
    parser = argparse.ArgumentParser(description="LogShield Model & SCS Engine Live Inspector")
    parser.add_argument("--demo", action="store_true", help="Run curated sample logs (with & without secrets)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive shell mode")
    parser.add_argument("--file", "-f", type=str, help="Path to log file to process")
    parser.add_argument("--max-lines", "-m", type=int, default=5000, help="Max lines to process for file mode (default: 5000, 0 for all)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print every sanitized log line to stdout")

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.interactive:
        run_interactive()
    elif args.file:
        run_file(args.file, max_lines=args.max_lines, verbose=args.verbose)
    else:
        # Default to demo if no args passed
        run_demo()


if __name__ == "__main__":
    main()
