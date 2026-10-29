import os
import sys
import docx

print("Exporting LogShield_Final_Report_Complete.docx to LogShield_Final_Report_Complete.md...")

doc = docx.Document(r"D:\LOGSHEILD\LogShield_Final_Report_Complete.docx")

md_lines = []

for el in doc.element.body:
    tag = el.tag.split("}")[-1]
    if tag == "p":
        p = docx.text.paragraph.Paragraph(el, doc)
        txt = p.text.strip()
        style = p.style.name if p.style else "Normal"
        if not txt:
            # only add empty line if previous line wasn't empty
            if md_lines and md_lines[-1] != "":
                md_lines.append("")
            continue
        
        if style == "Heading 1":
            md_lines.append(f"\n# {txt}\n")
        elif style == "Heading 2":
            md_lines.append(f"\n## {txt}\n")
        elif style == "Heading 3":
            md_lines.append(f"\n### {txt}\n")
        elif style == "List Paragraph":
            md_lines.append(f"- {txt}")
        elif style == "Caption" or txt.startswith("Figure ") or txt.startswith("Table "):
            md_lines.append(f"\n*{txt}*\n")
        else:
            md_lines.append(f"{txt}\n")
            
    elif tag == "tbl":
        tbl = docx.table.Table(el, doc)
        # Check if single cell code listing
        if len(tbl.rows) == 1 and len(tbl.columns) == 1:
            code_text = tbl.rows[0].cells[0].text.strip()
            md_lines.append("\n```python\n" + code_text + "\n```\n")
        else:
            # Regular data table
            table_md = []
            headers = [c.text.strip().replace("\n", " ") for c in tbl.rows[0].cells]
            table_md.append("| " + " | ".join(headers) + " |")
            table_md.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in tbl.rows[1:]:
                row_cells = [c.text.strip().replace("\n", "<br>") for c in row.cells]
                table_md.append("| " + " | ".join(row_cells) + " |")
            md_lines.append("\n" + "\n".join(table_md) + "\n")

out_md = r"D:\LOGSHEILD\LogShield_Final_Report_Complete.md"
full_md = "\n".join(md_lines)
with open(out_md, "w", encoding="utf-8") as f:
    f.write(full_md)

print(f"Successfully saved complete report to: {out_md}")
print(f"File size: {os.path.getsize(out_md)} bytes")
print(f"Total lines: {len(md_lines)}")
