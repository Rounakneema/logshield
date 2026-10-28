import win32com.client
import os

docx_path = os.path.abspath(r'd:\LOGSHEILD\LogShield_IEEE_Paper_Official.docx')
pdf_path = os.path.abspath(r'd:\LOGSHEILD\LogShield_IEEE_Paper_Official.pdf')

word = win32com.client.Dispatch('Word.Application')
word.Visible = False

try:
    print(f'Opening: {docx_path}')
    doc = word.Documents.Open(docx_path)
    
    # Check sections count
    print(f'Number of sections: {doc.Sections.Count}')
    sec1 = doc.Sections(1)
    print(f'Sec 1 Columns: {sec1.PageSetup.TextColumns.Count}')
    if doc.Sections.Count > 1:
        sec2 = doc.Sections(2)
        print(f'Sec 2 Columns: {sec2.PageSetup.TextColumns.Count}')
    
    print(f'Page count: {doc.ComputeStatistics(2)}') # 2 = wdStatisticPages
    
    # Save as PDF (wdFormatPDF = 17)
    print(f'Exporting PDF: {pdf_path}')
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close(False)
    print(f'Exported PDF successfully! Size: {os.path.getsize(pdf_path)} bytes')
finally:
    word.Quit()
