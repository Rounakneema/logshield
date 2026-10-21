#!/usr/bin/env python3
"""
LogShield Accuracy & Performance Evaluation Suite
===================================================
Evaluates LogShield SCS Multi-Stage Engine against labeled ground truth.
Usage:
    python scripts/evaluate_accuracy.py --sample-size 10000
    python scripts/evaluate_accuracy.py --all
"""

import os
import sys
import time
import argparse
from collections import defaultdict

# Ensure sidecar import works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sidecar.logmask.scorer import SCSEngine


def main():
    parser = argparse.ArgumentParser(description="LogShield Accuracy Evaluator")
    parser.add_argument("--sample-size", "-n", type=int, default=10000, help="Number of lines to evaluate")
    parser.add_argument("--all", action="store_true", help="Evaluate all 100,000 lines")
    parser.add_argument("--log-file", default="logs.txt", help="Path to logs file")
    parser.add_argument("--truth-file", default="ground_truth.txt", help="Path to ground truth file")
    args = parser.parse_args()

    log_file = args.log_file
    truth_file = args.truth_file

    if not os.path.exists(log_file) or not os.path.exists(truth_file):
        print(f"Error: Need both {log_file} and {truth_file}")
        sys.exit(1)

    print("Loading ground truth annotations...")
    truth_labels = {}  # line_number -> label
    truth_types = {}   # line_number -> secret type
    with open(truth_file, "r", encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                line_id = int(parts[0])
                truth_labels[line_id] = parts[1]
                truth_types[line_id] = parts[2] if len(parts) > 2 else "UNKNOWN"

    engine = SCSEngine()
    
    # Global metrics
    tp, fp, tn, fn = 0, 0, 0, 0
    type_stats = defaultdict(lambda: {"tp": 0, "fn": 0, "fp": 0, "tn": 0})
    latencies = []

    limit = None if args.all else args.sample_size
    print(f"Evaluating LogShield against {'ALL' if limit is None else limit:,} lines...")
    start_time = time.time()
    
    with open(log_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if limit and i > limit:
                break

            line_str = line.strip()
            if not line_str:
                continue
                
            t0 = time.perf_counter()
            results = engine.extract_and_score(line_str)
            t_elapsed = (time.perf_counter() - t0) * 1000.0
            latencies.append(t_elapsed)

            action = "ALLOW"
            if results:
                top_decision = max(results, key=lambda r: r.score).decision
                if top_decision in ["MASK", "FLAG"]:
                    action = "REDACT"
            
            expected = truth_labels.get(i, "NORMAL")
            s_type = truth_types.get(i, "NONE")
            
            is_secret = expected in ["SECRET", "PII"]
            did_redact = (action == "REDACT")
            
            if is_secret and did_redact:
                tp += 1
                type_stats[s_type]["tp"] += 1
            elif is_secret and not did_redact:
                fn += 1
                type_stats[s_type]["fn"] += 1
            elif not is_secret and did_redact:
                fp += 1
                type_stats[s_type]["fp"] += 1
            elif not is_secret and not did_redact:
                tn += 1
                type_stats[s_type]["tn"] += 1
                
            if i % 5000 == 0:
                print(f"Processed {i:,} lines... Current F1: {2*tp/(2*tp+fp+fn) if (2*tp+fp+fn) else 0:.4f}")

    total_time = time.time() - start_time
    total_evaluated = tp + fp + tn + fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fmr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    latencies.sort()
    p95_lat = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    p99_lat = latencies[int(len(latencies) * 0.99)] if latencies else 0.0

    print("\n" + "=" * 68)
    print("           LOGSHIELD ENTERPRISE ACCURACY & LATENCY REPORT")
    print("=" * 68)
    print(f"  Total Lines Evaluated : {total_evaluated:,}")
    print(f"  Total Elapsed Time    : {total_time:.2f} s ({total_evaluated / total_time:.0f} lines/sec)")
    print(f"  Latency (Per Line)    : Avg: {avg_lat:.3f} ms | P95: {p95_lat:.3f} ms | P99: {p99_lat:.3f} ms")
    print("-" * 68)
    print(f"  True Positives  (TP)  : {tp:,}")
    print(f"  False Positives (FP)  : {fp:,}")
    print(f"  True Negatives  (TN)  : {tn:,}")
    print(f"  False Negatives (FN)  : {fn:,}")
    print("-" * 68)
    print(f"  Precision             : {precision:.6f}  ({precision*100:.2f}%)")
    print(f"  Recall                : {recall:.6f}  ({recall*100:.2f}%)")
    print(f"  F1-Score              : {f1:.6f}  ({f1*100:.2f}%)")
    print(f"  False Mask Rate (FMR) : {fmr:.6f}")
    print("=" * 68)

    print("\nCategory Breakdown:")
    print(f"  {'Category':<24} {'TP':>6} {'FN':>6} {'FP':>6} {'Recall':>8}")
    print(f"  {'-'*24} {'---':>6} {'---':>6} {'---':>6} {'------':>8}")
    for cat, stats in sorted(type_stats.items()):
        cat_tp, cat_fn, cat_fp = stats["tp"], stats["fn"], stats["fp"]
        if cat_tp + cat_fn > 0:
            cat_rec = cat_tp / (cat_tp + cat_fn)
            print(f"  {cat:<24} {cat_tp:>6} {cat_fn:>6} {cat_fp:>6} {cat_rec*100:>7.2f}%")
        elif cat_fp > 0:
            print(f"  {cat:<24} {'-':>6} {'-':>6} {cat_fp:>6} {'N/A (FP)':>8}")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    main()
