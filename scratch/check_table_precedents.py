import io
import sys
import docx
from docx.text.paragraph import Paragraph
from docx.table import Table

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = docx.Document(r'C:\Users\Asus\.gemini\antigravity\brain\236c4749-0fde-4dca-8814-d7425598de3f\.user_uploaded\media_1793188527179_7471e50a.docx')

body_children = list(doc.element.body)
tbl_count = 0
for idx, child in enumerate(body_children):
    if child.tag.endswith('tbl'):
        tbl = Table(child, doc)
        prev_p = ''
        for p_i in range(idx - 1, -1, -1):
            if body_children[p_i].tag.endswith('p'):
                prev_p = Paragraph(body_children[p_i], doc).text.strip()
                if prev_p:
                    break
        print(f"Table index {tbl_count} (rows={len(tbl.rows)}, cols={len(tbl.columns)}) preceded by: '{prev_p[:65]}'")
        tbl_count += 1
