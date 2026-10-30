# LogShield: IEEE Research Manuscript (6–8 Pages)

This directory contains the publication-grade implementation research paper for **LogShield**, formatted according to standard IEEE Conference / Transactions specifications (`IEEEtran.cls`), fully deslopped and mathematically formalized.

---

## Paper Details

- **Title:** *LogShield: A Context-Aware, In-Pod Secret Sanitization and Zero-Knowledge Lineage Tracking Architecture for Kubernetes Container Log Streams*
- **Target Venue:** IEEE Conference on Communications and Network Security (CNS) / IEEE Transactions on Dependable and Secure Computing (TDSC) / IEEE S&P.
- **Estimated Length:** 7–8 pages in IEEE two-column format (~5,600 words + 5 figures + 2 algorithms + 4 tables + 26 citations).
- **Prose Quality:** Fully deslopped per technical writing standards (active voice, zero AI tropes/filler, zero em-dashes, no bold-lead bullets, formal mathematical proofs).

---

## Directory Structure

```
d:/LOGSHEILD/paper/
├── logshield_ieee_paper.tex       # Complete IEEEtran LaTeX source
├── README.md                      # Compilation and overview documentation
└── figures/                       # High-resolution vector/raster diagram assets
    ├── fig7_architecture.png      # System architecture & in-pod interception
    ├── fig6_pipeline.png          # Six-stage detection pipeline (wide)
    ├── fig2_decision_gate.png     # Tri-state decision gate boundaries
    ├── fig5_ablation.png          # 4-way ablation study progression
    ├── fig4_benchmark.png         # Latency percentiles & throughput
    └── fig10_lineage.png          # HMAC-SHA256 blind sprawl graph
```

---

## Manuscript Structure & Mathematical Formulations

1. **Section I: Introduction**
   - Microservice observability requirements, CWE-532/CWE-798 vulnerabilities, analysis of 413 NVD CVEs.
   - Architectural failure modes of static code scanners (Gitleaks, TruffleHog), cloud-side DLPs (Datadog SDS, GCP DLP), and raw entropy filters.
   - Five concrete contributions of LogShield.

2. **Section II: Threat Model & System Invariants**
   - Four adversary capabilities: Downstream Log Consumer, Network Eavesdropper, Malicious Insider, Payload Injector.
   - Five formal invariants: Zero Plaintext Egress, Vault Secrecy, Zero-Knowledge Lineage, Forward-Secure Audit Immutability, and Deterministic Linear Processing Boundedness.
   - **Table I:** Formal mathematical notation table.

3. **Section III: Related Work**
   - Synthesizes findings from Zhi et al. (APSEC 2020), Aghili et al. (ACM FSE 2025), Slagell & Yurcik (NCSA), Portillo-Dominguez et al. (SafeLog), Meli et al. (NDSS 2019), Basak et al. (SecretBench), Saha et al. (COMSNETS 2020), Ahmed et al. (MSR 2026), and Huang et al. (ACM FSE 2024).

4. **Section IV: System Architecture**
   - In-pod Kubernetes sidecar IPC model using shared `emptyDir` memory volumes.
   - Detailed Six-Stage Detection Pipeline (Fig. 2) with Aho-Corasick early-exit filtering.
   - Tri-state Decision Gate: PASS ($S < 50$), FLAG ($50 \le S < 80$), REDACT ($S \ge 80$).

5. **Section V: Mathematical Formulation & Algorithmic Design**
   - **Prefix-Stripped Shannon Entropy:** $H(\hat{s}) = - \sum_{c \in \Sigma} P(c) \log_2 P(c)$, $\hat{s} = s \setminus \text{Prefix}(s)$, with 3-sigma Gaussian rejection rule.
   - **8-Dimensional Secret Confidence Score (SCS):** $S(s) = \lfloor 100 \cdot \sigma(\mathbf{w}^T \mathbf{x} + b) \rfloor$ with Non-Negative Least Squares (NNLS) weights (**Table II**).
   - **Aho-Corasick Automaton Linear Bound:** $T_{\text{prefilter}}(N) = O(N)$.
   - **Blind HMAC-SHA256 Secret Lineage Graphing:** Bipartite graph $\mathcal{G} = (\mathcal{V}_{\text{pod}}, \mathcal{V}_{\text{sec}}, \mathcal{E})$ and Sprawl Risk Index $\mathcal{R}(\phi_s)$.
   - **Forward-Secure Audit Hash Chaining:** $\mathcal{H}_k = \text{SHA256}(\mathcal{H}_{k-1} \parallel A_k)$ with **Theorem 1** tamper-detection proof.
   - **Algorithm 1:** In-Pod Stream Interception and Multi-Factor Sanitization.

6. **Section VI: SecureReveal Vault Architecture**
   - AES-256-GCM AEAD authenticated encryption with 96-bit CSPRNG IVs and `RefID` additional authenticated data.
   - Constant-time actor verification (`hmac.compare_digest`) preventing side-channel timing attacks.
   - **Algorithm 2:** SecureReveal Decryption and Audit Logging.

7. **Section VII: Implementation & Empirical Evaluation**
   - 50,000-line ground-truth benchmark dataset (SecretBench + LogHub).
   - **Table III:** 4-Way Ablation Study (Regex vs. Entropy vs. SCS vs. LogShield Full Pipeline).
   - **Table IV:** Processing Latency across Pipeline Stages (Mean: 0.078 ms, P95: 0.23 ms, P99: 0.41 ms, Throughput $>12,800$ lines/s/core).
   - Active 5-microservice Kubernetes cluster deployment testbed (`auth`, `payment`, `user`, `inventory`, `notification`) under continuous synthetic traffic.

8. **Sections VIII–XI:**
   - Security Analysis (Algorithmic ReDoS resistance, Multi-line token reconstruction, Fail-Open policy).
   - Discussion & Future Work (Kernel-space eBPF redaction, Hardware enclaves / SGX, Post-quantum lineage).
   - Conclusion & 26 formal IEEE citations.

---

## Compiling the Paper

### Overleaf
1. Go to [Overleaf](https://www.overleaf.com/) $\to$ **New Project** $\to$ **Upload Project**.
2. Upload the `paper/` directory.
3. Select **pdfLaTeX** as the compiler and click **Recompile**.

### Local LaTeX Installation
```bash
cd d:/LOGSHEILD/paper
pdflatex logshield_ieee_paper.tex
pdflatex logshield_ieee_paper.tex
```
