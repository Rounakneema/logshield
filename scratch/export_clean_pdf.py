import win32com.client
import os
import sys

docx_path = os.path.abspath(r'd:\LOGSHEILD\LogShield_IEEE_Paper_Official.docx')
pdf_path = os.path.abspath(r'd:\LOGSHEILD\LogShield_IEEE_Paper_Official.pdf')

print("Starting Word Dispatch...", flush=True)
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0 # wdAlertsNone

try:
    print(f"Opening: {docx_path}", flush=True)
    doc = word.Documents.Open(
        FileName=docx_path,
        ConfirmConversions=False,
        ReadOnly=True,
        AddToRecentFiles=False,
        Visible=False
    )
    
    print(f"Sections: {doc.Sections.Count}, Pages: {doc.ComputeStatistics(2)}", flush=True)
    
    # Save as PDF
    print(f"Saving PDF to: {pdf_path}", flush=True)
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close(False)
    print(f"Export successful! File size: {os.path.getsize(pdf_path)} bytes", flush=True)
finally:
    word.Quit()
    print("Word application terminated cleanly.", flush=True)
