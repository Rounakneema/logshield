import json
import re

def clean_str(s):
    if not s:
        return ""
    # Remove em dashes and en dashes
    s = s.replace('—', ' - ').replace('–', ' - ')
    # Escape backslashes, backticks, and ${} for JS template strings
    s = s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    return s.strip()

def process_elements(elems, extra_tables=None, extra_figs=None):
    lines = []
    i = 0
    n = len(elems)
    
    while i < n:
        el = elems[i]
        
        # Check if next element is a table and current element is its caption
        if el['type'] == 'p' and i + 1 < n and elems[i+1]['type'] == 'tbl':
            p_text = el['text']
            m = re.match(r'^(?:Table\s+([A-Za-z0-9\.]+)\s*[:\-]\s*(.*)|(.*))', p_text)
            if 'Table' in p_text and m and m.group(1):
                num = m.group(1).strip()
                caption = clean_str(m.group(2) or "")
            else:
                num = "X"
                caption = clean_str(p_text)
            
            tbl_data = elems[i+1]['data']
            headers = [clean_str(c) for c in tbl_data[0]] if tbl_data else []
            rows = [[clean_str(c) for c in row] for row in tbl_data[1:]] if len(tbl_data) > 1 else []
            
            headers_js = json.dumps(headers, ensure_ascii=False)
            rows_js = json.dumps(rows, ensure_ascii=False)
            
            lines.append(f'  o.push(...tbl("{num}", "{caption}", {headers_js}, {rows_js}));\n')
            i += 2
            continue
            
        if el['type'] == 'tbl':
            # Standalone table without preceding caption
            tbl_data = el['data']
            headers = [clean_str(c) for c in tbl_data[0]] if tbl_data else []
            rows = [[clean_str(c) for c in row] for row in tbl_data[1:]] if len(tbl_data) > 1 else []
            headers_js = json.dumps(headers, ensure_ascii=False)
            rows_js = json.dumps(rows, ensure_ascii=False)
            lines.append(f'  o.push(...tbl("", "Data Table", {headers_js}, {rows_js}));\n')
            i += 1
            continue
            
        if el['type'] == 'p':
            txt = el['text']
            style = el.get('style', '')
            
            # Check for figure caption
            fig_match = re.match(r'^Figure\s+([A-Za-z0-9\.]+)\s*[:\-]\s*(.*)', txt)
            if fig_match:
                f_num = fig_match.group(1).strip()
                f_cap = clean_str(fig_match.group(2).strip())
                # Map figure key
                f_key = f"fig{f_num.replace('.', '_')}"
                if f_num == "1.1" or f_num == "1.2":
                    f_key = "f_pipeline"
                elif f_num == "4.1":
                    f_key = "f_arch"
                elif f_num == "4.2":
                    f_key = "f_pipeline"
                elif f_num == "4.3":
                    f_key = "f_arch"
                elif f_num == "4.4" or f_num == "4.5":
                    f_key = "f_lineage"
                elif f_num == "4.6":
                    f_key = "f_containment"
                elif f_num == "5.1":
                    f_key = "f_ml"
                elif f_num == "5.2":
                    f_key = "f_ablation"
                elif f_num == "5.3":
                    f_key = "f_benchmark"
                elif f_num == "5.4":
                    f_key = "f_evasion"
                elif f_num == "5.6":
                    f_key = "f_containment"
                elif f_num == "6.1":
                    f_key = "f_benchmark"
                
                lines.append(f'  o.push(...fig("{f_num}", "{f_key}", "{f_cap}", 0.85));\n')
                i += 1
                continue
                
            # Check for Headings
            if style == 'Heading 1' or txt.startswith('CHAPTER'):
                lines.append(f'  o.push(h1(`{clean_str(txt)}`));\n')
                i += 1
                continue
            elif style == 'Heading 2' or re.match(r'^[1-9]\.\s+[A-Z\s]{3,}', txt):
                lines.append(f'  o.push(h2(`{clean_str(txt)}`));\n')
                i += 1
                continue
            elif style == 'Heading 3' or re.match(r'^(?:[ivx]+\.|[1-9]\.[0-9]+)\s+', txt):
                lines.append(f'  o.push(h3(`{clean_str(txt)}`));\n')
                i += 1
                continue
                
            # Check for List Bullet / List Paragraph
            if style in ('List Paragraph', 'List Bullet') or txt.startswith('•') or txt.startswith('- '):
                # Collect all contiguous bullet items
                bullet_items = []
                while i < n and elems[i]['type'] == 'p' and (elems[i].get('style') in ('List Paragraph', 'List Bullet') or elems[i]['text'].startswith('•') or elems[i]['text'].startswith('- ')):
                    b_txt = elems[i]['text']
                    if b_txt.startswith('•') or b_txt.startswith('- '):
                        b_txt = b_txt[2:].strip()
                    bullet_items.append(clean_str(b_txt))
                    i += 1
                items_js = json.dumps(bullet_items, ensure_ascii=False)
                lines.append(f'  o.push(...bullets({items_js}));\n')
                continue
                
            # Normal paragraph
            # Check if it looks like code block (e.g. imports, defs)
            if style == 'HTML Preformatted' or txt.startswith('def ') or txt.startswith('import ') or txt.startswith('class ') or txt.startswith('apiVersion:'):
                lines.append(f'  o.push(p(`{clean_str(txt)}`, {{ line: 240, font: "Consolas", size: 20 }}));\n')
            else:
                lines.append(f'  o.push(p(`{clean_str(txt)}`));\n')
            i += 1
            
    return "".join(lines)

print("Parser function compiled successfully.")
