import win32com.client
import os

word = win32com.client.Dispatch('Word.Application')
word.Visible = True
docx_path = os.path.abspath('LogShield_IEEE_Paper_Official.docx')
print("Opening docx in visible Word window...", flush=True)
try:
    doc = word.Documents.Open(docx_path)
    print("Opened successfully!", flush=True)
    pdf_path = os.path.abspath('LogShield_IEEE_Paper_Official.pdf')
    print("Saving PDF...", flush=True)
    doc.SaveAs(pdf_path, FileFormat=17)
    print("Saved PDF successfully!", flush=True)
    doc.Close(False)
except Exception as e:
    print("Error:", e, flush=True)
finally:
    word.Quit()
    print("Done.", flush=True)
