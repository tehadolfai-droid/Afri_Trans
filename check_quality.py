"""Show full body content of expanded sections to verify writing quality."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('AFRI_Trans_Report_2026.docx')

sections = ['7.18', '7.19', '7.20', '7.21', '7.22', '7.23', '9.15', '9.16', '9.17']
capture = None
body_lines = []

for p in doc.paragraphs:
    t = p.text.strip()
    sn = p.style.name if p.style else ''
    
    if sn == 'Heading 3':
        for s in sections:
            if t.startswith(s + ' '):
                # Print previous section body
                if capture and body_lines:
                    print(f'\n--- {capture} body ---')
                    for line in body_lines:
                        print(f'  {line}')
                capture = s
                body_lines = []
                print(f'\n► {t}')
                break
    elif capture and sn == 'Normal' and t:
        body_lines.append(t)
    elif capture and sn == 'Heading 3' and not any(t.startswith(s+' ') for s in sections):
        if capture and body_lines:
            print(f'\n--- {capture} body ---')
            for line in body_lines:
                print(f'  {line}')
        capture = None
        body_lines = []

# Print last section
if capture and body_lines:
    print(f'\n--- {capture} body ---')
    for line in body_lines:
        print(f'  {line}')
