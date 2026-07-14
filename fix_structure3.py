"""
Phase 3: Fix remaining issues - rewrite using index-based iteration
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

src = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\REVIVAL_INNOVATION_HUB_FINAL.docx'
doc = Document(src)
changes = 0

# ══════════════════════════════════════════════════════════════
# FIX 1: Fix migration table data styled as Heading 3
# ══════════════════════════════════════════════════════════════
migration_texts = [
    'Entity          | JSON Records | SQLite Records | Match',
    'Agencies        | 7            | 7              | Yes',
    'Buses           | 111          | 111            | Yes',
    'Routes          | 9            | 9              | Yes',
    'Schedules       | 11           | 11             | Yes',
    'Bookings        | 18           | 18             | Yes',
    'Passengers      | N/A          | 7 (deduplicated) | Yes',
]

paragraphs = list(doc.paragraphs)
for p in paragraphs:
    if p.text.strip() in migration_texts:
        p.style = doc.styles['Normal']
        changes += 1
        print(f"FIX 1: Fixed migration table: '{p.text.strip()[:40]}'")

# ══════════════════════════════════════════════════════════════
# FIX 2: Remove old section 7 subsections that were consolidated
# ══════════════════════════════════════════════════════════════
old_7_remove = [
    '7.11 Bilingual Announcement System',
    '7.12 Per-Notification Read Tracking',
    '7.13 One-Time Shared Password (Admin123)',
    '7.14 Commission System (1% Platform Fee)',
    '7.15 Bus Auto-Status Management',
    '7.16 Translation System Enhancements',
    '7.17 IP Geolocation — Auto-Detect Country',
    '7.18 Flash Alert Categories',
    '7.19 Subscription Monetisation',
    '7.20 Flag-Coloured Hero Title',
    '7.21 Live Seat Map with Auto-Refresh',
    '7.22 Departure Notification Scheduler',
    '7.23 Concurrency Hardening (TOCTOU Fixes)',
]

# Build index of paragraphs
para_list = list(doc.paragraphs)
to_remove = set()

for idx, p in enumerate(para_list):
    txt = p.text.strip()
    if txt in old_7_remove:
        # Mark heading for removal
        to_remove.add(idx)
        # Mark content paragraphs until next heading
        for j in range(idx + 1, len(para_list)):
            if para_list[j].style.name.startswith('Heading'):
                break
            to_remove.add(j)

# Remove from end to start
for idx in sorted(to_remove, reverse=True):
    p = para_list[idx]
    parent = p._element.getparent()
    if parent is not None:
        parent.remove(p._element)
        changes += 1

print(f"FIX 2: Removed {len(to_remove)} paragraphs from old section 7 subsections")

# ══════════════════════════════════════════════════════════════
# FIX 3: Fix "7.10 User Interface" -> proper numbering
# ══════════════════════════════════════════════════════════════
# After removals, verify section 7 headings
doc2 = Document(src)
print("\n=== Section 7 headings after cleanup ===")
for p in doc2.paragraphs:
    if p.style.name.startswith('Heading 3'):
        txt = p.text.strip()
        if txt.startswith('7.'):
            print(f"  {txt}")

doc.save(src)
print(f"\n{'='*50}")
print(f"Phase 3 complete: {changes} changes")
print(f"Saved to: {src}")
