import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('LogShield_Final_Report_backup.docx') as z:
    rels_xml = z.read('word/_rels/document.xml.rels')
    root = ET.fromstring(rels_xml)
    rId_to_target = {}
    for rel in root:
        rId = rel.attrib.get('Id')
        target = rel.attrib.get('Target')
        rId_to_target[rId] = target

    doc_xml = z.read('word/document.xml')
    doc_root = ET.fromstring(doc_xml)
    
    # Iterate through paragraphs and find blip r:embed
    for p in doc_root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        p_text = ''.join(p.itertext()).strip()
        blips = [el.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') 
                 for el in p.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')]
        blips = [b for b in blips if b]
        if blips:
            media_files = [rId_to_target.get(b, '') for b in blips]
            print(f'P text: "{p_text[:70]}" -> Embed: {blips} -> Media: {media_files}')
