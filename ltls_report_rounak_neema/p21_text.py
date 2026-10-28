import win32com.client
import os

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    doc = word.Documents.Open(os.path.abspath('ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.docx'))
    print("Total paragraphs:", len(doc.Paragraphs))
    for p in doc.Paragraphs:
        if p.Range.Information(3) == 21: # Page 21
            t = p.Range.Text.strip()
            if t:
                print("P21 text:", t[:80])
    doc.Close(False)
finally:
    word.Quit()
