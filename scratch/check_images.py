import docx
import xml.etree.ElementTree as ET

doc = docx.Document('LogShield_Final_Report_backup.docx')
for p_idx, p in enumerate(doc.paragraphs):
    images = []
    for r in p.runs:
        if 'drawing' in r._r.xml:
            tree = ET.fromstring(r._r.xml)
            for elem in tree.iter():
                if elem.tag.endswith('blip'):
                    images.append(elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'))
    if images or 'Figure ' in p.text:
        print(f"P{p_idx}: text='{p.text[:60]}' | images={images}")
