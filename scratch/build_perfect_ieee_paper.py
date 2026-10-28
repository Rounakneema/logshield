import os, sys, re, zipfile, io
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docx.text.paragraph import Paragraph
from docx.table import Table

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sort_references import old_to_new, sorted_refs
from remap_citations import remap_text_citations

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for edge, val in borders.items():
        if val is not None:
            tag = f'w:{edge}'
            el = tcBorders.find(qn(tag))
            if el is None:
                el = OxmlElement(tag)
                tcBorders.append(el)
            for k, v in val.items():
                el.set(qn(f'w:{k}'), str(v))

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def apply_ieee_booktabs(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    top_rule = {'sz': 8, 'val': 'single', 'color': '000000'}
    mid_rule = {'sz': 4, 'val': 'single', 'color': '000000'}
    bot_rule = {'sz': 8, 'val': 'single', 'color': '000000'}
    none_rule = {'val': 'none'}
    
    num_rows = len(table.rows)
    for r_idx, row in enumerate(table.rows):
        is_first = (r_idx == 0)
        is_last = (r_idx == num_rows - 1)
        for c_idx, cell in enumerate(row.cells):
            t = top_rule if is_first else none_rule
            b = bot_rule if is_last else (mid_rule if is_first else none_rule)
            set_cell_borders(cell, top=t, bottom=b, left=none_rule, right=none_rule)
            if col_widths and c_idx < len(col_widths):
                cell.width = col_widths[c_idx]

def make_callout_box(doc, title_text, code_lines):
    p_box = doc.add_paragraph()
    p_box.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_box.paragraph_format.space_before = Pt(6)
    p_box.paragraph_format.space_after = Pt(6)
    p_box.paragraph_format.line_spacing = 1.15
    p_box.paragraph_format.left_indent = Inches(0.15)
    p_box.paragraph_format.right_indent = Inches(0.15)
    p_box.paragraph_format.first_line_indent = Pt(0)
    
    r_h = p_box.add_run(title_text + "\n")
    r_h.font.name = "Times New Roman"
    r_h.font.size = Pt(8.0)
    r_h.font.bold = True
    r_h.font.italic = True
    
    code_body = "\n".join(code_lines)
    r_c = p_box.add_run(code_body)
    r_c.font.name = "Consolas"
    r_c.font.size = Pt(7.0)
    r_c.font.color.rgb = RGBColor(30, 41, 59)

def make_algorithm_box(doc, algo_title, req_text, ens_text, steps):
    p_algo = doc.add_paragraph()
    p_algo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_algo.paragraph_format.space_before = Pt(8)
    p_algo.paragraph_format.space_after = Pt(8)
    p_algo.paragraph_format.line_spacing = 1.15
    p_algo.paragraph_format.first_line_indent = Pt(0)
    
    r_top = p_algo.add_run("――――――――――――――――――――――――――――――――――――――――――\n")
    r_top.font.size = Pt(6.0); r_top.font.bold = True
    
    r_t = p_algo.add_run(algo_title + "\n")
    r_t.font.name = "Times New Roman"; r_t.font.size = Pt(8.5); r_t.font.bold = True
    
    r_req = p_algo.add_run("Require: ")
    r_req.font.name = "Times New Roman"; r_req.font.size = Pt(8.0); r_req.font.bold = True
    r_req_t = p_algo.add_run(req_text + "\n")
    r_req_t.font.name = "Times New Roman"; r_req_t.font.size = Pt(8.0)
    
    r_ens = p_algo.add_run("Ensure: ")
    r_ens.font.name = "Times New Roman"; r_ens.font.size = Pt(8.0); r_ens.font.bold = True
    r_ens_t = p_algo.add_run(ens_text + "\n")
    r_ens_t.font.name = "Times New Roman"; r_ens_t.font.size = Pt(8.0)
    
    r_mid = p_algo.add_run("――――――――――――――――――――――――――――――――――――――――――\n")
    r_mid.font.size = Pt(5.0); r_mid.font.color.rgb = RGBColor(140, 140, 140)
    
    for st in steps:
        r_st = p_algo.add_run(st + "\n")
        r_st.font.name = "Times New Roman"; r_st.font.size = Pt(7.5)
        
    r_bot = p_algo.add_run("――――――――――――――――――――――――――――――――――――――――――")
    r_bot.font.size = Pt(6.0); r_bot.font.bold = True

def switch_to_1col(doc):
    sec = doc.add_section(docx.enum.section.WD_SECTION.CONTINUOUS)
    sec.top_margin = Inches(0.75); sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(0.625); sec.right_margin = Inches(0.625)
    cols = sec._sectPr.xpath('./w:cols')
    if cols:
        cols[0].set(qn('w:num'), '1')
    else:
        sec._sectPr.append(parse_xml(r'<w:cols xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:num="1"/>'))
    return sec

def switch_to_2col(doc):
    sec = doc.add_section(docx.enum.section.WD_SECTION.CONTINUOUS)
    sec.top_margin = Inches(0.75); sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(0.625); sec.right_margin = Inches(0.625)
    cols = sec._sectPr.xpath('./w:cols')
    if cols:
        cols[0].set(qn('w:num'), '2')
        cols[0].set(qn('w:space'), '360')
    else:
        sec._sectPr.append(parse_xml(r'<w:cols xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:num="2" w:space="360"/>'))
    return sec

def build_paper():
    src_path = r"C:\Users\Asus\.gemini\antigravity\brain\236c4749-0fde-4dca-8814-d7425598de3f\.user_uploaded\media_1793188527179_7471e50a.docx"
    doc_src = docx.Document(src_path)
    
    doc_out = docx.Document()
    
    # Section 1: Title & Authors (1 column)
    sec1 = doc_out.sections[0]
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(0.625)
    sec1.right_margin = Inches(0.625)
    
    # Title
    p_title = doc_out.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.paragraph_format.first_line_indent = Pt(0)
    r_title = p_title.add_run("LogShield: In-Pod Secret Sanitization and Autonomous Closed-Loop Containment for Cloud-Native Microservices")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(24.0)
    r_title.font.bold = True
    
    # Author Block: Row 1 (3 Authors)
    tbl_auth1 = doc_out.add_table(rows=1, cols=3)
    tbl_auth1.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors_r1 = [
        ("Rounak Neema", "rounak.neema046@nmims.in"),
        ("Manas Borse", "manas.borse057@nmims.in"),
        ("Arnab Chowdhury", "arnab.chowdhury032@nmims.in"),
    ]
    for ci, (name, email) in enumerate(authors_r1):
        cell = tbl_auth1.rows[0].cells[ci]
        cell.width = Inches(2.40)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(0)
        
        r_n = p.add_run(name + "\n")
        r_n.font.name = "Times New Roman"; r_n.font.size = Pt(10.5); r_n.font.bold = True
        
        r_d = p.add_run("Dept. of Computer Engineering\nMPSTME, NMIMS University\nMumbai, India\n")
        r_d.font.name = "Times New Roman"; r_d.font.size = Pt(8.5)
        
        r_e = p.add_run(email)
        r_e.font.name = "Times New Roman"; r_e.font.size = Pt(8.5); r_e.font.italic = True
        
        set_cell_borders(cell, top={'val': 'none'}, bottom={'val': 'none'}, left={'val': 'none'}, right={'val': 'none'})

    # Spacing between author rows
    p_auth_sp = doc_out.add_paragraph()
    p_auth_sp.paragraph_format.space_before = Pt(4)
    p_auth_sp.paragraph_format.space_after = Pt(0)
    p_auth_sp.paragraph_format.line_spacing = 1.0

    # Author Block: Row 2 (2 Authors, Centered)
    tbl_auth2 = doc_out.add_table(rows=1, cols=2)
    tbl_auth2.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors_r2 = [
        ("Prince Roy", "prince.roy031@nmims.in"),
        ("Rudrani Ingle", "Rudrani.Ingle@nmims.edu"),
    ]
    for ci, (name, email) in enumerate(authors_r2):
        cell = tbl_auth2.rows[0].cells[ci]
        cell.width = Inches(2.80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(0)
        
        r_n = p.add_run(name + "\n")
        r_n.font.name = "Times New Roman"; r_n.font.size = Pt(10.5); r_n.font.bold = True
        
        r_d = p.add_run("Dept. of Computer Engineering\nMPSTME, NMIMS University\nMumbai, India\n")
        r_d.font.name = "Times New Roman"; r_d.font.size = Pt(8.5)
        
        r_e = p.add_run(email)
        r_e.font.name = "Times New Roman"; r_e.font.size = Pt(8.5); r_e.font.italic = True
        
        set_cell_borders(cell, top={'val': 'none'}, bottom={'val': 'none'}, left={'val': 'none'}, right={'val': 'none'})
        
    p_sep = doc_out.add_paragraph()
    p_sep.paragraph_format.space_before = Pt(4)
    p_sep.paragraph_format.space_after = Pt(8)
    
    # Section 2: Body starts in 2 columns
    switch_to_2col(doc_out)
    
    image_paths = {
        "fig1": r"d:\LOGSHEILD\paper\figures\fig1_architecture.png",
        "fig2": r"d:\LOGSHEILD\paper\figures\fig2_pipeline.png",
        "fig3": r"d:\LOGSHEILD\paper\figures\fig6_lineage.png",
        "fig4": r"d:\LOGSHEILD\paper\figures\fig4_ablation.png",
        "fig5": r"d:\LOGSHEILD\paper\figures\fig7_evasion_benchmark.png",
        "fig6": r"d:\LOGSHEILD\paper\figures\fig8_containment_lifecycle.png",
        "fig7": r"d:\LOGSHEILD\paper\figures\fig5_benchmark.png",
    }
    
    body_elements = list(doc_src.element.body)
    p_elements = []
    current_tbl_index = 0
    for elem in body_elements:
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            p = Paragraph(elem, doc_src)
            txt = p.text.strip()
            if not txt or txt.startswith("LogShield: In-Pod") or "Department of Computer Engineering" in txt:
                continue
            if txt.startswith("This study was conducted as part of the Capstone"):
                continue # Skip Capstone note completely
            if txt.lower() == "references" or txt.startswith(("[1]", "[1]\t")):
                # Stop reading body elements here; references are generated cleanly at the end
                break
            p_elements.append(('p', p, txt))
        elif tag == 'tbl':
            tbl = Table(elem, doc_src)
            p_elements.append(('tbl', tbl, current_tbl_index))
            current_tbl_index += 1
            
    print(f"Total elements to process: {len(p_elements)}")
    
    idx = 0
    while idx < len(p_elements):
        kind, obj, meta = p_elements[idx]
        
        if kind == 'p':
            text_raw = meta
            
            # Abstract
            if text_raw.startswith("Abstract"):
                p_out = doc_out.add_paragraph()
                p_out.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_out.paragraph_format.line_spacing = 1.05
                p_out.paragraph_format.space_after = Pt(4)
                p_out.paragraph_format.first_line_indent = Pt(0)
                m = re.match(r'Abstract[—\-\s]+(.*)', text_raw, re.DOTALL)
                body = remap_text_citations(m.group(1) if m else text_raw)
                r_h = p_out.add_run("Abstract—")
                r_h.font.name = "Times New Roman"; r_h.font.size = Pt(9.0); r_h.font.bold = True; r_h.font.italic = True
                r_b = p_out.add_run(body)
                r_b.font.name = "Times New Roman"; r_b.font.size = Pt(9.0); r_b.font.bold = True
                idx += 1
                continue
                
            # Index Terms
            if text_raw.startswith("Index Terms"):
                p_out = doc_out.add_paragraph()
                p_out.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_out.paragraph_format.line_spacing = 1.05
                p_out.paragraph_format.space_after = Pt(8)
                p_out.paragraph_format.first_line_indent = Pt(0)
                m = re.match(r'Index Terms[—\-\s]+(.*)', text_raw, re.DOTALL)
                body = m.group(1) if m else text_raw
                r_h = p_out.add_run("Index Terms—")
                r_h.font.name = "Times New Roman"; r_h.font.size = Pt(9.0); r_h.font.bold = True; r_h.font.italic = True
                r_b = p_out.add_run(body)
                r_b.font.name = "Times New Roman"; r_b.font.size = Pt(9.0); r_b.font.bold = True
                idx += 1
                continue
                
            # Capstone note
            if text_raw.startswith("This study was conducted as part of the Capstone"):
                p_out = doc_out.add_paragraph()
                p_out.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_out.paragraph_format.line_spacing = 1.0
                p_out.paragraph_format.space_after = Pt(8)
                p_out.paragraph_format.first_line_indent = Pt(0)
                r = p_out.add_run(text_raw)
                r.font.name = "Times New Roman"; r.font.size = Pt(8.0); r.font.italic = True
                idx += 1
                continue
                
            # Major Heading Level 1
            m_h1 = re.match(r'^([I|V|X]+\.\s+.*)', text_raw)
            if m_h1:
                p_out = doc_out.add_paragraph()
                p_out.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_out.paragraph_format.space_before = Pt(11)
                p_out.paragraph_format.space_after = Pt(4)
                p_out.paragraph_format.keep_with_next = True
                p_out.paragraph_format.first_line_indent = Pt(0)
                r = p_out.add_run(text_raw.upper())
                r.font.name = "Times New Roman"; r.font.size = Pt(10.0); r.font.bold = True
                idx += 1
                continue
                
            # Secondary Heading Level 2
            m_h2 = re.match(r'^([A-Z]\.\s+.*)', text_raw)
            if m_h2 and len(text_raw) < 70 and not text_raw.startswith("TABLE"):
                p_out = doc_out.add_paragraph()
                p_out.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_out.paragraph_format.space_before = Pt(8)
                p_out.paragraph_format.space_after = Pt(2)
                p_out.paragraph_format.keep_with_next = True
                p_out.paragraph_format.first_line_indent = Pt(0)
                r = p_out.add_run(text_raw)
                r.font.name = "Times New Roman"; r.font.size = Pt(10.0); r.font.italic = True
                idx += 1
                continue
                
            # Acknowledgment
            if text_raw.lower() == "acknowledgment":
                p_out = doc_out.add_paragraph()
                p_out.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_out.paragraph_format.space_before = Pt(14)
                p_out.paragraph_format.space_after = Pt(4)
                p_out.paragraph_format.keep_with_next = True
                p_out.paragraph_format.first_line_indent = Pt(0)
                r = p_out.add_run("ACKNOWLEDGMENT")
                r.font.name = "Times New Roman"; r.font.size = Pt(10.0); r.font.bold = True
                
                # Insert humanized, deslopped acknowledgment prose
                p_ack = doc_out.add_paragraph()
                p_ack.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_ack.paragraph_format.line_spacing = 1.05
                p_ack.paragraph_format.space_before = Pt(0)
                p_ack.paragraph_format.space_after = Pt(6)
                p_ack.paragraph_format.first_line_indent = Pt(10.8)
                r_ack = p_ack.add_run(
                    "The authors thank the maintainers of SecretBench, TruffleHog, and Gitleaks for open-sourcing "
                    "their detection datasets and rule engines. We also thank the Department of Computer Engineering "
                    "at NMIMS University for providing computing facilities and laboratory infrastructure for our "
                    "Kubernetes testbed cluster."
                )
                r_ack.font.name = "Times New Roman"; r_ack.font.size = Pt(10.0)
                
                # Advance past source acknowledgment paragraph if present
                if idx + 1 < len(p_elements) and p_elements[idx + 1][0] == 'p':
                    idx += 1
                idx += 1
                continue
                
            # Figure Insertion & Caption
            if text_raw.startswith("Fig."):
                m_f = re.match(r'Fig\.\s*(\d+)\.', text_raw)
                fig_num = m_f.group(1) if m_f else "1"
                img_key = f"fig{fig_num}"
                
                p_img = doc_out.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(6)
                p_img.paragraph_format.space_after = Pt(2)
                p_img.paragraph_format.first_line_indent = Pt(0)
                if img_key in image_paths and os.path.exists(image_paths[img_key]):
                    r_i = p_img.add_run()
                    r_i.add_picture(image_paths[img_key], width=Inches(3.40))
                    
                p_cap = doc_out.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(8)
                p_cap.paragraph_format.first_line_indent = Pt(0)
                r_c = p_cap.add_run(text_raw)
                r_c.font.name = "Times New Roman"; r_c.font.size = Pt(8.0)
                idx += 1
                continue
                
            # Table Title Paragraph
            if text_raw.startswith("TABLE "):
                tbl_num_str = text_raw
                idx += 1
                tbl_desc_str = ""
                if idx < len(p_elements) and p_elements[idx][0] == 'p':
                    cand_desc = p_elements[idx][2]
                    if not cand_desc.startswith(('I.', 'II.', 'A.', 'B.', 'TABLE', 'Fig.', 'Algorithm')):
                        tbl_desc_str = cand_desc
                        idx += 1
                        
                p_tnum = doc_out.add_paragraph()
                p_tnum.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_tnum.paragraph_format.space_before = Pt(16)
                p_tnum.paragraph_format.space_after = Pt(2)
                p_tnum.paragraph_format.keep_with_next = True
                p_tnum.paragraph_format.first_line_indent = Pt(0)
                r = p_tnum.add_run(tbl_num_str)
                r.font.name = "Times New Roman"; r.font.size = Pt(8.5); r.font.bold = True
                
                if tbl_desc_str:
                    p_tdesc = doc_out.add_paragraph()
                    p_tdesc.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_tdesc.paragraph_format.space_before = Pt(2)
                    p_tdesc.paragraph_format.space_after = Pt(5)
                    p_tdesc.paragraph_format.keep_with_next = True
                    p_tdesc.paragraph_format.first_line_indent = Pt(0)
                    r = p_tdesc.add_run(tbl_desc_str)
                    r.font.name = "Times New Roman"; r.font.size = Pt(8.0); r.font.italic = True
                    
                continue
                
            # Regular Body Paragraph
            rem = remap_text_citations(text_raw)
            p_out = doc_out.add_paragraph()
            p_out.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_out.paragraph_format.line_spacing = 1.05
            p_out.paragraph_format.space_before = Pt(0)
            p_out.paragraph_format.space_after = Pt(0)
            p_out.paragraph_format.first_line_indent = Pt(10.8)
            
            m_runin = re.match(r'^((?:[A-Za-z0-9\-\s\(\)]+[:—])|(?:Invariant \d+[^:]*:)|(?:Theorem \d+[^:]*:))(.*)', rem, re.DOTALL)
            if m_runin and len(m_runin.group(1)) < 60:
                r_h = p_out.add_run(m_runin.group(1))
                r_h.font.name = "Times New Roman"; r_h.font.size = Pt(10.0); r_h.font.italic = True
                r_t = p_out.add_run(m_runin.group(2))
                r_t.font.name = "Times New Roman"; r_t.font.size = Pt(10.0)
            else:
                r_t = p_out.add_run(rem)
                r_t.font.name = "Times New Roman"; r_t.font.size = Pt(10.0)
                
            idx += 1
            continue
            
        elif kind == 'tbl':
            tbl = obj
            tbl_idx = meta
            
            if tbl_idx == 0:
                idx += 1
                continue
                
            if tbl_idx == 1:
                lines = [
                    'logger.debug(f"DB URI: {DATABASE_URL}")',
                    '# postgres://admin:MyP@ssw0rd@prod-db:5432/app',
                    'logger.error(f"Auth error: {headers[\'Authorization\']}")',
                    '# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'logger.info(f"Payment token: {STRIPE_SECRET_KEY}")',
                    '# sk_live_51H7x8...',
                    'logger.debug(f"Environment: {os.environ}")',
                    '# AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE...'
                ]
                make_callout_box(doc_out, "Listing 1: Representative Credential Leakage in Application Logs", lines)
                idx += 1
                continue
                
            if tbl_idx == 3:
                lines = [
                    'volumes:',
                    '- name: log-buffer',
                    '  emptyDir:',
                    '    medium: Memory',
                    '    sizeLimit: 128Mi'
                ]
                make_callout_box(doc_out, "Listing 2: Memory-Backed Shared emptyDir In-Pod Volume Configuration", lines)
                idx += 1
                continue
                
            if tbl_idx == 5:
                steps = [
                    "1:   Open file descriptor fd ← tail(P)",
                    "2:   while true do",
                    "3:       L ← ReadLine(fd)",
                    "4:       if L = EOF then Sleep(10 ms); continue; end if",
                    "5:       (Lnorm, Tfused) ← PreprocessAndFuse(L)",
                    "6:       if AhoCorasickScan(Lnorm, Dkeys) = ∅ and |Tfused| = 0 then",
                    "7:           PrintStdout(L); continue",
                    "8:       end if",
                    "9:       Cctx ← EvaluateContext(Lnorm)",
                    "10:     Ccand ← ExtractCandidates(Lnorm, Tfused, Cctx)",
                    "11:     Lout ← L",
                    "12:     for all s ∈ Ccand do",
                    "13:         x ← BuildFeatureVector(s, Lnorm, Cctx)",
                    "14:         S ← min(100, ∑(wi · xi))",
                    "15:         if S ≥ 80 then",
                    "16:             RefID ← GenerateRefID()",
                    "17:             VaultInsert(RefID, s, S)",
                    "18:             φ* ← HMAC-SHA256(Klineage, Canonicalize(s))",
                    "19:             if φ* ∉ Eexempt then",
                    "20:                 LineageRecord(φ*, PodUID, Namespace)",
                    "21:                 AssessAndContain(RefID, φ*, Category(s), S)",
                    "22:             end if",
                    "23:             Lout ← Replace(Lout, s.raw_slice, [REDACTED: RefID])",
                    "24:         else if 50 ≤ S < 80 then",
                    "25:             Lout ← AppendTag(Lout, [FLAGGED:SCS=S])",
                    "26:         end if",
                    "27:     end for",
                    "28:     PrintStdout(Lout)",
                    "29:  end while"
                ]
                make_algorithm_box(doc_out, "Algorithm 1: In-Pod Stream Interception and Autonomous Containment",
                                   "Log path P, dictionary Dkeys, weights w, key Klineage",
                                   "Sanitized logs to stdout; automated containment actions",
                                   steps)
                idx += 1
                continue
                
            if tbl_idx == 6:
                steps = [
                    "1:   t ← CurrentTimestamp()",
                    "2:   CommitAuditEntry(t, Cact, RefID, ATTEMPTED)",
                    "3:   if not ConstantTimeVerify(Cact, AuthorizedActors) then",
                    "4:       CommitAuditEntry(t, Cact, RefID, DENIED)",
                    "5:       return Error(Unauthorized)",
                    "6:   end if",
                    "7:   C, expires_at ← FetchVaultRecord(RefID)",
                    "8:   if t > expires_at then",
                    "9:       CommitAuditEntry(t, Cact, RefID, EXPIRED)",
                    "10:     return Error(Expired)",
                    "11:  end if",
                    "12:  if ValidateFernetHMAC(Kv, C) then",
                    "13:      s ← FernetDecrypt(Kv, C)",
                    "14:      CommitAuditEntry(t, Cact, RefID, SUCCESS)",
                    "15:      return s",
                    "16:  else",
                    "17:      CommitAuditEntry(t, Cact, RefID, TAMPER_DETECTED)",
                    "18:      return Error(Integrity Verification Failed)",
                    "19:  end if"
                ]
                make_algorithm_box(doc_out, "Algorithm 2: SecureReveal Decryption and Audit Logging",
                                   "RefID, actor credentials Cact, Reason, vault key Kv",
                                   "Decrypted plaintext secret s or authorization failure",
                                   steps)
                idx += 1
                continue
                
            # Table 8: TABLE IV (Controlled 6-Stage Ablation Study) -> FULL RECONSTRUCTION!
            if tbl_idx == 8:
                rows_data = [
                    ["Config", "Architecture Description", "Precision", "Recall", "F1-Score", "F2-Score", "FP Rate", "Avg. Latency"],
                    ["Part A: Standard In-the-Wild Evaluation (N = 9,205, evasion vectors excluded)", "", "", "", "", "", "", ""],
                    ["Stage 1", "Regex-Only Baseline (600 standard rules)", "0.8437", "1.0000", "0.9152", "0.9643", "17.16%", "6.528 ms"],
                    ["Stage 2", "Regex + Aho-Corasick Early-Exit Filter", "0.8437", "1.0000", "0.9152", "0.9643", "17.16%", "0.209 ms"],
                    ["Stage 3", "Regex + AC + Context Window Proximity", "0.8944", "0.9854", "0.9377", "0.9658", "10.90%", "0.384 ms"],
                    ["Stage 4", "Regex + AC + Context + 6-Factor SCS (T = 80)", "1.0000", "0.9993", "0.9997", "0.9995", "0.00%*", "0.504 ms"],
                    ["Part B: Combined Adversarial Stress-Test (N = 10,000, 795 evasion vectors counted as FN)", "", "", "", "", "", "", ""],
                    ["Stage 5", "Stage 4 Pipeline under Evasion (Token Fusion Disabled)", "1.0000", "0.8472", "0.9173", "0.8737", "0.00%*", "0.504 ms"],
                    ["Stage 6", "LogShield Full Pipeline (Stage 4 + Token Fusion Active)", "1.0000", "0.9130†", "0.9545†", "0.9291†", "0.00%*", "0.586 ms"],
                ]
                new_tbl = doc_out.add_table(rows=len(rows_data), cols=8)
                new_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                new_tbl.autofit = True
                for r_i, row in enumerate(rows_data):
                    for c_i, val in enumerate(row):
                        cell = new_tbl.rows[r_i].cells[c_i]
                        cell.text = val
                        p = cell.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i not in (0, 1) else WD_ALIGN_PARAGRAPH.LEFT
                        p.paragraph_format.space_before = Pt(2.5)
                        p.paragraph_format.space_after = Pt(2.5)
                        p.paragraph_format.line_spacing = 1.15
                        if len(p.runs) > 0:
                            p.runs[0].font.name = "Times New Roman"
                            p.runs[0].font.size = Pt(7.5)
                            if r_i == 0 or 'Part' in val or 'Stage 6' in val:
                                p.runs[0].font.bold = True
                                
                apply_ieee_booktabs(new_tbl)
                
                p_note = doc_out.add_paragraph()
                p_note.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_note.paragraph_format.space_before = Pt(2)
                p_note.paragraph_format.space_after = Pt(6)
                p_note.paragraph_format.first_line_indent = Pt(0)
                r_n = p_note.add_run("*Rule-of-Three 95% upper confidence bound for FPR in 4,778 true negatives is FPR ≤ 0.063%; exact Clopper-Pearson 95% CI for precision is [0.9992, 1.0000]. †Evaluated on the dedicated balanced adversarial evasion corpus (N = 2,400).")
                r_n.font.name = "Times New Roman"; r_n.font.size = Pt(7.0); r_n.font.italic = True
                
                idx += 1
                continue
                
            # Tables 2, 4, 7, 9, 10, 11, 12
            rows_cnt = len(tbl.rows)
            cols_cnt = len(tbl.columns)
            new_tbl = doc_out.add_table(rows=rows_cnt, cols=cols_cnt)
            new_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            new_tbl.autofit = True
            
            font_size = Pt(7.0) if cols_cnt >= 7 else Pt(7.5)
            
            for ri in range(rows_cnt):
                for ci in range(cols_cnt):
                    txt = tbl.rows[ri].cells[ci].text.strip()
                    c_out = new_tbl.rows[ri].cells[ci]
                    c_out.text = txt
                    p_c = c_out.paragraphs[0]
                    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 1 and cols_cnt > 2 else WD_ALIGN_PARAGRAPH.LEFT
                    p_c.paragraph_format.space_before = Pt(2.5)
                    p_c.paragraph_format.space_after = Pt(2.5)
                    p_c.paragraph_format.line_spacing = 1.15
                    if len(p_c.runs) > 0:
                        p_c.runs[0].font.name = "Times New Roman"
                        p_c.runs[0].font.size = font_size
                        if ri == 0 or 'Part' in txt or 'Stage 6' in txt:
                            p_c.runs[0].font.bold = True
                            
            apply_ieee_booktabs(new_tbl)
            
            p_post = doc_out.add_paragraph()
            p_post.paragraph_format.space_before = Pt(0)
            p_post.paragraph_format.space_after = Pt(6)
            
            idx += 1
            continue

    # References Section
    p_ref_head = doc_out.add_paragraph()
    p_ref_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref_head.paragraph_format.space_before = Pt(14)
    p_ref_head.paragraph_format.space_after = Pt(6)
    p_ref_head.paragraph_format.keep_with_next = True
    p_ref_head.paragraph_format.first_line_indent = Pt(0)
    r_rf = p_ref_head.add_run("REFERENCES")
    r_rf.font.name = "Times New Roman"
    r_rf.font.size = Pt(10.0)
    r_rf.font.bold = True
    
    for idx_ref, ref in enumerate(sorted_refs, 1):
        p_ref = doc_out.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(3.0)
        p_ref.paragraph_format.space_after = Pt(3.0)
        p_ref.paragraph_format.left_indent = Inches(0.25)
        p_ref.paragraph_format.first_line_indent = Inches(-0.25)
        
        r_num = p_ref.add_run(f"[{idx_ref}]\t")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(8.0)
        
        r_txt = p_ref.add_run(ref["citation"])
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(8.0)
        
    out_docx_path = os.path.abspath("LogShield_IEEE_Paper_Official.docx")
    doc_out.save(out_docx_path)
    print(f"Successfully generated: {out_docx_path} ({os.path.getsize(out_docx_path)} bytes)")

if __name__ == "__main__":
    build_paper()
