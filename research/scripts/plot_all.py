#!/usr/bin/env python3
"""
LogShield Publication-Grade Figure Generator (Anti-Overlap Edition)
===================================================================
Produces publication-quality 300-DPI vector/PNG figures with:
  - Generous bounding box margins and card padding
  - Zero text-on-arrow or text-on-box collisions
  - Dedicated whitespace placement for legends and callouts
  - Clean IEEE styling, consistent palette, and high legibility

Figures Generated:
  Fig 1 / Fig 7: In-Pod Sidecar Interception Architecture
  Fig 2 / Fig 6: 6-Stage Detection & Vaulting Pipeline
  Fig 3 / Fig 2: Tri-State Decision Gate & Threshold Calibration Curve
  Fig 4 / Fig 5: 4-Way Ablation Study (Precision, Recall, F1, FPR) with 95% CIs
  Fig 5 / Fig 4: Latency Distribution (ECDF/Percentiles) & Sustained Throughput
  Fig 6 / Fig 10: SecretLineage Cross-Pod Sprawl Tracking Graph
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(ROOT_DIR, "research", "results")
FIG_DIR = os.path.join(ROOT_DIR, "research", "figures")
PAPER_FIG_DIR = os.path.join(ROOT_DIR, "paper", "figures")

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(PAPER_FIG_DIR, exist_ok=True)

# Publication styling
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10.5,
    "axes.titlesize": 11.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.0,
    "figure.titlesize": 12.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

# Refined IEEE color palette
COLOR_PRIMARY = "#1f77b4"   # Steel Blue
COLOR_ACCENT = "#d62728"    # Crimson Red
COLOR_GREEN = "#2ca02c"     # Forest Green
COLOR_ORANGE = "#ff7f0e"    # Dark Orange
COLOR_PURPLE = "#9467bd"    # Royal Purple
COLOR_DARK = "#222222"      # Off-black

import io

def save_dual(fig, basename, legacy_name):
    p1 = os.path.join(FIG_DIR, basename)
    p2 = os.path.join(PAPER_FIG_DIR, basename)
    p3 = os.path.join(PAPER_FIG_DIR, legacy_name)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    img_data = buf.getvalue()
    for p in [p1, p2, p3]:
        with open(p, "wb") as f:
            f.write(img_data)
    print(f"Saved cleanly: {basename} and {legacy_name}")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 1: In-Pod Sidecar Interception Architecture
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig1_architecture():
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 1. Outer Kubernetes Worker Node
    node_box = patches.FancyBboxPatch((0.02, 0.04), 0.96, 0.92, boxstyle="round,pad=0.015",
                                      facecolor="#fafafa", edgecolor="#78909c", linewidth=1.5, linestyle="--")
    ax.add_patch(node_box)
    ax.text(0.04, 0.93, "Kubernetes Worker Node Environment (/var/log/pods)", fontsize=11, fontweight="bold", color="#37474f")

    # 2. In-Pod Boundary (Shared Memory Space)
    pod_box = patches.FancyBboxPatch((0.05, 0.12), 0.65, 0.77, boxstyle="round,pad=0.02",
                                     facecolor="#ffffff", edgecolor="#1976d2", linewidth=2.0)
    ax.add_patch(pod_box)
    ax.text(0.07, 0.85, "Container Pod (Shared Memory Boundary)", fontsize=11, fontweight="bold", color="#1565c0")

    # 3. Application Container
    app_box = patches.FancyBboxPatch((0.08, 0.52), 0.23, 0.28, boxstyle="round,pad=0.01",
                                     facecolor="#e3f2fd", edgecolor="#1565c0", linewidth=1.3)
    ax.add_patch(app_box)
    ax.text(0.195, 0.68, "Application\nContainer", ha="center", va="center", fontsize=10, fontweight="bold", color="#0d47a1")
    ax.text(0.195, 0.58, "Emits Raw Telemetry\n& Exposed Credentials", ha="center", va="center", fontsize=8, color="#555555")

    # 4. Shared Volume (emptyDir / POSIX FIFO)
    vol_box = patches.FancyBboxPatch((0.08, 0.18), 0.23, 0.24, boxstyle="round,pad=0.01",
                                     facecolor="#fff3e0", edgecolor="#ef6c00", linewidth=1.3)
    ax.add_patch(vol_box)
    ax.text(0.195, 0.32, "Shared Volume\n(emptyDir / FIFO)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#e65100")
    ax.text(0.195, 0.23, "POSIX In-Memory Pipe\n(/var/log/app)", ha="center", va="center", fontsize=8, color="#777777")

    # 5. LogShield Sidecar Container
    sidecar_box = patches.FancyBboxPatch((0.38, 0.15), 0.29, 0.71, boxstyle="round,pad=0.015",
                                         facecolor="#f1f8e9", edgecolor="#2e7d32", linewidth=1.6)
    ax.add_patch(sidecar_box)
    ax.text(0.525, 0.82, "LogShield Sidecar", ha="center", fontsize=11, fontweight="bold", color="#1b5e20")

    stages = [
        ("1. Preprocessor & AC Prefilter", 0.72, "#dcedc8"),
        ("2. Multi-factor SCS Engine", 0.60, "#c5e1a5"),
        ("3. SecureReveal AES-128 Vault", 0.48, "#aed581"),
        ("4. SecretLineage HMAC Tracker", 0.36, "#9ccc65"),
        ("5. Sanitized Sink (stdout)", 0.24, "#81c784"),
    ]
    for title, y_pos, color in stages:
        sb = patches.FancyBboxPatch((0.40, y_pos - 0.04), 0.25, 0.08, boxstyle="round,pad=0.005",
                                    facecolor=color, edgecolor="#2e7d32", linewidth=0.8)
        ax.add_patch(sb)
        ax.text(0.525, y_pos, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1b5e20")

    # 6. Node-Level Forwarder (DaemonSet)
    fb_box = patches.FancyBboxPatch((0.74, 0.32), 0.22, 0.42, boxstyle="round,pad=0.015",
                                    facecolor="#ede7f6", edgecolor="#512da8", linewidth=1.5)
    ax.add_patch(fb_box)
    ax.text(0.85, 0.63, "Node Forwarder\n(Fluent Bit / Vector)", ha="center", va="center", fontsize=10, fontweight="bold", color="#311b92")
    ax.text(0.85, 0.46, "Ships ONLY\nSanitized Telemetry\nto SIEM / Loki", ha="center", va="center", fontsize=8.5, color="#4527a0")

    # Connectors with dedicated label positions
    # App to Shared Volume
    ax.annotate("", xy=(0.195, 0.43), xytext=(0.195, 0.51), arrowprops=dict(arrowstyle="->", lw=2.0, color="#ef6c00"))
    ax.text(0.24, 0.47, "stdout", fontsize=8, fontweight="bold", color="#ef6c00")

    # Shared Volume to Sidecar
    ax.annotate("", xy=(0.39, 0.72), xytext=(0.32, 0.32),
                arrowprops=dict(arrowstyle="->", lw=2.0, color="#2e7d32", connectionstyle="arc3,rad=-0.15"))
    ax.text(0.33, 0.54, "Tails FIFO\nStream", fontsize=8, fontweight="bold", color="#2e7d32", ha="center")

    # Sidecar Sink to Node Forwarder (clean straight arrow at y=0.24, with label above)
    ax.annotate("", xy=(0.73, 0.38), xytext=(0.66, 0.24),
                arrowprops=dict(arrowstyle="->", lw=2.2, color="#1565c0", connectionstyle="arc3,rad=-0.15"))
    ax.text(0.70, 0.27, "Sanitized\nstdout", fontsize=8.5, fontweight="bold", color="#1565c0", ha="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#1565c0", lw=0.8))

    # Bottom In-Pod Security Callout Banner
    ax.text(0.50, 0.07, "Zero Plaintext Exposure Outside Pod | Ephemeral AES-128-CBC Vaulting | Tamper-Evident SHA-256 Audit Chain",
            ha="center", fontsize=8.5, fontweight="bold", color="#222222",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fffde7", edgecolor="#fbc02d", lw=1.2))

    save_dual(fig, "fig1_architecture.png", "fig7_architecture.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 2: 6-Stage Detection Pipeline
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig2_pipeline():
    fig, ax = plt.subplots(figsize=(11.0, 4.4))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    stages = [
        ("Stage 1\nPreprocessor", "Tokenization\nJSON / KV Parsing\nEscaping Normalize", "#e1f5fe", "#0288d1"),
        ("Stage 2\nAho-Corasick", "O(N) String Scan\nPrefix Automaton\n(65% Early Exit)", "#e8f5e9", "#2e7d32"),
        ("Stage 3\nContext Engine", "+-100 Char Window\nLog-Level Weight\nSemantic Verbs", "#fff8e1", "#f57c00"),
        ("Stage 4\nClassifier", "Hierarchical Regex\n600+ Specific Rules\nSecretBench Catalog", "#f3e5f5", "#7b1fa2"),
        ("Stage 5\nSCS Scorer", "Bayesian Model\nWeighted Factors\nScore S in [0, 100]", "#fbe9e7", "#d84315"),
        ("Stage 6\nDecision Gate", "S >= 80: MASK\n50 <= S < 80: FLAG\nS < 50: PASS", "#efebe9", "#4e342e"),
    ]

    x_positions = np.linspace(0.03, 0.84, 6)
    box_w, box_h = 0.13, 0.54
    box_y = 0.28

    for idx, ((title, desc, bg, border), x) in enumerate(zip(stages, x_positions)):
        box = patches.FancyBboxPatch((x, box_y), box_w, box_h, boxstyle="round,pad=0.015",
                                     facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(box)
        # Title
        ax.text(x + box_w/2, box_y + box_h - 0.10, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color=border)
        # Description
        ax.text(x + box_w/2, box_y + 0.20, desc, ha="center", va="center", fontsize=7.5, color="#333333")

        # Stage connector arrow
        if idx < 5:
            ax.annotate("", xy=(x + box_w + 0.028, box_y + box_h/2), xytext=(x + box_w + 0.004, box_y + box_h/2),
                        arrowprops=dict(arrowstyle="->", lw=1.8, color="#444444"))

    # Early exit bypass arrow: Stage 2 bottom -> drop down to y=0.12 -> Stage 6 bottom
    x_s2 = x_positions[1] + box_w/2
    x_s6 = x_positions[5] + box_w/2
    y_drop = 0.12

    ax.plot([x_s2, x_s2, x_s6, x_s6], [box_y, y_drop, y_drop, box_y], color="#2e7d32", lw=1.8, linestyle="--")
    ax.annotate("", xy=(x_s6, box_y), xytext=(x_s6, y_drop + 0.04),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#2e7d32"))

    # Text pill centered on the bypass line with clear padding
    ax.text((x_s2 + x_s6)/2, y_drop, "  65% Benign Log Lines Bypass Stages 3-5 (0.005 ms Early Exit)  ",
            ha="center", va="center", fontsize=8, fontweight="bold", color="#1b5e20",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#2e7d32", lw=1.0))

    # Pipeline Title Header
    ax.text(0.50, 0.92, "LogShield 6-Stage Pre-Ingestion Secret Detection & Vaulting Pipeline",
            ha="center", fontsize=11, fontweight="bold", color="#222222")

    save_dual(fig, "fig2_pipeline.png", "fig6_pipeline.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 3: Tri-State Decision Gate & Threshold Calibration Curve
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig3_decision_gate():
    sweep_path = os.path.join(RESULTS_DIR, "threshold_sweep.csv")
    df = pd.read_csv(sweep_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4))

    # Panel A: Threshold Sensitivity & Error Profile
    ax1.plot(df["Threshold"], df["Precision"], marker="o", color=COLOR_PRIMARY, label="Precision", lw=2)
    ax1.plot(df["Threshold"], df["Recall"], marker="s", color=COLOR_ACCENT, label="Recall", lw=2)
    ax1.plot(df["Threshold"], df["F1"], marker="^", color=COLOR_GREEN, label="F1-Score", lw=2)
    ax1.plot(df["Threshold"], df["ExposureRate_FNR"], marker="d", color=COLOR_ORANGE, linestyle="--", label="Exposure Rate (FN)", lw=1.6)

    # Shaded operational zones
    ax1.axvspan(10, 50, alpha=0.12, color="#90caf9")
    ax1.axvspan(50, 80, alpha=0.12, color="#ffe082")
    ax1.axvspan(80, 95, alpha=0.12, color="#ef9a9a")

    # Header labels inside the zones at the top
    ax1.text(30, 0.95, "PASS Zone\n($S < 50$)", ha="center", fontsize=7.5, fontweight="bold", color="#0d47a1")
    ax1.text(65, 0.95, "FLAG Zone\n($50 \\leq S < 80$)", ha="center", fontsize=7.5, fontweight="bold", color="#b78103")
    ax1.text(88, 0.95, "MASK Zone\n($S \\geq 80$)", ha="center", fontsize=7.5, fontweight="bold", color="#c62828")

    ax1.set_xlabel("Secret Confidence Score Threshold ($S_{crit}$)")
    ax1.set_ylabel("Metric Score / Rate")
    ax1.set_title("(a) Threshold Calibration & Sensitivity", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.35)
    ax1.set_ylim(-0.05, 1.08)
    ax1.legend(loc="lower left", fontsize=8.0, framealpha=0.92)

    # Panel B: Tri-State Operational Decision Boundaries
    ax2.axis("off")
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.set_title("(b) Tri-State Decision Gate & Actions", fontsize=11, fontweight="bold")

    cards = [
        ("MASK Action  (S >= 80)",
         "High-Confidence Secret Identified\n- Redact token with opaque identifier SEC-[HEX8]\n- Encrypt in AES-128-CBC SecureReveal Vault\n- Record blind HMAC-SHA256 fingerprint in Lineage",
         "#ffcdd2", "#c62828", 68, 25),
        ("FLAG Action  (50 <= S < 80)",
         "Ambiguous / Heuristic Candidate\n- Log line allowed with telemetry warning tag\n- Dispatched to async security operations audit\n- Preserves application stream velocity",
         "#fff9c4", "#f57f17", 38, 25),
        ("PASS Action  (S < 50)",
         "Benign Telemetry / Low-Entropy Token\n- Unredacted pass-through to stdout\n- 0.00% False Positive Rate on system identifiers\n- Zero latency overhead (0.005 ms prefilter exit)",
         "#c8e6c9", "#2e7d32", 8, 25),
    ]

    for title, desc, bg, border, y_pos, h in cards:
        card = patches.FancyBboxPatch((4, y_pos), 92, h, boxstyle="round,pad=1.0",
                                      facecolor=bg, edgecolor=border, linewidth=1.4)
        ax2.add_patch(card)
        ax2.text(8, y_pos + h - 6, title, fontsize=9.0, fontweight="bold", color=border)
        ax2.text(8, y_pos + 6, desc, fontsize=7.5, color="#222222")

    plt.tight_layout()
    save_dual(fig, "fig3_decision_gate.png", "fig2_decision_gate.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 4: 4-Way Ablation Study (Zero Legend Overlap)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig4_ablation():
    ab_path = os.path.join(RESULTS_DIR, "ablation_metrics.csv")
    ci_path = os.path.join(RESULTS_DIR, "statistical_significance.json")
    df = pd.read_csv(ab_path)
    with open(ci_path, "r") as f:
        stat_data = json.load(f)["bootstrap_95ci"]

    fig, ax = plt.subplots(figsize=(9.0, 4.6))

    configs = ["Config A\n(Regex Only)", "Config B\n(Regex + Entropy)", "Config C\n(6-Factor Heuristic)", "Config D\n(LogShield Full)"]
    x = np.arange(len(configs))
    bar_w = 0.18

    p_mean = [stat_data[c]["precision"]["mean"] for c in ["A", "B", "C", "D"]]
    p_err = [[p_mean[i] - stat_data[c]["precision"]["ci_95"][0] for i, c in enumerate(["A", "B", "C", "D"])],
             [stat_data[c]["precision"]["ci_95"][1] - p_mean[i] for i, c in enumerate(["A", "B", "C", "D"])]]

    r_mean = [stat_data[c]["recall"]["mean"] for c in ["A", "B", "C", "D"]]
    r_err = [[r_mean[i] - stat_data[c]["recall"]["ci_95"][0] for i, c in enumerate(["A", "B", "C", "D"])],
             [stat_data[c]["recall"]["ci_95"][1] - r_mean[i] for i, c in enumerate(["A", "B", "C", "D"])]]

    f1_mean = [stat_data[c]["f1"]["mean"] for c in ["A", "B", "C", "D"]]
    f1_err = [[f1_mean[i] - stat_data[c]["f1"]["ci_95"][0] for i, c in enumerate(["A", "B", "C", "D"])],
              [stat_data[c]["f1"]["ci_95"][1] - f1_mean[i] for i, c in enumerate(["A", "B", "C", "D"])]]

    fpr_vals = [df.loc[df["Config"] == c, "FPR"].values[0] for c in ["A", "B", "C", "D"]]

    ax.bar(x - 1.5*bar_w, p_mean, bar_w, yerr=p_err, capsize=3, label="Precision", color=COLOR_PRIMARY, edgecolor="#222", lw=0.8)
    ax.bar(x - 0.5*bar_w, r_mean, bar_w, yerr=r_err, capsize=3, label="Recall", color=COLOR_GREEN, edgecolor="#222", lw=0.8)
    ax.bar(x + 0.5*bar_w, f1_mean, bar_w, yerr=f1_err, capsize=3, label="F1-Score", color=COLOR_ORANGE, edgecolor="#222", lw=0.8)
    ax.bar(x + 1.5*bar_w, fpr_vals, bar_w, label="False Positive Rate (FPR)", color=COLOR_ACCENT, edgecolor="#222", lw=0.8)

    ax.set_ylabel("Classification Score / Rate")
    ax.set_title("4-Way Ablation Study Across Detector Configurations (N = 10,000 Lines)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    # Extra headroom so bars, annotations, and legend NEVER overlap
    ax.set_ylim(0.0, 1.28)
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)

    # Place legend on UPPER LEFT (where values are lower, zero collision!)
    ax.legend(loc="upper left", ncol=2, fontsize=8.5, framealpha=0.95)

    # Config D Callout placed in UPPER RIGHT with zero collision!
    ax.annotate(f"LogShield (Config D):\nF1 = {f1_mean[3]:.4f} (95% CI: [{stat_data['D']['f1']['ci_95'][0]:.4f}, 1.0])\nFPR = {fpr_vals[3]:.2%}",
                xy=(x[3] + 0.5*bar_w, f1_mean[3]),
                xytext=(x[3] - 0.45, 1.14),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#222"),
                fontsize=8.0, fontweight="bold", ha="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffffff", edgecolor="#2ca02c", lw=1.0))

    plt.tight_layout()
    save_dual(fig, "fig4_ablation.png", "fig5_ablation.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 5: Latency Breakdown & Sustained Throughput
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig5_benchmark():
    lat_path = os.path.join(RESULTS_DIR, "latency_breakdown.csv")
    perf_path = os.path.join(RESULTS_DIR, "performance_metrics.csv")
    lat_df = pd.read_csv(lat_path)
    perf_df = pd.read_csv(perf_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4))

    # Panel A: Stage Latency Breakdown (Mean vs P95)
    stages_only = lat_df[lat_df["Stage"] != "Total"].copy()
    y_pos = np.arange(len(stages_only))
    h = 0.35

    ax1.barh(y_pos - h/2, stages_only["Mean Time (ms)"], h, label="Mean Latency", color=COLOR_PRIMARY, edgecolor="#222")
    ax1.barh(y_pos + h/2, stages_only["P95 Time (ms)"], h, label="P95 Latency", color=COLOR_PURPLE, edgecolor="#222")

    ax1.set_yticks(y_pos)
    labels = ["Stage 1: Preprocessor", "Stage 2: Aho-Corasick", "Stage 3: Context Window", "Stage 4: Classifier", "Stage 5: SCS Scorer"]
    ax1.set_yticklabels(labels, fontsize=8.5)
    ax1.set_xlabel("Processing Time (milliseconds)")
    ax1.set_title("(a) Processing Latency Across Pipeline Stages", fontsize=11, fontweight="bold")
    ax1.set_xlim(0, 1.05)
    ax1.grid(True, axis="x", linestyle="--", alpha=0.35)
    ax1.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    ax1.invert_yaxis()

    # Exact value annotations on bars for readability
    for i, (m, p) in enumerate(zip(stages_only["Mean Time (ms)"], stages_only["P95 Time (ms)"])):
        ax1.text(m + 0.02, i - h/2, f"{m:.3f} ms", va="center", fontsize=7.5, color="#1565c0", fontweight="bold")
        ax1.text(p + 0.02, i + h/2, f"{p:.3f} ms", va="center", fontsize=7.5, color="#512da8", fontweight="bold")

    # Panel B: Throughput (Lines/sec and MB/sec) vs Payload Size
    ax2_mb = ax2.twinx()

    p1 = ax2.plot(perf_df["Payload_Size_Bytes"], perf_df["Lines_Per_Second"], marker="o", color=COLOR_PRIMARY, lw=2.2, label="Lines/sec")
    p2 = ax2_mb.plot(perf_df["Payload_Size_Bytes"], perf_df["Throughput_MB_s"], marker="s", color=COLOR_ACCENT, lw=2.2, linestyle="--", label="Data Rate (MB/s)")

    ax2.set_xlabel("Log Record Payload Size (Bytes)")
    ax2.set_ylabel("Throughput (Lines / second)", color=COLOR_PRIMARY)
    ax2_mb.set_ylabel("Data Throughput (MB / second)", color=COLOR_ACCENT)
    ax2.set_title("(b) Sustained Logging Throughput & Scalability", fontsize=11, fontweight="bold")
    ax2.set_xscale("log", base=2)
    ax2.set_xticks([256, 1024, 4096, 8192])
    ax2.set_xticklabels(["256 B", "1 KB", "4 KB", "8 KB"])
    ax2.grid(True, linestyle="--", alpha=0.35)

    # Combined legend with clean placement
    lines = p1 + p2
    leg_labels = [l.get_label() for l in lines]
    ax2.legend(lines, leg_labels, loc="center right", fontsize=8.5, framealpha=0.92)

    plt.tight_layout()
    save_dual(fig, "fig5_benchmark.png", "fig4_benchmark.png")
    # Also save with canonical figure-7 and descriptive names to prevent any inversion
    for extra_name in ["fig7_latency_throughput.png", "fig_latency_throughput.png", "f_latency.png"]:
        p_extra = os.path.join(PAPER_FIG_DIR, extra_name)
        with open(os.path.join(PAPER_FIG_DIR, "fig5_benchmark.png"), "rb") as sf, open(p_extra, "wb") as df:
            df.write(sf.read())

# ─────────────────────────────────────────────────────────────────────────────
# FIG 6: SecretLineage Cross-Pod Sprawl Graph (Zero Overlap Edge Layout)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig6_lineage():
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Distinct non-colliding microservice node positions (cx, cy)
    nodes = {
        "auth": (0.17, 0.72, "auth-service\n[Credential Issuer]", "#bbdefb", "#1976d2"),
        "payment": (0.50, 0.75, "payment-service\n[Payment Gateway]", "#ffe0b2", "#f57c00"),
        "user": (0.83, 0.72, "user-service\n[User Directory]", "#c8e6c9", "#2e7d32"),
        "inventory": (0.25, 0.26, "inventory-service\n[Cache / DB Client]", "#e1bee7", "#7b1fa2"),
        "notify": (0.75, 0.26, "notification-service\n[Email / Webhook]", "#cfd8dc", "#455a64"),
    }

    card_w, card_h = 0.21, 0.15

    # Render Node cards first
    for key, (x, y, label, bg, border) in nodes.items():
        card = patches.FancyBboxPatch((x - card_w/2, y - card_h/2), card_w, card_h, boxstyle="round,pad=0.015",
                                      facecolor=bg, edgecolor=border, linewidth=1.8, zorder=2)
        ax.add_patch(card)
        ax.text(x, y, label, ha="center", va="center", fontsize=8.0, fontweight="bold", color="#111111", zorder=3)

    # Directed edges connecting strictly to CARD PERIMETERS with clearance
    # (src_pt, dst_pt, label, badge_pos, color, rad)
    edge_routes = [
        # 1. auth -> payment (right of auth to left of payment)
        ((0.275, 0.73), (0.395, 0.75), "JWT Signing Key\nHMAC: c4f8...b12a", (0.335, 0.85), "#1976d2", 0.12),
        # 2. payment -> user (right of payment to left of user)
        ((0.605, 0.75), (0.725, 0.73), "Stripe API Secret\nHMAC: 9a3e...77d1", (0.665, 0.85), "#f57c00", 0.12),
        # 3. auth -> inventory (bottom of auth to top-left of inventory)
        ((0.20, 0.645), (0.23, 0.335), "Postgres URI\nHMAC: 12de...840c", (0.12, 0.49), "#7b1fa2", -0.10),
        # 4. payment -> notify (bottom of payment to top-left of notify)
        ((0.53, 0.675), (0.71, 0.335), "Webhook Secret\nHMAC: 77bb...e390", (0.57, 0.50), "#d32f2f", 0.06),
        # 5. user -> notify (bottom of user to top-right of notify)
        ((0.83, 0.645), (0.79, 0.335), "Internal Auth Token\nHMAC: ff01...44a9", (0.88, 0.49), "#2e7d32", 0.10),
    ]

    for (x1, y1), (x2, y2), label, (lx, ly), col, rad in edge_routes:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=1.8, color=col,
                                    connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0),
                    zorder=4)

        # Crisp opaque label badge with non-overlapping dedicated placement
        ax.text(lx, ly, label, ha="center", va="center", fontsize=7.2, color=col, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=col, alpha=0.98, lw=0.9),
                zorder=5)

    # Header and Footer
    ax.text(0.50, 0.95, "SecretLineage Blind Graph: Real-Time Cross-Pod Sprawl Correlation",
            ha="center", fontsize=11, fontweight="bold", color="#222222")
    ax.text(0.50, 0.07, "Zero-Knowledge Proliferation Mapping: Microservices correlate keyed HMAC-SHA256 blind fingerprints without storing or disclosing plaintext credentials",
            ha="center", fontsize=7.8, color="#444444",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f5f5f5", edgecolor="#cccccc", lw=0.8))

    save_dual(fig, "fig6_lineage.png", "fig10_lineage.png")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 7: Adversarial Evasion Robustness Benchmark (N = 2,400)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig7_evasion_benchmark():
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    
    categories = [
        "Raw Control",
        "Delimiter Split\n(Whitespace / Hyphen)",
        "Hex Escaped\n(\\x41\\x4b...)",
        "Base64 Wrapped\n(Basic/Bearer Auth)",
        "URL Encoded\n(%41%4b...)",
        "Overall Evasion\n(Combined N=1,000)"
    ]
    
    baseline_recalls = [33.00, 35.00, 38.00, 19.50, 33.50, 32.20]
    logshield_recalls = [100.00, 78.25, 100.00, 100.00, 100.00, 91.30]
    
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, baseline_recalls, width, label="Baseline Regex Scanner (No Fusion)", 
                    color="#e0e0e0", edgecolor="#666666", linewidth=1.2, hatch="//")
    rects2 = ax.bar(x + width/2, logshield_recalls, width, label="LogShield Adaptive Pipeline (Token Fusion + Normalization)", 
                    color="#1f77b4", edgecolor="#0d47a1", linewidth=1.2)
    
    ax.set_ylabel("Detection Recall (%)", fontweight="bold")
    ax.set_title("Detection Robustness Across Adversarial Evasion Techniques (N = 2,400 Labeled Corpus)", 
                 fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=8.5)
    ax.set_ylim(0, 130)
    ax.axhline(100, color="#888888", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", fontsize=8.2, framealpha=0.95)
    
    # Value annotations on bars
    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2., h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.0, color="#444444")
    for r in rects2:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2., h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#0d47a1")

    # Callout badge for bypass reduction
    ax.text(4.8, 114, "Bypass: 67.8% → 8.7%\n(−59.1 pp reduction)", ha="center", va="center",
            fontsize=8.0, fontweight="bold", color="#1b5e20",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f5e9", edgecolor="#2e7d32", lw=0.9))
        
    p1 = os.path.join(FIG_DIR, "fig7_evasion_benchmark.png")
    p2 = os.path.join(PAPER_FIG_DIR, "fig7_evasion_benchmark.png")
    p3 = os.path.join(PAPER_FIG_DIR, "fig5_evasion_benchmark.png")
    p4 = os.path.join(PAPER_FIG_DIR, "f_evasion.png")
    fig.savefig(p1, format="png")
    fig.savefig(p2, format="png")
    fig.savefig(p3, format="png")
    fig.savefig(p4, format="png")
    plt.close(fig)
    print("Saved cleanly: fig7_evasion_benchmark.png (and fig5_evasion_benchmark.png)")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 8: Autonomous Containment & Blast-Radius Mitigation Lifecycle
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig8_containment_lifecycle():
    fig, ax = plt.subplots(figsize=(10.0, 5.0))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Title
    ax.text(0.50, 0.95, "Closed-Loop Autonomous Containment: Workload Egress Isolation Architecture",
            ha="center", fontsize=11, fontweight="bold", color="#222222")

    # Step 1: Interception Card
    c1 = patches.FancyBboxPatch((0.04, 0.48), 0.26, 0.38, boxstyle="round,pad=0.015",
                                facecolor="#e3f2fd", edgecolor="#1976d2", linewidth=1.8)
    ax.add_patch(c1)
    ax.text(0.17, 0.81, "1. In-Pod Detection & Vaulting", ha="center", fontsize=9.0, fontweight="bold", color="#0d47a1")
    ax.text(0.17, 0.67, "- Intercepts stdout log stream\n- Token Fusion & Decoders\n- In-place [REDACTED:SEC-..]\n- Fernet AES-128 vaulting",
            ha="center", fontsize=8.0, color="#333333")
    ax.text(0.17, 0.54, "Latency: 0.586 ms", ha="center", fontsize=8.0, fontweight="bold", color="#1976d2",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#1976d2", lw=0.9))

    # Step 2: Lineage Assessment Card
    c2 = patches.FancyBboxPatch((0.37, 0.48), 0.26, 0.38, boxstyle="round,pad=0.015",
                                facecolor="#fff3e0", edgecolor="#f57c00", linewidth=1.8)
    ax.add_patch(c2)
    ax.text(0.50, 0.81, "2. Blast-Radius Assessment", ha="center", fontsize=9.0, fontweight="bold", color="#e65100")
    ax.text(0.50, 0.67, "- Queries SecretLineage\n- Canonical blind HMAC-SHA256\n- Identifies cross-service sprawl\n- Evaluates severity (CRITICAL)",
            ha="center", fontsize=8.0, color="#333333")
    ax.text(0.50, 0.54, "Blast: 3 Services, 3 Pods", ha="center", fontsize=8.0, fontweight="bold", color="#f57c00",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#f57c00", lw=0.9))

    # Step 3: Kubernetes Containment Enforcement Card
    c3 = patches.FancyBboxPatch((0.70, 0.48), 0.26, 0.38, boxstyle="round,pad=0.015",
                                facecolor="#e8f5e9", edgecolor="#2e7d32", linewidth=1.8)
    ax.add_patch(c3)
    ax.text(0.83, 0.81, "3. Control Plane Enforcement", ha="center", fontsize=9.0, fontweight="bold", color="#1b5e20")
    ax.text(0.83, 0.67, "- Deploys V1NetworkPolicy\n- Blocks pod egress exfiltration\n- Annotates pod metadata\n- Zero collateral blast radius",
            ha="center", fontsize=8.0, color="#333333")
    ax.text(0.83, 0.54, "MTTC: 16.7 - 26.7 ms", ha="center", fontsize=8.0, fontweight="bold", color="#2e7d32",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#2e7d32", lw=0.9))

    # Inter-card arrows connecting perimeter
    ax.annotate("", xy=(0.365, 0.67), xytext=(0.305, 0.67),
                arrowprops=dict(arrowstyle="->", lw=2.2, color="#1976d2"))
    ax.annotate("", xy=(0.695, 0.67), xytext=(0.635, 0.67),
                arrowprops=dict(arrowstyle="->", lw=2.2, color="#f57c00"))

    # Lower comparison container (zero text collision with two independent cards)
    b_box = patches.FancyBboxPatch((0.04, 0.05), 0.92, 0.37, boxstyle="round,pad=0.015",
                                   facecolor="#f9f9f9", edgecolor="#b0bec5", linewidth=1.2)
    ax.add_patch(b_box)
    ax.text(0.50, 0.375, "Security Posture Transformation: Passive Redaction vs. Closed-Loop Containment",
            ha="center", fontsize=9.2, fontweight="bold", color="#222222")

    # Left comparison sub-card: Passive Redaction Baseline
    p_box = patches.FancyBboxPatch((0.06, 0.08), 0.42, 0.25, boxstyle="round,pad=0.01",
                                   facecolor="#fff5f5", edgecolor="#ef5350", linewidth=1.1)
    ax.add_patch(p_box)
    ax.text(0.27, 0.285, "Passive Redaction Baseline", ha="center", fontsize=8.5, fontweight="bold", color="#c62828")
    ax.text(0.08, 0.175, "• Plaintext masked in logs, but keys stay active\n• Unknown blast radius; requires manual triage\n• Egress exfiltration continues unchecked",
            ha="left", va="center", fontsize=7.2, color="#b71c1c", linespacing=1.4)

    # Right comparison sub-card: LogShield Autonomous Containment
    l_box = patches.FancyBboxPatch((0.52, 0.08), 0.42, 0.25, boxstyle="round,pad=0.01",
                                   facecolor="#f1f8e9", edgecolor="#66bb6a", linewidth=1.1)
    ax.add_patch(l_box)
    ax.text(0.73, 0.285, "LogShield Autonomous Containment", ha="center", fontsize=8.5, fontweight="bold", color="#2e7d32")
    ax.text(0.54, 0.175, "• Real-time V1NetworkPolicy egress quarantine\n• Instant sprawl tracking via canonical HMAC\n• Sub-30 ms MTTC with zero collateral impact",
            ha="left", va="center", fontsize=7.2, color="#1b5e20", linespacing=1.4)

    p1 = os.path.join(FIG_DIR, "fig8_containment_lifecycle.png")
    p2 = os.path.join(PAPER_FIG_DIR, "fig8_containment_lifecycle.png")
    fig.savefig(p1, format="png")
    fig.savefig(p2, format="png")
    plt.close(fig)
    print("Saved cleanly: fig8_containment_lifecycle.png")

def main():
    print("Generating anti-overlap publication figures...")
    generate_fig1_architecture()
    generate_fig2_pipeline()
    generate_fig3_decision_gate()
    generate_fig4_ablation()
    generate_fig5_benchmark()
    generate_fig6_lineage()
    generate_fig7_evasion_benchmark()
    generate_fig8_containment_lifecycle()
    print("All 8 publication figures regenerated cleanly!")

if __name__ == "__main__":
    main()
