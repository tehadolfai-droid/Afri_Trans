"""
Phase 1: Fix structural issues in REVIVAL INNOVATION HUB report.
- Merge two introductions into one
- Remove "Internship project report" subheading
- Merge sections 9.4 and 9.7 (duplicate race condition)
- Renumber sections 9.8-9.17 after merge
- Renumber section 9.10 -> 9.9 etc.
"""
import sys, io, shutil, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FIXED.docx'
out = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FINAL.docx'
shutil.copy2(src, out)
doc = Document(out)

def remove_paragraph(p):
    """Remove a paragraph element from the document."""
    parent = p._element.getparent()
    parent.remove(p._element)

def replace_text_preserve_style(p, new_text):
    """Replace all text in a paragraph, keeping the first run's formatting."""
    if not p.runs:
        return
    first_run = p.runs[0]
    for run in p.runs[1:]:
        run.text = ''
    first_run.text = new_text

changes = 0

# ══════════════════════════════════════════════════════════════
# FIX 1: Merge two introductions into one
# ══════════════════════════════════════════════════════════════
# Keep paragraphs 41-46 (general intro about RIT-VTC, Ferdsilinks context)
# Replace "1. Introduction" heading (para 65) with merged content
# Remove paragraphs 64-68 (second intro + "Internship project report")

# First, remove "Internship project report" subheading (para 64)
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == 'Internship project report':
        remove_paragraph(p)
        changes += 1
        print(f"FIX 1a: Removed 'Internship project report' subheading")
        break

# Now update the first INTRODUCTION (para 41) to include AFRI-Trans context
# Find the INTRODUCTION heading
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == 'INTRODUCTION':
        # Replace the intro paragraphs with a merged version
        # Para 42: general intro about internships
        # Para 43: RIT-VTC + Ferdsilinks context
        # Para 44: AFRI-Trans project description
        # Para 45: technical integration
        # Para 46: report documents experience
        # We keep these as-is, they already flow well
        print(f"FIX 1b: INTRODUCTION section kept (already good)")
        break

# Remove the DUPLICATE "1. Introduction" heading and its content (paras 65-76)
# These paragraphs repeat what's already in the first introduction
to_remove_intro = []
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == '1. Introduction' and i > 50:
        # Found the second introduction heading
        # Remove this heading and the content until "2. Problem Statement"
        to_remove_intro.append(p)
        for j in range(i+1, min(i+15, len(doc.paragraphs))):
            next_p = doc.paragraphs[j]
            if next_p.text.strip().startswith('2. Problem Statement'):
                break
            to_remove_intro.append(next_p)
        break

for p in to_remove_intro:
    remove_paragraph(p)
    changes += 1
print(f"FIX 1c: Removed duplicate introduction content ({len(to_remove_intro)} paragraphs)")

# ══════════════════════════════════════════════════════════════
# FIX 2: Merge sections 9.4 and 9.7 (duplicate race condition)
# ══════════════════════════════════════════════════════════════
# Section 9.4 (short version) at paragraph ~591
# Section 9.7 (detailed version) at paragraph ~618
# Strategy: Replace 9.4 content with 9.7's detailed content, remove 9.7

# Find 9.4 heading and 9.7 heading
sec_94_start = None
sec_97_start = None
sec_98_start = None

for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if txt == '9.4 Concurrent Booking Race Conditions':
        sec_94_start = i
    elif txt == '9.7 Concurrent Seat Booking (Race Condition)':
        sec_97_start = i
    elif txt == '9.8 Missing Feedback System':
        sec_98_start = i

if sec_94_start and sec_97_start and sec_98_start:
    # Update 9.4 heading to match 9.7's better title
    for p in doc.paragraphs:
        if p.text.strip() == '9.4 Concurrent Booking Race Conditions':
            replace_text_preserve_style(p, '9.4 Concurrent Seat Booking (Race Conditions)')
            changes += 1
            print("FIX 2a: Updated 9.4 heading")
            break
    
    # Replace 9.4 content (paragraphs after heading until next heading)
    # with 9.7's detailed content
    # First find 9.4 content range
    sec_94_content = []
    for j in range(sec_94_start + 1, sec_97_start):
        txt = doc.paragraphs[j].text.strip()
        if txt.startswith('9.5') or txt.startswith('9.6'):
            break
        sec_94_content.append(doc.paragraphs[j])
    
    # Find 9.7 content range
    sec_97_content = []
    for j in range(sec_97_start + 1, sec_98_start):
        sec_97_content.append(doc.paragraphs[j])
    
    # Remove old 9.4 content
    for p in sec_94_content:
        remove_paragraph(p)
        changes += 1
    
    # Insert 9.7's detailed content after 9.4 heading
    # We need to insert after the 9.4 heading element
    heading_elem = doc.paragraphs[sec_94_start]._element
    for cp in reversed(sec_97_content):
        heading_elem.addnext(copy.deepcopy(cp._element))
        changes += 1
    
    # Now remove the entire 9.7 section (heading + remaining content)
    # Find 9.7 heading again (may have shifted)
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == '9.7 Concurrent Seat Booking (Race Condition)':
            remove_paragraph(p)
            changes += 1
            # Remove content until 9.8
            while i < len(doc.paragraphs):
                if doc.paragraphs[i].text.strip().startswith('9.8'):
                    break
                remove_paragraph(doc.paragraphs[i])
                changes += 1
            break
    
    print(f"FIX 2b: Merged 9.4 and 9.7 into single section")

# ══════════════════════════════════════════════════════════════
# FIX 3: Renumber sections 9.5 onwards after merge
# ══════════════════════════════════════════════════════════════
# After merging 9.4+9.7, we need to renumber:
# Old 9.5 -> 9.5 (stays)
# Old 9.6 -> 9.6 (stays)
# Old 9.8 -> 9.7
# Old 9.9 -> 9.8
# Old 9.10 -> 9.9
# Old 9.11 -> 9.10
# Old 9.12 -> 9.11
# Old 9.13 -> 9.12
# Old 9.14 -> 9.13
# Old 9.15 -> 9.14
# Old 9.16 -> 9.15
# Old 9.17 -> 9.16

renumber_map = {
    '9.8 Missing Feedback System': '9.7 Missing Feedback System',
    '9.9 Bell Icon Colour Inconsistency': '9.8 Bell Icon Colour Inconsistency',
    '9.10 One-Time Shared Password Security': '9.9 One-Time Shared Password Security',
    '9.11 Bilingual Announcement Translation': '9.10 Bilingual Announcement Translation',
    '9.12 Session Staleness and Logout Cleanup': '9.11 Session Staleness and Logout Cleanup',
    '9.13 Translation Auto-Generation Timeout': '9.12 Translation Auto-Generation Timeout',
    '9.14 Country Auto-Detection Accuracy': '9.13 Country Auto-Detection Accuracy',
    '9.15 TOCTOU Race Condition in Agency Registration': '9.14 TOCTOU Race Condition in Agency Registration',
    '9.16 Booking Reference Counter Race': '9.15 Booking Reference Counter Race',
    '9.17 Free Departure Notification Delivery': '9.16 Free Departure Notification Delivery',
}

for p in doc.paragraphs:
    txt = p.text.strip()
    if txt in renumber_map:
        replace_text_preserve_style(p, renumber_map[txt])
        changes += 1

print(f"FIX 3: Renumbered sections 9.7-9.16")

# ══════════════════════════════════════════════════════════════
# FIX 4: Remove trailing "Scaling further" orphan paragraph
# ══════════════════════════════════════════════════════════════
for i, p in enumerate(doc.paragraphs):
    if p.text.strip().startswith('Scaling further: For Facebook-scale traffic'):
        remove_paragraph(p)
        changes += 1
        print("FIX 4: Removed orphan 'Scaling further' paragraph")
        break

# ══════════════════════════════════════════════════════════════
# FIX 5: Update Table of Contents reference in section headings
# ══════════════════════════════════════════════════════════════
# The TOC isn't in the docx paragraphs (it's a field), but we should
# ensure section numbering is consistent

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════
doc.save(out)
print(f"\n{'='*50}")
print(f"Phase 1 complete: {changes} changes")
print(f"Saved to: {out}")
