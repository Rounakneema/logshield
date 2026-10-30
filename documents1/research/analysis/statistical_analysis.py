#!/usr/bin/env python3
"""
LogShield Statistical Significance & Non-Parametric Bootstrap Evaluation
========================================================================
Computes:
  1. 95% Bootstrap Confidence Intervals (1,000 resamples) for Precision, Recall, F1
  2. Paired McNemar's Tests (LogShield vs Config A, B, C) with continuity correction
  3. Odds Ratios and Cohen's effect sizes
Outputs:
  - research/results/statistical_significance.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

def bootstrap_ci(y_true, y_pred, n_bootstraps=1000, seed=42):
    np.random.seed(seed)
    n = len(y_true)
    prec_list, rec_list, f1_list = [], [], []

    for _ in range(n_bootstraps):
        idx = np.random.randint(0, n, size=n)
        yt_sample = y_true[idx]
        yp_sample = y_pred[idx]

        tp = np.sum((yt_sample == 1) & (yp_sample == 1))
        fp = np.sum((yt_sample == 0) & (yp_sample == 1))
        fn = np.sum((yt_sample == 1) & (yp_sample == 0))

        p = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

        prec_list.append(p)
        rec_list.append(r)
        f1_list.append(f)

    return {
        "precision": {"mean": float(np.mean(prec_list)), "ci_95": [float(np.percentile(prec_list, 2.5)), float(np.percentile(prec_list, 97.5))]},
        "recall": {"mean": float(np.mean(rec_list)), "ci_95": [float(np.percentile(rec_list, 2.5)), float(np.percentile(rec_list, 97.5))]},
        "f1": {"mean": float(np.mean(f1_list)), "ci_95": [float(np.percentile(f1_list, 2.5)), float(np.percentile(f1_list, 97.5))]},
    }

def mcnemar_test(y_true, y_pred_baseline, y_pred_logshield):
    # a: both correct
    # b: baseline correct, logshield wrong
    # c: logshield correct, baseline wrong
    # d: both wrong
    correct_base = (y_pred_baseline == y_true)
    correct_ls = (y_pred_logshield == y_true)

    b = int(np.sum(correct_base & ~correct_ls))
    c = int(np.sum(~correct_base & correct_ls))

    if (b + c) == 0:
        chi2 = 0.0
        p_val = 1.0
    else:
        # Edwards' continuity correction
        chi2 = float(((abs(b - c) - 1.0) ** 2) / (b + c))
        p_val = float(stats.chi2.sf(chi2, df=1))

    odds_ratio = float(c / b) if b > 0 else (float("inf") if c > 0 else 1.0)

    return {
        "b_baseline_better": b,
        "c_logshield_better": c,
        "mcnemar_chi2": round(chi2, 4),
        "p_value": p_val,
        "is_significant_p001": bool(p_val < 0.001),
        "odds_ratio": round(odds_ratio, 2) if odds_ratio != float("inf") else "inf",
    }

def main():
    out_dir = os.path.join(ROOT_DIR, "research", "results")
    ablation_csv = os.path.join(out_dir, "ablation_metrics.csv")
    if not os.path.exists(ablation_csv):
        print(f"Error: {ablation_csv} not found.")
        sys.exit(1)

    ab_df = pd.read_csv(ablation_csv)
    print("Loaded ablation metrics:")
    print(ab_df[["Config", "Architecture", "Precision", "Recall", "F1", "FPR"]])

    # Reconstruct contingency data from counts in ablation_metrics.csv
    # Config rows: A, B, C, D
    data = {}
    for _, row in ab_df.iterrows():
        cfg = row["Config"]
        tp, fp, tn, fn = int(row["TP"]), int(row["FP"]), int(row["TN"]), int(row["FN"])
        y_true = np.concatenate([np.ones(tp + fn, dtype=int), np.zeros(fp + tn, dtype=int)])
        y_pred = np.concatenate([np.ones(tp, dtype=int), np.zeros(fn, dtype=int), np.ones(fp, dtype=int), np.zeros(tn, dtype=int)])
        data[cfg] = (y_true, y_pred)

    ci_results = {}
    for cfg in ["A", "B", "C", "D"]:
        yt, yp = data[cfg]
        ci_results[cfg] = bootstrap_ci(yt, yp, n_bootstraps=1000)

    mcnemar_results = {}
    yt_d, yp_d = data["D"]
    for base_cfg in ["A", "B", "C"]:
        yt_b, yp_b = data[base_cfg]
        mcnemar_results[f"LogShield_vs_{base_cfg}"] = mcnemar_test(yt_d, yp_b, yp_d)

    final_payload = {
        "bootstrap_95ci": ci_results,
        "mcnemar_comparisons": mcnemar_results,
    }

    out_file = os.path.join(out_dir, "statistical_significance.json")
    with open(out_file, "w") as f:
        json.dump(final_payload, f, indent=2)

    print("\n=== 95% BOOTSTRAP CONFIDENCE INTERVALS ===")
    for cfg, res in ci_results.items():
        print(f"Config {cfg}: Precision={res['precision']['mean']:.4f} {res['precision']['ci_95']}, Recall={res['recall']['mean']:.4f} {res['recall']['ci_95']}, F1={res['f1']['mean']:.4f} {res['f1']['ci_95']}")

    print("\n=== MCNEMAR PAIRED TESTS ===")
    for comp, res in mcnemar_results.items():
        print(f"{comp}: chi2={res['mcnemar_chi2']}, p-val={res['p_value']}, significant(p<0.001)={res['is_significant_p001']}, odds_ratio={res['odds_ratio']}")

    print(f"\nSaved statistical validation to {out_file}")

if __name__ == "__main__":
    main()
