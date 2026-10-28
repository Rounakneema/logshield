# LogShield Final Independent Machine Learning Audit Report

**Audit Execution Date:** 2026-10-21 15:59:48
**Status:** **ALL 7 CHECKS INDEPENDENTLY PASSED (ZERO DISCREPANCIES)**

## 1. Executive Summary & Audit Check Status

| Check # | Description | Status | Evidence Summary |
| :---: | :--- | :---: | :--- |
| **1** | Metric Recalculation from Raw Predictions | **PASS** | Evaluated on all 20,000 raw test rows. Metrics verified exact. |
| **2** | AUROC & AUPRC Attribution Check | **PASS** | Distinguishes normalized integer score (0.9580) from raw continuous prob (0.9608). |
| **3** | Paired McNemar Test (228 Gained Secrets) | **PASS** | $b=0, c=228, \chi^2=226.00, p=4.43 \times 10^{-51}$. Exact Binomial: two-sided $p=2^{-227} \approx 4.64 \times 10^{-69}$, one-sided $p=2^{-228} \approx 2.32 \times 10^{-69}$. Effect size: +4.48%. |
| **4** | Deployed Scorer Architecture Inspection | **PASS** | SCSEngine executes Normalized Integer SCS; does not run float exp(). |
| **5** | Disagreement Analysis (Norm vs Raw) | **PASS** | Quantified 928 disagreements (730 secrets lost, 198 false alarms prevented). Documented score proxy qualification. |
| **6** | Validation-Only Threshold Selection Proof | **PASS** | Maximum benign validation score is 66.90, making $T=67$ the exact minimum 0-FP threshold. $T=80$ provides a $+13.10$-point margin of safety. |
| **7** | Production Numerical Agreement | **PASS** | Saved outputs strictly match underlying test prediction CSV. |

## 2. Recomputed Metrics on Held-Out Test Set (20,000 Records)

| Model Formulation | Score Domain | TP | FP | TN | FN | Precision | Recall | F1-Score | AUROC | AUPRC | Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Domain-Expert Heuristic (S >= 80)** | Normalized Integer Score [0, 100] | 3595 | 0 | 14912 | 1493 | 1.0000 | 0.7066 | 0.8281 | 0.9580 | 0.9416 | 0.0912* |
| **ML-Trained NNLS (S >= 80)** | Normalized Integer Score [0, 100] | 3578 | 0 | 14912 | 1510 | 1.0000 | 0.7032 | 0.8258 | 0.9524 | 0.9389 | 0.0546* |
| **ML-Trained Logistic Normalized (S >= 80)** | Normalized Integer Score [0, 100] | 3823 | 0 | 14912 | 1265 | 1.0000 | 0.7514 | 0.8580 | 0.9580 | 0.9383 | 0.1162* |
| **ML-Trained Logistic Raw Prob (p >= 0.50)** | Continuous Calibrated Probability [0.0, 1.0] | 4553 | 198 | 14714 | 535 | 0.9583 | 0.8949 | 0.9255 | 0.9608 | 0.9466 | 0.0305* |

*> Note on Brier Score: For integer ranking models, dividing the operational score by 100 ($S/100$) represents a linear ranking proxy, not a calibrated posterior probability. True probability calibration strictly applies to the continuous logistic regression model ($p = \sigma(\mathbf{\beta}^T \mathbf{x} + b)$), which achieves a calibrated Brier score of 0.0305.*

## 3. Paired Four-Outcome Table (Heuristic vs ML Logistic Normalized)

| Outcome Category | Count | Interpretation |
| :--- | :---: | :--- |
| **Both Correct ($a$)** | 3,595 | Detected by both Domain Heuristic and ML Logistic model. |
| **Heuristic Only ($b$)** | 0 | Regressions (Heuristic detected, ML missed). |
| **ML Logistic Only ($c$)** | **228** | **Net Gain (ML detected, Heuristic missed). Matches claimed 228.** |
| **Neither Correct ($d$)** | 1,265 | Missed by both models (low-context / ambiguous tokens). |
| **Total Positive Secrets** | **5,088** | All evaluated positive secret ground-truth lines. |

### Statistical Significance:
- **McNemar's Test Statistic (Edwards correction):** $\chi^2 = \mathbf{226.0044}$
- **Asymptotic Two-Tailed $p$-Value:** $p = \mathbf{4.4336e-51}$ ($p \ll 0.001$)
- **Exact Binomial Sign Test (Two-Sided, $H_1: p \neq 0.5$):** $p = 2 \times 0.5^{228} = 2^{-227} = \mathbf{4.6365e-69}$
- **Exact Binomial Sign Test (One-Sided, $H_1: p > 0.5$):** $p = 0.5^{228} = 2^{-228} = \mathbf{2.3183e-69}$
- **Recall Effect Size:** $+4.48\%$ (95% CI: $[3.90\%, 5.06\%$])
- **Odds Ratio:** $\psi = \frac{c}{b} = \frac{228}{0} = \mathbf{\infty}$

## 4. Architectural Analysis: Normalized Integer Weights vs Raw Logistic Regression

The deployed engine in `sidecar/logmask/scorer.py` evaluates:
$$S(s) = \min\left(100, \sum_{i=1}^6 w_i \cdot f_i(s)\right)$$
with $w = [41, 29, 17, 13, 0, 0]$ loaded from `scripts/optimal_weights.json`.

The audit compared this deployed implementation against the raw logistic regression model ($p = \sigma(\beta^T x + b)$ at $p \ge 0.50$):
- **Disagreement Count:** Exactly **928 lines** (4.64% of test set).
- **False Positive Suppression:** Raw logistic regression produces **198 False Positives** on benign lines (Precision drops to 95.83%). In contrast, the deployed Normalized Integer model at $T=80$ produces **0 False Positives** (Precision: 100.00%).
- **Trade-off Justification:** The deployed sidecar deliberately operates at an ultra-conservative operating point ($S \ge 80$), trading 730 marginal secret detections to satisfy the zero-false-positive operational requirement for production container logs.

## 5. Dense Validation Threshold Sweep & Zero-FP Boundary Proof

Threshold selection was audited across all 20,000 instances in the validation partition:
- **Validation Negative Sample Size:** $N_{\text{benign}} = 15,027$ lines.
- **Validation Maximum Benign Score:** $\max S(s)_{y=0} = \mathbf{66.90}$
- **Exact Minimum 0-FP Integer Threshold:** $T_{\min} = \lfloor 66.90 \rfloor + 1 = \mathbf{67}$
- **Operational Safety Margin:** $T_{\text{mask}} = 80$ provides a $\mathbf{+13.10}$-point safety buffer above the maximum benign score.

| Threshold ($T$) | Val Precision | Val Recall | Val F1 | Val FP | Val FPR |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 50 | 0.6891 | 0.9432 | 0.7964 | 2098 | 13.923% |
| 60 | 0.6809 | 0.9051 | 0.7771 | 2092 | 13.883% |
| 64 | 0.6809 | 0.9051 | 0.7771 | 2092 | 13.883% |
| 65 | 0.9998 | 0.8860 | 0.9395 | 1 | 0.007% |
| 66 | 0.9998 | 0.8860 | 0.9395 | 1 | 0.007% |
| 67 | 1.0000 | 0.8860 | 0.9396 | 0 | 0.000% |
| 70 | 1.0000 | 0.8860 | 0.9396 | 0 | 0.000% |
| 75 | 1.0000 | 0.8858 | 0.9395 | 0 | 0.000% |
| 80 | 1.0000 | 0.7662 | 0.8676 | 0 | 0.000% |
| 85 | 1.0000 | 0.7232 | 0.8394 | 0 | 0.000% |
| 90 | 1.0000 | 0.6638 | 0.7979 | 0 | 0.000% |

**Empirical Conclusion:** The validation partition proves that at $T=66$, exactly $1\text{ FP}$ occurs; at $T=67$, false positives drop to strictly **$0\text{ FP}$**. Operating at $T_{\text{mask}} = 80$ was established entirely prior to evaluating the held-out test set.
