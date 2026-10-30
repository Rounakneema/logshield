import win32com.client
import os

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    doc = word.Documents.Open(os.path.abspath('ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.docx'))
    pages = doc.ComputeStatistics(2)
    print("Total pages in doc:", pages)
    # Check paragraphs with page breaks
    for i, p in enumerate(doc.Paragraphs):
        txt = p.Range.Text.strip()
        if 'CHAPTER' in txt or 'CERTIFICATE' in txt or 'DECLARATION' in txt or 'EXECUTIVE' in txt or 'TABLE OF CONTENTS' in txt:
            # get page number of this paragraph
            page_num = p.Range.Information(3) # 3 = wdActiveEndPageNumber
            print(f"Page {page_num}: {txt[:40]}")
    doc.Close(False)
finally:
    word.Quit()
