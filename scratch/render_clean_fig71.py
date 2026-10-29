import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap

print("Rendering perfected Figure 7.1...")

# Canvas dimensions: 16 inches x 9 inches at 300 DPI
fig, ax = plt.subplots(figsize=(16, 9.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')
ax.axis('off')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Main Title & Subtitle
ax.text(0.5, 0.965, 'LogShield: Summary of Five Major Technical Contributions', 
        ha='center', va='top', fontsize=18, fontweight='bold', color='#0f172a', family='DejaVu Sans')
ax.text(0.5, 0.925, 'Industry-Grade Kubernetes-Native Runtime Secret Sanitization and Autonomous Closed-Loop Containment', 
        ha='center', va='top', fontsize=11.5, fontstyle='italic', color='#475569', family='DejaVu Sans')

cards = [
    {
        'num': '01',
        'title': 'In-Pod Zero-Copy\nInterception',
        'sub': 'Local Memory Interception',
        'bullets': [
            'Memory-backed emptyDir IPC volume',
            'Zero plaintext network transit for secrets',
            'Complies with GDPR, HIPAA, PCI-DSS',
            'Sub-millisecond latency (0.504 ms avg)',
            'Zero application source or YAML changes'
        ],
        'primary': '#1d4ed8',   # Blue
        'accent': '#3b82f6',
        'bg': '#ffffff',
        'header_bg': '#1e40af'
    },
    {
        'num': '02',
        'title': 'Adaptive Evasion\nDefense',
        'sub': 'Sliding Token Fusion',
        'bullets': [
            'Sliding-window delimiter fusion',
            'Hex-escape & percent-encoding unescape',
            'Nested Base64 unnesting loop (depth ≤ 3)',
            'Evasion recall jumps 32.2% → 91.3%',
            'Slashes bypass rates from 67.8% → 8.7%'
        ],
        'primary': '#047857',   # Green
        'accent': '#10b981',
        'bg': '#ffffff',
        'header_bg': '#065f46'
    },
    {
        'num': '03',
        'title': 'Calibrated 6-Factor\nML Scorer',
        'sub': 'Supervised Confidence Engine',
        'bullets': [
            'L2 logistic regression on 60k samples',
            'Integer weights (w_sum = 100) for zero FP',
            'AUROC of 0.9580, AUPRC of 0.9383',
            'High-entropy UUID/ETag suppression',
            'Tri-state gate: PASS, FLAG, REDACT'
        ],
        'primary': '#b45309',   # Amber/Brown
        'accent': '#f59e0b',
        'bg': '#ffffff',
        'header_bg': '#92400e'
    },
    {
        'num': '04',
        'title': 'SecureReveal Vault &\nForward Audit',
        'sub': 'Authenticated Cryptography',
        'bullets': [
            'Fernet AES-128-CBC + HMAC-SHA256',
            'Forward-secure SHA-256 hash chaining',
            'Opaque reference ID: SEC-YYYY-XXXX',
            'Blind canonical HMAC sprawl lineage',
            'Scoped exemption engine for approved keys'
        ],
        'primary': '#6d28d9',   # Purple
        'accent': '#8b5cf6',
        'bg': '#ffffff',
        'header_bg': '#5b21b6'
    },
    {
        'num': '05',
        'title': 'Autonomous Closed-Loop\nContainment',
        'sub': 'Active Control-Plane Mitigation',
        'bullets': [
            'Multi-pod blast radius calculation B(s)',
            'Dynamic V1NetworkPolicy in 16.7–26.7 ms',
            'Whitelists UDP/TCP port 53 (CoreDNS)',
            'Prevents container probe crash loops',
            'Zero collateral impact on innocent pods'
        ],
        'primary': '#be123c',   # Rose/Crimson
        'accent': '#f43f5e',
        'bg': '#ffffff',
        'header_bg': '#9f1239'
    }
]

num_cards = len(cards)
margin_x = 0.032
margin_bottom = 0.09
card_gap = 0.016
card_w = (1.0 - (2 * margin_x) - ((num_cards - 1) * card_gap)) / num_cards  # ~0.174
card_h = 0.74
card_y = margin_bottom + 0.03  # 0.12

for i, card in enumerate(cards):
    cx = margin_x + i * (card_w + card_gap)
    cy = card_y
    
    # Subtle drop shadow behind card
    shadow = patches.FancyBboxPatch(
        (cx + 0.002, cy - 0.003), card_w, card_h,
        boxstyle="round,pad=0.002,rounding_size=0.015",
        facecolor='#e2e8f0',
        edgecolor='none',
        zorder=1
    )
    ax.add_patch(shadow)

    # Outer card with crisp rounded corners
    outer_box = patches.FancyBboxPatch(
        (cx, cy), card_w, card_h,
        boxstyle="round,pad=0.002,rounding_size=0.015",
        facecolor=card['bg'],
        edgecolor='#cbd5e1',
        linewidth=1.4,
        zorder=2
    )
    ax.add_patch(outer_box)
    
    # Top header banner
    header_h = 0.165
    header_y = cy + card_h - header_h
    header_box = patches.FancyBboxPatch(
        (cx, header_y), card_w, header_h,
        boxstyle="round,pad=0.002,rounding_size=0.015",
        facecolor=card['header_bg'],
        edgecolor='none',
        zorder=3
    )
    ax.add_patch(header_box)
    
    # Seamless bottom of header
    fill_rect = patches.Rectangle(
        (cx, header_y), card_w, 0.02,
        facecolor=card['header_bg'],
        edgecolor='none',
        zorder=3
    )
    ax.add_patch(fill_rect)

    # Number badge
    ax.text(
        cx + card_w * 0.14, header_y + header_h * 0.58,
        card['num'],
        fontsize=22, fontweight='bold', color='#ffffff',
        ha='center', va='center', zorder=4, family='DejaVu Sans'
    )
    
    # Header title
    ax.text(
        cx + card_w * 0.58, header_y + header_h * 0.50,
        card['title'],
        fontsize=10.5, fontweight='bold', color='#ffffff',
        ha='center', va='center', zorder=4, linespacing=1.2, family='DejaVu Sans'
    )
    
    # Subtitle Pill / Tag below header
    sub_y = header_y - 0.040
    sub_box = patches.FancyBboxPatch(
        (cx + 0.008, sub_y), card_w - 0.016, 0.028,
        boxstyle="round,pad=0.002,rounding_size=0.008",
        facecolor='#f8fafc',
        edgecolor=card['accent'],
        linewidth=1.2,
        zorder=3
    )
    ax.add_patch(sub_box)
    
    ax.text(
        cx + card_w / 2, sub_y + 0.014,
        card['sub'],
        fontsize=8.5, fontweight='bold', color=card['primary'],
        ha='center', va='center', zorder=4, family='DejaVu Sans'
    )
    
    # Bullets area with generous, clean vertical distribution
    wrap_width = 25  # Guarantees ZERO overflow
    bullet_start_y = sub_y - 0.038
    curr_y = bullet_start_y
    
    for bullet_idx, b_text in enumerate(card['bullets']):
        wrapped_lines = textwrap.wrap(b_text, width=wrap_width)
        
        # Bullet indicator dot
        dot_x = cx + 0.012
        dot_y = curr_y - 0.005
        ax.plot(dot_x, dot_y, marker='o', markersize=4.0, color=card['primary'], zorder=4)
        
        # Wrapped text lines
        for l_idx, line in enumerate(wrapped_lines):
            line_x = cx + 0.023
            ax.text(
                line_x, curr_y - (l_idx * 0.024),
                line,
                fontsize=8.5, color='#1e293b',
                va='top', ha='left', zorder=4, family='DejaVu Sans',
                fontweight='normal'
            )
        
        # Spacing to next bullet
        curr_y -= (len(wrapped_lines) * 0.024 + 0.026)

# Footer banner across bottom
footer_y = 0.038
footer_box = patches.FancyBboxPatch(
    (margin_x, footer_y), 1.0 - 2 * margin_x, 0.046,
    boxstyle="round,pad=0.003,rounding_size=0.010",
    facecolor='#f1f5f9',
    edgecolor='#cbd5e1',
    linewidth=1.2,
    zorder=2
)
ax.add_patch(footer_box)

ax.text(
    0.5, footer_y + 0.023,
    'All five contributions implemented, verified across 42 automated tests, and benchmarked on an isolated 5-microservice Kubernetes testbed.',
    ha='center', va='center', fontsize=10, fontweight='bold', color='#1e293b', family='DejaVu Sans', zorder=3
)

# Output destinations
paths = [
    r'paper/figures/fig_contributions_summary.png',
    r'fig_contributions_summary.png',
    r'C:\Users\Asus\.gemini\antigravity\brain\236c4749-0fde-4dca-8814-d7425598de3f\fig_contributions_summary.png'
]

os.makedirs('paper/figures', exist_ok=True)

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(paths[0], dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.15)
plt.savefig(paths[1], dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.15)
plt.savefig(paths[2], dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', pad_inches=0.15)
plt.close()

print("Generation complete!")
for p in paths:
    print(f"  Saved: {p} ({os.path.getsize(p)} bytes)")
