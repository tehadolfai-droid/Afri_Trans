"""Analyse image positions in the original docx."""
import zipfile
import xml.etree.ElementTree as ET

DOCX = 'AFRI_Trans_reports.docx'

# Read relationships to map rId -> image filename
rels = {}
with zipfile.ZipFile(DOCX) as z:
    # Parse document.xml.rels
    rels_xml = z.read('word/_rels/document.xml.rels')
    rel_root = ET.fromstring(rels_xml)
    ns_rels = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    for rel in rel_root:
        rid = rel.get('Id')
        target = rel.get('Target')
        if target and 'media' in target:
            rels[rid] = target.replace('media/', '')

    # Parse document.xml
    xml = z.read('word/document.xml')
    root = ET.fromstring(xml)

    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    }

    # Walk through body
    body = root.find('w:body', ns)
    for elem in body.iter():
        # Find drawing elements
        blips = elem.findall('.//a:blip', ns)
        for blip in blips:
            embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            img_name = rels.get(embed, 'unknown')
            # Find preceding paragraph text
            texts = []
            for t in elem.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text: texts.append(t.text)
            print(f'{embed} -> {img_name}  -> context: {" ".join(texts)[:100]}')
