#!/usr/bin/env python3
"""
LogShield Decision Threshold Calibration & Sensitivity Sweep
============================================================
Sweeps threshold S in [10, 95] on the validation dataset (val_20k.csv)
to characterize the trade-off between Secret Exposure Rate (ER) and False Positive Burden.
Outputs:
  - research/results/threshold_sweep.csv
"""

import os
import sys
import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from sidecar.logmask.scorer import SCSEngine

_engine = None
def _init_worker():
    global _engine
    _engine = SCSEngine()

def _score_line(row_tuple):
    idx, label, text = row_tuple
    # Returns (is_true_secret, max_raw_score)
    is_sec = 1 if label in ["SECRET", "PII"] else 0
    res = _engine.extract_and_score(text)
    max_score = max([r.score for r in res], default=0)
    return (is_sec, max_score)

def main():
    val_path = os.path.join(ROOT_DIR, "research", "datasets", "val_20k.csv")
    out_dir = os.path.join(ROOT_DIR, "research", "results")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading validation set from: {val_path}")
    df = pd.read_csv(val_path)
    # Filter to standard secret evaluation (SECRET, PII vs NORMAL, HARD_NEGATIVE)
    eval_df = df[df["LABEL"].isin(["SECRET", "PII", "NORMAL", "HARD_NEGATIVE"])].copy()
    print(f"Evaluating threshold sweep on {len(eval_df):,} lines...")

    tasks = [(i, row["LABEL"], str(row["LOG_TEXT"])) for i, row in eval_df.iterrows()]
    workers = max(1, cpu_count() - 2)
    with Pool(processes=workers, initializer=_init_worker) as pool:
        results = pool.map(_score_line, tasks, chunksize=100)

    # Threshold sweep from 10 to 95 in steps of 5
    thresholds = list(range(10, 100, 5))
    sweep_rows = []

    for thresh in thresholds:
        tp, fp, tn, fn = 0, 0, 0, 0
        for is_sec, score in results:
            pred = 1 if score >= thresh else 0
            if is_sec == 1 and pred == 1: tp += 1
            elif is_sec == 1 and pred == 0: fn += 1
            elif is_sec == 0 and pred == 1: fp += 1
            else: tn += 1

        prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        f2 = 5 * (prec * rec) / (4 * prec + rec) if (4 * prec + rec) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0  # Exposure Rate

        sweep_rows.append({
            "Threshold": thresh,
            "TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1": round(f1, 4),
            "F2": round(f2, 4),
            "FPR": round(fpr, 4),
            "ExposureRate_FNR": round(fnr, 4),
        })

    sweep_df = pd.DataFrame(sweep_rows)
    out_csv = os.path.join(out_dir, "threshold_sweep.csv")
    sweep_df.to_csv(out_csv, index=False)
    print("\n=== THRESHOLD SENSITIVITY SWEEP ===")
    print(sweep_df.to_string(index=False))
    print(f"\nSaved threshold sweep to {out_csv}")

if __name__ == "__main__":
    main()
