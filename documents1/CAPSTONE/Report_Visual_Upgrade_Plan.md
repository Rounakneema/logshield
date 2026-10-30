# LogShield Report — Visual Upgrade Plan
## How to Reduce Tables & Add 10–12 Impactful Images

---

## The Problem with the Current Report

The report has **14+ tables**. Academic reviewers skim. A wall of tables signals data dump, not insight. The fix: **replace 6 tables with visuals, and add 6 new original graphics** so the reader *feels* the system before they read it.

---

## Table Reduction Map

| Current Table | Replace With |
|---|---|
| §1.2 — Problem Statement (4-row comparison) | **Image 1** — Competitor comparison infographic |
| §1.3 — SCS Decision table | **Image 2** — Traffic light decision gate graphic |
| §2.1 — Literature Survey | **Image 3** — Radar chart showing LogShield vs. tools |
| §4.2 — Benchmark Results | **Image 4** — Bar chart: Precision / Recall / F1 |
| §4.3 — Ablation Table | **Image 5** — Grouped bar chart: A vs B vs C vs D |
| §7.1 — Advantages (9-row) | **Image 9** — Icon-grid benefit card layout |

Keep the remaining 8 tables — they contain technical data (edge cases, phase plan) that must stay as tables.

---

## 10–12 Image Generation Prompts (Ready to Use)

---

### Image 1 — Problem: Where Existing Tools Fail
**Section:** §1.2 Problem Statement
**Replaces:** The 4-row "Solution Category" table

**Prompt:**
> "A clean, bright, minimalist flat-design infographic. A horizontal timeline showing the software development lifecycle: (1) Code is Written, (2) Code is Committed to Git, (3) App Runs in Production, (4) Logs Sent to Cloud. Four tools are shown as labels below the timeline: 'Gitleaks' and 'TruffleHog' are placed at step 2, with a red X showing they are 'too late'. 'HashiCorp Vault' is placed at step 1, labelled 'prevents hardcoding — not logging'. 'Datadog SDS' is placed at step 4, labelled 'secret already left the pod'. In between steps 3 and 4, a bright green shield icon labelled 'LogShield' intercepts the flow with a green checkmark. White background, Inter font, professional explainer style, no excess decoration."

---

### Image 2 — SCS Decision Gate: The Traffic Light
**Section:** §1.3 Proposed Solution
**Replaces:** The 3-row SCS decision table

**Prompt:**
> "A clean, minimalist flat-design graphic showing three vertically stacked decision gates like a traffic light. Top gate: a red circle labelled 'SCS ≥ 80 — REDACT' with a small lock icon and text '[REDACTED: SEC-1049]'. Middle gate: an amber/yellow circle labelled 'SCS 50–79 — FLAG' with a flag icon and text '[FLAGGED: SEC-1049]'. Bottom gate: a green circle labelled 'SCS < 50 — PASS' with a checkmark and text 'Clean log line passed'. Light, bright background, modern UI design aesthetic, professional and minimal, Inter font."

---

### Image 3 — Competitor Radar Chart
**Section:** §2.1 Literature Survey
**Replaces:** The 4-row tool comparison table

**Prompt:**
> "A clean, professional radar/spider chart comparing 4 tools across 5 axes. The 5 axes are: 'Pre-Ingestion', 'Runtime Log Scanning', 'Encrypted Vault', 'Pattern Coverage', 'Zero Config K8s'. Four colored polygon overlays: Gitleaks (blue), HashiCorp Vault (purple), Datadog SDS (orange), and LogShield (bright green — largest, covering all 5 axes fully). White background, modern data visualization style, legend in the bottom right, Inter font, clean gridlines."

---

### Image 4 — Benchmark Bar Chart
**Section:** §4.2 Benchmark Results
**Replaces:** The single Precision/Recall/F1 table

**Prompt:**
> "A clean, modern data visualization bar chart. Three bars side by side: 'Precision' at 0.979 (teal/emerald), 'Recall' at 0.999 (blue), 'F1-Score' at 0.9889 (bright green, slightly taller). Each bar is annotated with its value on top. Below the chart, two smaller pill-shaped stat badges: 'Throughput: 12,847 lines/sec' and 'Avg Latency: 0.078ms'. White background, Inter font, minimal axis gridlines, professional data visualization style."

---

### Image 5 — Ablation Experiment Results
**Section:** §4.3 Ablation Experiment
**Replaces:** The 4-row ablation experiment table

**Prompt:**
> "A clean, professional grouped bar chart showing 4 experiment configurations and their F1-Scores. X-axis: A (Regex Only), B (Regex + Entropy), C (6-Factor SCS), D (Full Pipeline). Y-axis: F1-Score from 0.5 to 1.0. Bar heights: A=0.71, B=0.77, C=0.89, D=0.989. Bar D is highlighted in bright emerald green with a gold star or 'Best' badge on top. Other bars in a muted gray-blue. White background, Inter font, clean and minimal, annotated values on top of each bar."

---

### Image 6 — The 6-Stage Pipeline Flowchart
**Section:** §3.2 Core Innovation
**Supplements:** The ASCII art pipeline diagram (replace ASCII with a graphic)

**Prompt:**
> "A clean, vertical flowchart showing 6 colored stages connected by downward arrows. Stage 1: light gray box — 'Stage 1: Preprocessor — URL-decode, Base64-decode, JSON parse'. Stage 2: light blue box — 'Stage 2: Candidate Finder — Aho-Corasick prefilter, 65% early exit'. Stage 3: soft yellow box — 'Stage 3: Context Engine — keyword signals, log level'. Stage 4: soft orange box — 'Stage 4: Secret Classifier — 1361+ regex patterns'. Stage 5: light red box — 'Stage 5: Confidence Model — 8-factor Logistic Regression → SCS 0-100'. Stage 6: bright green box — 'Stage 6: Decision Gate — MASK / FLAG / PASS'. White background, Inter font, rounded rectangles, clean, professional."

---

### Image 7 — System Architecture Diagram
**Section:** §3.1 System Architecture
**Supplements:** The ASCII art pod diagram (replace ASCII with a graphic)

**Prompt:**
> "A clean, isometric flat-design architecture diagram showing one Kubernetes pod with a dotted border. Inside the pod: on the left, a gray box labelled 'Target App' with an arrow pointing right labelled 'app.log (emptyDir)'. In the center, a green box labelled 'LogShield Sidecar' containing three smaller nested boxes: 'LogMask Engine', 'SecureReveal Vault (SQLite)', 'Lineage Tracker (HMAC)'. From the sidecar, two arrows exit: one downward pointing to a blue cylinder labelled 'vault.db (AES-128-CBC)', and one to the right labelled 'Safe stdout → Fluent Bit → Loki'. White background, Inter font, professional cloud architecture diagram style."

---

### Image 8 — Eight-Pillar Coverage Chart
**Section:** §2.2 Eight-Pillar Taxonomy
**Supplements:** The 8-row taxonomy table

**Prompt:**
> "A clean, modern flat-design icon grid showing 8 pillars of secret detection. Arranged in a 4x2 grid. Each pillar is a rounded card with a small icon and label: (1) Pattern Specificity — magnifying glass icon, green checkmark. (2) Generic Heuristics — waveform icon, green checkmark. (3) Contextual Signals — speech bubble icon, green checkmark. (4) Structural Validation — brackets icon, green checkmark. (5) Encoding Awareness — code icon, green checkmark. (6) Variable Name Proximity — variable icon, green checkmark. (7) Multi-line Assembly — layers icon, yellow warning badge 'Phase 3'. (8) Active Validation — wifi icon, yellow warning badge 'Phase 4'. White background, Inter font, minimal card design."

---

### Image 9 — Advantage Icon Grid
**Section:** §7.1 Advantages
**Replaces:** The 9-row advantages table

**Prompt:**
> "A clean, professional infographic showing 9 benefit cards in a 3x3 grid. Each card is a small, rounded white box with a soft shadow, a colorful icon, and a short label: (1) shield icon — 'Pre-Ingestion Protection', (2) lightning icon — 'Sub-5ms Latency', (3) brain icon — 'ML-Calibrated Scoring', (4) eye icon — 'Context-Aware Detection', (5) tag icon — 'Vendor Attribution', (6) lock icon — 'AES-128 Encrypted Vault', (7) network icon — 'Secret Lineage Tracking', (8) plug icon — 'Zero-Config K8s Inject', (9) code icon — 'Open & Auditable'. Light gray background, Inter font, modern enterprise product design style."

---

### Image 10 — Secret Sprawl: Lineage Flow
**Section:** §8.3 Future Scope
**New addition — shows the HMAC lineage tracking concept visually**

**Prompt:**
> "A clean, minimal network graph diagram. In the center, a glowing orange node labelled 'Leaked Secret (HMAC Fingerprint)'. From it, lines connect outward to 4 surrounding gray rounded boxes, each labelled with a Kubernetes namespace: 'prod-ns', 'staging-ns', 'build-ns', 'tenant-a-ns'. Each connection line is labelled with a pod name like 'target-app-abc12'. Title at top: 'Secret Sprawl Lineage Map'. White background, Inter font, clean graph visualization, professional."

---

### Image 11 — Before / After Log Comparison
**Section:** §1.1 Introduction
**New addition — the single most impactful slide in the report**

**Prompt:**
> "A clean, side-by-side comparison card. Left side has a light red background labelled 'Before LogShield' showing a monospaced code block: 'INFO Connecting to DB: postgres://admin:MyP@ssw0rd123@prod:5432/app' with the password text highlighted in red. Right side has a light green background labelled 'After LogShield' showing: 'INFO Connecting to DB: postgres://admin:[REDACTED:SEC-A1B2:SCS=99]@prod:5432/app' with the REDACTED tag highlighted in green. A right-pointing arrow between the two panels. White background, Inter font, clear and minimal."

---

### Image 12 — Phase Timeline / Gantt
**Section:** §6 Phase-by-Phase Plan
**Supplements:** The 10-row phase plan table

**Prompt:**
> "A clean, horizontal Gantt-style timeline chart showing 10 phases across 10 weeks. Each phase is a horizontal colored bar. Phases 0–7 are colored solid emerald green and labelled 'Complete ✓'. Phase 8 (Dashboard) is colored amber/yellow and labelled 'In Progress'. Phase 9 (Production) is light gray and labelled 'Upcoming'. Week numbers (1–10) along the X-axis. Phase names on the Y-axis. White background, Inter font, professional project management style chart."

---

## Summary Placement Map

| # | Image | Section | Action |
|---|-------|---------|--------|
| 1 | Competitor Timeline | §1.2 | **Replaces** table |
| 2 | Traffic Light Decision Gate | §1.3 | **Replaces** table |
| 3 | Radar Chart | §2.1 | **Replaces** table |
| 4 | Benchmark Bar Chart | §4.2 | **Replaces** table |
| 5 | Ablation Bar Chart | §4.3 | **Replaces** table |
| 6 | 6-Stage Pipeline | §3.2 | **Replaces** ASCII art |
| 7 | Architecture Diagram | §3.1 | **Replaces** ASCII art |
| 8 | Eight-Pillar Grid | §2.2 | **Supplements** table |
| 9 | Advantage Icon Grid | §7.1 | **Replaces** table |
| 10 | Lineage Network Graph | §8.3 | **New addition** |
| 11 | Before/After Log Card | §1.1 | **New addition** |
| 12 | Phase Gantt Chart | §6 | **Supplements** table |
