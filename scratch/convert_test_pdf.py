import os
import win32com.client
import pymupdf as fitz

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
doc = word.Documents.Open(os.path.abspath('scratch/test_section_breaks.docx'))
doc.SaveAs(os.path.abspath('scratch/test_section_breaks.pdf'), FileFormat=17)
doc.Close()
word.Quit()

pdf = fitz.open('scratch/test_section_breaks.pdf')
print('Pages in test PDF:', len(pdf))
for i, p in enumerate(pdf):
    print(f'Page {i+1} blocks: {len(p.get_text("blocks"))}')
