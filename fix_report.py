"""Fix inaccuracies in REVIVAL INNOVATION HUB.docx"""
import sys, io, os, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL INNOVATION HUB.docx'
tmp = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FIXED.docx'

# Copy first so we don't hold a lock on original
shutil.copy2(src, tmp)
doc = Document(tmp)

changes = 0

# ── 1. Fix typo "Ethnologies" -> "Ethnologue" ──
for p in doc.paragraphs:
    if 'Ethnologies' in p.text:
        for run in p.runs:
            if 'Ethnologies' in run.text:
                run.text = run.text.replace('Ethnologies', 'Ethnologue')
                changes += 1
                print(f"FIXED: 'Ethnologies' -> 'Ethnologue'")

# ── 2. Fix typo "mobilemone" -> "mobilemoney" ──
for p in doc.paragraphs:
    if 'mobilemone' in p.text:
        for run in p.runs:
            if 'mobilemone' in run.text:
                run.text = run.text.replace('mobilemone', 'mobilemoney')
                changes += 1
                print(f"FIXED: 'mobilemone' -> 'mobilemoney'")

# ── 3. Fix bus capacity default 70 -> 71 ──
for p in doc.paragraphs:
    if 'DEFAULT 70' in p.text:
        for run in p.runs:
            if 'DEFAULT 70' in run.text:
                run.text = run.text.replace('DEFAULT 70', 'DEFAULT 71')
                changes += 1
                print(f"FIXED: capacity DEFAULT 70 -> 71")

# ── 4. Clean up markdown symbols from formal report ──
md_clean = [
    ('~~Implement rate limiting on login endpoints~~ ✅ Completed (10 attempts/15min per IP)',
     'Implement rate limiting on login endpoints — Completed (10 attempts/15min per IP)'),
    ('~~WebSocket-based real-time seat availability~~ ✅ Completed (HTTP polling, 30s interval)',
     'WebSocket-based real-time seat availability — Completed (HTTP polling, 30s interval)'),
    ('~~SMS/email booking confirmations~~ ✅ Completed (background scheduler, 90/45 min before departure)',
     'SMS/email booking confirmations — Completed (background scheduler, 90/45 min before departure)'),
]

for p in doc.paragraphs:
    for run in p.runs:
        for old, new in md_clean:
            if old in run.text:
                run.text = run.text.replace(old, new)
                changes += 1
                print(f"FIXED: Cleaned markdown strikethrough/emoji")

# ── 5. Fix Xhtml2pdf -> xhtml2pdf in references ──
for p in doc.paragraphs:
    if 'Xhtml2pdf' in p.text:
        for run in p.runs:
            if 'Xhtml2pdf' in run.text:
                run.text = run.text.replace('Xhtml2pdf', 'xhtml2pdf')
                changes += 1
                print(f"FIXED: 'Xhtml2pdf' -> 'xhtml2pdf'")

# ── 6. Remove duplicate race condition block (paragraphs 657-668) ──
# This block duplicates section 9.7 content that already exists at 618-628
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    # Target the exact duplicate block after section 9.17
    if 655 <= i <= 670:
        if any(text.startswith(s) for s in [
            'Challenge: Two passengers could select the same seat at the exact same time',
            'This is the same concurrency problem Facebook',
            'Solution: Two layers of protection were implemented',
        ]):
            for run in p.runs:
                run.text = ''
            changes += 1
            print(f"FIXED: Removed duplicate paragraph {i}")
        # Also remove the SQL code block and numbered list that follow
        if i >= 660 and i <= 669:
            if text and not text.startswith('Scaling further'):
                for run in p.runs:
                    run.text = ''
                changes += 1
                print(f"FIXED: Removed duplicate detail paragraph {i}")

# ── 7. Fix screenshot placeholders ──
for p in doc.paragraphs:
    if 'Insert screenshots here' in p.text:
        for run in p.runs:
            if 'Insert screenshots' in run.text:
                run.text = run.text.replace(
                    '(Insert screenshots here — 4–6 key screens showing homepage, search results, seat selection, booking form, e-ticket, ministry dashboard)',
                    '[Note: Screenshots to be inserted — (1) Homepage with search form and country flag, '
                    '(2) Search results with trip listings and pricing, '
                    '(3) Seat selection layout showing VIP/standard classes, '
                    '(4) Booking form with passenger details, '
                    '(5) E-ticket with QR reference and price breakdown, '
                    '(6) Ministry dashboard with agency registry]'
                )
                run.text = run.text.replace(
                    '(Insert screenshots here — 4–6 key screens showing homepage, search results, seat selection, booking form, e-ticket, mi',
                    '[Note: Screenshots to be inserted — (1) Homepage, (2) Search results, (3) Seat selection, '
                    '(4) Booking form, (5) E-ticket, (6) Ministry dashboard'
                )
                changes += 1
                print(f"FIXED: Updated screenshot placeholder")

# ── 8. Fix duplicate items in 11.1 Summary ──
# There are two "Interactive seat selection" and two "IP geolocation" lines
seen = {}
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    if not text:
        continue
    # Check for duplicates in summary section (paragraphs ~718-731)
    if 715 <= i <= 732:
        key = text[:50]
        if key in seen and key:
            # Duplicate — clear it
            for run in p.runs:
                run.text = ''
            changes += 1
            print(f"FIXED: Removed duplicate summary item at {i}: '{text[:50]}'")
        else:
            seen[key] = i

# ── 9. Remove trailing markdown strikethrough artifacts ──
# Check for any remaining ~~ or ✅
for p in doc.paragraphs:
    for run in p.runs:
        if '~~' in run.text or '✅' in run.text:
            original = run.text
            run.text = run.text.replace('~~', '').replace('✅', '[Done]')
            if run.text != original:
                changes += 1
                print(f"FIXED: Cleaned remaining markdown artifacts")

# ── Save ──
doc.save(tmp)
print(f"\n{'='*50}")
print(f"Total fixes applied: {changes}")
print(f"Saved to: {tmp}")
print(f"Original file unchanged at: {src}")
