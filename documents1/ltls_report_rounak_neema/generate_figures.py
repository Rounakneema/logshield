import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import shutil

out_dir = 'ltls_report_rounak_neema/figures'
os.makedirs(out_dir, exist_ok=True)

# Copy the NMIMS logo if present
if os.path.exists('ltls_assets/extracted_image1.png'):
    shutil.copy('ltls_assets/extracted_image1.png', os.path.join(out_dir, 'nmims_logo.png'))

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# ==================== FIGURE 1: SWOT Conceptual Framework ====================
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis('off')

ax.text(3, 6.5, 'HELPFUL\n(To Achieving Objectives)', ha='center', va='center', fontsize=12, fontweight='bold', color='#1e3a8a')
ax.text(7.5, 6.5, 'HARMFUL\n(To Achieving Objectives)', ha='center', va='center', fontsize=12, fontweight='bold', color='#991b1b')

ax.text(0.3, 4.5, 'INTERNAL\nORIGIN\n(Attributes of\nIndividual)', ha='center', va='center', fontsize=11, fontweight='bold', color='#334155', rotation=90)
ax.text(0.3, 1.8, 'EXTERNAL\nORIGIN\n(Attributes of\nEnvironment)', ha='center', va='center', fontsize=11, fontweight='bold', color='#334155', rotation=90)

rect_s = patches.FancyBboxPatch((1, 3.2), 4, 2.6, boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#3b82f6', linewidth=2)
ax.add_patch(rect_s)
ax.text(3, 5.3, 'STRENGTHS (S)', ha='center', va='center', fontsize=14, fontweight='bold', color='#1d4ed8')
ax.text(3, 4.2, '• Internal positive capabilities\n• Unique competitive advantages\n• Intrinsic talents & skills\n• Core competencies & mastery', ha='center', va='center', fontsize=10, color='#1e293b')

rect_w = patches.FancyBboxPatch((5.5, 3.2), 4, 2.6, boxstyle='round,pad=0.2', facecolor='#fef2f2', edgecolor='#ef4444', linewidth=2)
ax.add_patch(rect_w)
ax.text(7.5, 5.3, 'WEAKNESSES (W)', ha='center', va='center', fontsize=14, fontweight='bold', color='#b91c1c')
ax.text(7.5, 4.2, '• Internal vulnerabilities & gaps\n• Sub-optimal behavioral patterns\n• Skill deficits & resource limits\n• Inhibitors to performance', ha='center', va='center', fontsize=10, color='#1e293b')

rect_o = patches.FancyBboxPatch((1, 0.4), 4, 2.6, boxstyle='round,pad=0.2', facecolor='#f0fdf4', edgecolor='#22c55e', linewidth=2)
ax.add_patch(rect_o)
ax.text(3, 2.5, 'OPPORTUNITIES (O)', ha='center', va='center', fontsize=14, fontweight='bold', color='#15803d')
ax.text(3, 1.4, '• Favorable external trends\n• Emerging industry demands\n• Unmet market niches\n• Platforms for career expansion', ha='center', va='center', fontsize=10, color='#1e293b')

rect_t = patches.FancyBboxPatch((5.5, 0.4), 4, 2.6, boxstyle='round,pad=0.2', facecolor='#fffbeb', edgecolor='#f59e0b', linewidth=2)
ax.add_patch(rect_t)
ax.text(7.5, 2.5, 'THREATS (T)', ha='center', va='center', fontsize=14, fontweight='bold', color='#b45309')
ax.text(7.5, 1.4, '• External obstacles & hazards\n• Rapidly shifting landscape\n• Competitive pressures\n• Burnout & systemic stressors', ha='center', va='center', fontsize=10, color='#1e293b')

plt.tight_layout()
plt.savefig(f'{out_dir}/fig1_swot_framework.png', dpi=300)
plt.close()

# ==================== FIGURE 2: Johari Window Conceptual Model ====================
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

ax.text(3.2, 7.4, 'KNOWN TO SELF', ha='center', va='center', fontsize=13, fontweight='bold', color='#0f172a')
ax.text(7.6, 7.4, 'NOT KNOWN TO SELF', ha='center', va='center', fontsize=13, fontweight='bold', color='#0f172a')

ax.text(0.4, 5.2, 'KNOWN\nTO OTHERS', ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a', rotation=90)
ax.text(0.4, 2.0, 'NOT KNOWN\nTO OTHERS', ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a', rotation=90)

p1 = patches.FancyBboxPatch((1.2, 3.8), 4.0, 3.0, boxstyle='round,pad=0.15', facecolor='#dbeafe', edgecolor='#2563eb', linewidth=2.5)
ax.add_patch(p1)
ax.text(3.2, 6.2, 'QUADRANT I:\nOPEN ARENA', ha='center', va='center', fontsize=13, fontweight='bold', color='#1e40af')
ax.text(3.2, 4.8, 'Public Self\n• Behavior, attitudes, knowledge\n• Freely shared with the world\n• Basis for transparent teamwork\n• High mutual trust area', ha='center', va='center', fontsize=10, color='#1e293b')

p2 = patches.FancyBboxPatch((5.6, 3.8), 4.0, 3.0, boxstyle='round,pad=0.15', facecolor='#fef3c7', edgecolor='#d97706', linewidth=2.5)
ax.add_patch(p2)
ax.text(7.6, 6.2, 'QUADRANT II:\nBLIND SPOT', ha='center', va='center', fontsize=13, fontweight='bold', color='#b45309')
ax.text(7.6, 4.8, 'Unconscious Self\n• Behaviors seen by others\n• Unrecognized by oneself\n• Discovered via active feedback\n• Critical area for personal growth', ha='center', va='center', fontsize=10, color='#1e293b')

p3 = patches.FancyBboxPatch((1.2, 0.4), 4.0, 3.0, boxstyle='round,pad=0.15', facecolor='#f3e8ff', edgecolor='#9333ea', linewidth=2.5)
ax.add_patch(p3)
ax.text(3.2, 2.8, 'QUADRANT III:\nHIDDEN FACADE', ha='center', va='center', fontsize=13, fontweight='bold', color='#6b21a8')
ax.text(3.2, 1.4, 'Private Self\n• Secrets, fears, private thoughts\n• Kept concealed from others\n• Can drain cognitive energy\n• Minimized via vulnerability/trust', ha='center', va='center', fontsize=10, color='#1e293b')

p4 = patches.FancyBboxPatch((5.6, 0.4), 4.0, 3.0, boxstyle='round,pad=0.15', facecolor='#f1f5f9', edgecolor='#64748b', linewidth=2.5)
ax.add_patch(p4)
ax.text(7.6, 2.8, 'QUADRANT IV:\nUNKNOWN AREA', ha='center', va='center', fontsize=13, fontweight='bold', color='#334155')
ax.text(7.6, 1.4, 'Undiscovered Self\n• Latent talents & subconscious drives\n• Unexplored under normal states\n• Revealed under novel stress/crises\n• Great frontier of potential', ha='center', va='center', fontsize=10, color='#1e293b')

plt.tight_layout()
plt.savefig(f'{out_dir}/fig2_johari_model.png', dpi=300)
plt.close()

# ==================== FIGURE 3: Detailed SWOT Matrix for Rounak Neema ====================
fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis('off')

ax.text(5.5, 7.6, 'SWOT ANALYSIS MATRIX — ROUNAK NEEMA (ROLL NO: E244)', ha='center', va='center', fontsize=14, fontweight='bold', color='#0f172a')

# S Box
s_box = patches.FancyBboxPatch((0.8, 4.0), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#2563eb', linewidth=2)
ax.add_patch(s_box)
ax.text(3.05, 6.7, 'STRENGTHS (INTERNAL / HELPFUL)', ha='center', va='center', fontsize=12, fontweight='bold', color='#1d4ed8')
s_text = (
    '• Unusually High Curiosity:\n'
    '  - Relentless drive to understand core systems.\n'
    '  - Proactive exploration beyond syllabus limits.\n'
    '  - High intrinsic motivation for learning.\n\n'
    '• Good Technical Skills:\n'
    '  - Solid foundation in programming & systems.\n'
    '  - Rapid prototyping & algorithmic fluency.\n'
    '  - Practical debugging & architecture grasp.'
)
ax.text(1.0, 5.0, s_text, ha='left', va='center', fontsize=9.5, color='#1e293b', linespacing=1.3)

# W Box
w_box = patches.FancyBboxPatch((5.7, 4.0), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#fef2f2', edgecolor='#dc2626', linewidth=2)
ax.add_patch(w_box)
ax.text(7.95, 6.7, 'WEAKNESSES (INTERNAL / HARMFUL)', ha='center', va='center', fontsize=12, fontweight='bold', color='#b91c1c')
w_text = (
    '• Over-Commitment:\n'
    '  - Saying yes to too many projects/tasks.\n'
    '  - Bandwidth dilution and schedule friction.\n\n'
    '• Breadth Over Depth (Knowledge Dispersion):\n'
    '  - Shifting between tech stacks without mastery.\n'
    '  - Surface fluency without vertical specialization.\n\n'
    '• Procrastination Tendency:\n'
    '  - Delaying execution until extreme pressure.'
)
ax.text(5.9, 5.0, w_text, ha='left', va='center', fontsize=9.5, color='#1e293b', linespacing=1.3)

# O Box
o_box = patches.FancyBboxPatch((0.8, 0.4), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2)
ax.add_patch(o_box)
ax.text(3.05, 3.1, 'OPPORTUNITIES (EXTERNAL / HELPFUL)', ha='center', va='center', fontsize=12, fontweight='bold', color='#15803d')
o_text = (
    '• Dual Competency Synthesis:\n'
    '  - Combining Deep Technical & Public Skills.\n'
    '  - High industry demand for Developer Advocates,\n'
    '    Solutions Architects & Technical Leads.\n\n'
    '• Emerging Engineering Platforms:\n'
    '  - Tech conferences, open source leadership,\n'
    '    hackathons, and client-facing tech roles.\n'
    '  - Community mentoring and public technical demos.'
)
ax.text(1.0, 1.4, o_text, ha='left', va='center', fontsize=9.5, color='#1e293b', linespacing=1.3)

# T Box
t_box = patches.FancyBboxPatch((5.7, 0.4), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#fffbeb', edgecolor='#d97706', linewidth=2)
ax.add_patch(t_box)
ax.text(7.95, 3.1, 'THREATS (EXTERNAL / HARMFUL)', ha='center', va='center', fontsize=12, fontweight='bold', color='#b45309')
t_text = (
    '• Stage Fear & Presentation Anxiety:\n'
    '  - Apprehension in formal high-stakes speaking.\n'
    '  - Impedes external valuation of technical merit.\n\n'
    '• Burnout From Overwork:\n'
    '  - Chronic exhaustion from over-commitment.\n'
    '  - Cognitive fatigue & erratic sleep cycles.\n\n'
    '• Escalating Industry Hyper-Competition:\n'
    '  - Market rewards deep specialized authority.'
)
ax.text(5.9, 1.4, t_text, ha='left', va='center', fontsize=9.5, color='#1e293b', linespacing=1.3)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig3_rounak_swot_detailed.png', dpi=300)
plt.close()

# ==================== FIGURE 4: Detailed Johari Window for Rounak Neema ====================
fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis('off')

ax.text(5.5, 7.6, 'JOHARI WINDOW ANALYSIS — ROUNAK NEEMA (ROLL NO: E244)', ha='center', va='center', fontsize=14, fontweight='bold', color='#0f172a')
ax.text(3.05, 7.15, 'KNOWN TO SELF', ha='center', va='center', fontsize=11, fontweight='bold', color='#475569')
ax.text(7.95, 7.15, 'NOT KNOWN TO SELF', ha='center', va='center', fontsize=11, fontweight='bold', color='#475569')
ax.text(0.3, 5.2, 'KNOWN\nTO OTHERS', ha='center', va='center', fontsize=10, fontweight='bold', color='#475569', rotation=90)
ax.text(0.3, 1.8, 'NOT KNOWN\nTO OTHERS', ha='center', va='center', fontsize=10, fontweight='bold', color='#475569', rotation=90)

# Q1: Open Arena
p1 = patches.FancyBboxPatch((0.8, 3.8), 4.5, 3.0, boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#2563eb', linewidth=2)
ax.add_patch(p1)
ax.text(3.05, 6.4, 'OPEN ARENA (PUBLIC SELF)', ha='center', va='center', fontsize=12, fontweight='bold', color='#1d4ed8')
q1_t = (
    '• Strong Need for Understanding:\n'
    '  - Insatiable intellectual drive to deconstruct concepts.\n'
    '  - Known by peers as an inquisitive systems thinker.\n'
    '  - Demands first-principles reasoning in discussions.\n\n'
    '• Ambition:\n'
    '  - High professional and engineering aspirations.\n'
    '  - Visible hunger for high-impact achievements.\n'
    '  - Sets rigorous standards for team deliverables.'
)
ax.text(1.0, 4.9, q1_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.25)

# Q2: Blind Spot
p2 = patches.FancyBboxPatch((5.7, 3.8), 4.5, 3.0, boxstyle='round,pad=0.2', facecolor='#fef3c7', edgecolor='#d97706', linewidth=2)
ax.add_patch(p2)
ax.text(7.95, 6.4, 'BLIND SPOT (EXTERNAL PERCEPTION)', ha='center', va='center', fontsize=12, fontweight='bold', color='#b45309')
q2_t = (
    '• Did Not Listen to Anyone:\n'
    '  - Uncovered via candid peer feedback.\n'
    '  - Perceived as intellectually dismissive or dogmatic.\n'
    '  - Cognitive fixation on personal solution paths.\n'
    '  - Premature evaluation before others finish speaking.\n'
    '  - Creates conversational friction in collaborative tasks.'
)
ax.text(5.9, 4.9, q2_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.25)

# Q3: Hidden Facade
p3 = patches.FancyBboxPatch((0.8, 0.4), 4.5, 3.0, boxstyle='round,pad=0.2', facecolor='#f3e8ff', edgecolor='#9333ea', linewidth=2)
ax.add_patch(p3)
ax.text(3.05, 3.0, 'HIDDEN FACADE (CONCEALED SELF)', ha='center', va='center', fontsize=12, fontweight='bold', color='#6b21a8')
q3_t = (
    '• Chronic Overthinking:\n'
    '  - Endless internal scenario simulation & worst-casing.\n'
    '  - Analysis paralysis that delays actual initiation.\n\n'
    '• Less Self-Confidence (Subsurface Imposter Syndrome):\n'
    '  - Secret doubt regarding depth of technical mastery.\n'
    '  - Masked externally with assertive opinions.\n'
    '  - Internal fear of being judged as inadequate.'
)
ax.text(1.0, 1.5, q3_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.25)

# Q4: Unknown Area
p4 = patches.FancyBboxPatch((5.7, 0.4), 4.5, 3.0, boxstyle='round,pad=0.2', facecolor='#f1f5f9', edgecolor='#475569', linewidth=2)
ax.add_patch(p4)
ax.text(7.95, 3.0, 'UNKNOWN AREA (LATENT POTENTIAL)', ha='center', va='center', fontsize=12, fontweight='bold', color='#334155')
q4_t = (
    '• Only Performs Under Extreme Conditions:\n'
    '  - High-arousal crisis activation threshold.\n'
    '  - Peak cognitive focus unlocked only when deadlines loom.\n'
    '  - Dormant or disengaged in routine, low-stress environments.\n'
    '  - Untapped potential: Channeling flow state without\n'
    '    requiring psychological crisis or acute distress.'
)
ax.text(5.9, 1.5, q4_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.25)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig4_rounak_johari_detailed.png', dpi=300)
plt.close()

# ==================== FIGURE 5: Integrated SWOT-Johari Synthesis Matrix ====================
fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis('off')

ax.text(5.5, 7.6, 'INTEGRATED SWOT-JOHARI BEHAVIORAL DIAGNOSTIC MATRIX', ha='center', va='center', fontsize=14, fontweight='bold', color='#0f172a')

# Box 1: S x Open/Unknown
b1 = patches.FancyBboxPatch((0.8, 4.0), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2)
ax.add_patch(b1)
ax.text(3.05, 6.8, 'CORE ASSETS: STRENGTHS x OPEN ARENA', ha='center', va='center', fontsize=11, fontweight='bold', color='#15803d')
t1 = (
    '• High Curiosity + Need for Understanding:\n'
    '  Creates a formidable intellectual engine that enables\n'
    '  rapid assimilation of complex computing paradigms.\n'
    '• Technical Skills + Visible Ambition:\n'
    '  Positions Rounak for engineering leadership roles\n'
    '  provided technical excellence is validated publicly.\n'
    '• Strategic Alignment:\n'
    '  Anchor career identity around principled problem-solving.'
)
ax.text(1.0, 5.0, t1, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

# Box 2: W x Blind Spot / Facade
b2 = patches.FancyBboxPatch((5.7, 4.0), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#fef2f2', edgecolor='#dc2626', linewidth=2)
ax.add_patch(b2)
ax.text(7.95, 6.8, 'BEHAVIORAL FRICTION: WEAKNESS x BLIND SPOT', ha='center', va='center', fontsize=11, fontweight='bold', color='#b91c1c')
t2 = (
    '• Overthinking (Facade) -> "Did Not Listen" (Blind Spot):\n'
    '  Internal noise & imposter fear cause defensive cognitive\n'
    '  fixation, shutting out collaborative peer inputs.\n'
    '• Breadth Over Depth + Over-Commitment:\n'
    '  Scattered focus creates anxiety, reinforcing procrastination.\n'
    '• Strategic Remediation:\n'
    '  Embrace Active Listening & Strict Project Filtering (Max 2).'
)
ax.text(5.9, 5.0, t2, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

# Box 3: O x Latent / Hybrid
b3 = patches.FancyBboxPatch((0.8, 0.4), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#2563eb', linewidth=2)
ax.add_patch(b3)
ax.text(3.05, 3.2, 'GROWTH LEVERAGE: OPPORTUNITY x EXPANSION', ha='center', va='center', fontsize=11, fontweight='bold', color='#1d4ed8')
t3 = (
    '• Combining Technical Chops + Public Speaking:\n'
    '  Transforming internal curiosity into external authority\n'
    '  through technical blogs, workshops, and speaking.\n'
    '• Channeling Ambition into Developer Advocacy:\n'
    '  Bridging the rare chasm between low-level code & human\n'
    '  communication creates exponential career value.'
)
ax.text(1.0, 1.5, t3, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

# Box 4: T x Unknown / Crisis
b4 = patches.FancyBboxPatch((5.7, 0.4), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#fffbeb', edgecolor='#d97706', linewidth=2)
ax.add_patch(b4)
ax.text(7.95, 3.2, 'CRISIS PARADOX: THREATS x UNKNOWN AREA', ha='center', va='center', fontsize=11, fontweight='bold', color='#b45309')
t4 = (
    '• "Performs Under Extreme Conditions" -> Burnout Threat:\n'
    '  Relying on crisis-induced adrenaline is unsustainable\n'
    '  and leads directly to cognitive breakdown.\n'
    '• Stage Fear + Low Self-Confidence:\n'
    '  Overthinking amplifies anticipation anxiety before speeches.\n'
    '• Strategic Mitigation: Systematic desensitization & pacing.'
)
ax.text(5.9, 1.5, t4, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig5_integrated_swot_johari.png', dpi=300)
plt.close()

# ==================== FIGURE 6: Yerkes-Dodson Law of Arousal & Performance ====================
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
x = np.linspace(0, 10, 500)
y = 10 * np.exp(-((x - 5)**2) / 6.0)

ax.plot(x, y, color='#2563eb', linewidth=3.5, label='Standard Cognitive Performance Curve')
ax.fill_between(x, y, color='#dbeafe', alpha=0.4)

y_rounak = 10 * np.exp(-((x - 7.5)**2) / 3.0)
ax.plot(x, y_rounak, color='#dc2626', linewidth=3, linestyle='--', label='Rounak Neema: Crisis-Activated Operating Curve')

ax.axvspan(0, 3.5, color='#f1f5f9', alpha=0.5)
ax.axvspan(3.5, 6.5, color='#dcfce7', alpha=0.5)
ax.axvspan(6.5, 10, color='#fee2e2', alpha=0.5)

ax.text(1.75, 1.5, 'UNDER-AROUSAL\nZONE\n(Boredom / Inertia\nProcrastination)', ha='center', va='center', fontsize=10, fontweight='bold', color='#475569')
ax.text(5.0, 8.8, 'OPTIMAL FLOW\nZONE\n(Sustainable High\nPerformance)', ha='center', va='center', fontsize=10, fontweight='bold', color='#15803d')
ax.text(8.3, 3.5, 'OVER-AROUSAL\nZONE\n(Crisis Execution / High Anxiety\nBurnout Risk)', ha='center', va='center', fontsize=10, fontweight='bold', color='#991b1b')

ax.scatter([7.5], [10], color='#dc2626', s=120, zorder=5)
ax.annotate('Rounak\'s Latent Peak:\n"Performs Only Under Extreme Conditions"\n(High Adrenaline Trigger)',
            xy=(7.5, 9.8), xytext=(5.5, 7.2),
            arrowprops=dict(facecolor='#dc2626', shrink=0.08, width=2, headwidth=8),
            fontsize=9.5, fontweight='bold', color='#991b1b',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff', edgecolor='#dc2626'))

ax.set_title('THE YERKES-DODSON PERFORMANCE PARADOX: CRISIS-ACTIVATED EXECUTION', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
ax.set_xlabel('Arousal / Stress / Deadline Proximity Level', fontsize=11, fontweight='bold')
ax.set_ylabel('Cognitive Focus & Output Efficiency', fontsize=11, fontweight='bold')
ax.set_xlim(0, 10)
ax.set_ylim(0, 11)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='lower center', frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig6_yerkes_dodson.png', dpi=300)
plt.close()

# ==================== FIGURE 7: TOWS Strategic Matrix ====================
fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis('off')

ax.text(5.5, 7.6, 'TOWS STRATEGIC INTERVENTION MATRIX — ROUNAK NEEMA (E244)', ha='center', va='center', fontsize=14, fontweight='bold', color='#0f172a')

# SO Quadrant
so_box = patches.FancyBboxPatch((0.8, 4.0), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#eff6ff', edgecolor='#2563eb', linewidth=2)
ax.add_patch(so_box)
ax.text(3.05, 6.8, 'SO STRATEGIES (MAXI - MAXI)', ha='center', va='center', fontsize=11, fontweight='bold', color='#1d4ed8')
so_t = (
    '• Leverage Curiosity + Tech Chops to Dominate Hybrid Roles:\n'
    '  Target Developer Relations, Technical Architecture & Tech Lead\n'
    '  pathways requiring both technical acumen and public voice.\n'
    '• Establish Open-Source Thought Leadership:\n'
    '  Publish deep technical architectural analyses and tutorials\n'
    '  converting private curiosity into public authority.'
)
ax.text(1.0, 5.0, so_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

# WO Quadrant
wo_box = patches.FancyBboxPatch((5.7, 4.0), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#fef3c7', edgecolor='#d97706', linewidth=2)
ax.add_patch(wo_box)
ax.text(7.95, 6.8, 'WO STRATEGIES (MINI - MAXI)', ha='center', va='center', fontsize=11, fontweight='bold', color='#b45309')
wo_t = (
    '• Curate T-Shaped Specialization via Public Goals:\n'
    '  Counteract breadth dispersion by committing to 1 core domain\n'
    '  (e.g., distributed backend systems) backed by public deliverables.\n'
    '• Overcome Procrastination via Structured Commitments:\n'
    '  Use scheduled public presentations and hackathons as external\n'
    '  milestones to simulate healthy deadlines without crisis.'
)
ax.text(5.9, 5.0, wo_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

# ST Quadrant
st_box = patches.FancyBboxPatch((0.8, 0.4), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2)
ax.add_patch(st_box)
ax.text(3.05, 3.2, 'ST STRATEGIES (MAXI - MINI)', ha='center', va='center', fontsize=11, fontweight='bold', color='#15803d')
st_t = (
    '• Ground Stage Confidence in Technical Rigor:\n'
    '  Neutralize stage fear by preparing rock-solid live demos\n'
    '  and architectural diagrams where technical depth anchors poise.\n'
    '• Protect Energy Reserves via Deep Work Blocks:\n'
    '  Shield technical curiosity from burnout by ring-fencing\n'
    '  focus time and rejecting non-essential peripheral tasks.'
)
ax.text(1.0, 1.5, st_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

# WT Quadrant
wt_box = patches.FancyBboxPatch((5.7, 0.4), 4.5, 3.2, boxstyle='round,pad=0.2', facecolor='#fef2f2', edgecolor='#dc2626', linewidth=2)
ax.add_patch(wt_box)
ax.text(7.95, 3.2, 'WT STRATEGIES (MINI - MINI)', ha='center', va='center', fontsize=11, fontweight='bold', color='#b91c1c')
wt_t = (
    '• Implement Strict "Anti-Overcommitment" Circuit Breakers:\n'
    '  Cap concurrent active projects at maximum 2. Enforce explicit\n'
    '  "Saying No" protocols to prevent catastrophic burnout.\n'
    '• Desensitize Stage Anxiety via Low-Stakes Practice:\n'
    '  Join Toastmasters or weekly lab standups to deconstruct\n'
    '  performance anxiety before high-stakes final presentations.'
)
ax.text(5.9, 1.5, wt_t, ha='left', va='center', fontsize=9.2, color='#1e293b', linespacing=1.3)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig7_tows_strategic_matrix.png', dpi=300)
plt.close()

# ==================== FIGURE 8: 24-Month Professional Development Roadmap ====================
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 6)
ax.axis('off')

ax.text(5.5, 5.5, '24-MONTH PROFESSIONAL DEVELOPMENT ROADMAP (ROUNAK NEEMA)', ha='center', va='center', fontsize=14, fontweight='bold', color='#0f172a')

arrow = patches.FancyArrowPatch((0.5, 3.5), (10.5, 3.5), arrowstyle='-|>', mutation_scale=25, color='#3b82f6', linewidth=4)
ax.add_patch(arrow)

# Phase 1
p1 = patches.FancyBboxPatch((0.8, 0.8), 2.8, 2.3, boxstyle='round,pad=0.15', facecolor='#eff6ff', edgecolor='#2563eb', linewidth=2)
ax.add_patch(p1)
ax.plot([2.2, 2.2], [3.1, 3.5], color='#2563eb', linewidth=2, linestyle=':')
ax.scatter([2.2], [3.5], color='#2563eb', s=100, zorder=5)
ax.text(2.2, 2.7, 'PHASE 1 (0–6 MONTHS)', ha='center', va='center', fontsize=10, fontweight='bold', color='#1d4ed8')
ax.text(2.2, 1.8, 'Foundational Remediation\n• Anti-procrastination timeboxing\n• Active listening peer check-ins\n• Toastmasters speech exposure\n• Capped concurrent projects (<=2)', ha='center', va='center', fontsize=8.5, color='#1e293b')

# Phase 2
p2 = patches.FancyBboxPatch((4.1, 0.8), 2.8, 2.3, boxstyle='round,pad=0.15', facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2)
ax.add_patch(p2)
ax.plot([5.5, 5.5], [3.1, 3.5], color='#16a34a', linewidth=2, linestyle=':')
ax.scatter([5.5], [3.5], color='#16a34a', s=100, zorder=5)
ax.text(5.5, 2.7, 'PHASE 2 (6–12 MONTHS)', ha='center', va='center', fontsize=10, fontweight='bold', color='#15803d')
ax.text(5.5, 1.8, 'Competency Consolidation\n• T-shaped deep backend mastery\n• Tech writing & public speaking\n• Deliver 3 conference/meetup talks\n• Regulated work/rest rhythms', ha='center', va='center', fontsize=8.5, color='#1e293b')

# Phase 3
p3 = patches.FancyBboxPatch((7.4, 0.8), 2.8, 2.3, boxstyle='round,pad=0.15', facecolor='#fffbeb', edgecolor='#d97706', linewidth=2)
ax.add_patch(p3)
ax.plot([8.8, 8.8], [3.1, 3.5], color='#d97706', linewidth=2, linestyle=':')
ax.scatter([8.8], [3.5], color='#d97706', s=100, zorder=5)
ax.text(8.8, 2.7, 'PHASE 3 (12–24 MONTHS)', ha='center', va='center', fontsize=10, fontweight='bold', color='#b45309')
ax.text(8.8, 1.8, 'Leadership & Integration\n• Tech Lead / DevRel transition\n• Cross-functional team leadership\n• Mentoring junior engineers\n• Crisis-free high performance', ha='center', va='center', fontsize=8.5, color='#1e293b')

ax.text(2.2, 4.2, 'Milestone 1:\nOvercome Stage Fear', ha='center', va='center', fontsize=9, fontweight='bold', color='#1e40af', bbox=dict(boxstyle='round,pad=0.2', facecolor='#dbeafe', edgecolor='#93c5fd'))
ax.text(5.5, 4.2, 'Milestone 2:\nSpecialized Authority', ha='center', va='center', fontsize=9, fontweight='bold', color='#166534', bbox=dict(boxstyle='round,pad=0.2', facecolor='#bbf7d0', edgecolor='#86efac'))
ax.text(8.8, 4.2, 'Milestone 3:\nEngineering Leadership', ha='center', va='center', fontsize=9, fontweight='bold', color='#92400e', bbox=dict(boxstyle='round,pad=0.2', facecolor='#fef3c7', edgecolor='#fde68a'))

plt.tight_layout()
plt.savefig(f'{out_dir}/fig8_development_timeline.png', dpi=300)
plt.close()

print('All 8 figures successfully generated in', out_dir)
