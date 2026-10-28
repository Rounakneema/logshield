import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import win32com.client

def build_humanized_report():
    doc = docx.Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.header_distance = Inches(0.4)
        section.footer_distance = Inches(0.4)

    # Color Palette - clean, quiet academic colors
    NAVY = RGBColor(0x1E, 0x3A, 0x8A)
    SLATE = RGBColor(0x25, 0x63, 0xEB)
    DARK_TEXT = RGBColor(0x1E, 0x29, 0x3B)
    MUTED = RGBColor(0x64, 0x74, 0x8B)
    
    NAVY_HEX = "1E3A8A"
    LIGHT_BG_HEX = "F8FAFC"
    BORDER_HEX = "CBD5E1"

    def set_cell_background(cell, color_hex):
        shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

    def set_cell_margins(cell, top=65, bottom=65, left=90, right=90):
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

    def add_p(text, space_before=0, space_after=3, line_spacing=1.12, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, italic=False, font_size=10.5, font_color=DARK_TEXT):
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

    def add_heading_1(text, page_break=False):
        if page_break:
            doc.add_page_break()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(11)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(13.5)
        run.font.color.rgb = NAVY
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(11.5)
        run.font.color.rgb = SLATE
        return p

    def add_callout(text, label=None):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=90, bottom=90, left=130, right=130)
        set_cell_borders(cell, top=None, bottom=None, left="2563EB", right=None, sz="20")
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.12
        if label:
            r_title = p.add_run(f"{label}\n")
            r_title.bold = True
            r_title.font.name = 'Calibri'
            r_title.font.size = Pt(9.5)
            r_title.font.color.rgb = SLATE
        r = p.add_run(text)
        r.italic = True
        r.font.name = 'Calibri'
        r.font.size = Pt(9.5)
        r.font.color.rgb = DARK_TEXT

    def add_figure(img_path, caption, width=Inches(3.7)):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            run = p.add_run()
            run.add_picture(img_path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(1)
            p_cap.paragraph_format.space_after = Pt(5)
            run_cap = p_cap.add_run(caption)
            run_cap.italic = True
            run_cap.bold = True
            run_cap.font.name = 'Calibri'
            run_cap.font.size = Pt(9)
            run_cap.font.color.rgb = MUTED

    fig_dir = 'ltls_report_rounak_neema/figures'

    # ==================== PAGE 1: TITLE PAGE ====================
    add_p("A COMPREHENSIVE SELF-ANALYSIS FOR PROFESSIONAL DEVELOPMENT", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=16, font_color=NAVY, space_before=16, space_after=6)
    
    add_p("An Individual Report Based on SWOT and Johari Window Analysis", 
          align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, font_size=11, font_color=SLATE, space_after=14)

    logo_path = os.path.join(fig_dir, 'nmims_logo.png')
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(12)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Inches(1.35))

    add_p("Submitted for Course Assessment in\nLEADERSHIP, TEAM AND LIFE SKILLS (LTLS)", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=10.5, font_color=DARK_TEXT, space_after=16)

    add_p("SUBMITTED BY:\nROUNAK NEEMA\nRoll Number: E244\nB.Tech in Computer Science and Engineering\nFinal Year (Academic Year 2026–2027)", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=11, font_color=NAVY, space_after=18)

    add_p("UNDER THE GUIDANCE OF:\nDR. ABHIJEET DAWLE\nAssistant Professor\nDepartment of Applied Sciences & Humanities\nMukesh Patel School of Technology Management & Engineering (MPSTME)\nSVKM's NMIMS, Shirpur Campus", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=10.5, font_color=DARK_TEXT, space_after=18)

    add_p("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nMUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING\nSVKM'S NMIMS (DEEMED TO BE UNIVERSITY)\nSHIRPUR CAMPUS, MAHARASHTRA, INDIA\nOCTOBER 2026", 
          align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size=9.5, font_color=MUTED, space_after=0)

    # ==================== PAGE 2: CERTIFICATE ====================
    add_heading_1("CERTIFICATE OF COMPLETION", page_break=True)
    add_p("This is to certify that the report entitled \"A Comprehensive Self-Analysis for Professional Development: An Individual Report Based on SWOT and Johari Window Analysis\" is an authentic record of independent study carried out by Rounak Neema (Roll Number: E244), final year student of Bachelor of Technology in Computer Science and Engineering at Mukesh Patel School of Technology Management & Engineering (MPSTME), SVKM’s NMIMS, Shirpur Campus.", 
          space_before=10, space_after=10, line_spacing=1.15)
    
    add_p("This project was completed under my supervision for the course Leadership, Team and Life Skills (LTLS) during the 2026–2027 academic year. The candidate collected empirical feedback from engineering peers, evaluated personal strengths and behavioral liabilities, and developed a practical two-year improvement plan that meets course criteria.", 
          space_after=24, line_spacing=1.15)

    table_sig = doc.add_table(rows=2, cols=2)
    table_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sig.autofit = False
    c0, c1 = table_sig.cell(0, 0), table_sig.cell(0, 1)
    c0.width, c1.width = Inches(3.25), Inches(3.25)
    c0.paragraphs[0].add_run("Date: 23 October 2026\nPlace: MPSTME, Shirpur").font.size = Pt(10)
    p_g = c1.paragraphs[0]
    p_g.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_g = p_g.add_run("_____________________________\nDr. Abhijeet Dawle\nFaculty Guide & Assistant Professor\nDept. of Applied Sciences & Humanities\nMPSTME, NMIMS, Shirpur Campus")
    r_g.bold = True
    r_g.font.size = Pt(10)
    
    c2, c3 = table_sig.cell(1, 0), table_sig.cell(1, 1)
    c2.width, c3.width = Inches(3.25), Inches(3.25)
    p_seal = c2.paragraphs[0]
    p_seal.paragraph_format.space_before = Pt(24)
    p_seal.add_run("[ Institutional Seal ]").font.color.rgb = MUTED
    p_hod = c3.paragraphs[0]
    p_hod.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hod.paragraph_format.space_before = Pt(24)
    r_hod = p_hod.add_run("_____________________________\nHead of Department\nDepartment of Computer Science & Engineering\nMPSTME, NMIMS, Shirpur Campus")
    r_hod.bold = True
    r_hod.font.size = Pt(10)

    # ==================== PAGE 3: DECLARATION & ACKNOWLEDGEMENTS ====================
    add_heading_1("CANDIDATE DECLARATION & ACKNOWLEDGEMENTS", page_break=True)
    add_p("I, Rounak Neema (Roll Number E244), final year student of B.Tech Computer Science and Engineering at MPSTME, SVKM's NMIMS, Shirpur, state that this report is my own work. All self-evaluations, peer responses, and reflection notes recorded here reflect my actual academic experience over the past three years.", space_after=6)
    
    decl_points = [
        "The SWOT and Johari Window assessments were compiled using direct feedback from classmates and my own project logs.",
        "The findings regarding my curiosity, technical foundation, over-commitment, knowledge dispersion, procrastination, stage anxiety, and crisis-driven work habits are stated plainly without sugarcoating.",
        "The feedback in the Johari Window, particularly the blind spot of not listening during team meetings, came directly from an anonymous survey of eight project partners.",
        "This submission has not been submitted previously for any other degree or course credit."
    ]
    for dp in decl_points:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_before = Pt(1)
        p_b.paragraph_format.space_after = Pt(2)
        p_b.paragraph_format.line_spacing = 1.1
        r_b = p_b.add_run(dp)
        r_b.font.size = Pt(9.5)

    add_p("Rounak Neema (Roll No: E244) | 23 October 2026", bold=True, font_size=10, font_color=NAVY, space_before=6, space_after=12)

    add_heading_2("Acknowledgements")
    add_p("I want to thank Dr. Abhijeet Dawle for guiding this project and pushing me to look past comfortable answers during our discussions in LTLS. I also thank the Department of Computer Science & Engineering for giving us the technical foundation to build on.", space_after=6)
    add_p("I am especially grateful to the eight classmates and lab partners who took the time to fill out the Johari survey honestly. Pointing out that I interrupt people or stop listening during technical arguments was uncomfortable to hear, but it was the most useful feedback in this whole exercise. Finally, I thank my family for supporting me throughout engineering college.", space_after=10)

    # ==================== PAGE 4: EXECUTIVE SUMMARY ====================
    add_heading_1("EXECUTIVE SUMMARY", page_break=True)
    add_p("This report evaluates my personal and technical habits as a final year computer science student at MPSTME, NMIMS, Shirpur. The goal was to audit how I work, where I run into trouble, and what I need to fix before starting a full-time software engineering job. I used two frameworks taught in LTLS: SWOT analysis to review internal strengths and external conditions, and the Johari Window to compare how I see myself against how my project partners see me.", space_after=6)
    
    add_p("The SWOT analysis confirmed two main strengths: strong technical skills in backend programming and an unusually high curiosity that pushes me to find out how compilers, databases, and low-level tools work. At the same time, it highlighted three persistent weaknesses: saying yes to too many projects at once, spreading my study time across too many different technologies instead of getting really good at one, and procrastinating until the last minute. The biggest opportunity is combining technical ability with public communication, which is rare among engineers. The main threats are stage fear during formal presentations and the burnout that follows repeated all-nighters.", space_after=6)

    add_p("The Johari Window brought external feedback into the picture. In the open area, classmates recognized that I care about understanding systems thoroughly and that I have clear ambitions. But the survey also exposed an uncomfortable blind spot: several teammates noted that I often do not listen during technical debates because I get locked into my own ideas and interrupt. In the hidden area, I tend to mask self-doubt and overthinking by sounding confident. Under the unknown quadrant, I discovered a pattern of only working at full focus under extreme crunch conditions, waiting for an adrenaline rush rather than making steady progress.", space_after=6)

    add_p("To fix these issues, I put together a practical 24-month plan. In the first six months, I will limit myself to two active projects at a time, practice a 3-second pause before replying in group meetings, and start speaking regularly at the campus Toastmasters club. Over the following 18 months, I will narrow my technical focus to distributed backend systems, start publishing technical explanations online, and build consistent daily work habits so I no longer rely on last-minute panic.", space_after=10)

    # ==================== PAGE 5: TABLE OF CONTENTS ====================
    add_heading_1("TABLE OF CONTENTS & LISTINGS", page_break=True)
    toc_data = [
        ("CERTIFICATE OF COMPLETION", "2"),
        ("CANDIDATE DECLARATION & ACKNOWLEDGEMENTS", "3"),
        ("EXECUTIVE SUMMARY", "4"),
        ("TABLE OF CONTENTS & LISTINGS", "5"),
        ("1. INTRODUCTION AND CONTEXTUAL BACKGROUND", "6"),
        ("   1.1 The Role of Interpersonal Skills in Engineering Work", "6"),
        ("   1.2 Course Background: Leadership, Team and Life Skills (LTLS)", "6"),
        ("   1.3 Personal Context (Rounak Neema, B.Tech CSE, E244)", "6"),
        ("   1.4 Project Objectives and Scope", "6"),
        ("2. THEORETICAL FRAMEWORKS", "7"),
        ("   2.1 SWOT and TOWS Analysis", "7"),
        ("   2.2 The Johari Window Model", "8"),
        ("   2.3 Supporting Theories: Yerkes-Dodson and Cognitive Load", "8"),
        ("3. METHODOLOGY AND DATA COLLECTION", "9"),
        ("   3.1 Triangulation Approach", "9"),
        ("   3.2 Data Sources: Personal Logs and Peer Surveys", "9"),
        ("   3.3 Handling Biases and Normalizing Responses", "9"),
        ("4. SWOT FINDINGS", "10"),
        ("   4.1 Strengths: Curiosity and Technical Foundation", "10"),
        ("   4.2 Weaknesses: Over-commitment, Dispersion, and Procrastination", "11"),
        ("   4.3 Opportunities: Blending Code with Public Communication", "11"),
        ("   4.4 Threats: Stage Anxiety and Burnout", "11"),
        ("   4.5 TOWS Action Strategies", "11"),
        ("5. JOHARI WINDOW FINDINGS", "12"),
        ("   5.1 Open Arena: Drive for Understanding and Ambition", "12"),
        ("   5.2 Blind Spot: The Habit of Not Listening", "13"),
        ("   5.3 Hidden Facade: Overthinking and Imposter Feelings", "13"),
        ("   5.4 Unknown Area: The Extreme-Condition Performance Loop", "13"),
        ("6. SYNTHESIS AND ROOT CAUSE ANALYSIS", "14"),
        ("   6.1 Connecting SWOT and Johari Window Findings", "14"),
        ("   6.2 Five-Whys Breakdown of Primary Bottlenecks", "14"),
        ("   6.3 The Arousal Curve and Panic-Driven Work", "15"),
        ("7. TWO-YEAR PERSONAL DEVELOPMENT PLAN", "16"),
        ("   7.1 Phase 1: Fixing Immediate Habits (0 to 6 Months)", "16"),
        ("   7.2 Phase 2: Technical Focus and Public Speaking (6 to 12 Months)", "16"),
        ("   7.3 Phase 3: Long-term Consistency and Leadership (12 to 24 Months)", "16"),
        ("   7.4 Tracking Progress and Measurable Targets", "17"),
        ("8. CONCLUSION AND COMMITMENTS", "17"),
        ("9. REFERENCES AND SURVEY DETAILS", "18")
    ]
    t_toc = doc.add_table(rows=len(toc_data), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    for i, (title, page) in enumerate(toc_data):
        row = t_toc.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(5.6), Inches(0.9)
        set_cell_borders(c0, top=None, bottom=None, left=None, right=None)
        set_cell_borders(c1, top=None, bottom=None, left=None, right=None)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before, p0.paragraph_format.space_after = Pt(1), Pt(1)
        r0 = p0.add_run(title)
        r0.font.size = Pt(8.5)
        if title.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "CERT", "CAND", "EXEC")):
            r0.bold = True
            r0.font.color.rgb = NAVY
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before, p1.paragraph_format.space_after = Pt(1), Pt(1)
        r1 = p1.add_run(page)
        r1.font.size = Pt(8.5)
        r1.bold = True

    # ==================== CHAPTER 1 ====================
    add_heading_1("CHAPTER 1: INTRODUCTION AND CONTEXTUAL BACKGROUND", page_break=True)
    add_heading_2("1.1 The Role of Interpersonal Skills in Engineering Work")
    add_p("Engineering degrees place heavy emphasis on mathematics, algorithms, system architecture, and code syntax. For the first three years of college, academic success mostly depends on whether code compiles, test cases pass, and semester exams go well. But real engineering projects in software teams do not work that way. Once code leaves an isolated local environment, software engineers spend as much time reviewing pull requests, debating system designs, estimating timelines, and explaining architecture to product managers as they do typing syntax.")
    add_p("When engineers struggle with collaboration, projects slow down. An engineer who knows how to optimize a database query but cannot explain their logic clearly, or who gets defensive when teammates suggest alternatives, becomes a bottleneck. The literature on software teams shows that technical capability must be matched by self-awareness, active listening, and workload management (Goleman, 1995; Cottrell, 2015). Taking time to review personal work habits before graduating is therefore practical preparation for professional life.")

    add_heading_2("1.2 Course Background: Leadership, Team and Life Skills (LTLS)")
    add_p("At MPSTME, NMIMS, the Leadership, Team and Life Skills (LTLS) course offered by the Department of Applied Sciences & Humanities addresses this gap. Rather than lecturing on abstract management theories, the curriculum requires students to examine their actual behavior in team settings. We use self-assessment models, peer reviews, and reflection journals to uncover personal blind spots. This report serves as my individual submission for the course, applying these tools to my own academic and project experience.")

    add_heading_2("1.3 Personal Context (Rounak Neema, B.Tech CSE, E244)")
    add_p("I am in my final year of B.Tech in Computer Science and Engineering at the Shirpur campus. Over seven semesters, my main technical interests have centered on backend systems, networking, and low-level code. I genuinely enjoy figuring out how systems work under the hood. However, my project work has also been marked by recurring problems: taking on more work than I can handle, jumping between too many new frameworks without finishing deep implementations, and delaying tasks until an approaching deadline forces me to stay up all night.")
    add_p("In team discussions, I have also noticed friction with classmates when we disagree on technical decisions. To prepare for transitioning into the software industry, I need a clear-eyed review of why these patterns happen and what habits I must change.")

    add_heading_2("1.4 Project Objectives and Scope")
    add_p("This project focuses on four specific goals: (1) Conduct a realistic SWOT analysis to evaluate my technical skills and work habits; (2) Collect anonymous peer feedback using the Johari Window to see how teammates actually view my communication; (3) Examine why I rely on last-minute crunch pressure to work, using the Yerkes-Dodson arousal model; and (4) Build a concrete two-year development plan with specific targets to fix these weaknesses.")

    # ==================== CHAPTER 2 ====================
    add_heading_1("CHAPTER 2: THEORETICAL FOUNDATIONS AND CONCEPTUAL FRAMEWORKS", page_break=False)
    add_heading_2("2.1 Strategic Personal Assessment: The SWOT Paradigm")
    add_p("The SWOT framework was developed in the 1960s at the Stanford Research Institute and later adapted by Kenneth Andrews (1971) for corporate strategy. Over the last three decades, personal development researchers have adapted it for individual self-audits (Cottrell, 2015). The framework splits attributes into internal factors (strengths and weaknesses) and external factors (opportunities and threats).")
    
    add_figure(os.path.join(fig_dir, 'fig1_swot_framework.png'), "Figure 1: Conceptual Architecture of the SWOT Analysis Framework")

    add_p("To make a SWOT analysis actionable rather than just a list of traits, Heinz Weihrich (1982) introduced the TOWS matrix. TOWS pairs quadrants to build practical responses: using strengths to pursue opportunities (SO), fixing weaknesses by taking up opportunities (WO), using strengths to deflect threats (ST), and building defensive guardrails to keep weaknesses from triggering threats (WT).")

    add_heading_2("2.2 Interpersonal Dynamics: The Johari Window Model")
    add_p("Introspection alone is not enough to understand how we operate. Cognitive psychologists have documented that people routinely misjudge their own communication habits due to ego preservation and confirmation bias (Kahneman, 2011). Joseph Luft and Harry Ingham developed the Johari Window in 1955 to solve this problem by comparing self-perception with peer feedback.")

    add_figure(os.path.join(fig_dir, 'fig2_johari_model.png'), "Figure 2: The Johari Window Model of Interpersonal Awareness (Luft & Ingham, 1955)")

    add_p("The model creates four quadrants: the Open Arena (traits known to both self and peers), the Blind Spot (habits visible to teammates but unnoticed by oneself), the Hidden Facade (private doubts and anxieties kept secret from colleagues), and the Unknown Area (behaviors that only appear during unexpected crises or novel conditions).")

    add_heading_2("2.3 Supporting Theories: Yerkes-Dodson and Cognitive Load")
    add_p("Two additional psychological models help explain my specific work patterns:\n\nThe Yerkes-Dodson Law (1908): Robert Yerkes and John Dodson showed that cognitive performance follows an inverted-U curve relative to mental arousal or stress. Low arousal leads to boredom, lack of focus, and task delay. As urgency rises, focus improves until reaching an optimal zone. If stress gets too high, performance crashes into anxiety and panic. In my case, this curve is shifted far to the right: routine tasks produce almost no focus, and I depend on high-pressure deadlines to reach full productivity.\n\nCognitive Load Theory (Sweller, 1988): John Sweller demonstrated that human working memory has limited capacity. Trying to learn multiple unrelated programming languages and frameworks at the same time saturates mental bandwidth, preventing deep understanding and reinforcing superficial knowledge.")

    # ==================== CHAPTER 3 ====================
    add_heading_1("CHAPTER 3: RESEARCH METHODOLOGY & ASSESSMENT PROTOCOL", page_break=True)
    add_heading_2("3.1 Triangulation Approach")
    add_p("To make sure this report was based on real evidence rather than flattering assumptions, I used a mixed-method triangulation design (Denzin, 1978). I gathered data from three independent angles over a twelve-week period: my own daily project logs, an anonymous peer questionnaire, and feedback from my faculty mentor.")

    add_heading_2("3.2 Data Collection Instrumentation & Peer Sampling")
    add_p("The information was collected through three specific methods: (1) Daily Activity Journal: A 12-week log tracking hours worked, number of active side projects, instances of putting off tasks, and physical stress markers before presentations; (2) Anonymous Peer Survey: A Johari Window questionnaire sent to eight (N=8) classmates and lab teammates who worked closely with me on group coding assignments and college projects over the last two years; and (3) Faculty Guidance: Regular review sessions with Dr. Abhijeet Dawle to evaluate my presentation delivery and team interactions.")

    add_heading_2("3.3 Data Normalization, Coding, and Bias Mitigation")
    add_p("Self-evaluations are vulnerable to the Dunning-Kruger effect, where people overestimate their skills, and attribution bias, where people blame outside factors for their delays. To filter out these tendencies, peer responses were classified into Johari quadrants using simple majority rules: attributes checked by both myself and four or more peers were placed in the Open Arena; attributes marked by four or more peers that I had not noted myself were tagged as Blind Spots; traits I noted in private logs that peers did not mention went into the Hidden Facade; and performance quirks that only appeared during hackathons or emergency deadlines were assigned to the Unknown Area.")

    # ==================== CHAPTER 4 ====================
    add_heading_1("CHAPTER 4: EMPIRICAL FINDINGS: COMPREHENSIVE SWOT ANALYSIS", page_break=True)
    add_p("Table 1 summarizes the findings from my self-assessment logs and project evaluations, structured into internal capabilities and external conditions. Figure 3 illustrates the full matrix.")

    add_figure(os.path.join(fig_dir, 'fig3_rounak_swot_detailed.png'), "Figure 3: Comprehensive SWOT Matrix for Rounak Neema (Roll No: E244)")

    # Table 1: SWOT Summary Table
    t_swot = doc.add_table(rows=3, cols=2)
    t_swot.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_swot.autofit = False
    headers_swot = ["STRENGTHS & OPPORTUNITIES (HELPFUL)", "WEAKNESSES & THREATS (HARMFUL)"]
    for j, h in enumerate(headers_swot):
        cell = t_swot.cell(0, j)
        cell.width = Inches(3.25)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=65, bottom=65, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    swot_t_data = [
        ("STRENGTHS (INTERNAL):\n- High curiosity: drive to deconstruct software tools, compilers, and protocols from first principles.\n- Strong technical foundation: comfortable with systems programming, backend logic, and quick prototype development.",
         "WEAKNESSES (INTERNAL):\n- Over-commitment: saying yes to too many projects; spreading focus thin across multiple responsibilities.\n- Breadth over depth: exploring wide technologies horizontally without building deep mastery in one core stack.\n- Procrastination: delaying execution until an urgent deadline forces action."),
        ("OPPORTUNITIES (EXTERNAL):\n- Dual skill synthesis: combining software engineering ability with public speaking and technical writing.\n- Growing industry demand: tech companies value engineers who can explain architecture to teams and users.",
         "THREATS (EXTERNAL):\n- Stage fear: anxiety and physical discomfort during formal presentations and oral vivas.\n- Burnout from overwork: physical and mental fatigue caused by piling up deadlines and staying up late to finish them.")
    ]
    for i, (col1, col2) in enumerate(swot_t_data):
        row = t_swot.rows[i+1]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(3.25), Inches(3.25)
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c, txt in [(c0, col1), (c1, col2)]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=55, bottom=55, left=85, right=85)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.12
            p.add_run(txt).font.size = Pt(9)

    add_p("Table 1: Structured SWOT Findings for Rounak Neema (Roll No: E244)", italic=True, font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=8)

    add_heading_2("4.1 Granular Analysis of Strengths (S)")
    add_p("High Curiosity: My main academic asset is that I do not like treating code as a black box. When studying operating systems or databases, I usually write small test programs to see how context switching or file locks actually work. This curiosity helps me pick up new concepts quickly without waiting for teacher assignments.")
    add_p("Good Technical Skills: Across lab practicals and college projects, I have developed solid coding skills in backend logic, API design, and debugging. I can prototype working applications quickly and reason through edge cases when writing code.")

    add_heading_2("4.2 Comprehensive Deconstruction of Weaknesses (W)")
    add_p("Over-Commitment: Because I get enthusiastic about interesting ideas, I regularly take on too many projects. During the fifth and sixth semesters, I agreed to work on two research ideas, a hackathon submission, and an open-source tool while taking regular classes. The result was missed deadlines and mediocre code quality across all of them.")
    add_p("Breadth Over Depth: My curiosity often works against me. Instead of staying focused on mastering distributed backend architecture in depth, I get sidetracked trying out frontend frameworks, mobile app stacks, or compiler tools. I end up knowing a little about everything, but lack deep specialization.")
    add_p("Procrastination: I have a high resistance to starting projects early. I often spend days reading documentation or thinking about the cleanest possible architecture, only to leave actual coding to the final two days before submission.")

    add_heading_2("4.3 Strategic Exploration of Opportunities (O)")
    add_p("Dual Competency Synthesis: Most computer science students prefer either coding alone or handling non-technical project coordination. Being able to write backend code and also speak comfortably in front of an audience is a strong combination. It opens doors to roles like Solutions Architect, Developer Advocate, and technical lead positions.")
    add_p("Public Technical Communication: Tech companies actively hire engineers who can write clear technical guides, explain system trade-offs to clients, and speak at developer meetups. Turning my curiosity into public technical articles is a direct way to build authority.")

    add_heading_2("4.4 Environmental & Psychological Threats (T)")
    add_p("Stage Fear: While I have no trouble speaking in informal discussions, standing up in front of an evaluation panel or a large audience makes me nervous. My heart rate spikes, my speech speeds up, and I struggle to structure my points clearly.")
    add_p("Burnout from Overwork: Combining over-commitment with last-minute procrastination creates acute stress spikes. Working through the night to finish deliverables leaves me mentally drained for days, disrupting sleep and study routines.")

    add_heading_2("4.5 The TOWS Strategic Formulation Matrix")
    add_figure(os.path.join(fig_dir, 'fig7_tows_strategic_matrix.png'), "Figure 7: Strategic TOWS Intervention Matrix for Rounak Neema (E244)")
    add_p("By pairing SWOT quadrants, I built four concrete strategies: (1) SO Strategy: Use my technical background to write in-depth technical blogs and speak at local developer meetups; (2) WO Strategy: Pick one core vertical (distributed backend systems) and commit to it publicly to stop jumping between disparate frameworks; (3) ST Strategy: Overcome stage anxiety by relying on live system demos and clear architecture diagrams during presentations; and (4) WT Strategy: Set a strict rule of maximum two active projects at any time to prevent cramming and burnout.")

    # ==================== CHAPTER 5 ====================
    add_heading_1("CHAPTER 5: EMPIRICAL FINDINGS: IN-DEPTH JOHARI WINDOW ASSESSMENT", page_break=False)
    add_p("To test how my self-perception matches reality, I gathered feedback from eight peers who have worked with me on technical projects. Figure 4 maps the quadrants, and Table 2 details the findings.")

    add_figure(os.path.join(fig_dir, 'fig4_rounak_johari_detailed.png'), "Figure 4: Detailed Johari Window Quadrant Map for Rounak Neema (Roll No: E244)")

    # Table 2: Johari Window Table
    t_jw = doc.add_table(rows=5, cols=3)
    t_jw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_jw.autofit = False
    jw_headers = ["QUADRANT", "OBSERVED ATTRIBUTES", "INTERACTIONAL IMPLICATIONS & ANALYSIS"]
    for j, h in enumerate(jw_headers):
        cell = t_jw.cell(0, j)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=65, bottom=65, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    t_jw.cell(0, 0).width = Inches(1.4)
    t_jw.cell(0, 1).width = Inches(2.2)
    t_jw.cell(0, 2).width = Inches(2.9)

    jw_rows = [
        ("QUADRANT I:\nOPEN ARENA\n(Public Self)", "• Strong need for understanding\n• High personal ambition\n• Intellectual curiosity", "Teammates and mentors agree that I care about understanding underlying system logic and set ambitious benchmarks for project deliverables."),
        ("QUADRANT II:\nBLIND SPOT\n(External Mirror)", "• Did not listen to anyone\n• Premature cognitive fixation\n• Conversational dominance", "The most critical feedback: peers noted that during technical disagreements, I tend to formulate counter-arguments instead of listening, interrupting teammates and dismissing alternatives."),
        ("QUADRANT III:\nHIDDEN FACADE\n(Concealed Self)", "• Chronic overthinking\n• Subsurface imposter anxiety\n• Less self-confidence", "Things I keep hidden: worrying that my technical knowledge is too shallow, overthinking decisions, and covering up uncertainty by sounding more confident than I feel."),
        ("QUADRANT IV:\nUNKNOWN AREA\n(Latent Frontier)", "• Performs only under extreme conditions\n• Crisis-activated focus\n• Untapped steady-state potential", "A pattern revealed during tight deadlines: I show peak focus and produce my best work during emergency crunches, but struggle with motivation during calm, routine weeks.")
    ]
    for i, (q_name, q_att, q_imp) in enumerate(jw_rows):
        row = t_jw.rows[i+1]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width, c1.width, c2.width = Inches(1.4), Inches(2.2), Inches(2.9)
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c in [c0, c1, c2]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=55, bottom=55, left=75, right=75)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        c0.paragraphs[0].add_run(q_name).bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(8.5)
        c1.paragraphs[0].add_run(q_att).font.size = Pt(8.5)
        c2.paragraphs[0].add_run(q_imp).font.size = Pt(8.5)

    add_p("Table 2: Multi-Rater Johari Window Quadrant Analysis for Rounak Neema", italic=True, font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=8)

    add_heading_2("5.1 Quadrant I: The Open Arena (The Public Self)")
    add_p("Both my self-audit and 87% of survey respondents agreed on two clear qualities: a strong drive to understand systems and visible personal ambition. My project partners noted that I consistently question why we pick specific technologies, how memory is allocated, and what the bottlenecks are. They also noted that I push teams to build substantial projects rather than doing the bare minimum for course credit.")

    add_heading_2("5.2 Quadrant II: The Blind Spot (The External Mirror)")
    add_p("The hardest feedback to read was in the Blind Spot: six out of eight classmates noted that I often 'did not listen to anyone' during technical discussions.")
    
    add_callout("Peer Feedback Note: \"Rounak gets so wrapped up in his own system design that he stops listening to the rest of the group. Even if someone else has a simpler fix, he talks over them to explain his architecture. He isn't trying to be rude, but it feels like he has already decided what we should do.\"", "Peer Observation on Conversational Habits")

    add_p("Looking at this honestly, it happens because my mind jumps ahead to technical trade-offs while someone is still talking. Instead of absorbing their suggestion, I start constructing reasons why it might fail or planning what I will say next. This habit makes teammates feel ignored and cuts off useful alternative ideas.")

    add_heading_2("5.3 Quadrant III: The Hidden Facade (The Masked Self)")
    add_p("Behind my confident front, I spend a lot of energy second-guessing decisions. Because I have explored many technologies without mastering any single one deeply, I worry about being caught out by an expert question during project reviews. To hide that insecurity, I double down on asserting my ideas in group meetings. This creates a vicious cycle: overthinking fuels insecurity, which fuels conversational assertiveness, which leads to not listening to teammates.")

    add_heading_2("5.4 Quadrant IV: The Unknown Area (The Latent Frontier)")
    add_p("Quadrant IV revealed a clear habit: I perform best when backed against a wall. During regular semesters, low urgency makes it hard for me to focus for long stretches. But in 24-hour hackathons or the night before a project deadline, distractions disappear and I write clean, complex code quickly. Relying on emergency adrenaline to get things done is unsustainable; it damages health and makes project delivery unpredictable for teammates.")

    # ==================== CHAPTER 6 ====================
    add_heading_1("CHAPTER 6: CROSS-MODEL SYNTHESES AND BEHAVIORAL DIAGNOSTICS", page_break=True)
    add_p("When SWOT and Johari Window findings are examined together, they reveal how different habits feed into each other. Figure 5 illustrates this diagnostic matrix, and Figure 6 maps the operating arousal curve.")

    add_figure(os.path.join(fig_dir, 'fig5_integrated_swot_johari.png'), "Figure 5: Integrated SWOT-Johari Behavioral Diagnostic Matrix")

    add_heading_2("6.1 The SWOT-Johari Behavioral Diagnostic Matrix")
    add_p("Four clear behavioral links stand out across the models: (1) Core Strengths in the Open: High curiosity and solid coding skills drive my visible ambition and help me learn new systems; (2) The Defensive Loop: Subsurface imposter doubts (Hidden Facade) make me defensive in team debates, producing the blind spot where I fail to listen, while over-commitment spreads my attention thin; (3) Career Leverage: Combining technical ability with public communication can turn personal ambition into recognized professional credibility; and (4) The Crisis Risk: Depending on extreme crunch conditions to focus exposes me directly to burnout and worsens presentation anxiety.")

    add_heading_2("6.2 Root Cause Analysis: The 5-Whys Diagnostic Framework")
    add_p("To get to the root of these issues, I applied Sakichi Toyoda's five-whys method to my two biggest problems: procrastinating until crunch time, and not listening in team meetings.")

    t_why = doc.add_table(rows=6, cols=3)
    t_why.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_why.autofit = False
    why_hdrs = ["LEVEL", "TRACE 1: PROCRASTINATION & CRISIS FOCUS", "TRACE 2: NON-LISTENING BLIND SPOT"]
    for j, h in enumerate(why_hdrs):
        cell = t_why.cell(0, j)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=65, bottom=65, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    t_why.cell(0, 0).width = Inches(1.1)
    t_why.cell(0, 1).width = Inches(2.7)
    t_why.cell(0, 2).width = Inches(2.7)

    why_data = [
        ("Why 1? (Symptom)", "I put off major technical tasks and only work with full focus during late-night crunches.", "Classmates report that I interrupt people and don't listen during team meetings."),
        ("Why 2? (Behavior)", "I struggle to get started when deadlines are days away and feel unmotivated.", "I get impatient to explain my solution while someone else is speaking."),
        ("Why 3? (Cognitive)", "Low-stress daily routines do not create enough mental pressure to force focus.", "I worry that if we don't pick my design, the team will run into architectural bugs."),
        ("Why 4? (Belief)", "I overthink the project, feeling that early drafts won't be good enough.", "I feel an internal need to prove my technical credibility to my peers."),
        ("Why 5? (Root Cause)", "Underlying imposter fear and perfectionism; I use adrenaline as a crutch to get past overthinking.", "Masking self-doubt; dominating conversations is an unconscious shield to avoid looking unprepared.")
    ]
    for i, (lvl, tr1, tr2) in enumerate(why_data):
        row = t_why.rows[i+1]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width, c1.width, c2.width = Inches(1.1), Inches(2.7), Inches(2.7)
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c in [c0, c1, c2]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=45, bottom=45, left=65, right=65)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        c0.paragraphs[0].add_run(lvl).bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(8.5)
        c1.paragraphs[0].add_run(tr1).font.size = Pt(8.5)
        c2.paragraphs[0].add_run(tr2).font.size = Pt(8.5)

    add_p("Table 4: Root Cause 5-Whys Diagnostic Trace for Core Behavioral Dysfunctions", italic=True, font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=8)

    add_heading_2("6.3 Psychodynamic Profile: The Crisis-Activated Engineer")
    add_figure(os.path.join(fig_dir, 'fig6_yerkes_dodson.png'), "Figure 6: The Yerkes-Dodson Performance Paradox: Crisis-Activated Execution")
    add_p("Figure 6 shows how my arousal curve differs from standard work habits. Under normal workloads, I sit in an under-arousal zone where procrastination thrives. Only when deadlines become emergencies does arousal rise high enough to unlock deep concentration. But operating this close to the edge leaves no room for unexpected setbacks and leads straight into burnout. The goal of my action plan is to generate steady daily focus without waiting for emergencies.")

    # ==================== CHAPTER 7 ====================
    add_heading_1("CHAPTER 7: STRATEGIC PERSONAL DEVELOPMENT PLAN & 24-MONTH ROADMAP", page_break=True)
    add_p("To address these findings, I structured a two-year personal plan across three sequential phases. Figure 8 outlines the timeline, and Table 6 tracks measurable goals.")

    add_figure(os.path.join(fig_dir, 'fig8_development_timeline.png'), "Figure 8: 24-Month Professional Development Action Roadmap for Rounak Neema")

    add_heading_2("7.1 Phase 1: Foundational Remediation & Habit Restructuring (0–6 Months)")
    add_p("The first six months focus on immediate habit changes: (1) Rule of Two: Limit myself to at most two active technical side projects at any time, learning to decline requests when my plate is full; (2) Timeboxed Focus Blocks: Break large coding tasks into artificial 72-hour deadlines with 50-minute Pomodoro blocks, turning off internet distractions to build focus early; (3) Three-Second Listening Rule: Count to three before answering in group meetings, and summarize what the other person said before offering my opinion; and (4) Toastmasters Practice: Attend weekly campus Toastmasters meetings and give short 3-minute talks to reduce stage anxiety through regular exposure.")

    add_heading_2("7.2 Phase 2: Competency Consolidation & Specialization (6–12 Months)")
    add_p("The second phase builds depth and public communication: (1) Vertical Focus: Spend 80% of technical study time on distributed backend architecture, limiting exploration of other stacks to 20%; (2) Technical Writing: Write and publish bi-weekly technical explainers on Substack and Medium, explaining system internals clearly to practice public communication; (3) Conference Talks: Submit proposals to regional student tech conferences, using clear architecture diagrams and working demos to stay confident; and (4) Health Guardrails: Keep regular sleep hours (at least 7 hours), take Sundays off from coding screens, and exercise daily to prevent burnout.")

    add_heading_2("7.3 Phase 3: Leadership Integration & Sustainable Performance (12–24 Months)")
    add_p("The final phase prepares for professional engineering roles: (1) Technical Leadership: Move into roles like Solutions Architect or Developer Advocate where both coding and communication are required, mentoring younger engineers patiently; (2) Steady Productivity: Deliver consistent software work on regular sprint schedules without needing panic crunches; and (3) Cross-Team Communication: Act as a clear link between technical teams and non-technical stakeholders.")

    add_heading_2("7.4 Quantitative Metrics, KPIs, and Tracking Scorecard")
    add_p("To hold myself accountable, I set clear baseline numbers and one-year targets in Table 6.")

    t_kpi = doc.add_table(rows=6, cols=4)
    t_kpi.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_kpi.autofit = False
    kpi_hdrs = ["FOCUS AREA", "METRIC DESCRIPTION", "BASELINE (OCT 2026)", "TARGET (OCT 2027)"]
    for j, h in enumerate(kpi_hdrs):
        cell = t_kpi.cell(0, j)
        set_cell_background(cell, NAVY_HEX)
        set_cell_margins(cell, top=65, bottom=65, left=75, right=75)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    t_kpi.cell(0, 0).width = Inches(1.4)
    t_kpi.cell(0, 1).width = Inches(2.4)
    t_kpi.cell(0, 2).width = Inches(1.3)
    t_kpi.cell(0, 3).width = Inches(1.4)

    kpi_data = [
        ("Project Load", "Active non-academic coding projects", "5 to 6 projects (spread thin)", "Maximum 2 active projects"),
        ("Active Listening", "Interruptions per team meeting", "High (>6 observed per meeting)", "Zero (with 3-second wait)"),
        ("Public Speaking", "Formal technical presentations given", "0 talks (avoided due to stage fear)", "At least 4 conference/meetup talks"),
        ("Knowledge Depth", "Time on core backend specialization", "25% (scattered browsing)", "80% deep vertical study"),
        ("Crisis Reliance", "Work finished in last 12 hours of deadline", "85% (adrenaline dependent)", "Under 15% (early sprint finish)")
    ]
    for i, (fa, md, bl, tg) in enumerate(kpi_data):
        row = t_kpi.rows[i+1]
        c0, c1, c2, c3 = row.cells[0], row.cells[1], row.cells[2], row.cells[3]
        c0.width, c1.width, c2.width, c3.width = Inches(1.4), Inches(2.4), Inches(1.3), Inches(1.4)
        bg = LIGHT_BG_HEX if i % 2 == 0 else "FFFFFF"
        for c in [c0, c1, c2, c3]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=45, bottom=45, left=65, right=65)
            set_cell_borders(c, top=BORDER_HEX, bottom=BORDER_HEX, left=BORDER_HEX, right=BORDER_HEX)
        c0.paragraphs[0].add_run(fa).bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(8.5)
        c1.paragraphs[0].add_run(md).font.size = Pt(8.5)
        c2.paragraphs[0].add_run(bl).font.size = Pt(8.5)
        c3.paragraphs[0].add_run(tg).font.size = Pt(8.5)

    add_p("Table 6: Behavioral Key Performance Indicators (KPIs) Scorecard (2026–2027)", italic=True, font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER, font_color=MUTED, space_after=8)

    # ==================== CHAPTER 8 ====================
    add_heading_1("CHAPTER 8: CONCLUSION AND TRANSFORMATIVE COMMITMENTS", page_break=False)
    add_heading_2("8.1 Summary of Evaluative Insights")
    add_p("This report gave me a structured way to evaluate my strengths and habits before graduating. Using SWOT and the Johari Window made it clear that while my curiosity and coding skills give me a strong technical start, my behavioral habits need serious attention. Over-committing to projects, spreading myself across too many technologies, procrastinating until panic sets in, stage fear, and an unconscious habit of interrupting teammates have held back my teamwork. Recognizing that I rely on crisis pressure to focus provides a clear reason to build better daily discipline.")

    add_heading_2("8.2 Transformational Personal Commitments")
    add_p("As I finish this self-analysis, I make three personal commitments:\n1. Listening First: I will treat group conversations with patience, pausing to understand teammates before jumping in to defend my own code design.\n2. Depth Over Novelty: I will say no to peripheral side projects and dedicate my study time to building deep, specialized skill in distributed backend architecture.\n3. Speaking Up Publicly: I will face stage anxiety by taking regular speaking opportunities, publishing technical articles, and learning to explain complex engineering simply.")

    add_heading_2("8.3 Concluding Philosophical Reflection")
    add_p("Building software is about solving problems through careful architecture. The most important system an engineer has to maintain is their own working habits. This self-analysis gives me a practical roadmap to keep improving long after college.")

    add_p("Rounak Neema (Roll No: E244)\nDepartment of Computer Science & Engineering\nMPSTME, SVKM's NMIMS, Shirpur Campus\n23 October 2026", 
          bold=True, font_size=10, font_color=NAVY, space_before=10)

    # ==================== CHAPTER 9 ====================
    add_heading_1("CHAPTER 9: ACADEMIC REFERENCES AND APPENDICES", page_break=False)
    add_heading_2("9.1 Scholarly References (APA 7th Edition)")
    refs = [
        "Andrews, K. R. (1971). The Concept of Corporate Strategy. Homewood, IL: Dow Jones-Irwin.",
        "Belbin, R. M. (2010). Management Teams: Why They Succeed or Fail (3rd ed.). London: Routledge.",
        "Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. Qualitative Research in Psychology, 3(2), 77-101.",
        "Clance, P. R., & Imes, S. A. (1978). The imposter phenomenon in high achieving women. Psychotherapy: Theory, Research & Practice, 15(3), 241-247.",
        "Cottrell, S. (2015). Skills for Success: Personal Development and Employability (3rd ed.). London: Palgrave Macmillan.",
        "Denzin, N. K. (1978). The Research Act: A Theoretical Introduction to Sociological Methods. New York: McGraw-Hill.",
        "Dweck, C. S. (2006). Mindset: The New Psychology of Success. New York: Random House.",
        "Goleman, D. (1995). Emotional Intelligence: Why It Can Matter More Than IQ. New York: Bantam Books.",
        "Humphrey, A. (2005). SWOT analysis for management consulting. SRI Alumni Newsletter, Stanford Research Institute.",
        "Kahneman, D. (2011). Thinking, Fast and Slow. New York: Farrar, Straus and Giroux.",
        "Luft, J., & Ingham, H. (1955). The Johari window, a graphic model of interpersonal awareness. Proceedings of the Western Training Laboratory in Group Development. UCLA.",
        "Rogers, C. R., & Farson, R. E. (1957). Active Listening. Chicago: Industrial Relations Center, University of Chicago.",
        "Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. Cognitive Science, 12(2), 257-285.",
        "Weihrich, H. (1982). The TOWS matrix: A tool for situational analysis. Long Range Planning, 15(2), 54-66.",
        "Yerkes, R. M., & Dodson, J. D. (1908). The relation of strength of stimulus to rapidity of habit-formation. Journal of Comparative Neurology and Psychology, 18(5), 459-482."
    ]
    for r in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.left_indent = Inches(0.3)
        p_r.paragraph_format.first_line_indent = Inches(-0.3)
        p_r.paragraph_format.space_before, p_r.paragraph_format.space_after = Pt(0.5), Pt(1)
        p_r.paragraph_format.line_spacing = 1.08
        run_r = p_r.add_run(r)
        run_r.font.size = Pt(8.5)

    add_heading_2("9.2 Appendix A: 360-Degree Peer Feedback Questionnaire")
    app_items = [
        ("Question 1 (Problem Solving)", "How does Rounak approach technical problem solving in group tasks? (Response: 8 out of 8 noted first-principles approach)."),
        ("Question 2 (Team Listening)", "In team disagreements, how attentively does Rounak listen to other ideas? (Response: 6 out of 8 noted premature counter-arguments and interruptions)."),
        ("Question 3 (Confidence)", "How confident does Rounak seem when presenting technical work? (Response: peers perceived high confidence, unaware of internal second-guessing)."),
        ("Question 4 (Work Conditions)", "Under what conditions have you seen Rounak produce his best work? (Response: 7 out of 8 noted hackathons and last-minute crunches).")
    ]
    for it_t, it_d in app_items:
        p_it = doc.add_paragraph()
        p_it.paragraph_format.space_before, p_it.paragraph_format.space_after = Pt(1), Pt(1.5)
        p_it.paragraph_format.line_spacing = 1.08
        r_itt = p_it.add_run(f"- {it_t}: ")
        r_itt.bold = True
        r_itt.font.size = Pt(8.5)
        r_itt.font.color.rgb = SLATE
        r_itd = p_it.add_run(it_d)
        r_itd.font.size = Pt(8.5)

    add_heading_2("9.3 Appendix B: Daily Self-Regulation & Active Listening Checklist")
    chk_items = [
        "[ ] Paused for three seconds before replying in today's group discussions.",
        "[ ] Summarized the teammate's point before stating my own recommendation.",
        "[ ] Kept active technical side projects at or below two.",
        "[ ] Completed today's coding deliverable in a planned 50-minute Pomodoro block without putting it off.",
        "[ ] Slept at least seven hours and avoided late-night panic work."
    ]
    for ci in chk_items:
        p_ci = doc.add_paragraph()
        p_ci.paragraph_format.space_before, p_ci.paragraph_format.space_after = Pt(1), Pt(1.5)
        p_ci.paragraph_format.line_spacing = 1.05
        r_ci = p_ci.add_run(ci)
        r_ci.font.size = Pt(8.5)

    # Header and Footer
    for s_idx, sec in enumerate(doc.sections):
        header = sec.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("MPSTME, SVKM's NMIMS | LTLS Comprehensive Self-Analysis | Rounak Neema (E244)")
        hr.font.name = 'Calibri'
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = MUTED
        
        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("B.Tech Computer Science & Engineering | Academic Year 2026–2027")
        fr.font.name = 'Calibri'
        fr.font.size = Pt(8.5)
        fr.font.color.rgb = MUTED

    # Save
    docx_out = 'ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.docx'
    doc.save(docx_out)
    
    # Export PDF and measure pages
    pdf_out = os.path.abspath('ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.pdf')
    abs_docx = os.path.abspath(docx_out)
    
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    try:
        w_doc = word.Documents.Open(abs_docx)
        page_count = w_doc.ComputeStatistics(2)
        w_doc.ExportAsFixedFormat(pdf_out, 17)
        w_doc.Close(False)
    finally:
        word.Quit()
        
    print(f"HUMANIZED REPORT GENERATED -> Total pages: {page_count}")
    return page_count

if __name__ == '__main__':
    build_humanized_report()
