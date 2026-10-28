import win32com.client
import os

docx_path = os.path.abspath(r'd:\LOGSHEILD\LogShield_IEEE_Paper_Official.docx')
pdf_path = os.path.abspath(r'd:\LOGSHEILD\LogShield_IEEE_Paper_Official.pdf')

word = win32com.client.Dispatch('Word.Application')
word.Visible = False

try:
    print(f'Opening: {docx_path}', flush=True)
    doc = word.Documents.Open(docx_path)
    print(f'Sections: {doc.Sections.Count}', flush=True)
    print(f'Page count: {doc.ComputeStatistics(2)}', flush=True)
    print(f'Exporting PDF: {pdf_path}', flush=True)
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close(False)
    print(f'Exported PDF successfully! Size: {os.path.getsize(pdf_path)} bytes', flush=True)
finally:
    word.Quit()
