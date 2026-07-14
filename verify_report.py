import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

doc = Document(r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FIXED.docx')

print('=== FINAL VERIFICATION ===')

# 1. Typos
for label, term in [('Ethnologies', 'Ethnologies'), ('mobilemone typo', 'mobilemone '), ('DEFAULT 70', 'DEFAULT 70'), ('Xhtml2pdf', 'Xhtml2pdf')]:
    found = any(term in p.text for p in doc.paragraphs)
    print(f'{"FAIL" if found else "OK"}: Typo "{label}"')

# 2. Markdown artifacts
md_found = False
for p in doc.paragraphs:
    if '~~' in p.text:
        md_found = True
        print(f'FAIL: ~~ in: {p.text[:60]}')
print(f'{"FAIL" if md_found else "OK"}: No ~~ strikethrough artifacts')

# 3. Duplicate race condition block
count = sum(1 for p in doc.paragraphs if 'This is the same concurrency problem Facebook' in p.text)
print(f'{"OK" if count <= 1 else "FAIL"}: Race condition block appears {count} time(s)')

# 4. Screenshot placeholder
old_ph = sum(1 for p in doc.paragraphs if '4-6 key screens' in p.text)
new_ph = sum(1 for p in doc.paragraphs if 'Screenshots to be inserted' in p.text)
print(f'{"OK" if old_ph == 0 else "FAIL"}: Old placeholder removed')
print(f'{"OK" if new_ph > 0 else "FAIL"}: New placeholder added')

# 5. Capacity default
cap_ok = not any('DEFAULT 70' in p.text for p in doc.paragraphs)
print(f'{"OK" if cap_ok else "FAIL"}: Bus capacity default is 71')

# 6. Summary duplicates
seen = {}
dupes = 0
for i, p in enumerate(doc.paragraphs):
    if 715 <= i <= 735 and p.text.strip():
        key = p.text.strip()[:50]
        if key in seen:
            dupes += 1
        seen[key] = i
print(f'{"OK" if dupes == 0 else "FAIL"}: {dupes} duplicate summary items')

# 7. Sections
headings = [p.text.strip() for p in doc.paragraphs if p.style.name.startswith('Heading')]
print(f'OK: {len(headings)} headings')

# 8. Stats
total = len(doc.paragraphs)
non_empty = sum(1 for p in doc.paragraphs if p.text.strip())
print(f'OK: {total} paragraphs, {non_empty} non-empty')
print()
print('File: REVIVAL_INNOVATION_HUB_FIXED.docx')
