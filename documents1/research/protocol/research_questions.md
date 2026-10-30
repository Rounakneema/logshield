# LogShield Experimental Research Protocol & Hypotheses

**Protocol Version:** 1.0  
**Target Paper:** IEEE Transactions on Dependable and Secure Computing / IEEE S&P / EuroS&P format  
**Date:** 2026-10-21  

---

## 1. Research Questions (RQs)

- **RQ1 (Detection Efficacy):** Does the multi-stage, context-aware Secret Confidence Score (SCS) engine achieve superior detection accuracy ($F_1 \ge 0.98$) across diverse credential families (API keys, cloud tokens, database URIs, asymmetric private keys, and PII) compared to conventional rule-based baselines (pure Regex, pure Shannon entropy, and naive context matching)?
  - *Hypothesis $H_1$:* Integrating semantic context and structural validation will significantly improve precision ($p < 0.001$, McNemar's test) over pure regex and entropy baselines.

- **RQ2 (Hard-Negative Suppression):** Can LogShield effectively discriminate high-entropy benign tokens (Git SHA-1 commit hashes, UUIDv4 identifiers, cryptographic checksums, tracing IDs, and Docker digests) from true cryptographic credentials, achieving a False Positive Rate $\text{FPR} < 0.005$?
  - *Hypothesis $H_2$:* Context weighting combined with candidate token structure constraints eliminates $>99\%$ of false alarms triggered by pseudo-random system identifiers.

- **RQ3 (Ablation Impact):** What is the marginal contribution of each factor and stage (Preprocessor token isolation, Aho-Corasick early exit, semantic context windowing, Shannon entropy thresholds, and regex classification) to detection quality and computational throughput?
  - *Hypothesis $H_3$:* Aho-Corasick early filtering provides $>10\times$ throughput acceleration on benign logs, while context weighting accounts for the majority of false-positive reduction.

- **RQ4 (Latency & Runtime Overhead):** Can LogShield operate as an in-pod Kubernetes sidecar within enterprise latency budgets ($P99 < 1.0\text{ ms}$) and maintain sustained throughput exceeding $10,000\text{ lines/s/core}$ with $<50\text{ MB}$ memory footprint?
  - *Hypothesis $H_4$:* The prefilter and single-pass pipeline design constrain per-line median overhead to $<0.3\text{ ms}$, rendering in-pod sidecar deployment transparent to application workloads.

- **RQ5 (Cryptographic Robustness & Exposure Reduction):** Does in-pod pre-ingestion redaction effectively reduce secret exposure rates to downstream aggregators to $<0.01\%$ while providing tamper-evident retrieval through authenticated symmetric vaulting (SecureReveal) and blind sprawl tracking (SecretLineage)?
  - *Hypothesis $H_5$:* Intercepting logs in shared memory before host serialization eliminates unencrypted log transmission, while HMAC-SHA256 blind fingerprinting enables cross-pod sprawl detection without exposing secret values.

---

## 2. Experimental Variables & Metrics

### Independent Variables
- Detector Configuration (Regex-only, Entropy-only, Context-only, Heuristic SCS, Full LogShield)
- Log Line Payload Size (256 B, 1 KB, 4 KB)
- Secret Density & Category (AWS, Stripe, GitHub, Private Key, Database, JWT, PII, Benign Normal, Hard Negative, Adversarial)
- Decision Threshold $S_{crit} \in [10, 95]$

### Dependent Evaluation Metrics
- **Detection Quality:** True Positives ($TP$), False Positives ($FP$), True Negatives ($TN$), False Negatives ($FN$), Precision ($P$), Recall ($R$), $F_1\text{-score}$, False Positive Rate ($FPR = \frac{FP}{FP + TN}$).
- **Performance:** Mean Latency ($\mu$), Median ($P50$), 95th Percentile ($P95$), 99th Percentile ($P99$), Sustained Throughput (lines/s and MB/s).
- **Security & Integrity:** Secret Exposure Rate ($ER = \frac{FN}{Total\ Secrets}$), Hash Chain Verification Success Rate ($CR$), Cryptographic Verification Latency.
