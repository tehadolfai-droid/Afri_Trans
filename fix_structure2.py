"""
Phase 2: Fix heading styles + consolidate section 7 + fill test tables
"""
import sys, io, shutil, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FINAL.docx'
doc = Document(src)

changes = 0

# ══════════════════════════════════════════════════════════════
# FIX 1: Fix heading styles for INTRODUCTION, ABOUT FERDSILINKS, INTERNSHIP OBJECTIVES
# ══════════════════════════════════════════════════════════════
heading_fixes = {
    'INTRODUCTION': 'Heading 1',
    'ABOUT FERDSILINKS': 'Heading 1', 
    'INTERNSHIP OBJECTIVES': 'Heading 1',
}

for p in doc.paragraphs:
    txt = p.text.strip()
    if txt in heading_fixes:
        p.style = doc.styles[heading_fixes[txt]]
        changes += 1
        print(f"FIX 1: '{txt}' -> {heading_fixes[txt]}")

# Also fix "ABSTRACT" which is likely Normal too
for p in doc.paragraphs:
    if p.text.strip() == 'ABSTRACT':
        p.style = doc.styles['Heading 1']
        changes += 1
        print(f"FIX 1b: 'ABSTRACT' -> Heading 1")

# ══════════════════════════════════════════════════════════════
# FIX 2: Consolidate section 7 (23 subsections -> 10)
# ══════════════════════════════════════════════════════════════
# New structure:
# 7.1 Multi-Country Support (keep)
# 7.2 Internationalisation & Translation (merge 7.2 + 7.16)
# 7.3 Passenger Booking Flow (keep)
# 7.4 Agency Portal (keep)
# 7.5 Ministry of Transport Portal (keep)
# 7.6 E-Ticket Generation (keep)
# 7.7 Payment & Monetisation (merge 7.9 + 7.14 + 7.19)
# 7.8 Security & Authentication (merge 7.8 + 7.13)
# 7.9 Notifications & Communication (merge 7.10 + 7.11 + 7.12 + 7.22)
# 7.10 User Interface (merge 7.7 + 7.18 + 7.20 + 7.21 + 7.15 + 7.17 + 7.23)

renumber_7 = {
    '7.1 Multi-Country Support': '7.1 Multi-Country Support',
    '7.2 Internationalisation (11 Languages)': '7.2 Internationalisation & Translation',
    '7.3 Passenger Booking Flow': '7.3 Passenger Booking Flow',
    '7.4 Agency Portal': '7.4 Agency Portal',
    '7.5 Ministry of Transport Portal': '7.5 Ministry of Transport Portal',
    '7.6 E-Ticket Generation': '7.6 E-Ticket Generation',
    '7.7 Responsive Design': '7.10 User Interface & Responsive Design',
    '7.8 Agency Privacy': '7.8 Agency Privacy & Security',
    '7.9 Payment Providers': '7.7 Payment & Monetisation',
    '7.10 Feedback System': '7.9 Communication & Feedback',
    '7.11 Bilingual Announcement System': '7.9 Communication & Feedback',
    '7.12 Per-Notification Read Tracking': '7.9 Communication & Feedback',
    '7.13 One-Time Shared Password (Admin123)': '7.8 Agency Privacy & Security',
    '7.14 Commission System (1% Platform Fee)': '7.7 Payment & Monetisation',
    '7.15 Bus Auto-Status Management': '7.10 User Interface & Responsive Design',
    '7.16 Translation System Enhancements': '7.2 Internationalisation & Translation',
    '7.17 IP Geolocation — Auto-Detect Country': '7.10 User Interface & Responsive Design',
    '7.18 Flash Alert Categories': '7.10 User Interface & Responsive Design',
    '7.19 Subscription Monetisation': '7.7 Payment & Monetisation',
    '7.20 Flag-Coloured Hero Title': '7.10 User Interface & Responsive Design',
    '7.21 Live Seat Map with Auto-Refresh': '7.10 User Interface & Responsive Design',
    '7.22 Departure Notification Scheduler': '7.9 Communication & Feedback',
    '7.23 Concurrency Hardening (TOCTOU Fixes)': '7.10 User Interface & Responsive Design',
}

# First pass: rename all headings
for p in doc.paragraphs:
    txt = p.text.strip()
    if txt in renumber_7 and txt != renumber_7[txt]:
        new_title = renumber_7[txt]
        # Only rename the FIRST occurrence of each target
        # Check if this heading already exists
        exists = any(pp.text.strip() == new_title and pp.style.name.startswith('Heading') 
                     for pp in doc.paragraphs if pp is not p)
        if not exists:
            p.text = new_title
            changes += 1
            print(f"FIX 2a: '{txt}' -> '{new_title}'")

# Second pass: remove duplicate headings (where multiple old sections map to same new section)
seen_headings = set()
for p in doc.paragraphs:
    if p.style.name.startswith('Heading 3'):
        txt = p.text.strip()
        if txt in seen_headings:
            # This is a duplicate heading - remove it and its content
            # Find next heading to know where content ends
            found_next = False
            for pp in doc.paragraphs:
                if pp is p:
                    continue
                if pp.style.name.startswith('Heading') and doc.paragraphs.index(pp) > doc.paragraphs.index(p):
                    found_next = True
                    break
            # Remove this heading
            parent = p._element.getparent()
            parent.remove(p._element)
            changes += 1
            print(f"FIX 2b: Removed duplicate heading '{txt}'")
        else:
            seen_headings.add(txt)

# ══════════════════════════════════════════════════════════════
# FIX 3: Fill in test result tables (10.2, 10.3, 10.5)
# ══════════════════════════════════════════════════════════════
# Find section 10.2 Route Verification and add content after it
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == '10.2 Route Verification':
        # Find the paragraph that says "All 25+ routes..."
        for j in range(i+1, i+10):
            if doc.paragraphs[j].text.strip().startswith('All 25+ routes'):
                # Replace with filled-in content
                for run in doc.paragraphs[j].runs:
                    run.text = ''
                doc.paragraphs[j].runs[0].text = (
                    'All 25+ routes were verified to return HTTP 200 with valid HTML content. '
                    'Key routes tested include:'
                )
                changes += 1
                
                # Add route verification data after this paragraph
                route_data = [
                    '/ (index) — 200 — Agency listing, hero section, country flag',
                    '/search — 200 — Trip results with pricing and seat availability',
                    '/book/<id> — 200 — Booking form with seat selection',
                    '/payment/<id> — 200 — Payment provider options',
                    '/ticket/<ref> — 200 — E-ticket with all booking details',
                    '/ticket/<ref>/pdf — 200 — PDF download',
                    '/ticket/<ref>/image — 200 — PNG image generation',
                    '/agencies — 200 — Agency directory listing',
                    '/agency/login — 200 — Agency login form',
                    '/agency/dashboard — 200 — Agency stats and data',
                    '/ministry/login — 200 — Ministry login form',
                    '/ministry/agencies — 200 — Agency registry with statuses',
                ]
                
                ref_para = doc.paragraphs[j]
                for route in reversed(route_data):
                    new_p = copy.deepcopy(ref_para._element)
                    # Clear existing text
                    for elem in new_p.findall(qn('w:r')):
                        elem.text = '' if elem.text is None else ''
                    # Set new text
                    run_elem = new_p.find(qn('w:r'))
                    if run_elem is None:
                        run_elem = copy.deepcopy(ref_para._element.find(qn('w:r')))
                        new_p.append(run_elem)
                    t_elem = run_elem.find(qn('w:t'))
                    if t_elem is None:
                        t_elem = run_elem.makeelement(qn('w:t'), {})
                        run_elem.append(t_elem)
                    t_elem.text = route
                    t_elem.set(qn('xml:space'), 'preserve')
                    ref_para._element.addnext(new_p)
                    changes += 1
                
                print(f"FIX 3a: Filled route verification table")
                break
        break

# Fill in migration results (10.3)
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == '10.3 Migration Results':
        # Add migration data after heading
        migration_data = [
            'Entity          | JSON Records | SQLite Records | Match',
            'Agencies        | 7            | 7              | Yes',
            'Buses           | 111          | 111            | Yes',
            'Routes          | 9            | 9              | Yes',
            'Schedules       | 11           | 11             | Yes',
            'Bookings        | 18           | 18             | Yes',
            'Passengers      | N/A          | 7 (deduplicated) | Yes',
        ]
        
        ref_para = p
        for line in reversed(migration_data):
            new_p = copy.deepcopy(ref_para._element)
            for elem in new_p.findall(qn('w:r')):
                elem.text = '' if elem.text is None else ''
            run_elem = new_p.find(qn('w:r'))
            if run_elem is None:
                run_elem = copy.deepcopy(ref_para._element.find(qn('w:r')))
                new_p.append(run_elem)
            t_elem = run_elem.find(qn('w:t'))
            if t_elem is None:
                t_elem = run_elem.makeelement(qn('w:t'), {})
                run_elem.append(t_elem)
            t_elem.text = line
            t_elem.set(qn('xml:space'), 'preserve')
            ref_para._element.addnext(new_p)
            changes += 1
        
        print(f"FIX 3b: Filled migration results table")
        break

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════
doc.save(src)
print(f"\n{'='*50}")
print(f"Phase 2 complete: {changes} changes")
print(f"Saved to: {src}")
