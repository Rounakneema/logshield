# LogShield: In-Pod Secret Sanitization and Autonomous Closed-Loop Containment for Kubernetes Log Streams

**Rounak Neema**  
*Department of Computer Engineering, Mukesh Patel School of Technology Management & Engineering, NMIMS University, Mumbai, India*  
rounak.neema@nmims.edu  

**Capstone Research Group**  
*Cloud-Native Security Laboratory Project, LogShield Initiative, Mumbai, India*  
research@logshield.internal  

---

### Abstract
Microservice architectures managed by Kubernetes clusters generate huge volumes of container telemetry. Under continuous delivery pressures, developers often emit confidential credentials into standard output streams, including database connection strings, cloud access keys, private keys, and OAuth headers (CWE-532). Static scanners cannot inspect dynamically assembled runtime strings, and existing defenses leave major gaps. Centralized cloud sanitizers require network egress of raw log lines, exposing organizations to transit interception and violating data privacy regulations such as GDPR and HIPAA, while passive log redactors mask text after the fact but leave compromised credentials active in production environments until manual triage occurs hours or days later. To tackle these vulnerabilities, we present LogShield, a Kubernetes sidecar framework for real-time secret sanitization, keyed privacy-preserving lineage tracking, and autonomous closed-loop containment within the pod boundary. Masked credentials are encrypted locally in the SecureReveal Vault using Fernet authenticated encryption (AES-128-CBC with HMAC-SHA256), paired with a tamper-evident SHA-256 hash-chained audit ledger with remote SIEM anchoring. LogShield combines an O(N) Aho-Corasick prefilter, an adaptive sliding-window token fusion engine that defeats delimiter-split and hex-escaped obfuscation, a 6-factor Secret Confidence Score (SCS) model, and a tri-state decision gate; when active leaks emerge, it appraises blast radius and enforces automated mitigation via dynamic Kubernetes V1NetworkPolicy egress isolation and cloud credential rotation webhooks. To track cross-service credential sprawl without sharing plaintext strings, LogShield applies canonical keyed blind HMAC-SHA256 fingerprinting to join multi-representation artifacts (raw, Base64, Hex, URL-encoded), supported by a scoped exemption engine for pre-registered credentials. LogShield is evaluated across four experimental corpora, an isolated Kubernetes control plane testbed, and an end-to-end 5-microservice cluster. In standard ablation testing (N = 9,205), LogShield achieves an F1-score of 0.9997 (precision 1.0000, recall 0.9993) with zero false positives on benign controls (FPR ≤ 0.063%). On a balanced 2,400-sample adversarial evasion benchmark, Token Fusion raises detection recall from 32.20% to 91.30%, lowering evasion bypasses from 67.80% to 8.70% (a 59.1 percentage-point reduction) while producing no false positives on benign high-entropy system tokens. In separate statistical validation on 20,000 held-out entries, the ML-trained normalized model detects 228 additional secrets over domain-expert heuristic weights ($\chi^2 = 226.00, p = 4.43 \times 10^{-51}$) at a strictly zero false-positive threshold (T = 80). LogShield achieves automated workload egress quarantine with 16.7–26.7 ms policy dispatch latency and validated zero collateral disruption on non-leaking workloads in live Kubernetes testing.

*Index Terms*—Cloud-native security, Kubernetes sidecar, log sanitization, secret detection, CWE-532, Shannon entropy, Aho-Corasick automaton, NetworkPolicy quarantine, secret lineage.

---

## I. Introduction

Containerized microservices managed by Kubernetes form the primary foundation for cloud-native software systems; within these clusters, application logging offers the central source of telemetry for operational observability, distributed debugging, and security monitoring. Large-scale cloud deployments routinely create terabytes of unstructured application output each day.

High logging volumes create persistent security risks. Under rapid deployment schedules and complex runtime debugging requirements, developers regularly emit data structures containing raw credentials. Prevalent examples include logging complete HTTP headers, dumping environment variables during exceptions, and printing database URIs during connection timeouts:

```python
logger.debug(f"DB URI: {DATABASE_URL}")  # postgres://admin:MyP@ssw0rd@prod-db:5432/app
logger.error(f"Auth error: {headers['Authorization']}")  # Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
logger.info(f"Payment token: {STRIPE_SECRET_KEY}")  # sk_live_51H7x8...
logger.debug(f"Environment: {os.environ}")  # AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE...
```

When emitted to standard output (`stdout`), these strings pass directly to node-level forwarding daemons (such as Fluent Bit or Vector) and travel across network perimeters to centralized log platforms (such as Elasticsearch, Grafana Loki, or Datadog). Once indexed, credentials are stored in plain text, accessible to anyone with log read permissions. This vulnerability corresponds to CWE-532 (Insertion of Sensitive Information into Log File) and CWE-798 (Use of Hard-coded Credentials).

![Figure 1: LogShield in-pod deployment](figures/fig1_architecture.png)  
*Fig. 1. LogShield in-pod deployment. Co-located within the Kubernetes pod, the sidecar intercepts raw logs over a shared memory-backed emptyDir (tmpfs), detects secrets with adaptive token fusion, isolates them in an encrypted vault, enforces autonomous egress quarantine, and emits sanitized logs to container stdout.*

---

## II. Threat Model & System Invariants

### Formal Security Invariants
- **Invariant 1 (Policy-Conditioned Sanitization Invariant):** For any candidate credential $s \in \mathcal{C}_{\text{cand}}$ detected within log line $L$, if its confidence score satisfies $S(s) \ge T_{\text{mask}}$ (where operational threshold $T_{\text{mask}} = 80$), then $s$ is strictly replaced with an opaque surrogate tag before emission:
  $$\forall s \in \mathcal{C}_{\text{cand}}, S(s) \ge T_{\text{mask}} \implies s \notin L' \land \tau(s) \in L'$$
- **Invariant 2 (Vault Secrecy & Authenticated Integrity):** Plaintext credentials are encrypted using Fernet authenticated encryption (AES-128-CBC with HMAC-SHA256) before storage:
  $$C = \text{Fernet-Encrypt}_{K_v}(s)$$
- **Invariant 3 (Keyed Privacy-Preserving Blind Lineage):** Lineage records store only keyed blind fingerprints:
  $$\phi^* = \text{HMAC-SHA256}(K_{\text{lineage}}, \mathcal{C}(s))$$
- **Invariant 4 (Tamper-Evident Audit Ledger with Remote Anchoring):** Audit records are linked sequentially via SHA-256 hash chains.
- **Invariant 5 (Bounded Processing Complexity):** Regex matching is gated by keyword verification and bounded by an asynchronous 5.0 ms watchdog timer.
- **Invariant 6 (Workload-Scoped Egress Quarantine):** When containment triggers for a leaking pod $P_{\text{leak}}$, dynamic `V1NetworkPolicy` isolation applies strictly to $P_{\text{leak}}$.

---

## IV. System Architecture

![Figure 2: LogShield 6-Stage Detection Pipeline](figures/fig2_pipeline.png)  
*Fig. 2. The LogShield six-stage detection pipeline: ingestion, multi-line normalization and sliding-window Token Fusion (Stage 1), Aho-Corasick candidate keyword filtering (Stage 2), dynamic context scoring (Stage 3), layered pattern classification (Stage 4), 6-factor SCS scoring (Stage 5), and tri-state decision gating (Stage 6).*

---

## V. Secret Lineage Graph

![Figure 3: Secret Lineage Graph](figures/fig6_lineage.png)  
*Fig. 3. Secret lineage graph, mapping cross-pod credential proliferation using canonical HMAC-SHA256 blind fingerprints across mixed encodings with zero node collision.*

---

## VII. Experimental Evaluation

### C. Controlled Multi-Stage Ablation Analysis

Table IV and Fig. 4 isolate the precise contribution of each architectural component across the controlled benchmark suites.

#### TABLE IV: Controlled 6-Stage Ablation Study Isolating Individual Pipeline Mechanisms on Identical Benchmark Inputs

| Config | Architecture Description | Precision | Recall | F1-Score | F2-Score | FP Rate | Avg. Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Part A** | **Standard In-the-Wild Evaluation ($N = 9,205$, Evasion Vectors Excluded)** | | | | | | |
| **Stage 1** | Regex-Only Baseline (600 standard rules) | 0.8437 | 1.0000 | 0.9152 | 0.9643 | 17.16% | 6.528 ms |
| **Stage 2** | Regex + Aho-Corasick Early-Exit Filter | 0.8437 | 1.0000 | 0.9152 | 0.9643 | 17.16% | 0.209 ms |
| **Stage 3** | Regex + AC + Context Window Proximity | 0.8944 | 0.9854 | 0.9377 | 0.9658 | 10.90% | 0.384 ms |
| **Stage 4** | Regex + AC + Context + 6-Factor SCS ($T = 80$) | **1.0000** | **0.9993** | **0.9997** | **0.9995** | **0.00%**\* | **0.504 ms** |
| **Part B** | **Combined Adversarial Stress-Test ($N = 10,000$, 795 Evasion Vectors Counted as False Negatives)** | | | | | | |
| **Stage 5** | Stage 4 Pipeline under Evasion (Token Fusion Disabled) | **1.0000** | 0.8472 | 0.9173 | 0.8737 | **0.00%**\* | 0.504 ms |
| **Stage 6** | **LogShield Full Pipeline** (Stage 4 + Token Fusion Active) | **1.0000** | **0.9130**† | **0.9545**† | **0.9291**† | **0.00%**\* | **0.586 ms** |

*\* Rule-of-Three 95% upper confidence bound for FPR in 4,778 true negatives is $\text{FPR} \le 0.063\%$; exact Clopper-Pearson 95% CI for precision is $[0.9992, 1.0000]$.*  
*† Evaluated on the dedicated balanced adversarial evasion corpus ($N = 2,400$).*

![Figure 4: Controlled Ablation Study](figures/fig4_ablation.png)  
*Fig. 4. Controlled ablation study: precision, recall, and F1-score across detector configurations on the standard in-the-wild benchmark corpus ($N = 9,205$).*

---

### D. Adversarial Evasion Benchmark on 2,400 Labeled Samples

![Figure 5: Adversarial Evasion Benchmark](figures/fig7_evasion_benchmark.png)  
*Fig. 5. Adversarial evasion benchmark: detection recall comparison between the Baseline Scanner and the LogShield Adaptive Pipeline across the five evasion categories ($N = 2,400$).*

---

### E. Live Kubernetes Cluster Containment & Phase-Defined Latencies

![Figure 6: Closed-Loop Containment Lifecycle](figures/fig8_containment_lifecycle.png)  
*Fig. 6. Closed-loop autonomous containment lifecycle: real-time detection, SecretLineage blast radius correlation, dynamic V1NetworkPolicy egress quarantine, and zero collateral workload impact.*

---

### G. Latency and Throughput Across Operational Regimes

![Figure 7: Processing Latency and Throughput Scaling](figures/fig5_benchmark.png)  
*Fig. 7. Processing latency breakdown across the stages (left) and throughput scaling across payload sizes from 256 B to 8 KB (right).*
