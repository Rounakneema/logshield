import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import win32com.client

def create_report():
    doc = docx.Document()
    
    # ------------------ Page Margins ------------------
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.header_distance = Inches(0.5)
        section.footer_distance = Inches(0.5)

    # ------------------ Color Palette ------------------
    NAVY_HEX = "1E3A8A"
    SLATE_HEX = "2563EB"
    DARK_TEXT_HEX = "1E293B"
    MUTED_HEX = "64748B"
    LIGHT_BG_HEX = "F8FAFC"
    BORDER_HEX = "CBD5E1"
    
    NAVY = RGBColor(0x1E, 0x3A, 0x8A)
    SLATE = RGBColor(0x25, 0x63, 0xEB)
    DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B)
    MUTED = RGBColor(0x64, 0x74, 0x8B)

    # ------------------ Helper Functions ------------------
    def set_cell_background(cell, color_hex):
        shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{margin_name}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_cell_borders(cell, top="CCCCCC", bottom="CCCCCC", left=None, right=None, sz="4"):
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        
        borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
        for b_name, b_color in borders.items():
            if b_color:
                node = OxmlElement(f'w:{b_name}')
                node.set(qn('w:val'), 'single')
                node.set(qn('w:sz'), sz)
                node.set(qn('w:space'), '0')
                node.set(qn('w:color'), b_color)
                tcBorders.append(node)
            else:
                node = OxmlElement(f'w:{b_name}')
                node.set(qn('w:val'), 'none')
                tcBorders.append(node)
        tcPr.append(tcBorders)

    def add_p(text, style='Normal', space_before=0, space_after=6, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, italic=False, font_size=11, font_color=DARK_TEXT):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Calibri'
        run.font.size = Pt(font_size)
        run.font.color.rgb = font_color
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(15)
        run.font.color.rgb = NAVY
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12.5)
        run.font.color.rgb = SLATE
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(11)
        run.font.color.rgb = DARK_TEXT
        return p

    def add_callout(text, title=None):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        set_cell_borders(cell, top=None, bottom=None, left="2563EB", right=None, sz="24")
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if title:
            r_title = p.add_run(f"INSIGHT: {title}\n")
            r_title.bold = True
            r_title.font.name = 'Calibri'
            r_title.font.size = Pt(10.5)
            r_title.font.color.rgb = SLATE
        r = p.add_run(text)
        r.italic = True
        r.font.name = 'Calibri'
        r.font.size = Pt(10)
        r.font.color.rgb = DARK_TEXT
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_figure(img_path, caption, width=Inches(6.0)):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run()
            run.add_picture(img_path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            run_cap = p_cap.add_run(caption)
            run_cap.italic = True
            run_cap.bold = True
            run_cap.font.name = 'Calibri'
            run_cap.font.size = Pt(9.5)
            run_cap.font.color.rgb = MUTED

    fig_dir = 'ltls_report_rounak_neema/figures'

    # =========================================================================
    # PAGE 1: TITLE PAGE
    # =========================================================================
    add_p("A COMPREHENSIVE SELF-ANALYSIS FOR PROFESSIONAL DEVELOPMENT", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=18, font_color=NAVY, space_before=18, space_after=8)
    
    add_p("An Individual Diagnostic Investigation Based on SWOT Matrix and Johari Window Frameworks", 
          align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, font_size=12, font_color=SLATE, space_after=18)

    # University Logo
    logo_path = os.path.join(fig_dir, 'nmims_logo.png')
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(14)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Inches(1.5))

    add_p("Submitted in Partial Fulfillment of the Academic Requirements for the Course\nLEADERSHIP, TEAM AND LIFE SKILLS (LTLS)", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=11, font_color=DARK_TEXT, space_after=18)

    add_p("SUBMITTED BY:\nROUNAK NEEMA\nRoll Number: E244\nB.Tech in Computer Science and Engineering\nFinal Year (Academic Year 2026–2027)", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=11.5, font_color=NAVY, space_after=20)

    add_p("UNDER THE GUIDANCE OF:\nDR. ABHIJEET DAWLE\nAssistant Professor\nDepartment of Applied Sciences & Humanities\nMukesh Patel School of Technology Management & Engineering (MPSTME)\nSVKM's NMIMS, Shirpur Campus", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=11, font_color=DARK_TEXT, space_after=22)

    add_p("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nMUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING\nSVKM'S NMIMS (DEEMED TO BE UNIVERSITY)\nSHIRPUR CAMPUS, MAHARASHTRA, INDIA\nOCTOBER 2026", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=10.5, font_color=MUTED, space_after=0)

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: CERTIFICATE OF COMPLETION
    # =========================================================================
    add_p("SVKM's NMIMS\nMUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING\nSHIRPUR CAMPUS, MAHARASHTRA", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=12, font_color=NAVY, space_before=10, space_after=14)
    
    add_heading_1("CERTIFICATE OF COMPLETION")
    
    add_p("This is to certify that the comprehensive academic report entitled “A Comprehensive Self-Analysis for Professional Development: An Individual Report Based on SWOT and Johari Window Analysis” is a bonafide record of independent introspective and empirical research carried out by ROUNAK NEEMA (Roll Number: E244), a bonafide student of Bachelor of Technology in Computer Science and Engineering, Final Year, at Mukesh Patel School of Technology Management & Engineering (MPSTME), SVKM’s NMIMS, Shirpur Campus, for the course Leadership, Team and Life Skills (LTLS) during the Academic Year 2026–2027.", 
          space_before=12, space_after=14, line_spacing=1.2)
    
    add_p("This self-analysis report demonstrates authentic engagement with psychodynamic models, 360-degree peer evaluation protocols, and behavioral remediation strategies. The candidate has actively synthesized qualitative and quantitative feedback into an actionable 24-month professional development roadmap. The work presented herein has been completed under my direct supervision and satisfies all prescribed institutional standards for academic evaluation.", 
          space_after=30, line_spacing=1.2)

    # Signature Table
    table_sig = doc.add_table(rows=2, cols=2)
    table_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sig.autofit = False
    
    c0 = table_sig.cell(0, 0)
    c0.width = Inches(3.25)
    c0.paragraphs[0].add_run("Date: 23 October 2026\nPlace: MPSTME, Shirpur").font.size = Pt(10.5)
    
    c1 = table_sig.cell(0, 1)
    c1.width = Inches(3.25)
    p_g = c1.paragraphs[0]
    p_g.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_g = p_g.add_run("_____________________________\nDr. Abhijeet Dawle\nFaculty Guide & Assistant Professor\nDept. of Applied Sciences & Humanities\nMPSTME, NMIMS, Shirpur Campus")
    r_g.bold = True
    r_g.font.size = Pt(10.5)
    
    c2 = table_sig.cell(1, 0)
    c2.width = Inches(3.25)
    p_seal = c2.paragraphs[0]
    p_seal.paragraph_format.space_before = Pt(30)
    p_seal.add_run("[ Institutional Seal ]").font.color.rgb = MUTED
    
    c3 = table_sig.cell(1, 1)
    c3.width = Inches(3.25)
    p_hod = c3.paragraphs[0]
    p_hod.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hod.paragraph_format.space_before = Pt(30)
    r_hod = p_hod.add_run("_____________________________\nHead of Department\nDepartment of Computer Science & Engineering\nMPSTME, NMIMS, Shirpur Campus")
    r_hod.bold = True
    r_hod.font.size = Pt(10.5)

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: DECLARATION BY CANDIDATE
    # =========================================================================
    add_heading_1("CANDIDATE DECLARATION")
    
    add_p("I, ROUNAK NEEMA, Roll Number E244, student of Bachelor of Technology in Computer Science and Engineering, Final Year, at Mukesh Patel School of Technology Management & Engineering (MPSTME), SVKM’s NMIMS, Shirpur Campus, hereby declare that this report entitled “A Comprehensive Self-Analysis for Professional Development: An Individual Report Based on SWOT and Johari Window Analysis” represents my own authentic and original analytical effort.", 
          space_before=14, space_after=14, line_spacing=1.2)
    
    add_p("I solemnly confirm that:", space_after=6)
    bullets = [
        "The empirical observations, self-reflections, and psychometric assessments detailed in this report are grounded in genuine personal experiences and validated through peer feedback collected during my B.Tech tenure.",
        "The diagnostic evaluations regarding my strengths (unusually high curiosity, technical competence), weaknesses (over-commitment, breadth-over-depth dispersion, procrastination), opportunities (combining technical and public communication skills), and threats (stage fear, burnout vulnerability) are authentic and unvarnished.",
        "The interpersonal observations categorized under the Johari Window—specifically the blind spot of conversational non-listening, hidden overthinking and imposter insecurity, and latent crisis-activated performance—were derived transparently from multi-rater peer surveys.",
        "This submission has not been submitted previously in part or full to any other university, institute, or board for the award of any degree, diploma, or academic distinction.",
        "All scholarly literature, models, frameworks, and secondary sources referenced throughout this study have been cited ethically in accordance with academic standards."
    ]
    for b in bullets:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_before = Pt(2)
        p_b.paragraph_format.space_after = Pt(4)
        p_b.paragraph_format.line_spacing = 1.15
        r_b = p_b.add_run(b)
        r_b.font.name = 'Calibri'
        r_b.font.size = Pt(10.5)

    add_p("\n\n_____________________________\nROUNAK NEEMA\nRoll Number: E244\nB.Tech Computer Science & Engineering, Final Year\nMPSTME, SVKM's NMIMS, Shirpur Campus\nDate: 23 October 2026", 
          space_before=24, space_after=10, bold=True, font_color=NAVY)

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: ACKNOWLEDGEMENTS
    # =========================================================================
    add_heading_1("ACKNOWLEDGEMENTS")
    
    add_p("The formulation and completion of this comprehensive self-analysis report would not have been possible without the invaluable guidance, constructive critique, and intellectual support of numerous mentors, faculty members, and peers at Mukesh Patel School of Technology Management & Engineering (MPSTME), SVKM’s NMIMS, Shirpur.", 
          space_before=14, space_after=12, line_spacing=1.2)
    
    add_p("First and foremost, I express my deepest intellectual gratitude and profound respect to my faculty mentor and guide, DR. ABHIJEET DAWLE, Assistant Professor, Department of Applied Sciences & Humanities. His pedagogical expertise in organizational behavior, leadership development, and life skills provided the conceptual scaffolding necessary to conduct this rigorous self-inquiry. His constant encouragement challenged me to look beyond surface-level traits, confront deeply rooted behavioral vulnerabilities, and construct a grounded development plan.", 
          space_after=12, line_spacing=1.2)
    
    add_p("I extend my sincere appreciation to the Department of Computer Science & Engineering and the Department of Applied Sciences & Humanities at MPSTME, Shirpur, for fostering an academic ecosystem that values holistic engineer development. Balancing intense algorithmic rigor with interpersonal and self-regulatory mastery is rare, and the LTLS curriculum serves as an essential bridge for aspiring engineers.", 
          space_after=12, line_spacing=1.2)
    
    add_p("I am profoundly indebted to my peers, project teammates, and batchmates who participated in the 360-degree Johari Window evaluation. Providing unvarnished, honest feedback regarding conversational blind spots—particularly highlighting my tendency to fixate cognitively and fail to listen attentively during team debates—demanded candor. Their authentic observations proved pivotal in illuminating areas of interpersonal friction that self-reflection alone could never have detected.", 
          space_after=12, line_spacing=1.2)
    
    add_p("Finally, I extend my heartfelt gratitude to my family for their unwavering encouragement, emotional ballast, and belief in my intellectual pursuits throughout my engineering journey.", 
          space_after=16, line_spacing=1.2)

    doc.add_page_break()

    # =========================================================================
    # PAGE 5: EXECUTIVE SUMMARY
    # =========================================================================
    add_heading_1("EXECUTIVE SUMMARY")
    
    add_p("This comprehensive diagnostic report articulates an in-depth, empirically grounded personal and professional self-analysis for Rounak Neema (Roll No: E244), a final-year Bachelor of Technology student in Computer Science and Engineering at Mukesh Patel School of Technology Management & Engineering (MPSTME), SVKM’s NMIMS, Shirpur Campus. Prepared as an individual academic submission for the Leadership, Team and Life Skills (LTLS) curriculum, this investigation utilizes two foundational behavioral and strategic paradigms—the SWOT (Strengths, Weaknesses, Opportunities, Threats) Matrix and the Johari Window Model—triangulated with cognitive psychodynamics to evaluate professional readiness, behavioral liabilities, and leadership maturity.", 
          space_before=12, space_after=10, line_spacing=1.2)
    
    add_p("Core findings from the empirical SWOT assessment identify distinct competitive advantages anchored in an unusually high intellectual curiosity and robust technical skills in software engineering, system architecture, and computational problem-solving. However, these assets are severely constrained by internal vulnerabilities: chronic over-commitment stemming from an inability to decline peripheral initiatives, a tendency to prioritize horizontal breadth over deep vertical specialization, and habitual procrastination driven by perfectionism. Externally, the analysis identifies a high-value strategic opportunity to synthesize deep technical competence with public communication skills—positioning the candidate for hybrid high-impact roles such as Solutions Architect, Developer Advocate, or Technical Product Lead. Conversely, acute external threats include crippling stage fear (glossophobia) during high-stakes presentations and severe vulnerability to physiological and cognitive burnout resulting from chronic overwork.", 
          space_after=10, line_spacing=1.2)

    add_p("The Johari Window assessment, constructed through multi-rater peer evaluations, reveals critical disparities between self-perception and external observation. In the Open Arena, peers recognize a strong drive for foundational understanding and palpable professional ambition. Crucially, the external mirror exposed a major Blind Spot: a persistent conversational pattern wherein the candidate 'did not listen to anyone,' characterized by premature cognitive fixation and defensive debate. Within the Hidden Facade, the candidate harbors chronic internal overthinking and subsurface imposter anxiety, masked externally by technical assertiveness. Most significantly, the Unknown Area revealed a latent performance paradox: an operational profile that 'only performs under extreme conditions'—an adrenaline-coupled coping mechanism that activates peak focus during crisis states but induces inertia during calm operational cycles.", 
          space_after=10, line_spacing=1.2)

    add_p("To translate these diagnostics into sustainable behavioral transformation, an integrated TOWS matrix and a phased 24-month Personal Development Plan (PDP) have been engineered. The roadmap establishes concrete intervention protocols: Phase 1 (0–6 Months) focuses on immediate remediation through strict project-capping (max 2 active initiatives), active listening behavioral drills, and Toastmasters public speaking desensitization; Phase 2 (6–12 Months) consolidates vertical technical specialization while executing public technical writing and conference demos; Phase 3 (12–24 Months) operationalizes sustainable engineering leadership, peer mentorship, and crisis-independent flow states. Ultimately, this report serves as an authentic developmental compass for navigating the critical transition from engineering academia to high-impact technology leadership.", 
          space_after=12, line_spacing=1.2)

    doc.add_page_break()

    # =========================================================================
    # PAGE 6: TABLE OF CONTENTS & LISTINGS
    # =========================================================================
    add_heading_1("TABLE OF CONTENTS")
    
    toc_data = [
        ("CERTIFICATE OF COMPLETION", "ii"),
        ("CANDIDATE DECLARATION", "iii"),
        ("ACKNOWLEDGEMENTS", "iv"),
        ("EXECUTIVE SUMMARY", "v"),
        ("1. INTRODUCTION AND CONTEXTUAL BACKGROUND", "1"),
        ("   1.1 The Imperative of Behavioral Competency in Engineering Education", "1"),
        ("   1.2 Pedagogical Framework: Leadership, Team and Life Skills (LTLS)", "2"),
        ("   1.3 Personal Profile and Candidate Context (Rounak Neema, E244)", "2"),
        ("   1.4 Objectives and Scope of the Investigation", "3"),
        ("   1.5 Report Organization and Structural Architecture", "3"),
        ("2. THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS", "4"),
        ("   2.1 Strategic Personal Assessment: The SWOT Paradigm", "4"),
        ("   2.2 Interpersonal Dynamics: The Johari Window Model", "5"),
        ("   2.3 Psychological & Cognitive Foundations", "5"),
        ("   2.4 Epistemological Convergence: Integrating Introspection and Extrospection", "6"),
        ("3. RESEARCH METHODOLOGY & ASSESSMENT PROTOCOL", "7"),
        ("   3.1 Multi-Method Triangulation Research Design", "7"),
        ("   3.2 Data Collection Instrumentation & Peer Sampling", "7"),
        ("   3.3 Data Normalization, Coding, and Bias Mitigation", "8"),
        ("4. EMPIRICAL FINDINGS: COMPREHENSIVE SWOT ANALYSIS", "9"),
        ("   4.1 Granular Analysis of Strengths (S)", "9"),
        ("   4.2 Comprehensive Deconstruction of Weaknesses (W)", "10"),
        ("   4.3 Strategic Exploration of Opportunities (O)", "10"),
        ("   4.4 Environmental & Psychological Threats (T)", "11"),
        ("   4.5 The TOWS Strategic Formulation Matrix", "11"),
        ("5. EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT", "12"),
        ("   5.1 Quadrant I: The Open Arena (The Public Self)", "12"),
        ("   5.2 Quadrant II: The Blind Spot (The External Mirror)", "13"),
        ("   5.3 Quadrant III: The Hidden Facade (The Masked Self)", "13"),
        ("   5.4 Quadrant IV: The Unknown Area (The Latent Frontier)", "14"),
        ("6. CROSS-MODEL SYNTHESES AND BEHAVIORAL DIAGNOSTICS", "15"),
        ("   6.1 The SWOT-Johari Behavioral Diagnostic Matrix", "15"),
        ("   6.2 Root Cause Analysis: The 5-Whys Diagnostic Framework", "16"),
        ("   6.3 Psychodynamic Profile: The Crisis-Activated Engineer", "16"),
        ("7. STRATEGIC PERSONAL DEVELOPMENT PLAN & 24-MONTH ROADMAP", "17"),
        ("   7.1 Phase 1: Foundational Remediation & Habit Restructuring (0–6 Months)", "17"),
        ("   7.2 Phase 2: Competency Consolidation & Specialization (6–12 Months)", "18"),
        ("   7.3 Phase 3: Leadership Integration & Sustainable Performance (12–24 Months)", "18"),
        ("   7.4 Quantitative Metrics, KPIs, and Tracking Scorecard", "19"),
        ("8. CONCLUSION AND TRANSFORMATIVE COMMITMENTS", "20"),
        ("9. ACADEMIC REFERENCES AND APPENDICES", "21")
    ]
    
    t_toc = doc.add_table(rows=len(toc_data), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    for i, (title, page) in enumerate(toc_data):
        row = t_toc.rows[i]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(5.6)
        c1.width = Inches(0.9)
        set_cell_borders(c0, top=None, bottom=None, left=None, right=None)
        set_cell_borders(c1, top=None, bottom=None, left=None, right=None)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        p0.paragraph_format.line_spacing = 1.05
        r0 = p0.add_run(title)
        r0.font.name = 'Calibri'
        r0.font.size = Pt(9.5)
        if title.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "CERTIFICATE", "CANDIDATE", "ACKNOW", "EXEC")):
            r0.bold = True
            r0.font.color.rgb = NAVY
            
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        p1.paragraph_format.line_spacing = 1.05
        r1 = p1.add_run(page)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)
        r1.bold = True

    add_p("\nLIST OF FIGURES & TABLES", bold=True, font_size=11, font_color=NAVY, space_before=10, space_after=4)
    figs_tables = [
        ("Figure 1: SWOT Analysis Conceptual Framework", "Page 4"),
        ("Figure 2: The Johari Window Conceptual Model (Luft & Ingham)", "Page 5"),
        ("Figure 3: Detailed SWOT Analysis Matrix for Rounak Neema (E244)", "Page 9"),
        ("Figure 4: Detailed Johari Window Quadrant Map for Rounak Neema (E244)", "Page 12"),
        ("Figure 5: Integrated SWOT-Johari Behavioral Diagnostic Matrix", "Page 15"),
        ("Figure 6: The Yerkes-Dodson Performance vs. Arousal Paradox", "Page 16"),
        ("Figure 7: Strategic TOWS Intervention Matrix", "Page 11"),
        ("Figure 8: 24-Month Professional Development Action Roadmap Timeline", "Page 17"),
        ("Table 1: Structured SWOT Findings for Rounak Neema", "Page 9"),
        ("Table 2: Multi-Rater Johari Window Quadrant Analysis", "Page 12"),
        ("Table 3: TOWS Action Implementation Matrix", "Page 11"),
        ("Table 4: Root Cause 5-Whys Diagnostic Trace", "Page 16"),
        ("Table 5: 24-Month Phased Action Implementation Schedule", "Page 19"),
        ("Table 6: Behavioral Key Performance Indicators (KPIs) Scorecard", "Page 19")
    ]
    for ft, pg in figs_tables:
        p_ft = doc.add_paragraph()
        p_ft.paragraph_format.space_before = Pt(1)
        p_ft.paragraph_format.space_after = Pt(1)
        p_ft.paragraph_format.line_spacing = 1.05
        r_ft = p_ft.add_run(f"• {ft}")
        r_ft.font.name = 'Calibri'
        r_ft.font.size = Pt(9)
        r_pg = p_ft.add_run(f" ...... {pg}")
        r_pg.italic = True
        r_pg.font.size = Pt(9)
        r_pg.font.color.rgb = MUTED

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION AND CONTEXTUAL BACKGROUND
    # =========================================================================
    add_heading_1("CHAPTER 1: INTRODUCTION AND CONTEXTUAL BACKGROUND")
    
    add_heading_2("1.1 The Imperative of Behavioral Competency in Engineering Education")
    add_p("The contemporary technological paradigm is characterized by unprecedented volatility, algorithmic complexity, and rapid obsolescence. Within computer science and software engineering, traditional pedagogy has historically prioritized hard technical proficiencies—such as data structures, computational complexity, distributed systems architecture, and database theory. However, contemporary empirical research across global software enterprises indicates that technical acumen alone is a necessary but profoundly insufficient condition for sustained career excellence and organizational leadership (Goleman, 1995; Dweck, 2006).", space_after=8)
    
    add_p("Modern engineering problems are rarely solved in isolation. Modern technology stacks require cross-functional collaboration, socio-technical alignment, transparent communication, and rapid cognitive adaptability. Software engineers who possess brilliant technical capabilities but lack emotional intelligence, active listening competencies, and self-regulatory discipline often encounter severe professional ceilings. They struggle with interpersonal friction in agile environments, fall prey to cognitive fatigue and burnout, and fail to translate their computational insights into business value. Consequently, systematic self-analysis, introspective rigor, and structured behavioral development have emerged as vital imperatives for graduating engineering students preparing to transition from structured academia into competitive industry ecosystems.", space_after=10)

    add_heading_2("1.2 Institutional and Pedagogical Framework: Leadership, Team and Life Skills (LTLS)")
    add_p("Mukesh Patel School of Technology Management & Engineering (MPSTME) at SVKM's NMIMS University recognizes that world-class engineers must embody both intellectual rigor and personal leadership maturity. The course 'Leadership, Team and Life Skills' (LTLS), administered under the Department of Applied Sciences & Humanities, serves as a cornerstone behavioral curriculum designed to cultivate emotional intelligence, interpersonal fluency, self-awareness, and ethical leadership among engineering undergraduates.", space_after=8)
    
    add_p("The primary pedagogy of LTLS departs from conventional passive lectures; it demands rigorous experiential engagement, psychometric profiling, collaborative simulations, and reflective inquiry. By mandating comprehensive self-diagnostic projects, the course obligates students to hold an unvarnished mirror to their psychological architecture. Rather than relying on self-congratulatory assumptions, students must evaluate their habits, blind spots, cognitive defense mechanisms, and stress responses. This report fulfills the capstone individual submission requirement for LTLS, operationalizing these pedagogical principles through empirical self-investigation.", space_after=10)

    add_heading_2("1.3 Personal Profile and Candidate Context (Rounak Neema, E244)")
    add_p("The subject of this comprehensive self-analysis is ROUNAK NEEMA (Roll Number: E244), currently in the final year of the Bachelor of Technology in Computer Science and Engineering program at MPSTME, NMIMS, Shirpur Campus. Throughout seven semesters of rigorous technical training, my academic and technical pursuits have centered on low-level systems programming, backend architectures, runtime security, and scalable distributed infrastructures.", space_after=8)
    
    add_p("While my academic record and software engineering projects reflect robust technical problem-solving capabilities, my operational trajectory has been characterized by sharp behavioral paradoxes. An insatiable intellectual curiosity has driven me to explore vast landscapes of computing paradigms; however, this same trait has manifested as chronic over-commitment, superficial knowledge dispersion, and severe procrastination. Furthermore, while my peers recognize my intense drive and technical ambition, team collaborations have frequently experienced friction due to an unconscious habit of non-listening and cognitive fixation. As I prepare to graduate and enter the technology workforce, conducting this rigorous, evidence-based self-analysis is essential to identify psychological bottlenecks and build sustainable behavioral competencies.", space_after=10)

    add_heading_2("1.4 Objectives and Scope of the Investigation")
    add_p("The primary objective of this academic research is to conduct an uncompromising, multidimensional diagnostic evaluation of my personal and professional attributes, establishing an empirical foundation for a 24-month developmental roadmap. Specifically, this study aims to:", space_after=6)
    
    obj_bullets = [
        "Systematically deconstruct internal proficiencies and liabilities using the classic SWOT framework, validated against actual project deliverables and engineering coursework.",
        "Illuminate hidden interpersonal dynamics and cognitive blind spots through a rigorous, multi-rater Johari Window analysis incorporating 360-degree feedback from eight academic peers and project teammates.",
        "Examine the psychodynamic interplay between personal weaknesses (over-commitment, breadth dispersion, procrastination) and external threats (stage fear, professional burnout).",
        "Investigate the psychological architecture of the 'performs only under extreme conditions' paradox using the Yerkes-Dodson Law of Arousal and Performance.",
        "Formulate a high-impact TOWS strategy and an actionable, phased Personal Development Plan (PDP) featuring quantifiable Key Performance Indicators (KPIs) to guide my early-career trajectory."
    ]
    for ob in obj_bullets:
        p_ob = doc.add_paragraph(style='List Bullet')
        p_ob.paragraph_format.space_before = Pt(2)
        p_ob.paragraph_format.space_after = Pt(3)
        p_ob.paragraph_format.line_spacing = 1.15
        r_ob = p_ob.add_run(ob)
        r_ob.font.name = 'Calibri'
        r_ob.font.size = Pt(10.5)

    add_heading_2("1.5 Report Organization and Structural Architecture")
    add_p("This report is systematically structured into nine cohesive chapters. Chapter 1 establishes the rationale, institutional background, and candidate profile. Chapter 2 reviews the theoretical frameworks (SWOT, Johari Window, Cognitive Load Theory, Yerkes-Dodson Law). Chapter 3 outlines the research methodology and 360-degree peer survey protocol. Chapter 4 and Chapter 5 present the empirical findings from the SWOT and Johari Window analyses, respectively. Chapter 6 integrates both models through a behavioral diagnostic matrix and 5-Whys root-cause analysis. Chapter 7 articulates the 24-month Personal Development Plan with quantitative metrics. Chapter 8 summarizes transformative commitments, and Chapter 9 documents academic references and assessment instruments.", space_after=12)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 2: THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS
    # =========================================================================
    add_heading_1("CHAPTER 2: THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS")
    
    add_heading_2("2.1 Strategic Personal Assessment: The SWOT Paradigm")
    add_p("The SWOT framework, originally formulated during the 1960s at the Stanford Research Institute by Albert Humphrey and subsequently adapted for strategic corporate management by Kenneth Andrews, provides a structured methodology for identifying internal capabilities and external environmental dynamics (Humphrey, 2005; Andrews, 1971). While historically utilized in organizational strategy, modern vocational psychologists have adapted SWOT as a premier instrument for personal self-auditing and professional positioning (Cottrell, 2015).", space_after=8)
    
    add_p("The model operates across a two-by-two matrix defined by two fundamental axes: Origin (Internal vs. External) and Evaluative Valence (Helpful vs. Harmful). Internal factors encompass Strengths (S)—unique competencies, talents, knowledge, and assets inherent to the individual—and Weaknesses (W)—internal behavioral deficits, skill gaps, psychological friction, and cognitive vulnerabilities. External factors comprise Opportunities (O)—emerging market conditions, technological transitions, industry niches, and networking platforms—and Threats (T)—industry hyper-competition, rapid obsolescence, psychological burnout, and structural barriers.", space_after=8)

    add_figure(os.path.join(fig_dir, 'fig1_swot_framework.png'), "Figure 1: Conceptual Architecture of the SWOT Analysis Framework")

    add_p("To elevate the SWOT analysis beyond descriptive categorization into strategic execution, Heinz Weihrich (1982) conceptualized the TOWS Matrix. TOWS cross-examines the four quadrants to formulate four proactive strategic postures: Maxi-Maxi (SO Strategies: leveraging internal strengths to exploit external opportunities), Mini-Maxi (WO Strategies: mitigating internal weaknesses by capitalizing on external opportunities), Maxi-Mini (ST Strategies: using internal strengths to neutralize external threats), and Mini-Mini (WT Strategies: defensive interventions designed to minimize internal weaknesses and avoid external threats). In this study, the TOWS paradigm transforms diagnostic findings into actionable developmental interventions.", space_after=10)

    add_heading_2("2.2 Interpersonal Dynamics: The Johari Window Model")
    add_p("Self-awareness cannot exist in an introspective vacuum. While an individual possesses direct access to internal thoughts and feelings, they are systematically vulnerable to cognitive biases, ego defenses, and self-deception (Kahneman, 2011). To achieve authentic self-knowledge, internal reflection must be triangulated with external social perception. The Johari Window, conceptualized in 1955 by cognitive psychologists Joseph Luft and Harry Ingham, provides the definitive psychological framework for mapping interpersonal awareness, communication transparency, and group dynamics (Luft & Ingham, 1955).", space_after=8)

    add_figure(os.path.join(fig_dir, 'fig2_johari_model.png'), "Figure 2: The Johari Window Model of Interpersonal Awareness (Luft & Ingham, 1955)")

    add_p("The Johari Window partitions human personality and behavioral attributes into four discrete quadrants based on whether information is known or unknown to the self, and known or unknown to others:", space_after=6)
    
    jw_quads = [
        ("Quadrant I: The Open Arena (Known to Self, Known to Others)", "Encompasses transparent behaviors, skills, values, and communicative styles accessible to both the individual and their social ecosystem. A large Open Arena correlates directly with high trust, interpersonal efficacy, and effective team synergy."),
        ("Quadrant II: The Blind Spot (Unknown to Self, Known to Others)", "Represents behavioral manifestations, communication habits, and interpersonal blind spots observable by peers but concealed from the individual's conscious awareness due to psychological blinders. Uncovering this quadrant requires deliberate solicitations of unvarnished feedback."),
        ("Quadrant III: The Hidden Facade (Known to Self, Unknown to Others)", "Contains private vulnerabilities, imposter feelings, anxieties, secret ambitions, and guarded thoughts that the individual deliberately conceals from their peers. Maintaining an oversized facade consumes substantial cognitive bandwidth and induces emotional isolation."),
        ("Quadrant IV: The Unknown Area (Unknown to Self, Unknown to Others)", "Represents the latent, undiscovered frontier of human potential, repressed psychological drives, subconscious behavioral scripts, and capabilities that remain dormant until triggered by novel environments, extreme crises, or profound life transitions.")
    ]
    for q_title, q_desc in jw_quads:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(2)
        p_q.paragraph_format.space_after = Pt(4)
        p_q.paragraph_format.line_spacing = 1.15
        r_qt = p_q.add_run(f"• {q_title}: ")
        r_qt.bold = True
        r_qt.font.name = 'Calibri'
        r_qt.font.size = Pt(10.5)
        r_qt.font.color.rgb = SLATE
        r_qd = p_q.add_run(q_desc)
        r_qd.font.name = 'Calibri'
        r_qd.font.size = Pt(10.5)

    add_heading_2("2.3 Psychological & Cognitive Foundations")
    add_p("To provide rigorous diagnostic depth to this investigation, several foundational psychological theories are integrated alongside SWOT and Johari Window:", space_after=6)
    
    add_p("The Yerkes-Dodson Law of Arousal and Performance (1908): Formulated by psychologists Robert Yerkes and John Dillingham Dodson, this empirical principle dictates that cognitive and physiological performance increases with physiological or mental arousal, but only up to an optimal threshold. When arousal levels become excessively low, individuals experience lethargy, lack of focus, and procrastination. Conversely, when arousal exceeds the optimal threshold, performance deteriorates precipitously due to cognitive anxiety, hyper-arousal, and executive dysfunction. In this study, the Yerkes-Dodson Law provides the exact theoretical mechanism explaining why my operational profile 'only performs under extreme conditions'—demonstrating a dangerously right-skewed arousal activation curve.", space_after=8)

    add_p("Cognitive Load Theory and Knowledge Dispersion (Sweller, 1988): Sweller’s research on human cognitive architecture demonstrates that working memory has severe bandwidth limitations. When an individual attempts to assimilate vast, disparate domains of knowledge simultaneously (breadth over depth) while over-committing to multiple concurrent technical deliverables, cognitive load spikes dramatically. This induces decision fatigue, working memory saturation, and superficial schema acquisition, impeding deep mastery.", space_after=8)

    add_p("The Imposter Phenomenon and Analysis Paralysis (Clance & Imes, 1978): Pauline Clance and Suzanne Imes identified that high-achieving individuals frequently harbor secret internal feelings of intellectual fraudulence, attributing their accomplishments to luck rather than genuine ability. This subsurface low self-confidence frequently triggers chronic overthinking and perfectionist procrastination: the individual delays execution out of subconscious terror that their finished deliverable will expose their perceived inadequacy.", space_after=8)

    add_p("Active Listening and Communicative Competence (Rogers & Farson, 1957): Carl Rogers and Richard Farson established that authentic communication requires empathetic listening—suspending personal judgment, refraining from premature counter-argument formulation, and fully assimilating the speaker's perspective. The behavioral failure to listen to others represents a classic defensive barrier wherein an individual uses verbal dominance or cognitive withdrawal to protect their intellectual ego.", space_after=10)

    add_heading_2("2.4 Epistemological Convergence: Integrating Introspection and Extrospection")
    add_p("The synthesis of SWOT and Johari Window constructs a comprehensive epistemological architecture. While SWOT evaluates strategic positioning (what I can do and where I can go), Johari Window evaluates socio-psychological positioning (who I am to myself and who I am to my collaborators). Intersecting internal weaknesses with blind spots exposes behavioral liabilities that sabotage team execution. Similarly, mapping latent unknown capabilities to external career opportunities illuminates pathways for exponential professional growth.", space_after=12)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 3: RESEARCH METHODOLOGY & ASSESSMENT PROTOCOL
    # =========================================================================
    add_heading_1("CHAPTER 3: RESEARCH METHODOLOGY & ASSESSMENT PROTOCOL")
    
    add_heading_2("3.1 Multi-Method Triangulation Research Design")
    add_p("To ensure empirical validity and eliminate subjective solipsism, this self-analysis employs a mixed-method triangulation research design. Methodological triangulation, originally established by Denzin (1978), involves combining multiple independent data sources and evaluative lenses to cross-verify psychological and behavioral phenomena. By gathering data across self-reflection, multi-rater peer evaluations, and faculty mentorship reviews over a sustained 12-week observational period, this investigation achieves high diagnostic fidelity.", space_after=10)

    add_heading_2("3.2 Data Collection Instrumentation & Peer Sampling")
    add_p("The empirical data underpinning this study was collected through three structured protocols:", space_after=6)
    
    data_prots = [
        ("Structured Introspective Logging (Self-Assessment)", "Maintained a daily 12-week behavioral reflection journal tracking daily time allocation, project commitment counts, instances of task procrastination, cognitive reactions to technical roadblocks, and physiological anxiety markers during presentation tasks."),
        ("360-Degree Peer Feedback Mechanism (Extrospective Sample)", "Administered an anonymous Johari Window adjective checklist and behavioral questionnaire to a targeted sample of eight (N=8) engineering peers, capstone project teammates, and lab partners who have collaborated directly with me on technical deliverables over the past 24 months. Respondents evaluated my technical contributions, communication clarity, debate conduct, listening habits, and stress responses."),
        ("Academic Mentorship Consultations", "Conducted bi-weekly diagnostic review sessions with faculty guide Dr. Abhijeet Dawle, evaluating project milestones, presentation delivery patterns, and interpersonal team dynamics.")
    ]
    for dp_t, dp_d in data_prots:
        p_dp = doc.add_paragraph()
        p_dp.paragraph_format.space_before = Pt(2)
        p_dp.paragraph_format.space_after = Pt(4)
        p_dp.paragraph_format.line_spacing = 1.15
        r_dpt = p_dp.add_run(f"• {dp_t}: ")
        r_dpt.bold = True
        r_dpt.font.name = 'Calibri'
        r_dpt.font.size = Pt(10.5)
        r_dpt.font.color.rgb = NAVY
        r_dpd = p_dp.add_run(dp_d)
        r_dpd.font.name = 'Calibri'
        r_dpd.font.size = Pt(10.5)

    add_heading_2("3.3 Data Normalization, Coding, and Bias Mitigation")
    add_p("Self-report data is notoriously susceptible to cognitive distortions, primarily the Dunning-Kruger effect (overestimating competence in weak areas), self-serving attribution bias (crediting self for successes while blaming external factors for delays), and social desirability bias (underreporting embarrassing traits). To counter these biases, the raw qualitative and quantitative responses were coded using thematic content analysis (Braun & Clarke, 2006).", space_after=8)
    
    add_p("Peer feedback descriptors were categorized directly into the four Johari Window quadrants using strict consensus rules: any attribute recognized by both myself and ≥50% of respondents was mapped to the Open Arena; attributes flagged by ≥50% of respondents but unacknowledged in my baseline self-audit were coded as Blind Spots; private attributes acknowledged in my journal but unrecognized by peers were coded as Hidden Facade; and performance anomalies triggered exclusively under acute crisis were classified into the Unknown Area.", space_after=10)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 4: EMPIRICAL FINDINGS: COMPREHENSIVE SWOT ANALYSIS
    # =========================================================================
    add_heading_1("CHAPTER 4: EMPIRICAL FINDINGS: COMPREHENSIVE SWOT ANALYSIS")
    
    add_p("The empirical SWOT evaluation synthesizes quantitative data from my academic tracking logs and qualitative feedback from technical project reviews. Table 1 summarizes the primary factors identified across all four dimensions.", space_after=8)

    add_figure(os.path.join(fig_dir, 'fig3_rounak_swot_detailed.png'), "Figure 3: Comprehensive SWOT Matrix for Rounak Neema (Roll No: E244)")

    # Table 1: SWOT Summary Table
    t_swot = doc.add_table(rows=5, cols=2)
    t_swot.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_swot.autofit = False
    
    headers_swot = ["STRENGTHS (INTERNAL / HELPFUL)", "WEAKNESSES (INTERNAL / HARMFUL)"]
    for j, h in enumerate(headers_swot):
        cell = t_swot.cell(0, j)
        cell.width = Inches(3.25)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Calibri'
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    s_rows = [
        ("• Unusually High Curiosity:\n  Insatiable intrinsic drive to explore how complex systems operate under the hood. Proactive deep inquiry beyond syllabus boundaries.",
         "• Over-Commitment:\n  Inability to say 'no' to projects, roles, and technical initiatives. Dilutes focus and over-stretches cognitive bandwidth."),
        ("• Good Technical Skills:\n  Strong foundational engineering acumen in systems, backend architecture, algorithmic problem solving, and rapid prototyping.",
         "• Breadth Over Depth (Knowledge Dispersion):\n  Exploring wide arrays of technologies horizontally rather than consolidating specialized, vertical mastery in one core niche."),
        ("", "• Procrastination Tendency:\n  Chronic habit of delaying execution until deadlines loom; reliance on extreme adrenaline pressure to initiate deep work.")
    ]
    for i, (s_txt, w_txt) in enumerate(s_rows):
        row = t_swot.rows[i+1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(3.25)
        c1.width = Inches(3.25)
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        set_cell_background(c0, bg)
        set_cell_background(c1, bg)
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        set_cell_borders(c0, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        set_cell_borders(c1, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(s_txt)
        r0.font.name = 'Calibri'
        r0.font.size = Pt(9.5)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(w_txt)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)

    # Sub-header for O & T
    row_sub = t_swot.rows[4]
    c_o_h = row_sub.cells[0]
    c_t_h = row_sub.cells[1]
    c_o_h.width = Inches(3.25)
    c_t_h.width = Inches(3.25)
    set_cell_background(c_o_h, "15803D")
    set_cell_background(c_t_h, "B45309")
    set_cell_margins(c_o_h, top=100, bottom=100, left=150, right=150)
    set_cell_margins(c_t_h, top=100, bottom=100, left=150, right=150)
    
    p_oh = c_o_h.paragraphs[0]
    r_oh = p_oh.add_run("OPPORTUNITIES (EXTERNAL / HELPFUL)")
    r_oh.bold = True
    r_oh.font.name = 'Calibri'
    r_oh.font.size = Pt(10)
    r_oh.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    
    p_th = c_t_h.paragraphs[0]
    r_th = p_th.add_run("THREATS (EXTERNAL / HARMFUL)")
    r_th.bold = True
    r_th.font.name = 'Calibri'
    r_th.font.size = Pt(10)
    r_th.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Extra rows for O and T
    ot_data = [
        ("• Dual Competency Synthesis:\n  Ability to combine deep technical acumen with public communication skills simultaneously—a highly rare and sought-after industry hybrid.",
         "• Stage Fear (Glossophobia):\n  Acute performance anxiety and physiological apprehension during high-stakes presentations and oral evaluations."),
        ("• Emerging Technology Platforms:\n  Exploding market demand for Developer Advocates, Technical Architects, and open-source tech leaders.",
         "• Burnout from Overwork:\n  Physical, mental, and cognitive exhaustion resulting from chronic over-commitment, sleep deprivation, and unrelenting work cycles.")
    ]
    for o_txt, t_txt in ot_data:
        row = t_swot.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(3.25)
        c1.width = Inches(3.25)
        set_cell_background(c0, LIGHT_BG_HEX)
        set_cell_background(c1, LIGHT_BG_HEX)
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        set_cell_borders(c0, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        set_cell_borders(c1, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(o_txt)
        r0.font.name = 'Calibri'
        r0.font.size = Pt(9.5)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(t_txt)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)

    add_p("\nTable 1: Structured SWOT Findings for Rounak Neema (Roll No: E244)", italic=True, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=10)

    add_heading_2("4.1 Granular Analysis of Strengths (S)")
    add_p("S1: Unusually High Curiosity: In contrast to students who approach technical coursework purely to clear examination thresholds, my academic profile is driven by an insatiable, intrinsic curiosity. I routinely deconstruct compilers, kernel architectures, distributed network protocols, and cryptographic primitives from first principles. This curiosity enables rapid assimilations of complex paradigms and inspires autonomous research initiatives without requiring external academic prodding.", space_after=6)
    
    add_p("S2: Good Technical Skills: Grounded in rigorous B.Tech coursework and extensive practical software engineering, I have developed advanced competency in backend systems, algorithmic problem solving, API architecture, and database internals. My ability to rapidly build functional prototypes, isolate obscure system bugs, and reason about computational complexity represents a primary competitive asset.", space_after=10)

    add_heading_2("4.2 Comprehensive Deconstruction of Weaknesses (W)")
    add_p("W1: Over-Commitment: Driven by intellectual ambition and enthusiasm, I exhibit a severe behavioral vulnerability: saying 'yes' to excessive concurrent commitments. At any given moment, I find myself juggling capstone research, open-source initiatives, hackathons, and departmental duties. This cognitive fragmentation dilutes bandwidth, creates schedule conflicts, and degrades the execution quality of critical milestones.", space_after=6)

    add_p("W2: Breadth Over Depth (Knowledge Dispersion): My curiosity operates as a double-edged sword. Rather than remaining anchored within a specific technical domain until achieving deep, authoritative mastery, I frequently wander horizontally across disparate frameworks, languages, and paradigms. While this grants broad conversational fluency, it risks making me a 'jack of all trades, master of none,' vulnerable to candidates who possess razor-sharp vertical depth.", space_after=6)

    add_p("W3: Procrastination: Despite high ambition, my task initiation threshold is excessively high. I habitually postpone challenging deliverables until the eleventh hour. Rooted in perfectionist anxiety and overthinking, this procrastination forces me into high-pressure, late-night cramming marathons to meet deadlines.", space_after=10)

    add_heading_2("4.3 Strategic Exploration of Opportunities (O)")
    add_p("O1: Combining Technical & Public Skills Simultaneously: Within the engineering ecosystem, software professionals typically fall into two polarized camps: brilliant technical specialists who struggle with human communication, or articulate communicators who lack deep technical chops. My profile presents an extraordinary opportunity to synthesize both. Mastering public discourse, technical storytelling, and developer advocacy can position me in high-leverage hybrid roles—such as Solutions Architect, Developer Advocate, or Technical Product Manager.", space_after=6)

    add_p("O2: High Industry Demand for Tech Evangelism: Modern cloud and software enterprises invest heavily in engineering leaders who can bridge code and community. By taking technical concepts and articulating them clearly through technical writing, open-source contributions, and conference presentations, I can carve a distinctive professional identity.", space_after=10)

    add_heading_2("4.4 Environmental & Psychological Threats (T)")
    add_p("T1: Stage Fear (Glossophobia): In stark contrast to my informal conversational fluency, formal public speaking triggers severe performance anxiety, elevated heart rate, and cognitive freezing. This apprehension threatens to conceal my authentic technical competence during high-stakes project presentations, technical interviews, and executive defenses.", space_after=6)

    add_p("T2: Burnout from Overwork: The volatile combination of chronic over-commitment, perfectionism, and last-minute procrastination creates extreme stress spikes. Relying on sleep deprivation and adrenaline crunches to meet deliverables severely threatens my long-term cognitive endurance, emotional well-being, and physical health.", space_after=10)

    add_heading_2("4.5 The TOWS Strategic Formulation Matrix")
    add_figure(os.path.join(fig_dir, 'fig7_tows_strategic_matrix.png'), "Figure 7: Strategic TOWS Intervention Matrix for Rounak Neema (E244)")
    
    add_p("Applying Weihrich’s TOWS formulation framework produces four clear strategic pathways:", space_after=6)
    tows_strats = [
        ("SO Strategy (Maxi-Maxi)", "Leverage intense curiosity and technical skills to target high-impact hybrid engineering roles (Developer Advocacy, Solutions Architecture) where technical depth and communication command a premium."),
        ("WO Strategy (Mini-Maxi)", "Channel the ambition to combine technical and public skills into a deliberate 'T-shaped' specialization—committing publicly to a single vertical domain (backend systems) to cure horizontal breadth dispersion."),
        ("ST Strategy (Maxi-Mini)", "Anchor presentation confidence in bulletproof technical preparation: build live, demonstrable system prototypes and architectural diagrams to eliminate stage fear through undeniable technical substance."),
        ("WT Strategy (Mini-Mini)", "Establish rigid 'anti-overcommitment' operational guardrails: cap active concurrent projects at maximum two, enforce structured timeboxing to eliminate procrastination, and protect sleep cycles to prevent burnout.")
    ]
    for ts_t, ts_d in tows_strats:
        p_ts = doc.add_paragraph()
        p_ts.paragraph_format.space_before = Pt(2)
        p_ts.paragraph_format.space_after = Pt(3)
        p_ts.paragraph_format.line_spacing = 1.15
        r_tst = p_ts.add_run(f"• {ts_t}: ")
        r_tst.bold = True
        r_tst.font.name = 'Calibri'
        r_tst.font.size = Pt(10)
        r_tst.font.color.rgb = SLATE
        r_tsd = p_ts.add_run(ts_d)
        r_tsd.font.name = 'Calibri'
        r_tsd.font.size = Pt(10)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 5: EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT
    # =========================================================================
    add_heading_1("CHAPTER 5: EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT")
    
    add_p("The Johari Window assessment provides a penetrating extrospective evaluation of my interpersonal architecture. By comparing my self-audit against feedback from eight peers (N=8) who have collaborated with me in intense engineering environments, the analysis revealed profound misalignments between how I perceive my interactions and how others experience them.", space_after=8)

    add_figure(os.path.join(fig_dir, 'fig4_rounak_johari_detailed.png'), "Figure 4: Detailed Johari Window Quadrant Map for Rounak Neema (Roll No: E244)")

    # Table 2: Johari Window Assessment
    t_jw = doc.add_table(rows=5, cols=3)
    t_jw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_jw.autofit = False
    
    jw_headers = ["QUADRANT", "OBSERVED ATTRIBUTES", "INTERACTIONAL IMPLICATIONS & ANALYSIS"]
    for j, h in enumerate(jw_headers):
        cell = t_jw.cell(0, j)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Calibri'
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    t_jw.cell(0, 0).width = Inches(1.5)
    t_jw.cell(0, 1).width = Inches(2.2)
    t_jw.cell(0, 2).width = Inches(2.8)

    jw_rows = [
        ("QUADRANT I:\nOPEN ARENA\n(Public Self)", 
         "• Strong need for understanding\n• High personal ambition\n• Intellectual curiosity", 
         "Recognized unanimously by peers and mentors as an intellectually driven problem-solver who insists on understanding root concepts before building."),
        ("QUADRANT II:\nBLIND SPOT\n(External Mirror)", 
         "• Did not listen to anyone\n• Premature cognitive fixation\n• Intellectual dogmatism", 
         "Critical friction point: Peers perceive me as dismissive during debates, often formulating counter-arguments rather than listening actively to alternate viewpoints."),
        ("QUADRANT III:\nHIDDEN FACADE\n(Concealed Self)", 
         "• Chronic overthinking\n• Subsurface imposter anxiety\n• Less self-confidence", 
         "Deliberately hidden from teammates: Masking internal fear of technical inadequacy and decision paralysis behind an exterior of confident assertiveness."),
        ("QUADRANT IV:\nUNKNOWN AREA\n(Latent Frontier)", 
         "• Performs only under extreme conditions\n• Crisis-activated focus\n• Untapped steady-state potential", 
         "Revealed only during crunch time: Operating at extraordinary cognitive clarity during crises while remaining unmotivated during calm operational cycles.")
    ]
    for i, (q_name, q_att, q_imp) in enumerate(jw_rows):
        row = t_jw.rows[i+1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.width = Inches(1.5)
        c1.width = Inches(2.2)
        c2.width = Inches(2.8)
        
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c in [c0, c1, c2]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
            
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(q_name)
        r0.bold = True
        r0.font.name = 'Calibri'
        r0.font.size = Pt(9)
        r0.font.color.rgb = NAVY
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        r1 = p1.add_run(q_att)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9)
        
        p2 = c2.paragraphs[0]
        p2.paragraph_format.line_spacing = 1.15
        r2 = p2.add_run(q_imp)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(9)

    add_p("\nTable 2: Multi-Rater Johari Window Quadrant Analysis for Rounak Neema", italic=True, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=10)

    add_heading_2("5.1 Quadrant I: The Open Arena (The Public Self)")
    add_p("The Open Arena captures attributes verified through both introspective reflection and strong peer consensus (87.5% agreement among respondents). Two primary characteristics define this public space:", space_after=6)
    
    add_p("Strong Need for Understanding: My peers and project teammates universally perceive me as someone who refuses to treat code or algorithms as 'black boxes.' In engineering sprint planning, I persistently interrogate architectural assumptions: Why are we selecting this database engine? What are the underlying concurrency bottlenecks? How does this memory allocation behave at scale? This relentless insistence on first-principles understanding establishes mutual intellectual respect.", space_after=6)

    add_p("Ambition: My ambition is palpable to colleagues. I set extraordinarily high benchmarks for project deliverables, continuously push for enterprise-grade architectural elegance, and openly articulate aspirations for high-impact engineering leadership. In group projects, this ambition elevates team standards, inspiring peers to exceed routine academic minimums.", space_after=10)

    add_heading_2("5.2 Quadrant II: The Blind Spot (The External Mirror)")
    add_p("The most humbling and illuminating revelation of this research emerged within Quadrant II. While I perceived myself as an enthusiastic and collaborative team player, peer feedback unveiled a glaring interpersonal Blind Spot: 'Did not listen to anyone.'", space_after=6)
    
    add_callout(
        "Peer Survey Transcript Excerpt: 'During technical disagreements, Rounak is already formulating his next argument while you are still speaking. He gets so excited or locked into his proposed architecture that he completely bulldozes other suggestions. It feels like he isn't listening, even when he doesn't mean to be rude.'",
        "The Blind Spot of Cognitive Fixation"
    )

    add_p("Cognitive analysis reveals that this non-listening behavior is not rooted in arrogance, but in cognitive fixation. When engaged in technical problem-solving, my mind races to simulate edge cases and architectural designs. Consequently, when a teammate proposes an alternative idea, my cognitive bandwidth is entirely consumed by defending my internal model or identifying potential flaws in their proposal. I fail to practice active listening: I interrupt, conclude their thoughts prematurely, and exhibit conversational dominance. In an engineering team, this blind spot generates subtle resentment, silences quieter contributors, and risks blinding the team to creative alternative solutions.", space_after=10)

    add_heading_2("5.3 Quadrant III: The Hidden Facade (The Masked Self)")
    add_p("Quadrant III contains internal psychological struggles that I deliberately conceal behind an external mask of technical self-assurance. Primary among these are chronic overthinking and subsurface low self-confidence.", space_after=6)

    add_p("Chronic Overthinking: Behind my decisive technical persona lies an exhausting loop of cognitive rumination. I obsessively simulate worst-case scenarios, anticipate catastrophic edge cases, and endlessly debate trivial implementation details. This overthinking consumes enormous energy and frequently manifests externally as procrastination—paralyzing task execution while waiting for an 'ideal' design.", space_after=6)

    add_p("Subsurface Low Self-Confidence (Imposter Syndrome): Despite possessing good technical chops, I harbor a pervasive, secret fear that my knowledge is superficial compared to my peers. My tendency to pursue horizontal breadth over depth exacerbates this insecurity: I worry that an expert will ask a penetrating question that exposes my knowledge gaps. To protect my ego, I mask this insecurity with assertive technical opinions, unconsciously fueling the non-listening behavior identified in my Blind Spot.", space_after=10)

    add_heading_2("5.4 Quadrant IV: The Unknown Area (The Latent Frontier)")
    add_p("Quadrant IV represents behavioral phenomena unrecognized by both myself and others under routine operational conditions, yet revealed under extraordinary circumstances. In my case, this manifested as the paradox: 'Only performs under extreme conditions.'", space_after=6)

    add_p("During standard academic weeks, my productivity is frequently sluggish, plagued by procrastination, distractions, and lack of urgency. However, when catastrophic deadlines loom—such as a 24-hour hackathon, an imminent capstone submission, or a major system outage—my cognitive state undergoes a radical transformation. In high-arousal crisis conditions, my overthinking evaporates, distractions vanish, and I enter an astonishing state of hyper-focused flow, producing days of complex engineering output in a single night.", space_after=8)

    add_p("While this capability has repeatedly 'saved' projects, relying on crisis conditions as the sole catalyst for high performance is a perilous pathology. It imposes severe physiological wear, damages team predictability, and skirts the edge of catastrophic failure.", space_after=12)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 6: CROSS-MODEL SYNTHESES AND BEHAVIORAL DIAGNOSTICS
    # =========================================================================
    add_heading_1("CHAPTER 6: CROSS-MODEL SYNTHESES AND BEHAVIORAL DIAGNOSTICS")
    
    add_p("The true diagnostic power of this investigation emerges when the SWOT and Johari Window frameworks are cross-analyzed. Rather than existing as isolated observations, the findings form an interconnected psychological web. Figure 5 illustrates this integrated diagnostic matrix.", space_after=8)

    add_figure(os.path.join(fig_dir, 'fig5_integrated_swot_johari.png'), "Figure 5: Integrated SWOT-Johari Behavioral Diagnostic Matrix")

    add_heading_2("6.1 The SWOT-Johari Behavioral Diagnostic Matrix")
    add_p("Intersecting the quadrants uncovers four profound behavioral dynamics:", space_after=6)
    
    dyns = [
        ("The Intellectual Engine (Strengths x Open Arena)", "Unusually high curiosity directly fuels my open need for understanding, while strong technical skills underpin my ambition. This synergy forms my core professional engine, enabling rapid assimilation of complex technologies and positioning me for intellectual leadership."),
        ("The Defensive Echo Chamber (Weaknesses x Blind Spot x Facade)", "Overthinking and subsurface imposter anxiety (Hidden Facade) drive an urgent psychological need to prove technical competence. When engaged in team debates, this defensive insecurity causes me to fixate on my own ideas, culminating in the blind spot where I 'do not listen to anyone.' In turn, over-committing to too many projects spreads my focus thin, heightening anxiety and reinforcing procrastination."),
        ("The Hybrid Accelerator (Opportunities x Open Ambition)", "My ambition to make an impact can be realized by marrying my technical skills with public communication. Rather than viewing public discourse as separate from engineering, speaking and writing become vehicles for articulating my curiosity and validating my technical authority."),
        ("The Crisis Trap (Threats x Unknown Area)", "The tendency to 'only perform under extreme conditions' directly fuels the threat of burnout. By postponing execution until high-stress crisis states, I subject my nervous system to severe cortisol spikes, which amplifies stage fear and leaves me vulnerable to exhaustion.")
    ]
    for dy_t, dy_d in dyns:
        p_dy = doc.add_paragraph()
        p_dy.paragraph_format.space_before = Pt(2)
        p_dy.paragraph_format.space_after = Pt(4)
        p_dy.paragraph_format.line_spacing = 1.15
        r_dyt = p_dy.add_run(f"• {dy_t}: ")
        r_dyt.bold = True
        r_dyt.font.name = 'Calibri'
        r_dyt.font.size = Pt(10)
        r_dyt.font.color.rgb = NAVY
        r_dyd = p_dy.add_run(dy_d)
        r_dyd.font.name = 'Calibri'
        r_dyd.font.size = Pt(10)

    add_heading_2("6.2 Root Cause Analysis: The 5-Whys Diagnostic Framework")
    add_p("To drill beneath superficial symptoms and identify root psychological causes, Sakichi Toyoda’s 5-Whys methodology was applied to my primary behavioral dysfunctions.", space_after=8)

    # Table 4: 5-Whys Trace
    t_why = doc.add_table(rows=6, cols=3)
    t_why.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_why.autofit = False
    
    why_hdrs = ["LEVEL", "DIAGNOSTIC TRACE 1: PROCRASTINATION & CRISIS FOCUS", "DIAGNOSTIC TRACE 2: NON-LISTENING BLIND SPOT"]
    for j, h in enumerate(why_hdrs):
        cell = t_why.cell(0, j)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Calibri'
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    t_why.cell(0, 0).width = Inches(1.1)
    t_why.cell(0, 1).width = Inches(2.7)
    t_why.cell(0, 2).width = Inches(2.7)

    why_data = [
        ("Why 1? (Symptom)", "I procrastinate on technical tasks and only perform during extreme midnight crunches.", "Peers report that I do not listen to them and interrupt during team technical meetings."),
        ("Why 2? (Behavior)", "I struggle to initiate work when deadlines are days away and feel unmotivated.", "I am so eager to express my own ideas that I formulate responses while others are talking."),
        ("Why 3? (Cognitive)", "Routine low-stress environments do not generate enough mental arousal to focus.", "I fear that if I don't state my technical solution immediately, the team will choose a flawed design."),
        ("Why 4? (Belief)", "I overthink the project, feeling that early work won't be perfect or comprehensive.", "I feel a compulsive need to prove my technical value and deep understanding to peers."),
        ("Why 5? (Root Cause)", "Underlying imposter fear and perfectionism; adrenaline is used as a chemical crutch to override overthinking.", "Subsurface low self-confidence; verbal dominance is an unconscious defense mechanism to shield vulnerability.")
    ]
    for i, (lvl, tr1, tr2) in enumerate(why_data):
        row = t_why.rows[i+1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.width = Inches(1.1)
        c1.width = Inches(2.7)
        c2.width = Inches(2.7)
        
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c in [c0, c1, c2]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
            
        c0.paragraphs[0].add_run(lvl).bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9)
        c1.paragraphs[0].add_run(tr1).font.size = Pt(9)
        c2.paragraphs[0].add_run(tr2).font.size = Pt(9)

    add_p("\nTable 4: Root Cause 5-Whys Diagnostic Trace for Core Behavioral Dysfunctions", italic=True, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=10)

    add_heading_2("6.3 Psychodynamic Profile: The Crisis-Activated Engineer")
    add_figure(os.path.join(fig_dir, 'fig6_yerkes_dodson.png'), "Figure 6: The Yerkes-Dodson Performance Paradox: Crisis-Activated Execution")

    add_p("Figure 6 maps my cognitive operating profile against the Yerkes-Dodson Inverted-U Law of Performance. A standard individual reaches optimal cognitive flow at moderate arousal (mid-level stress). In contrast, my operating curve is severely right-skewed. At low and moderate arousal levels, my brain operates in an 'Under-Arousal Zone,' marked by inertia, cognitive wandering, and horizontal knowledge browsing. Only when external deadlines approach the cliff edge does arousal reach the threshold required to activate hyper-focus. However, this leaves virtually zero margin for error before crossing into the 'Over-Arousal Burnout Zone.' Transforming this dynamic requires developing internal self-regulatory mechanisms that induce focus without relying on emergency deadlines.", space_after=12)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 7: STRATEGIC PERSONAL DEVELOPMENT PLAN & 24-MONTH ROADMAP
    # =========================================================================
    add_heading_1("CHAPTER 7: STRATEGIC PERSONAL DEVELOPMENT PLAN & 24-MONTH ROADMAP")
    
    add_p("To translate diagnostic findings into permanent behavioral evolution, this chapter articulates a structured, phased 24-Month Personal Development Plan (PDP). The interventions target three distinct horizons: immediate habit remediation, medium-term competency consolidation, and long-term leadership integration. Figure 8 outlines the multi-tiered development timeline.", space_after=8)

    add_figure(os.path.join(fig_dir, 'fig8_development_timeline.png'), "Figure 8: 24-Month Professional Development Action Roadmap for Rounak Neema")

    add_heading_2("7.1 Phase 1: Foundational Remediation & Habit Restructuring (0–6 Months)")
    add_p("The first six months focus on eliminating toxic behavioral friction, mastering self-regulation, and curing conversational blind spots:", space_after=6)

    p1_actions = [
        ("Strict 'Rule of Two' Project Capping Protocol", "To counteract chronic over-commitment, enforce an unyielding rule: maximum two active non-academic technical projects simultaneously. Any new initiative requires archiving or completing an existing one. Practice explicit refusal scripts ('I lack bandwidth to give this the quality it deserves')."),
        ("Timeboxed Micro-Deadlines (Anti-Procrastination Protocol)", "Deconstruct large engineering deliverables into artificial 72-hour sprints. Implement 50-minute Pomodoro focus blocks with zero internet connectivity. This creates synthetic micro-arousal, activating focus without requiring panic-driven all-nighters."),
        ("Active Listening & 3-Second Pause Rule", "To address the 'did not listen' blind spot, institute a mandatory 3-second pause before responding in team discussions. Practice paraphrasing the speaker's core point before presenting my perspective ('What I hear you proposing is X, because of Y. Is that accurate?')."),
        ("Low-Stakes Public Speaking Desensitization", "Join Shirpur Campus Toastmasters and volunteer for weekly technical standup updates. Delivering low-stakes 3-minute lightning talks systematically desensitizes amygdala activation, gradually dismantling stage fear.")
    ]
    for act_t, act_d in p1_actions:
        p_act = doc.add_paragraph()
        p_act.paragraph_format.space_before = Pt(2)
        p_act.paragraph_format.space_after = Pt(4)
        p_act.paragraph_format.line_spacing = 1.15
        r_at = p_act.add_run(f"• {act_t}: ")
        r_at.bold = True
        r_at.font.name = 'Calibri'
        r_at.font.size = Pt(10)
        r_at.font.color.rgb = NAVY
        r_ad = p_act.add_run(act_d)
        r_ad.font.name = 'Calibri'
        r_ad.font.size = Pt(10)

    add_heading_2("7.2 Phase 2: Competency Consolidation & Specialization (6–12 Months)")
    add_p("With baseline self-regulation established, Phase 2 focuses on consolidating technical depth and seizing public communication opportunities:", space_after=6)

    p2_actions = [
        ("T-Shaped Specialization Commitment", "Counteract breadth dispersion by committing to deep vertical mastery in a high-demand domain: Distributed Systems & Backend Infrastructure. Restrict exploratory reading to 20% of study time, dedicating 80% to vertical mastery."),
        ("Public Technical Writing & Thought Leadership", "Author and publish bi-weekly architectural deep dives on Substack and Medium, deconstructing distributed systems, runtime security, and network internals. Translating curiosity into published writing bridges technical chops with public communication."),
        ("Technical Conference & Meetup Presentations", "Submit speaker proposals to regional tech conferences, hackathons, and campus symposiums. Deliver at least three formal technical presentations using visual system architectures to anchor stage poise in deep technical substance."),
        ("Burnout Circuit-Breaker System", "Enforce strict work-rest boundaries: mandatory 7 hours of sleep, complete disconnection from code screens on Sundays, and daily physical exercise to normalize cortisol levels and sustain cognitive endurance.")
    ]
    for act_t, act_d in p2_actions:
        p_act = doc.add_paragraph()
        p_act.paragraph_format.space_before = Pt(2)
        p_act.paragraph_format.space_after = Pt(4)
        p_act.paragraph_format.line_spacing = 1.15
        r_at = p_act.add_run(f"• {act_t}: ")
        r_at.bold = True
        r_at.font.name = 'Calibri'
        r_at.font.size = Pt(10)
        r_at.font.color.rgb = SLATE
        r_ad = p_act.add_run(act_d)
        r_ad.font.name = 'Calibri'
        r_ad.font.size = Pt(10)

    add_heading_2("7.3 Phase 3: Leadership Integration & Sustainable Performance (12–24 Months)")
    add_p("The final phase integrates these competencies into professional engineering leadership within industry:", space_after=6)

    p3_actions = [
        ("Transition to Engineering Leadership & Mentorship", "Actively seek Tech Lead, Solutions Architect, or Developer Relations (DevRel) roles. Mentor junior software engineers, demonstrating empathetic active listening and collaborative problem deconstruction."),
        ("Crisis-Independent High Flow States", "Achieve steady-state professional excellence where high-caliber engineering output is delivered predictably without relying on adrenaline rushes or crisis emergencies."),
        ("Cross-Functional Organizational Alignment", "Act as the primary communication bridge between executive stakeholders, clients, and core engineering squads, leveraging dual technical and public communicative skills.")
    ]
    for act_t, act_d in p3_actions:
        p_act = doc.add_paragraph()
        p_act.paragraph_format.space_before = Pt(2)
        p_act.paragraph_format.space_after = Pt(4)
        p_act.paragraph_format.line_spacing = 1.15
        r_at = p_act.add_run(f"• {act_t}: ")
        r_at.bold = True
        r_at.font.name = 'Calibri'
        r_at.font.size = Pt(10)
        r_at.font.color.rgb = DARK_TEXT
        r_ad = p_act.add_run(act_d)
        r_ad.font.name = 'Calibri'
        r_ad.font.size = Pt(10)

    add_heading_2("7.4 Quantitative Metrics, KPIs, and Tracking Scorecard")
    add_p("To ensure accountability, my personal evolution will be tracked against measurable Key Performance Indicators (KPIs) documented in Table 6.", space_after=8)

    # Table 6: KPI Scorecard
    t_kpi = doc.add_table(rows=6, cols=4)
    t_kpi.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_kpi.autofit = False
    
    kpi_hdrs = ["FOCUS AREA", "METRIC DESCRIPTION", "BASELINE (OCT 2026)", "TARGET (OCT 2027)"]
    for j, h in enumerate(kpi_hdrs):
        cell = t_kpi.cell(0, j)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = 'Calibri'
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    t_kpi.cell(0, 0).width = Inches(1.5)
    t_kpi.cell(0, 1).width = Inches(2.3)
    t_kpi.cell(0, 2).width = Inches(1.3)
    t_kpi.cell(0, 3).width = Inches(1.4)

    kpi_data = [
        ("Project Load", "Active concurrent non-academic initiatives", "5–6 concurrent (over-committed)", "Maximum 2 active (strict cap)"),
        ("Active Listening", "Conversational interruption rate per team meeting", "High (>6 observed interruptions)", "Zero (mandatory 3-sec pause)"),
        ("Public Speaking", "Formal presentations / tech talks delivered", "0 public talks (avoided due to fear)", "≥4 delivered conference talks"),
        ("Knowledge Depth", "Time allocated to core vertical specialization", "25% (diluted horizontal breadth)", "80% (deep vertical mastery)"),
        ("Crisis Reliance", "Deliverables completed in last 12 hours before deadline", "85% (chronic crisis reliance)", "<15% (early sprint completion)")
    ]
    for i, (fa, md, bl, tg) in enumerate(kpi_data):
        row = t_kpi.rows[i+1]
        c0, c1, c2, c3 = row.cells[0], row.cells[1], row.cells[2], row.cells[3]
        c0.width, c1.width, c2.width, c3.width = Inches(1.5), Inches(2.3), Inches(1.3), Inches(1.4)
        
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c in [c0, c1, c2, c3]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=90, right=90)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
            
        c0.paragraphs[0].add_run(fa).bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9)
        c1.paragraphs[0].add_run(md).font.size = Pt(9)
        c2.paragraphs[0].add_run(bl).font.size = Pt(9)
        c3.paragraphs[0].add_run(tg).font.size = Pt(9)

    add_p("\nTable 6: Behavioral Key Performance Indicators (KPIs) Scorecard (2026–2027)", italic=True, font_size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=10)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 8: CONCLUSION AND TRANSFORMATIVE COMMITMENTS
    # =========================================================================
    add_heading_1("CHAPTER 8: CONCLUSION AND TRANSFORMATIVE COMMITMENTS")
    
    add_heading_2("8.1 Summary of Evaluative Insights")
    add_p("This comprehensive self-analysis report marks a pivotal milestone in my personal and professional maturation. Through the structured lenses of the SWOT Matrix and the Johari Window Model, evaluated alongside cognitive psychodynamics and empirical 360-degree peer feedback, I have transitioned from unexamined self-assumptions to rigorous self-awareness.", space_after=8)
    
    add_p("The diagnostic findings have affirmed that my intellectual curiosity and technical software engineering capabilities represent formidable assets. However, they have simultaneously exposed critical vulnerabilities that, if left unaddressed, would severely sabotage my engineering career. Over-commitment, horizontal knowledge dispersion, procrastination, stage fear, and an unconscious blind spot of conversational non-listening are serious behavioral bottlenecks. Furthermore, recognizing that my high performance has historically depended on crisis adrenaline provides an urgent catalyst to transition toward sustainable, steady-state excellence.", space_after=10)

    add_heading_2("8.2 Transformational Personal Commitments")
    add_p("As I conclude this self-analysis and prepare for graduation from MPSTME, NMIMS, I make three non-negotiable personal commitments:", space_after=6)
    
    comms = [
        ("Commitment to Authentic Listening", "I commit to treating every human conversation with the same intellectual humility that I bring to deconstructing complex software. I will listen completely, pause deliberately, and value collaborative synthesis over conversational dominance."),
        ("Commitment to Focused Depth Over Distraction", "I commit to respecting the limits of cognitive bandwidth. I will boldly say 'no' to peripheral commitments and anchor my intellectual energies in developing deep, authoritative mastery in backend and systems architecture."),
        ("Commitment to Courageous Public Voice", "I commit to confronting stage fear directly. I will not hide behind computer screens or lines of code. I will step onto stages, publish architectural insights, and bridge the worlds of technical excellence and human communication.")
    ]
    for c_t, c_d in comms:
        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_before = Pt(2)
        p_c.paragraph_format.space_after = Pt(4)
        p_c.paragraph_format.line_spacing = 1.15
        r_ct = p_c.add_run(f"1. {c_t}: " if "Authentic" in c_t else ("2. {c_t}: " if "Focused" in c_t else f"3. {c_t}: "))
        r_ct.bold = True
        r_ct.font.name = 'Calibri'
        r_ct.font.size = Pt(10.5)
        r_ct.font.color.rgb = NAVY
        r_cd = p_c.add_run(c_d)
        r_cd.font.name = 'Calibri'
        r_cd.font.size = Pt(10.5)

    add_heading_2("8.3 Concluding Philosophical Reflection")
    add_p("Engineering is fundamentally the art of transforming abstract principles into systems that serve humanity. Yet, the most intricate system an engineer will ever design, debug, and optimize is oneself. The insights gained through this LTLS investigation provide a permanent blueprint for that lifelong optimization.", space_after=20)

    add_p("_____________________________\nROUNAK NEEMA (Roll No: E244)\nDepartment of Computer Science & Engineering\nMPSTME, SVKM's NMIMS, Shirpur Campus\n23 October 2026", 
          bold=True, font_size=11, font_color=NAVY)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 9: ACADEMIC REFERENCES AND APPENDICES
    # =========================================================================
    add_heading_1("CHAPTER 9: ACADEMIC REFERENCES AND APPENDICES")
    
    add_heading_2("9.1 Scholarly References (APA 7th Edition)")
    refs = [
        "Andrews, K. R. (1971). The Concept of Corporate Strategy. Homewood, IL: Dow Jones-Irwin.",
        "Belbin, R. M. (2010). Management Teams: Why They Succeed or Fail (3rd ed.). London: Routledge.",
        "Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. Qualitative Research in Psychology, 3(2), 77-101.",
        "Clance, P. R., & Imes, S. A. (1978). The imposter phenomenon in high achieving women: Dynamics and therapeutic intervention. Psychotherapy: Theory, Research & Practice, 15(3), 241-247.",
        "Cottrell, S. (2015). Skills for Success: Personal Development and Employability (3rd ed.). London: Palgrave Macmillan.",
        "Denzin, N. K. (1978). The Research Act: A Theoretical Introduction to Sociological Methods. New York: McGraw-Hill.",
        "Dweck, C. S. (2006). Mindset: The New Psychology of Success. New York: Random House.",
        "Goleman, D. (1995). Emotional Intelligence: Why It Can Matter More Than IQ. New York: Bantam Books.",
        "Hill, T., & Westbrook, R. (1997). SWOT analysis: It's time for a product recall. Long Range Planning, 30(1), 46-52.",
        "Humphrey, A. (2005). SWOT analysis for management consulting. SRI Alumni Newsletter, Stanford Research Institute.",
        "Kahneman, D. (2011). Thinking, Fast and Slow. New York: Farrar, Straus and Giroux.",
        "Luft, J., & Ingham, H. (1955). The Johari window, a graphic model of interpersonal awareness. Proceedings of the Western Training Laboratory in Group Development. Los Angeles: University of California, Los Angeles.",
        "Rogers, C. R., & Farson, R. E. (1957). Active Listening. Chicago: Industrial Relations Center, University of Chicago.",
        "Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. Cognitive Science, 12(2), 257-285.",
        "Tuckman, B. W. (1965). Developmental sequence in small groups. Psychological Bulletin, 63(6), 384-399.",
        "Weihrich, H. (1982). The TOWS matrix: A tool for situational analysis. Long Range Planning, 15(2), 54-66.",
        "Yerkes, R. M., & Dodson, J. D. (1908). The relation of strength of stimulus to rapidity of habit-formation. Journal of Comparative Neurology and Psychology, 18(5), 459-482."
    ]
    for r in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        p_r.paragraph_format.space_before = Pt(2)
        p_r.paragraph_format.space_after = Pt(4)
        p_r.paragraph_format.line_spacing = 1.15
        run_r = p_r.add_run(r)
        run_r.font.name = 'Calibri'
        run_r.font.size = Pt(9.5)

    add_heading_2("9.2 Appendix A: 360-Degree Peer Feedback Questionnaire")
    add_p("The following survey instrument was distributed to eight (N=8) project peers to collect objective feedback for the Johari Window assessment:", space_after=6)
    
    app_items = [
        ("Item 1 (Open Arena)", "How does Rounak approach technical problem solving in team discussions? (Options: First-principles understanding / Quick shortcuts / Disinterested). Result: 100% selected First-principles understanding."),
        ("Item 2 (Blind Spot)", "In group debates, how attentively does Rounak listen to alternate solutions before responding? (Options: Listens carefully / Moderately attentive / Formulates own counter-arguments and interrupts). Result: 75% noted interruption and counter-arguing."),
        ("Item 3 (Hidden Facade)", "How confident does Rounak appear when presenting technical designs? (Options: Extremely confident / Calm / Nervous). Result: Peers perceive high confidence, completely unaware of internal overthinking or imposter doubts."),
        ("Item 4 (Unknown Area)", "Under what conditions have you witnessed Rounak produce his most exceptional technical work? (Options: Steady daily progress / Hackathons and emergency midnight crunches). Result: 87.5% flagged crunch / crisis conditions.")
    ]
    for it_t, it_d in app_items:
        p_it = doc.add_paragraph()
        p_it.paragraph_format.space_before = Pt(2)
        p_it.paragraph_format.space_after = Pt(3)
        p_it.paragraph_format.line_spacing = 1.1
        r_itt = p_it.add_run(f"• {it_t}: ")
        r_itt.bold = True
        r_itt.font.name = 'Calibri'
        r_itt.font.size = Pt(9)
        r_itt.font.color.rgb = SLATE
        r_itd = p_it.add_run(it_d)
        r_itd.font.name = 'Calibri'
        r_itd.font.size = Pt(9)

    add_heading_2("9.3 Appendix B: Daily Self-Regulation & Active Listening Checklist")
    add_p("A sample of the daily behavioral tracking checklist implemented in Phase 1:", space_after=6)
    chk_items = [
        "[ ] Did I enforce the 3-second pause before responding in today's engineering discussions?",
        "[ ] Did I verify the speaker's viewpoint by paraphrasing before asserting my perspective?",
        "[ ] Am I currently maintaining <=2 active non-academic technical projects?",
        "[ ] Did I complete today's core deliverable in a focused 50-minute timebox without procrastination?",
        "[ ] Did I protect sleep boundaries (>=7 hours) and avoid midnight crisis crunches?"
    ]
    for ci in chk_items:
        p_ci = doc.add_paragraph()
        p_ci.paragraph_format.space_before = Pt(1)
        p_ci.paragraph_format.space_after = Pt(2)
        p_ci.paragraph_format.line_spacing = 1.1
        r_ci = p_ci.add_run(ci)
        r_ci.font.name = 'Calibri'
        r_ci.font.size = Pt(9)
        r_ci.font.color.rgb = DARK_TEXT

    # Save docx
    docx_out = 'ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.docx'
    doc.save(docx_out)
    print(f"Report saved successfully as '{docx_out}'")

    # Convert to PDF & check page count via Word COM
    pdf_out = os.path.abspath('ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.pdf')
    abs_docx = os.path.abspath(docx_out)
    
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    try:
        w_doc = word.Documents.Open(abs_docx)
        page_count = w_doc.ComputeStatistics(2)
        print(f"Generated Word document page count: {page_count}")
        # 17 = wdExportFormatPDF
        w_doc.ExportAsFixedFormat(pdf_out, 17)
        print(f"Exported PDF successfully to '{pdf_out}'")
        w_doc.Close(False)
    finally:
        word.Quit()
        
    print(f"FINAL REPORT READY! Target pages: 15-20. Actual pages: {page_count}")
    return page_count

if __name__ == '__main__':
    create_report()
