import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
doc=Document('AFRI_Trans_reports.docx')
for i,p in enumerate(doc.paragraphs):
    t=p.text.strip()
    if not t: continue
    for kw in ['7.17','7.18','7.19','7.20','7.21','7.22','7.23','9.14','9.15','9.16','9.17']:
        if kw in t:
            s=p.style.name if p.style else 'None'
            print(f'i={i:3d}  style={s:15s}  {t[:100]}')
            break
