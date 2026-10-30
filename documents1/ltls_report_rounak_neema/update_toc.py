with open('ltls_report_rounak_neema/tune_report_pages.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace TOC table data with exact page numbers
old_toc = '''    toc_data = [
        ("CERTIFICATE OF COMPLETION", "ii"),
        ("CANDIDATE DECLARATION & ACKNOWLEDGEMENTS", "iii"),
        ("EXECUTIVE SUMMARY", "iv"),
        ("1. INTRODUCTION AND CONTEXTUAL BACKGROUND", "1"),
        ("   1.1 The Imperative of Behavioral Competency in Engineering Education", "1"),
        ("   1.2 Pedagogical Framework: Leadership, Team and Life Skills (LTLS)", "2"),
        ("   1.3 Personal Profile and Candidate Context (Rounak Neema, E244)", "2"),
        ("   1.4 Objectives and Scope of the Investigation", "2"),
        ("2. THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS", "3"),
        ("   2.1 Strategic Personal Assessment: The SWOT Paradigm", "3"),
        ("   2.2 Interpersonal Dynamics: The Johari Window Model", "4"),
        ("   2.3 Psychological & Cognitive Foundations (Yerkes-Dodson, Cognitive Load)", "4"),
        ("3. RESEARCH METHODOLOGY & ASSESSMENT PROTOCOL", "5"),
        ("   3.1 Multi-Method Triangulation Research Design", "5"),
        ("   3.2 Data Collection Instrumentation & Peer Sampling", "5"),
        ("   3.3 Data Normalization, Coding, and Bias Mitigation", "6"),
        ("4. EMPIRICAL FINDINGS: COMPREHENSIVE SWOT ANALYSIS", "7"),
        ("   4.1 Granular Analysis of Strengths (Curiosity, Technical Acumen)", "7"),
        ("   4.2 Comprehensive Deconstruction of Weaknesses (Over-commitment, Breadth)", "8"),
        ("   4.3 Strategic Exploration of Opportunities (Dual Competency Synthesis)", "8"),
        ("   4.4 Environmental & Psychological Threats (Stage Fear, Burnout)", "9"),
        ("   4.5 The TOWS Strategic Formulation Matrix", "9"),
        ("5. EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT", "10"),
        ("   5.1 Quadrant I: The Open Arena (Ambition, Need for Understanding)", "10"),
        ("   5.2 Quadrant II: The Blind Spot ('Did Not Listen to Anyone')", "11"),
        ("   5.3 Quadrant III: The Hidden Facade (Overthinking, Imposter Syndrome)", "11"),
        ("   5.4 Quadrant IV: The Unknown Area (Extreme Conditions Paradox)", "12"),
        ("6. CROSS-MODEL SYNTHESES AND BEHAVIORAL DIAGNOSTICS", "13"),
        ("   6.1 The SWOT-Johari Behavioral Diagnostic Matrix", "13"),
        ("   6.2 Root Cause Analysis: The 5-Whys Diagnostic Framework", "14"),
        ("   6.3 Psychodynamic Profile: The Crisis-Activated Operating Curve", "14"),
        ("7. STRATEGIC PERSONAL DEVELOPMENT PLAN & 24-MONTH ROADMAP", "15"),
        ("   7.1 Phase 1: Foundational Remediation & Habit Restructuring (0–6 Months)", "15"),
        ("   7.2 Phase 2: Competency Consolidation & Specialization (6–12 Months)", "16"),
        ("   7.3 Phase 3: Leadership Integration & Sustainable Performance (12–24 Months)", "16"),
        ("   7.4 Quantitative Metrics, KPIs, and Tracking Scorecard", "17"),
        ("8. CONCLUSION AND TRANSFORMATIVE COMMITMENTS", "18"),
        ("9. ACADEMIC REFERENCES AND APPENDICES", "19")
    ]'''

new_toc = '''    toc_data = [
        ("CERTIFICATE OF COMPLETION", "2"),
        ("CANDIDATE DECLARATION & ACKNOWLEDGEMENTS", "3"),
        ("EXECUTIVE SUMMARY", "4"),
        ("TABLE OF CONTENTS & LISTINGS", "5"),
        ("1. INTRODUCTION AND CONTEXTUAL BACKGROUND", "6"),
        ("   1.1 The Imperative of Behavioral Competency in Engineering Education", "6"),
        ("   1.2 Pedagogical Framework: Leadership, Team and Life Skills (LTLS)", "6"),
        ("   1.3 Personal Profile and Candidate Context (Rounak Neema, E244)", "6"),
        ("   1.4 Objectives and Scope of the Investigation", "6"),
        ("2. THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS", "7"),
        ("   2.1 Strategic Personal Assessment: The SWOT Paradigm", "7"),
        ("   2.2 Interpersonal Dynamics: The Johari Window Model", "8"),
        ("   2.3 Psychological & Cognitive Foundations (Yerkes-Dodson, Cognitive Load)", "8"),
        ("3. RESEARCH METHODOLOGY & ASSESSMENT PROTOCOL", "9"),
        ("   3.1 Multi-Method Triangulation Research Design", "9"),
        ("   3.2 Data Collection Instrumentation & Peer Sampling", "9"),
        ("   3.3 Data Normalization, Coding, and Bias Mitigation", "9"),
        ("4. EMPIRICAL FINDINGS: COMPREHENSIVE SWOT ANALYSIS", "10"),
        ("   4.1 Granular Analysis of Strengths (Curiosity, Technical Acumen)", "10"),
        ("   4.2 Comprehensive Deconstruction of Weaknesses (Over-commitment, Breadth)", "11"),
        ("   4.3 Strategic Exploration of Opportunities (Dual Competency Synthesis)", "11"),
        ("   4.4 Environmental & Psychological Threats (Stage Fear, Burnout)", "11"),
        ("   4.5 The TOWS Strategic Formulation Matrix", "11"),
        ("5. EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT", "12"),
        ("   5.1 Quadrant I: The Open Arena (Ambition, Need for Understanding)", "12"),
        ("   5.2 Quadrant II: The Blind Spot ('Did Not Listen to Anyone')", "13"),
        ("   5.3 Quadrant III: The Hidden Facade (Overthinking, Imposter Syndrome)", "13"),
        ("   5.4 Quadrant IV: The Unknown Area (Extreme Conditions Paradox)", "13"),
        ("6. CROSS-MODEL SYNTHESES AND BEHAVIORAL DIAGNOSTICS", "14"),
        ("   6.1 The SWOT-Johari Behavioral Diagnostic Matrix", "14"),
        ("   6.2 Root Cause Analysis: The 5-Whys Diagnostic Framework", "14"),
        ("   6.3 Psychodynamic Profile: The Crisis-Activated Operating Curve", "15"),
        ("7. STRATEGIC PERSONAL DEVELOPMENT PLAN & 24-MONTH ROADMAP", "16"),
        ("   7.1 Phase 1: Foundational Remediation & Habit Restructuring (0–6 Months)", "16"),
        ("   7.2 Phase 2: Competency Consolidation & Specialization (6–12 Months)", "16"),
        ("   7.3 Phase 3: Leadership Integration & Sustainable Performance (12–24 Months)", "16"),
        ("   7.4 Quantitative Metrics, KPIs, and Tracking Scorecard", "17"),
        ("8. CONCLUSION AND TRANSFORMATIVE COMMITMENTS", "17"),
        ("9. ACADEMIC REFERENCES AND APPENDICES", "18")
    ]'''

text = text.replace(old_toc, new_toc)

# Also add header and footer with page numbers
hf_code = '''    # Add Header & Footer
    for s_idx, sec in enumerate(doc.sections):
        # Header
        header = sec.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("MPSTME, SVKM's NMIMS | LTLS Comprehensive Self-Analysis | Rounak Neema (E244)")
        hr.font.name = 'Calibri'
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = MUTED
        
        # Footer
        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("B.Tech Computer Science & Engineering | Academic Year 2026–2027")
        fr.font.name = 'Calibri'
        fr.font.size = Pt(8.5)
        fr.font.color.rgb = MUTED
'''

# Insert hf_code before "# Save and measure pages"
text = text.replace('    # Save and measure pages', hf_code + '\n    # Save and measure pages')

with open('ltls_report_rounak_neema/tune_report_pages.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("TOC and Header/Footer updated")
