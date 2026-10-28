# LogShield Reconciled Statistical Analysis & Hypothesis Testing Report

**Date:** 21 October 2026  
**Methodology:** Finite-Sample Inference, Exact Clopper-Pearson Intervals, Rule of Three, Paired McNemar Tests, and 1,000-Iteration Non-Parametric Bootstrapping  
**Associated Scripts:** `research/audit/reconcile_all.py`, `research/scripts/run_detection_and_ablation.py`  
**Datasets:** Standard In-The-Wild Corpus ($N=9,205$) and Combined Adversarial Stress Corpus ($N=10,000$)

---

## 1. Experimental Objectives & Statistical Framework

The primary statistical goal of this audit is to rigorously test whether LogShield's multi-factor, context-aware architecture yields a statistically significant improvement over baseline methods, and to quantify the uncertainty surrounding its empirical performance metrics—particularly its zero false-positive rate.

### Research Hypotheses
We formalize three primary null hypotheses:
- **$H_{0,1}$ (Precision Superiority):** The false-positive suppression of LogShield (Config D) is indistinguishable from regex-only (Config A) or regex+entropy (Config B) detection.
- **$H_{0,2}$ (Detection Recall):** The contextual and entropy scoring mechanisms in LogShield do not increase secret recall relative to single-factor heuristics.
- **$H_{0,3}$ (Operational Equivalency):** Discrepancies between LogShield and baseline models are attributable to random sampling variance within the test corpus.

---

## 2. Finite-Sample Uncertainty & The Zero False-Positive Rate

### 2.1 The Degenerate Bootstrap Problem
In standard empirical software engineering literature, non-parametric bootstrapping is frequently employed to generate confidence intervals. However, when an empirical evaluation observes zero false positives ($FP = 0$ out of $N_{\text{neg}} = 4,778$), standard resampling draws only from the set $\{0\}$, producing a degenerate interval $[\text{FPR}_{\text{lower}}, \text{FPR}_{\text{upper}}] = [0.0, 0.0]$ and $[\text{Precision}_{\text{lower}}, \text{Precision}_{\text{upper}}] = [1.0, 1.0]$. 

This is methodologically unsound: an observed zero in a sample of size $n$ does not establish that the population parameter is zero.

### 2.2 Mathematical Bounding via the Rule of Three
To quantify the upper bound of the true false-positive rate when $k = 0$ events are observed in $n$ independent trials, we apply the Poisson approximation to the binomial distribution (Hanley & Lippman-Hand, 1983; Louis, 1981):

$$P(k = 0 \mid p, n) = (1 - p)^n \le \alpha$$

Taking the natural logarithm of both sides:
$$n \ln(1 - p) \le \ln(\alpha)$$

Using the first-order Taylor expansion $\ln(1 - p) \approx -p$ for small $p$:
$$-n p \le \ln(\alpha) \implies p \le \frac{-\ln(\alpha)}{n}$$

For a two-sided 95% confidence interval ($\alpha = 0.05$, with $\ln(0.05) \approx -2.99573$):
$$\hat{p}_{95\%} \le \frac{2.995732}{n} \approx \frac{3}{n}$$

Applying this formulation to our evaluation:
- Number of evaluated true negatives: $n = N_{\text{TN}} + N_{\text{FP}} = 4,778 + 0 = 4,778$.
- Observed false positives: $k = 0$.

$$\text{FPR}_{\text{upper, 95\%}} = \frac{2.995732}{4,778} = 0.0006270 \quad (0.0627\%)$$

**Statistical Interpretation:**  
We can assert with 95% confidence that LogShield's true false-positive rate in production is **at most 0.0627%** (less than 6.3 false alarms per 10,000 benign lines processed).

### 2.3 Exact Clopper-Pearson Intervals
The Clopper-Pearson method inverts the equal-tailed binomial test to compute exact confidence limits using the Beta distribution:

$$\text{Lower Bound} = \text{Beta}\left(\frac{\alpha}{2};\, k,\, n - k + 1\right)$$
$$\text{Upper Bound} = \text{Beta}\left(1 - \frac{\alpha}{2};\, k + 1,\, n - k\right)$$

#### Summary of Exact 95% Confidence Intervals:
| Metric | Point Estimate | Exact 95% Confidence Interval | Method |
| :--- | :---: | :---: | :--- |
| **False Positive Rate (FPR)** | 0.000000 | **$[0.000000,\, 0.000627]$** | Rule of Three / Exact Binomial |
| **Precision** | 1.000000 | **$[0.999167,\, 1.000000]$** | Exact Clopper-Pearson ($\text{Beta}(0.025; 4424, 1)$) |
| **Recall (Standard Corpus)** | 0.999322 | **$[0.998246,\, 0.999816]$** | Exact Clopper-Pearson ($TP=4424, FN=3$) |
| **Recall (Adversarial Corpus)**| 0.847248 | **$[0.837265,\, 0.856860]$** | Exact Clopper-Pearson ($TP=4424, FN=798$) |

---

## 3. Paired Hypothesis Testing (McNemar Test)

Because all four configurations (A, B, C, D) were evaluated on the exact same test dataset ($N=9,205$), individual test decisions are paired. We apply McNemar's test for paired nominal data with Edwards' continuity correction.

### 3.1 Contingency Matrix Formulation
For any baseline model $M_{\text{base}}$ versus LogShield $M_{\text{LS}}$:
- $a$: Both models correct.
- $b$: $M_{\text{base}}$ correct, $M_{\text{LS}}$ incorrect (LogShield regression).
- $c$: $M_{\text{base}}$ incorrect, $M_{\text{LS}}$ correct (LogShield improvement).
- $d$: Both models incorrect.

The test statistic with continuity correction is:
$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} \sim \chi^2(1)$$

### 3.2 Empirical Results

#### Comparison 1: LogShield (Config D) vs Regex-Only Baseline (Config A)
- Discordant classifications:
  - $b$ (Config A correct, Config D wrong): **3** (three multi-line PEM key chunks that bypassed context)
  - $c$ (Config D correct, Config A wrong): **820** (820 high-entropy benign identifiers falsely flagged by Config A)
- Test Statistic:
  $$\chi^2 = \frac{(|3 - 820| - 1)^2}{3 + 820} = \frac{(816)^2}{823} = \frac{665856}{823} = 809.06$$
- $p$-value: **$p = 5.79 \times 10^{-178}$** ($p \ll 0.001$)
- Odds Ratio: $\psi = \frac{c}{b} = \frac{820}{3} = \mathbf{273.33}$

**Conclusion:** Reject $H_{0,1}$ and $H_{0,3}$. LogShield is 273 times more likely to correct an error made by regex matching than to introduce an error where regex was correct.

#### Comparison 2: LogShield (Config D) vs Regex + Shannon Entropy (Config B)
- Discordant classifications:
  - $b$ (Config B correct, Config D wrong): **0**
  - $c$ (Config D correct, Config B wrong): **1,021** (718 false positives on UUIDs + 303 false negatives on low-entropy structured secrets)
- Test Statistic:
  $$\chi^2 = \frac{(|0 - 1021| - 1)^2}{1021} = \frac{(1020)^2}{1021} = 1019.00$$
- $p$-value: **$p = 1.33 \times 10^{-223}$** ($p \ll 0.001$)

**Conclusion:** Reject $H_{0,1}$. Entropy thresholding ($H \ge 3.5$) actively harms detection by missing low-entropy structured secrets while still triggering on high-entropy hex strings. LogShield strictly dominates Config B.

#### Comparison 3: LogShield (Config D) vs 6-Factor Heuristic SCS (Config C)
- Discordant classifications:
  - $b$ (Config C correct, Config D wrong): **0**
  - $c$ (Config D correct, Config C wrong): **530** (521 false positives + 9 false negatives)
- Test Statistic:
  $$\chi^2 = \frac{(|0 - 530| - 1)^2}{530} = 528.00$$
- $p$-value: **$p = 7.69 \times 10^{-117}$** ($p \ll 0.001$)

**Conclusion:** The addition of structural validation and calibrated tri-state gating significantly improves upon uncalibrated multi-factor scoring.

---

## 4. 1,000-Iteration Non-Parametric Bootstrap Distributions

To characterize the stability of performance metrics under resampling, we executed 1,000 bootstrap iterations ($B=1000$) with replacement across the $N=9,205$ evaluation corpus.

| Configuration | Metric | Mean | 95% Percentile Interval (Lower) | 95% Percentile Interval (Upper) | Standard Error ($\sigma$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Config A: Regex-Only** | Precision | 0.8436 | 0.8343 | 0.8540 | 0.0050 |
| | Recall | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| | F1-Score | 0.9152 | 0.9096 | 0.9213 | 0.0030 |
| **Config B: Regex + Entropy** | Precision | 0.8516 | 0.8418 | 0.8622 | 0.0052 |
| | Recall | 0.9308 | 0.9235 | 0.9385 | 0.0038 |
| | F1-Score | 0.8894 | 0.8827 | 0.8964 | 0.0035 |
| **Config C: 6-Factor SCS** | Precision | 0.8945 | 0.8862 | 0.9034 | 0.0044 |
| | Recall | 0.9973 | 0.9957 | 0.9987 | 0.0008 |
| | F1-Score | 0.9431 | 0.9383 | 0.9480 | 0.0025 |
| **Config D: LogShield Full** | Precision | 1.0000 | 1.0000* | 1.0000 | 0.0000 |
| | Recall | 0.9993 | 0.9984 | 1.0000 | 0.0004 |
| | **F1-Score** | **0.9997** | **0.9992** | **1.0000** | **0.0002** |

*\*Note: As established in Section 2, the exact Clopper-Pearson lower bound of 0.9992 supersedes the empirical bootstrap lower bound of 1.0000.*

---

## 5. Threshold Sensitivity & Receiver Operating Characteristics

To validate the tri-state decision gate thresholds ($T_{\text{flag}} = 50$, $T_{\text{mask}} = 80$), we swept the decision threshold $T \in [0, 100]$ in increments of 5 across the validation split ($N=20,000$).

```
Secret Confidence Score (SCS) Distribution:
  0 ───[PASS Zone: S < 50]─── 50 ───[FLAG Zone: 50 <= S < 80]─── 80 ───[MASK Zone: S >= 80]─── 100
  ├── Benign Text: μ = 4.2      ├── Ambiguous Context: μ = 62.4     ├── Verified Credentials: μ = 94.8
  └── Hard Negatives: μ = 18.6   └── Low-Entropy Tokens: μ = 58.1    └── High-Entropy Keys: μ = 98.2
```

### Empirical Metrics Across Decision Thresholds:
- **Area Under the ROC Curve (AUROC):** $\mathbf{0.9998}$
- **Area Under the Precision-Recall Curve (AUPRC):** $\mathbf{0.9999}$
- **Optimal Youden Index ($J = \text{TPR} - \text{FPR}$):** Achieved at $T = 75$ ($J = 0.9993$).
- **F1 Maximization Peak:** Spans $T \in [70, 85]$, confirming that $T_{\text{mask}} = 80$ is robustly positioned within the optimal performance plateau.

---

## 6. Adversarial Stress-Test Statistical Profile

When evaluating the combined adversarial dataset ($N=10,000$, incorporating 795 evasion attempts):

- **True Positives ($TP$):** 4,424
- **False Positives ($FP$):** 0
- **True Negatives ($TN$):** 4,778
- **False Negatives ($FN$):** 798 ($3\text{ standard} + 795\text{ evasions}$)
- **Combined Precision:** $\mathbf{1.0000}$ (95% CI: $[0.9992, 1.0000]$)
- **Combined Recall:** $\mathbf{0.8472}$ (95% CI: $[0.8373, 0.8569]$)
- **Combined F1-Score:** $\mathbf{0.9173}$ (95% CI: $[0.9104, 0.9240]$)

### Threat Boundary Summary
LogShield's statistical performance demonstrates a strict bifurcation:
1. **Accidental Developer Exposures (Standard Corpus):** Detection is near-perfect ($\text{F1} = 0.9997$, $\text{FPR} \le 0.063\%$).
2. **Intentional Obfuscation (Adversarial Corpus):** Single-pass string tokenizers fail on split and chunked vectors ($\text{Recall} = 0.0\%$). LogShield must be paired with host-level behavioral instrumentation if insider evasion is in scope.
