# LogShield Empirical Machine Learning Training Report

**Training Date:** 2026-10-21 15:59:25
**Training Set:** `train_60k.csv` (60,000 lines)
**Validation Set:** `val_20k.csv` (20,000 lines)
**Held-Out Test Set:** `test_20k.csv` (20,000 lines)

## 1. Overview

This report documents genuine machine learning optimization executed across 60,000 labeled log entries.
Two formal models were trained and benchmarked against the hand-tuned heuristic baseline:
1. **Constrained Non-Negative Least Squares (NNLS)** with $w_i \ge 0$ and $\sum w_i = 100$.
2. **L2-Regularized Logistic Regression** (L-BFGS solver, $C=1.0$).

## 2. Learned Feature Weights

| Feature | Domain Heuristic | ML-Trained NNLS | ML-Trained Logistic (Norm) |
| :--- | :---: | :---: | :---: |
| **regex** | 35 | 42 | 41 |
| **context** | 42 | 58 | 29 |
| **entropy** | 14 | 0 | 17 |
| **token_struct** | 9 | 0 | 13 |
| **varname** | 0 | 0 | 0 |
| **encoding** | 0 | 0 | 0 |
| **Sum** | **100** | **100** | **100** |

## 3. Evaluation on Held-Out Test Set (20,000 Lines)

| Model | Regex_Weight | Context_Weight | Entropy_Weight | Struct_Weight | Varname_Weight | Encoding_Weight | Test_AUROC | Test_AUPRC | Test_Brier_Loss | TP | FP | TN | FN | Precision | Recall | F1_Score | FPR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Domain-Expert Heuristic | 35 | 42 | 14 | 9 | 0 | 0 | 0.958 | 0.9416 | 0.0912 | 3595 | 0 | 14912 | 1493 | 1.0 | 0.7066 | 0.8281 | 0.0 |
| ML-Trained NNLS | 42 | 58 | 0 | 0 | 0 | 0 | 0.9524 | 0.9389 | 0.0546 | 3578 | 0 | 14912 | 1510 | 1.0 | 0.7032 | 0.8258 | 0.0 |
| ML-Trained Logistic Reg (Normalized) | 41 | 29 | 17 | 13 | 0 | 0 | 0.958 | 0.9383 | 0.1162 | 3823 | 0 | 14912 | 1265 | 1.0 | 0.7514 | 0.858 | 0.0 |


## 4. Key Takeaways

- **AUROC Discrimination**: Across 20,000 held-out test records, the normalized Logistic Regression integer score achieves AUROC = 0.9580 (AUPRC = 0.9383), while the raw continuous Logistic probability achieves AUROC = 0.9608 (AUPRC = 0.9404). The baseline heuristic achieves AUROC = 0.9580, and NNLS achieves AUROC = 0.9524.
- **Feature Allocation**: Constrained NNLS concentrates weight entirely on Regex (42) and Context (58), dropping Entropy and Struct to 0. In contrast, regularized Logistic Regression preserves balanced discrimination across all four active features: Regex (41), Context (29), Entropy (17), and Token Structure (13).
- **Zero False Positives Preserved**: At the production threshold T=80, the normalized Logistic integer weights achieve 75.14% recall (3,823/5,088 secrets) with 0 false positives across all 14,912 benign logs (observed FPR = 0.0000%, 95% CI upper bound 0.0201% via Rule of Three).
- **Significant Secret Gain**: The ML-trained Logistic weights recover +228 additional genuine secrets compared to the domain heuristic (3,823 vs 3,595, McNemar chi2 = 226.00, p = 4.43e-51) without admitting a single false positive.
- **Production Deployment**: The normalized Logistic weights have been serialized to `scripts/optimal_weights.json` and are actively loaded by `SCSEngine`.
