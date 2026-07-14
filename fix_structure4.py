"""
Phase 4: Fix section 7 numbering - robust run-based approach
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FINAL.docx'
doc = Document(src)
changes = 0

# Map old headings to new
renumber = {
    '7.10 User Interface & Responsive Design': ('7.10', '7.7'),
    '7.8 Agency Privacy & Security': (None, None),  # already correct after renumber below
    '7.7 Payment & Monetisation': ('7.7', '7.9'),
    '7.9 Communication & Feedback': ('7.9', '7.10'),
}

# First pass: collect all section 7 headings
sec7_headings = []
for p in doc.paragraphs:
    txt = p.text.strip()
    if p.style.name.startswith('Heading') and txt.startswith('7.'):
        sec7_headings.append(p)

# Step 1: Rename 7.7 -> 7.9 (Payment), 7.9 -> 7.10 (Feedback), 7.10 -> 7.7 (UI)
# Do in reverse to avoid collisions
rename_map = [
    ('7.10 User Interface & Responsive Design', '7.7 User Interface & Responsive Design'),
    ('7.9 Communication & Feedback', '7.10 Communication & Feedback'),
    ('7.7 Payment & Monetisation', '7.9 Payment & Monetisation'),
]

for old_full, new_full in rename_map:
    old_num = old_full.split(' ')[0]
    new_num = new_full.split(' ')[0]
    new_label = new_full[len(new_num)+1:]
    
    for p in sec7_headings:
        if p.text.strip() == old_full:
            # Replace the number in the runs
            full_text = p.text.strip()
            # Find which run has the number
            for run in p.runs:
                if old_num in run.text:
                    run.text = run.text.replace(old_num, new_num, 1)
                    changes += 1
                    print(f"RENAMED: '{old_full}' -> '{new_full}'")
                    break
            break

doc.save(src)
print(f"\n{'='*50}")
print(f"Phase 4 complete: {changes} changes")
print(f"Saved to: {src}")

# Verify
doc2 = Document(src)
print("\n=== Section 7 headings after fix ===")
for p in doc2.paragraphs:
    t = p.text.strip()
    if t.startswith('7.') and p.style.name.startswith('Heading'):
        print(f"  {t}")
