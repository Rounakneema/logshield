import re
import json

def clean_js(s):
    if not s:
        return ""
    s = s.replace('—', ' - ').replace('–', ' - ')
    s = s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    return s.strip()

with open('scratch/user_capstone_full_text.md', 'r', encoding='utf-8') as f:
    full_text = f.read()

# Split into chapters
chap_splits = re.split(r'\n(?=CHAPTER\s+[1-7]:|APPENDIX\s+[A-D]:|REFERENCES\b)', full_text)

sections = {}
for split in chap_splits:
    split = split.strip()
    if not split:
        continue
    m = re.match(r'^(CHAPTER\s+[1-7]|APPENDIX\s+[A-D]|REFERENCES)', split)
    if m:
        key = m.group(1).replace(' ', '_')
        sections[key] = split

print("Found sections:", list(sections.keys()))

def parse_markdown_section(text):
    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Check for Heading 1 (CHAPTER X)
        if re.match(r'^CHAPTER\s+[1-7]:', line):
            out.append(f'  o.push(h1(`{clean_js(line)}`));\n')
            i += 1
            continue
            
        # Check for Heading 2 (e.g. "1. BACKGROUND" or "2. MOTIVATION")
        if re.match(r'^[0-9]+\.\s+[A-Z\s,–—\(\)/]{3,}', line):
            out.append(f'  o.push(h2(`{clean_js(line)}`));\n')
            i += 1
            continue
            
        # Check for Heading 3 (e.g. "i. The Problem of Secrets in Logs", "Stage 1 — Preprocessor")
        if re.match(r'^(?:[ivx]+\.|Stage\s+[1-6]\s*[—\-–]|A\.[0-9]|D\.[0-9])', line):
            out.append(f'  o.push(h3(`{clean_js(line)}`));\n')
            i += 1
            continue
            
        # Check for Table
        if line.startswith('Table ') and ':' in line:
            # Table caption
            tm = re.match(r'^Table\s+([A-Za-z0-9\.]+)\s*:\s*(.*)', line)
            t_num = tm.group(1).strip() if tm else ""
            t_cap = clean_js(tm.group(2).strip()) if tm else clean_js(line)
            
            i += 1
            # Next should be table markdown
            headers = []
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                cells = [clean_js(c.strip()) for c in row_line.split('|')[1:-1]]
                if not headers:
                    headers = cells
                elif not re.match(r'^[\s\-:]+$', "".join(cells)):
                    rows.append(cells)
                i += 1
                
            headers_js = json.dumps(headers, ensure_ascii=False)
            rows_js = json.dumps(rows, ensure_ascii=False)
            out.append(f'  o.push(...tbl("{t_num}", `{t_cap}`, {headers_js}, {rows_js}));\n')
            continue
            
        # Check for Figure
        if line.startswith('Figure ') and ':' in line:
            fm = re.match(r'^Figure\s+([A-Za-z0-9\.]+)\s*:\s*(.*)', line)
            f_num = fm.group(1).strip() if fm else ""
            f_cap = clean_js(fm.group(2).strip()) if fm else clean_js(line)
            f_key = f"f_{f_num.replace('.', '_')}"
            out.append(f'  o.push(...fig("{f_num}", "{f_key}", `{f_cap}`, 0.85));\n')
            i += 1
            continue
            
        # Check for bullets
        if line.startswith('•') or line.startswith('- ') or re.match(r'^[0-9]+\.\s+[A-Z]', line) and len(line) < 120 and ('Interception' in line or 'Scoring' in line or 'Resistance' in line or 'Latency' in line or 'Recovery' in line or 'Tracking' in line or 'Containment' in line or 'Experience' in line):
            bullet_items = []
            while i < n and (lines[i].strip().startswith('•') or lines[i].strip().startswith('- ')):
                b_txt = lines[i].strip()
                if b_txt.startswith('•') or b_txt.startswith('- '):
                    b_txt = b_txt[2:].strip()
                bullet_items.append(clean_js(b_txt))
                i += 1
            if bullet_items:
                items_js = json.dumps(bullet_items, ensure_ascii=False)
                out.append(f'  o.push(...bullets({items_js}));\n')
                continue
                
        # Normal paragraph
        out.append(f'  o.push(p(`{clean_js(line)}`));\n')
        i += 1
        
    return "".join(out)

# 1. Generate ch12.js
ch1_code = parse_markdown_section(sections.get('CHAPTER_1', ''))
ch2_code = parse_markdown_section(sections.get('CHAPTER_2', ''))

with open('report_js/ch12.js', 'w', encoding='utf-8') as f:
    f.write('const { h1, h2, h3, p, bullets, tbl, fig, c } = require("./lib");\n\n')
    f.write('module.exports = function () {\n  const o = [];\n')
    f.write(ch1_code)
    f.write('\n')
    f.write(ch2_code)
    f.write('\n  return o;\n};\n')
print("Wrote report_js/ch12.js successfully.")

# 2. Generate ch34.js
ch3_code = parse_markdown_section(sections.get('CHAPTER_3', ''))
ch4_code = parse_markdown_section(sections.get('CHAPTER_4', ''))

with open('report_js/ch34.js', 'w', encoding='utf-8') as f:
    f.write('const { h1, h2, h3, p, bullets, tbl, fig, c } = require("./lib");\n\n')
    f.write('module.exports = function () {\n  const o = [];\n')
    f.write(ch3_code)
    f.write('\n')
    f.write(ch4_code)
    f.write('\n  return o;\n};\n')
print("Wrote report_js/ch34.js successfully.")

# 3. Generate ch567.js
ch5_code = parse_markdown_section(sections.get('CHAPTER_5', ''))
ch6_code = parse_markdown_section(sections.get('CHAPTER_6', ''))
ch7_code = parse_markdown_section(sections.get('CHAPTER_7', ''))

with open('report_js/ch567.js', 'w', encoding='utf-8') as f:
    f.write('const { h1, h2, h3, p, bullets, tbl, fig, c } = require("./lib");\n\n')
    f.write('module.exports = function () {\n  const o = [];\n')
    f.write(ch5_code)
    f.write('\n')
    f.write(ch6_code)
    f.write('\n')
    f.write(ch7_code)
    f.write('\n  return o;\n};\n')
print("Wrote report_js/ch567.js successfully.")
