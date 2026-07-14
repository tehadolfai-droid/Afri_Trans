"""Verify the final structure and content quality of the output document."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('AFRI_Trans_Report_2026.docx')

# Show full structure around the fixed areas
print('=== Sections 7.17 → 7.23 (correct order check) ===')
capture = False
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    sn = p.style.name if p.style else ''
    if '7.17 IP Geolocation' in t:
        capture = True
    if capture and i < 550:
        if t:
            # Show every paragraph with style info
            prefix = '→' if sn == 'Heading 3' else ' '
            print(f'{prefix} [{sn:12s}] {t[:120]}')
    if capture and '9.' in t[:5] and sn == 'Heading 2':
        break

print('\n=== Sections 9.14 → 9.17 (correct order check) ===')
capture = False
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    sn = p.style.name if p.style else ''
    if '9.14 Country Auto-Detection' in t:
        capture = True
    if capture and i < 620:
        if t:
            prefix = '→' if sn == 'Heading 3' else ' '
            print(f'{prefix} [{sn:12s}] {t[:120]}')
    if capture and '10.' in t[:5] and sn == 'Heading 2':
        break

# Count images
print(f'\nImages: {len(doc.inline_shapes)}')
print(f'Total paragraphs: {len(doc.paragraphs)}')
print(f'Total characters: {sum(len(p.text) for p in doc.paragraphs):,}')
