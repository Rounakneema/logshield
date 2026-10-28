import win32com.client
import os

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    doc = word.Documents.Open(os.path.abspath('ltls_report_rounak_neema/ROUNAK_NEEMA_E244_LTLS_PROJECT_REPORT.docx'))
    print("Total pages in doc:", doc.ComputeStatistics(2))
    
    # Check what is on each page
    pages_dict = {}
    for p in doc.Paragraphs:
        pg = p.Range.Information(3)
        txt = p.Range.Text.strip()
        if txt:
            if pg not in pages_dict:
                pages_dict[pg] = []
            pages_dict[pg].append(txt[:50])
            
    for pg in sorted(pages_dict.keys()):
        print(f"--- PAGE {pg} ({len(pages_dict[pg])} items) ---")
        print("  Top:   ", pages_dict[pg][0])
        print("  Bottom:", pages_dict[pg][-1])
        
    doc.Close(False)
finally:
    word.Quit()
