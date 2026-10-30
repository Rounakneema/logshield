#!/usr/bin/env python3
"""
LogShield Detection & Ablation Benchmark Suite
==============================================
Evaluates 4 detector configurations:
  Config A: Regex-Only Baseline (600 standard rules)
  Config B: Regex + Shannon Entropy (H >= 3.5)
  Config C: 6-Factor SCS Baseline (Heuristic weights, no AC early-exit)
  Config D: LogShield Full Pipeline (AC + Preprocessor + Context + Classifier + SCS + Gating)

Computes:
  - TP, FP, TN, FN, Precision, Recall, F1, F2, FPR, FMR
  - Latency per line (ms)
  - Per-category breakdown (AWS, GitHub, JWT, Stripe, DB, Private Key, PII, etc.)
  - Hard negative rejection rate (Git commit, UUID, Trace ID, Sha256, etc.)
  - Adversarial robustness analysis
"""

import os
import sys
import time
import math
import argparse
import pandas as pd
import numpy as np
from collections import defaultdict
from multiprocessing import Pool, cpu_count

# Ensure sidecar import works
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from sidecar.logmask.scorer import SCSEngine
from sidecar.logmask.factors.regex_factor import RegexFactor
from sidecar.logmask.factors.entropy_factor import EntropyFactor
from sidecar.logmask.preprocessor import LogPreprocessor
from sidecar.logmask.factors.context_factor import ContextEngine

def calc_raw_shannon_entropy(token: str) -> float:
    if len(token) < 8:
        return 0.0
    freq = {}
    for c in token:
        freq[c] = freq.get(c, 0) + 1
    total = len(token)
    return -sum((n / total) * math.log2(n / total) for n in freq.values())

class BenchmarkRunner:
    def __init__(self):
        self.engine = SCSEngine()
        self.preprocessor = LogPreprocessor()
        self.regex_factor = RegexFactor()
        self.entropy_factor = EntropyFactor()
        self.context_engine = ContextEngine()

    def evaluate_line(self, line: str):
        """Evaluates a single line across all 4 configurations."""
        line = line.strip()
        t_start = time.perf_counter()

        # Config D: LogShield Full Pipeline
        t0 = time.perf_counter()
        res_d = self.engine.extract_and_score(line)
        lat_d = (time.perf_counter() - t0) * 1000.0
        pred_d = 1 if any(r.decision in ["MASK", "FLAG"] for r in res_d) else 0

        # Preprocessor extraction for baselines
        t0 = time.perf_counter()
        prep = self.preprocessor.process(line)
        tokens = [t.value for t in prep.tokens] if prep else []

        # Config A: Regex Only
        t_a0 = time.perf_counter()
        pred_a = 0
        for token in tokens:
            sc, _ = self.regex_factor.evaluate(token, line)
            if sc > 0:
                pred_a = 1
                break
        lat_a = (time.perf_counter() - t_a0) * 1000.0 + (t_a0 - t0) * 1000.0

        # Config B: Regex + Entropy >= 3.5
        t_b0 = time.perf_counter()
        pred_b = 0
        for token in tokens:
            sc, _ = self.regex_factor.evaluate(token, line)
            if sc > 0 and calc_raw_shannon_entropy(token) >= 3.5:
                pred_b = 1
                break
        lat_b = (time.perf_counter() - t_b0) * 1000.0 + (t_b0 - t0) * 1000.0

        # Config C: 6-Factor SCS Baseline (equal weights, no AC early exit)
        t_c0 = time.perf_counter()
        pred_c = 0
        for token_obj in (prep.tokens if prep else []):
            token = token_obj.value
            sc_regex, _ = self.regex_factor.evaluate(token, line)
            sc_entropy = self.entropy_factor.evaluate(token)
            sc_context = self.context_engine.score(token, line, "")
            # Equal weight combination
            raw_c = (sc_regex + sc_entropy + sc_context) / 3.0 * 100.0
            if raw_c >= 50.0:
                pred_c = 1
                break
        lat_c = (time.perf_counter() - t_c0) * 1000.0 + (t_c0 - t0) * 1000.0

        return {
            "pred_a": pred_a, "lat_a": lat_a,
            "pred_b": pred_b, "lat_b": lat_b,
            "pred_c": pred_c, "lat_c": lat_c,
            "pred_d": pred_d, "lat_d": lat_d,
        }

_worker_runner = None
def _init_worker():
    global _worker_runner
    _worker_runner = BenchmarkRunner()

def _worker_task(row_tuple):
    idx, label, s_type, text = row_tuple
    res = _worker_runner.evaluate_line(text)
    return (idx, label, s_type, res)

def compute_metrics(tp, fp, tn, fn, latencies):
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    f2 = 5 * (prec * rec) / (4 * prec + rec) if (4 * prec + rec) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fmr = fp / (tp + fp) if (tp + fp) > 0 else 0.0
    mean_lat = float(np.mean(latencies)) if latencies else 0.0
    p50_lat = float(np.percentile(latencies, 50)) if latencies else 0.0
    p95_lat = float(np.percentile(latencies, 95)) if latencies else 0.0
    p99_lat = float(np.percentile(latencies, 99)) if latencies else 0.0
    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1": round(f1, 4),
        "F2": round(f2, 4),
        "FPR": round(fpr, 4),
        "FMR": round(fmr, 4),
        "Latency_Mean_ms": round(mean_lat, 4),
        "Latency_P50_ms": round(p50_lat, 4),
        "Latency_P95_ms": round(p95_lat, 4),
        "Latency_P99_ms": round(p99_lat, 4),
    }

def main():
    parser = argparse.ArgumentParser(description="LogShield Ablation & Detection Benchmark Suite")
    parser.add_argument("--dataset", default=os.path.join(ROOT_DIR, "research", "datasets", "benchmark_50k.csv"))
    parser.add_argument("--sample-size", "-n", type=int, default=20000, help="Number of rows to benchmark (e.g. 20000 or 50000)")
    parser.add_argument("--workers", "-w", type=int, default=max(1, cpu_count() - 2))
    args = parser.parse_args()

    out_dir = os.path.join(ROOT_DIR, "research", "results")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading dataset from: {args.dataset}")
    df = pd.read_csv(args.dataset)
    if args.sample_size and args.sample_size < len(df):
        df = df.sample(n=args.sample_size, random_state=42).reset_index(drop=True)
    print(f"Evaluating on {len(df):,} rows using {args.workers} workers...")

    tasks = [(i, row["LABEL"], row["TYPE"], str(row["LOG_TEXT"])) for i, row in df.iterrows()]

    t_start = time.time()
    with Pool(processes=args.workers, initializer=_init_worker) as pool:
        results = pool.map(_worker_task, tasks, chunksize=100)
    total_time = time.time() - t_start
    print(f"Completed evaluation in {total_time:.2f} seconds ({len(df)/total_time:.1f} lines/sec aggregate)")

    # Aggregate counts across configs
    counts = {
        "A": {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "lat": []},
        "B": {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "lat": []},
        "C": {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "lat": []},
        "D": {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "lat": []},
    }

    # Category stats for Config D
    cat_stats = defaultdict(lambda: {"total": 0, "tp": 0, "fn": 0, "fp": 0, "tn": 0})
    hard_neg_stats = defaultdict(lambda: {"total": 0, "rejected": 0, "false_alarm": 0})
    adversarial_stats = defaultdict(lambda: {"total": 0, "detected": 0, "missed": 0})

    for idx, label, s_type, res in results:
        # Standard secret target: SECRET and PII
        # Normal targets: NORMAL and HARD_NEGATIVE
        is_true_secret = (label in ["SECRET", "PII"])
        is_adversarial = (label == "ADVERSARIAL")
        is_hard_negative = (label == "HARD_NEGATIVE")
        is_normal = (label == "NORMAL")

        for cfg, key_pred, key_lat in [("A", "pred_a", "lat_a"), ("B", "pred_b", "lat_b"), ("C", "pred_c", "lat_c"), ("D", "pred_d", "lat_d")]:
            pred = res[key_pred]
            counts[cfg]["lat"].append(res[key_lat])
            
            # Standard metrics benchmark (Secret vs Non-Secret)
            if is_true_secret:
                if pred == 1: counts[cfg]["tp"] += 1
                else: counts[cfg]["fn"] += 1
            elif is_hard_negative or is_normal:
                if pred == 1: counts[cfg]["fp"] += 1
                else: counts[cfg]["tn"] += 1

        # Detailed breakdown for LogShield (Config D)
        pred_d = res["pred_d"]
        if is_true_secret:
            cat_stats[s_type]["total"] += 1
            if pred_d == 1: cat_stats[s_type]["tp"] += 1
            else: cat_stats[s_type]["fn"] += 1
        elif is_hard_negative:
            hard_neg_stats[s_type]["total"] += 1
            if pred_d == 0: hard_neg_stats[s_type]["rejected"] += 1
            else: hard_neg_stats[s_type]["false_alarm"] += 1
        elif is_adversarial:
            adversarial_stats[s_type]["total"] += 1
            if pred_d == 1: adversarial_stats[s_type]["detected"] += 1
            else: adversarial_stats[s_type]["missed"] += 1

    # Format Table I Ablation Results
    ablation_rows = []
    configs_desc = {
        "A": "Regex-Only Baseline (600 standard rules)",
        "B": "Regex + Shannon Entropy (H >= 3.5)",
        "C": "6-Factor SCS Baseline (Heuristic weights)",
        "D": "LogShield Full Pipeline (AC + Context + SCS)",
    }
    for cfg in ["A", "B", "C", "D"]:
        c = counts[cfg]
        m = compute_metrics(c["tp"], c["fp"], c["tn"], c["fn"], c["lat"])
        m["Config"] = cfg
        m["Architecture"] = configs_desc[cfg]
        ablation_rows.append(m)

    ablation_df = pd.DataFrame(ablation_rows)[["Config", "Architecture", "TP", "FP", "TN", "FN", "Precision", "Recall", "F1", "F2", "FPR", "Latency_Mean_ms", "Latency_P95_ms", "Latency_P99_ms"]]
    ablation_csv_path = os.path.join(out_dir, "ablation_metrics.csv")
    ablation_df.to_csv(ablation_csv_path, index=False)
    print("\n=== ABLATION STUDY RESULTS ===")
    print(ablation_df.to_string(index=False))

    # Format Category Breakdown for Config D
    cat_rows = []
    for cat, st in sorted(cat_stats.items()):
        rec = st["tp"] / st["total"] if st["total"] > 0 else 0.0
        cat_rows.append({"Category": cat, "Total": st["total"], "Detected_TP": st["tp"], "Missed_FN": st["fn"], "Recall": round(rec, 4)})
    cat_df = pd.DataFrame(cat_rows)
    cat_csv_path = os.path.join(out_dir, "category_breakdown.csv")
    cat_df.to_csv(cat_csv_path, index=False)
    print("\n=== TOP SECRET CATEGORY RECALL (CONFIG D) ===")
    print(cat_df.to_string(index=False))

    # Format Hard Negative Rejection Breakdown
    hn_rows = []
    for hn, st in sorted(hard_neg_stats.items()):
        rej_rate = st["rejected"] / st["total"] if st["total"] > 0 else 0.0
        hn_rows.append({"HardNegativeType": hn, "Total": st["total"], "TrueNegative_Suppressed": st["rejected"], "FalsePositive_Alarm": st["false_alarm"], "SuppressionRate": round(rej_rate, 4)})
    hn_df = pd.DataFrame(hn_rows)
    hn_csv_path = os.path.join(out_dir, "hard_negative_breakdown.csv")
    hn_df.to_csv(hn_csv_path, index=False)
    print("\n=== HARD NEGATIVE SUPPRESSION BREAKDOWN ===")
    print(hn_df.to_string(index=False))

    # Save Adversarial Summary
    adv_rows = []
    for adv, st in sorted(adversarial_stats.items()):
        det_rate = st["detected"] / st["total"] if st["total"] > 0 else 0.0
        adv_rows.append({"AdversarialVariant": adv, "Total": st["total"], "Detected": st["detected"], "Missed": st["missed"], "DetectionRate": round(det_rate, 4)})
    adv_df = pd.DataFrame(adv_rows)
    adv_csv_path = os.path.join(out_dir, "adversarial_breakdown.csv")
    adv_df.to_csv(adv_csv_path, index=False)
    print("\n=== ADVERSARIAL VARIANT SUMMARY ===")
    print(adv_df.to_string(index=False))

    print(f"\nAll benchmark results successfully saved to: {out_dir}")

if __name__ == "__main__":
    main()
