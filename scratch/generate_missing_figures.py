import matplotlib.pyplot as plt
import numpy as np

# Set font family
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# 1. Generate fig_latency_throughput.png (Figure 5.4)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

# Left: Stage latency breakdown
stages = [
    'Stage 1:\nToken Fusion',
    'Stage 2:\nAho-Corasick',
    'Stage 3:\nContext Engine',
    'Stage 4:\n3-Pass Classifier',
    'Stage 5:\nML Scorer',
    'Stage 6:\nDecision Gate'
]
latencies = [0.082, 0.068, 0.142, 0.168, 0.014, 0.092]
colors = ['#2b5c8f', '#3670a3', '#4184b8', '#4c99cc', '#6baed6', '#9ecae1']

bars1 = ax1.bar(stages, latencies, color=colors, edgecolor='#1a365d', linewidth=1.2, width=0.6)
ax1.axhline(y=0.504, color='#d9534f', linestyle='--', linewidth=1.8, label='Mean End-to-End Latency: 0.504 ms')
ax1.axhline(y=1.0, color='#e67e22', linestyle=':', linewidth=1.5, label='NFR1 Target Ceiling: 1.0 ms')

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.006, f'{yval:.3f} ms', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.set_ylabel('Mean Latency per Line (milliseconds)', fontsize=11, fontweight='bold', color='#111111')
ax1.set_title('(a) Processing Latency Breakdown Across Pipeline Stages', fontsize=12, fontweight='bold', pad=12, color='#111111')
ax1.set_ylim(0, 1.15)
ax1.legend(loc='upper right', framealpha=0.95, fontsize=9.5)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Right: Throughput across regimes
regimes = [
    'Diagnostic Dump\n(1,024 B, multi-token)',
    'Real Ingestion\n(238 B, 25% vaulting)',
    'Candidate Token\n(180 B, 1 candidate)',
    'Microservice Stream\n(120 B, 65% early exit)',
    'Pure Benign Bypass\n(140 B, 0 keywords)'
]
throughputs = [75, 287, 1705, 4786, 178571]

y_pos = np.arange(len(regimes))
bars2 = ax2.barh(y_pos, throughputs, color='#1f77b4', edgecolor='#0d47a1', linewidth=1.2, height=0.55)

for i, v in enumerate(throughputs):
    ax2.text(v * 1.25, i, f'{v:,} lines/s', va='center', fontsize=9.5, fontweight='bold', color='#111111')

ax2.set_xscale('log')
ax2.set_xlim(10, 800000)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(regimes, fontsize=9.5)
ax2.set_xlabel('Single-Core Ingestion Throughput (lines/sec, log scale)', fontsize=11, fontweight='bold', color='#111111')
ax2.set_title('(b) Throughput Scaling Across Operational Regimes', fontsize=12, fontweight='bold', pad=12, color='#111111')
ax2.axvline(x=4500, color='#27ae60', linestyle='--', linewidth=1.5, label='NFR2 Target Floor: 4,500 lines/s')
ax2.legend(loc='lower right', framealpha=0.95, fontsize=9.5)
ax2.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('paper/figures/fig_latency_throughput.png', dpi=300, bbox_inches='tight')
plt.close()
print('Generated paper/figures/fig_latency_throughput.png successfully.')

# 2. Generate fig_contributions_summary.png (Figure 7.1)
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
ax.axis('off')

# Title
ax.text(0.5, 0.95, 'LogShield: Summary of Five Major Technical Contributions', 
        ha='center', va='top', fontsize=16, fontweight='bold', color='#111827')
ax.text(0.5, 0.90, 'Industry-Grade Kubernetes-Native Runtime Secret Sanitization and Autonomous Containment', 
        ha='center', va='top', fontsize=11, fontstyle='italic', color='#4b5563')

cards = [
    {
        'num': '01',
        'title': 'In-Pod Zero-Copy\nInterception',
        'sub': 'Local Memory Interception',
        'desc': '• Memory-backed emptyDir IPC volume\n• Zero network transit for plaintext secrets\n• Complies with GDPR, HIPAA, PCI-DSS 4.0\n• Sub-millisecond latency (0.504 ms avg)\n• Zero application source or YAML changes',
        'color': '#1e3a8a',
        'accent': '#3b82f6',
        'bg': '#eff6ff'
    },
    {
        'num': '02',
        'title': 'Adaptive Evasion\nDefense',
        'sub': 'Sliding Token Fusion',
        'desc': '• Sliding-window delimiter fusion\n• Hex-escape & percent-encoding unescaping\n• Nested Base64 unnesting loop (depth <= 3)\n• Evasion recall jumps 32.2% -> 91.3%\n• Slashes bypass rates from 67.8% -> 8.7%',
        'color': '#065f46',
        'accent': '#10b981',
        'bg': '#ecfdf5'
    },
    {
        'num': '03',
        'title': 'Calibrated 6-Factor\nML Scorer',
        'sub': 'Supervised Confidence Engine',
        'desc': '• L2 logistic regression trained on 60k lines\n• Integer weights (w_sum = 100) for zero FP\n• AUROC of 0.9580, AUPRC of 0.9383\n• High-entropy UUID/ETag/digest suppression\n• Tri-state gate: PASS, FLAG, REDACT',
        'color': '#7c2d12',
        'accent': '#f97316',
        'bg': '#fff7ed'
    },
    {
        'num': '04',
        'title': 'SecureReveal Vault &\nForward Audit',
        'sub': 'Authenticated Cryptography',
        'desc': '• Fernet AES-128-CBC + HMAC-SHA256\n• Forward-secure SHA-256 hash chaining\n• Opaque reference ID: SEC-YYYYMMDD-XXXX\n• Blind canonical HMAC sprawl lineage\n• Scoped exemption engine for pre-approved keys',
        'color': '#4c1d95',
        'accent': '#8b5cf6',
        'bg': '#f5f3ff'
    },
    {
        'num': '05',
        'title': 'Autonomous Closed-Loop\nContainment',
        'sub': 'Active Control-Plane Mitigation',
        'desc': '• Multi-pod blast radius calculation B(s)\n• Dynamic V1NetworkPolicy in 16.7-26.7 ms\n• Whitelists UDP/TCP port 53 (CoreDNS)\n• Prevents container crash-loop probe failure\n• Zero collateral impact on innocent pods',
        'color': '#831843',
        'accent': '#ec4899',
        'bg': '#fdf2f8'
    }
]

box_w = 0.178
box_h = 0.72
gap = 0.018
start_x = 0.025

for i, card in enumerate(cards):
    x = start_x + i * (box_w + gap)
    y = 0.10
    
    # Outer box
    rect = plt.Rectangle((x, y), box_w, box_h, facecolor=card['bg'], edgecolor=card['accent'], 
                         linewidth=1.8, linestyle='-', transform=ax.transAxes, zorder=2)
    ax.add_patch(rect)
    
    # Header banner
    banner = plt.Rectangle((x, y + box_h - 0.18), box_w, 0.18, facecolor=card['color'], 
                           edgecolor='none', transform=ax.transAxes, zorder=3)
    ax.add_patch(banner)
    
    # Number badge
    ax.text(x + 0.015, y + box_h - 0.035, card['num'], transform=ax.transAxes,
            fontsize=18, fontweight='heavy', color='#ffffff', zorder=4)
    
    # Header title
    ax.text(x + box_w/2, y + box_h - 0.10, card['title'], transform=ax.transAxes,
            fontsize=10.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=4)
    
    # Subtitle
    ax.text(x + box_w/2, y + box_h - 0.22, card['sub'], transform=ax.transAxes,
            fontsize=9.5, fontweight='bold', color=card['color'], ha='center', va='top', zorder=4)
    
    # Description bullet points
    ax.text(x + 0.012, y + box_h - 0.27, card['desc'], transform=ax.transAxes,
            fontsize=8.5, color='#1f2937', va='top', ha='left', zorder=4, linespacing=1.65)

# Bottom note
ax.text(0.5, 0.04, 'All five contributions implemented, verified across 42 automated tests, and benchmarked on an isolated 5-microservice Kubernetes testbed.',
        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#374151')

plt.savefig('paper/figures/fig_contributions_summary.png', dpi=300, bbox_inches='tight')
plt.close()
print('Generated paper/figures/fig_contributions_summary.png successfully.')
