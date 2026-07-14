"""
Phase 5: Fix section numbering - shift 2->1 through 12->11
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FINAL.docx'
doc = Document(src)
changes = 0

# Also fix "User Roles" (unnumbered heading 3 under section 5)
# It should be 5.3 or similar

for p in doc.paragraphs:
    t = p.text.strip()
    if not p.style.name.startswith('Heading'):
        continue
    
    # Fix "User Roles" -> "5.3 User Roles"  
    if t == 'User Roles':
        for run in p.runs:
            if 'User' in run.text:
                run.text = '5.3 User Roles'
                changes += 1
                print(f"FIX: 'User Roles' -> '5.3 User Roles'")
                break
        continue
    
    # Match numbered headings: "N." or "N.M"
    m = re.match(r'^(\d+)\.(.*)', t)
    if not m:
        continue
    
    old_num = int(m.group(1))
    rest = m.group(2)
    new_num = old_num - 1
    
    if new_num < 1:
        print(f"  SKIP: '{t}' would become 0.")
        continue
    
    new_text = f"{new_num}.{rest}"
    
    # Replace in runs
    for run in p.runs:
        if f'{old_num}.' in run.text:
            run.text = run.text.replace(f'{old_num}.', f'{new_num}.', 1)
            changes += 1
            print(f"RENUMBER: '{t}' -> '{new_text}'")
            break

out = src.replace('.docx', '_V2.docx')
doc.save(out)
print(f"\n{'='*50}")
print(f"Phase 5 complete: {changes} changes")
print(f"Saved to: {out}")

# Verify
doc2 = Document(out)
print("\n=== All headings after renumbering ===")
for p in doc2.paragraphs:
    if p.style.name.startswith('Heading'):
        print(f"  [{p.style.name}] {p.text.strip()[:80]}")
