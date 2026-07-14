"""
Phase 6: Add Background section (new section 1) + TOC
- Insert "1. Background" before current "1. Problem Statement"
- Renumber: Problem Statement -> 2, Objectives -> 3, etc.
- Insert Table of Contents with TOC field code
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FINAL_V2.docx'
doc = Document(src)
changes = 0

# ══════════════════════════════════════════════════════════════
# STEP 1: Renumber all sections +1 (1->2, 2->3, etc.)
# ══════════════════════════════════════════════════════════════
# Collect all heading paragraphs to avoid modifying during iteration
heading_paras = []
for p in doc.paragraphs:
    if p.style.name.startswith('Heading') and p.text.strip():
        heading_paras.append(p)

# Sort by level (deepest first to avoid substring conflicts)
heading_paras.sort(key=lambda p: -len(p.text.strip()))

for p in heading_paras:
    t = p.text.strip()
    
    # Match "N. Title" or "N.M Title" 
    m = re.match(r'^(\d+)\.(.*)', t)
    if not m:
        continue
    
    old_num = int(m.group(1))
    rest = m.group(2)
    new_num = old_num + 1
    
    new_text = f"{new_num}.{rest}"
    
    for run in p.runs:
        if f'{old_num}.' in run.text:
            run.text = run.text.replace(f'{old_num}.', f'{new_num}.', 1)
            changes += 1
            print(f"RENUMBER: '{t}' -> '{new_text}'")
            break

# ══════════════════════════════════════════════════════════════
# STEP 2: Insert Background section before current section 2
# ══════════════════════════════════════════════════════════════
# Find "2. Problem Statement" paragraph
target_para = None
for p in doc.paragraphs:
    if p.text.strip().startswith('2.') and 'Problem Statement' in p.text:
        target_para = p
        break

if target_para:
    # Insert BEFORE target_para using XML manipulation
    parent = target_para._element.getparent()
    idx = list(parent).index(target_para._element)
    
    # Create heading paragraph
    heading_el = OxmlElement('w:p')
    heading_rPr = OxmlElement('w:rPr')
    heading_style = OxmlElement('w:pStyle')
    heading_style.set(qn('w:val'), 'Heading2')
    heading_rPr.append(heading_style)
    heading_el.append(heading_rPr)
    
    heading_r = OxmlElement('w:r')
    heading_t = OxmlElement('w:t')
    heading_t.text = '1. Background'
    heading_r.append(heading_t)
    heading_el.append(heading_r)
    
    parent.insert(idx, heading_el)
    changes += 1
    print("INSERTED: '1. Background' heading")
    
    # Insert background content paragraphs
    bg_content = [
        "Inter-city bus travel is the primary mode of transportation for millions of Africans. However, most bus booking systems are paper-based, fragmented by country, or operated by individual agencies with no centralised platform. This creates several problems:",
    ]
    
    bg_bullets = [
        "Passengers must visit physical terminals to book tickets",
        "No way to compare prices across multiple agencies",
        "Limited payment options, often cash-only",
        "No standardised ticketing or booking records",
    ]
    
    # Re-find target since we inserted before it
    for p in doc.paragraphs:
        if p.text.strip().startswith('1. Background'):
            target_para = p
            break
    
    # Insert content after heading, before "2. Problem Statement"
    parent = target_para._element.getparent()
    insert_idx = list(parent).index(target_para._element) + 1
    
    for i, text in enumerate(bg_content):
        p_el = OxmlElement('w:p')
        r_el = OxmlElement('w:r')
        t_el = OxmlElement('w:t')
        t_el.text = text
        r_el.append(t_el)
        p_el.append(r_el)
        parent.insert(insert_idx + i, p_el)
        changes += 1
    
    # Add bullet points
    bullet_offset = insert_idx + len(bg_content)
    for i, text in enumerate(bg_bullets):
        p_el = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        numPr = OxmlElement('w:numPr')
        ilvl = OxmlElement('w:ilvl')
        ilvl.set(qn('w:val'), '0')
        numId = OxmlElement('w:numId')
        numId.set(qn('w:val'), '1')
        numPr.append(ilvl)
        numPr.append(numId)
        pPr.append(numPr)
        p_el.append(pPr)
        
        r_el = OxmlElement('w:r')
        t_el = OxmlElement('w:t')
        t_el.text = text
        r_el.append(t_el)
        p_el.append(r_el)
        parent.insert(bullet_offset + i, p_el)
        changes += 1
    
    # Add closing sentence after bullets
    close_offset = bullet_offset + len(bg_bullets)
    close_text = "AFRI-Trans aims to solve these problems by providing a single, multi-country platform where passengers can search, compare, book, and pay for bus tickets across any African country."
    p_el = OxmlElement('w:p')
    r_el = OxmlElement('w:r')
    t_el = OxmlElement('w:t')
    t_el.text = close_text
    r_el.append(t_el)
    p_el.append(r_el)
    parent.insert(close_offset, p_el)
    changes += 1
    
    total = 1 + len(bg_content) + len(bg_bullets) + 1
    print(f"INSERTED: Background section ({total} elements)")

# ══════════════════════════════════════════════════════════════
# STEP 3: Insert Table of Contents before ABSTRACT
# ══════════════════════════════════════════════════════════════
abstract_para = None
for p in doc.paragraphs:
    if p.text.strip() == 'ABSTRACT':
        abstract_para = p
        break

if abstract_para:
    parent = abstract_para._element.getparent()
    idx = list(parent).index(abstract_para._element)
    
    # Add "TABLE OF CONTENTS" heading
    toc_heading = OxmlElement('w:p')
    toc_rPr = OxmlElement('w:rPr')
    toc_style = OxmlElement('w:pStyle')
    toc_style.set(qn('w:val'), 'Heading1')
    toc_rPr.append(toc_style)
    toc_heading.append(toc_rPr)
    
    toc_r = OxmlElement('w:r')
    toc_t = OxmlElement('w:t')
    toc_t.text = 'TABLE OF CONTENTS'
    toc_r.append(toc_t)
    toc_heading.append(toc_r)
    parent.insert(idx, toc_heading)
    changes += 1
    print("INSERTED: 'TABLE OF CONTENTS' heading")
    
    # Insert TOC field code paragraph (generates TOC when opened in Word)
    toc_field = OxmlElement('w:p')
    
    # Create TOC field
    fldChar_begin = OxmlElement('w:fldChar')
    fldChar_begin.set(qn('w:fldCharType'), 'begin')
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
    
    fldChar_separate = OxmlElement('w:fldChar')
    fldChar_separate.set(qn('w:fldCharType'), 'separate')
    
    fldChar_end = OxmlElement('w:fldChar')
    fldChar_end.set(qn('w:fldCharType'), 'end')
    
    r1 = OxmlElement('w:r')
    r1.append(fldChar_begin)
    toc_field.append(r1)
    
    r2 = OxmlElement('w:r')
    r2.append(instrText)
    toc_field.append(r2)
    
    r3 = OxmlElement('w:r')
    r3.append(fldChar_separate)
    toc_field.append(r3)
    
    # Placeholder text
    r4 = OxmlElement('w:r')
    t4 = OxmlElement('w:t')
    t4.text = '[Right-click and select "Update Field" to generate Table of Contents]'
    r4.append(t4)
    toc_field.append(r4)
    
    r5 = OxmlElement('w:r')
    r5.append(fldChar_end)
    toc_field.append(r5)
    
    parent.insert(idx + 1, toc_field)
    changes += 1
    print("INSERTED: TOC field code")

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════
out = src.replace('_V2.docx', '_V3.docx')
doc.save(out)
print(f"\n{'='*50}")
print(f"Phase 6 complete: {changes} changes")
print(f"Saved to: {out}")

# ══════════════════════════════════════════════════════════════
# VERIFY
# ══════════════════════════════════════════════════════════════
doc2 = Document(out)
print("\n=== Final heading structure ===")
for p in doc2.paragraphs:
    if p.style.name.startswith('Heading'):
        print(f"  [{p.style.name}] {p.text.strip()[:80]}")
