from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os

doc = Document()

for section in doc.sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)

for i in range(1, 6):
    h = doc.styles[f'Heading {i}']
    h.font.color.rgb = RGBColor(0x00, 0x7A, 0x5E)

DOC = doc  # alias for the template

# ═══════════════════ COVER ═══════════════════

for _ in range(4):
    doc.add_paragraph()

title = doc.add_heading('AFRI Trans', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in title.runs:
    run.font.size = Pt(48)
    run.font.color.rgb = RGBColor(0x00, 0x7A, 0x5E)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run('Multi-Country Inter-City Bus Ticketing Platform')
r.font.size = Pt(18)
r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub2.add_run('Internship Report')
r2.font.size = Pt(16)
r2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

doc.add_paragraph()
doc.add_paragraph()

info_lines = [
    'Presented by: TEH ADOLF BUOH',
    'Internship Period: June – July 2026',
    'Organisation: FERDSILINKS BUEA, CAMEROON',
]
for line in info_lines:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(line)
    r.font.size = Pt(12)

doc.add_page_break()

# ═══════════════════ TOC ═══════════════════

doc.add_heading('Table of Contents', level=1)
toc = [
    '1. Introduction',
    '2. Problem Statement',
    '3. Objectives',
    '4. Tools and Technologies Used',
    '5. System Architecture',
    '6. Database Design',
    '7. Complete File Structure',
    '8. Features Implemented',
    '9. Business Rules & Constraints',
    '10. Implementation Details',
    '11. Challenges and Solutions',
    '12. Testing and Results',
    '13. Conclusion and Future Work',
]
for t in toc:
    doc.add_paragraph(t, style='List Number')

doc.add_page_break()

# ═══════════════════ 1. INTRODUCTION ═══════════════════

doc.add_heading('1. Introduction', level=1)

doc.add_paragraph(
    'AFRI Trans is a web-based bus ticketing platform designed to serve all 54 African countries. '
    'The platform connects passengers with bus agencies through a unified booking system, while also '
    'providing administrative portals for agencies and government transport ministries. The system '
    'supports 11 languages, local currencies, country-specific payment providers, and per-country '
    'ministry oversight workflows.'
)
doc.add_paragraph(
    'This report documents the development of the AFRI Trans platform during my internship at '
    'Ferdsilink Buea, Cameroon. The project was built using Python Flask for the backend, SQLite '
    'for data persistence, and vanilla HTML/CSS/JavaScript for the frontend.'
)

doc.add_heading('1.1 Background', level=2)
doc.add_paragraph(
    'Inter-city bus travel is the primary mode of transportation for millions of Africans. However, '
    'most bus booking systems are paper-based, fragmented by country, or operated by individual '
    'agencies with no centralised platform. This creates several problems:'
)
bg_points = [
    'Passengers must visit physical terminals to book tickets',
    'No way to compare prices across multiple agencies',
    'Limited payment options, often cash-only',
    'No standardised ticketing or booking records',
    'Language barriers across different regions of Africa',
]
for b in bg_points:
    doc.add_paragraph(b, style='List Bullet')

doc.add_paragraph(
    'AFRI Trans aims to solve these problems by providing a single, multi-country platform where '
    'passengers can search, compare, book, and pay for bus tickets across any African country.'
)

doc.add_heading('1.2 UK English Convention', level=2)
doc.add_paragraph(
    'Throughout this project and report, UK English spelling is used exclusively. Key examples: '
    'colour (not color), organisation (not organization), normalised (not normalized), centre '
    '(not center), behaviour (not behavior), favour (not favor), licence (not license). This '
    'convention applies to all UI text, documentation, and code comments.'
)

# ═══════════════════ 2. PROBLEM STATEMENT ═══════════════════

doc.add_heading('2. Problem Statement', level=1)

problems = [
    ('Lack of Centralisation', 'No single platform exists for booking bus tickets across multiple African countries. Passengers must interact with each agency separately.'),
    ('Language Barriers', 'Africa has over 2,000 languages. A platform serving the continent must support multiple languages to be accessible. Currently 11 languages are supported.'),
    ('Currency and Payment Fragmentation', 'Each country uses a different currency and has different mobile money providers. A unified system must handle this complexity.'),
    ('Regulatory Requirements', 'Each country has its own Ministry of Transport that must approve and oversee agencies operating within its jurisdiction.'),
    ('Data Redundancy', 'Initial implementation used flat JSON file storage, leading to duplicate data, ID collisions, and referential integrity issues. Migrated to normalised SQLite.'),
    ('Agency Privacy', 'Competing agencies should not have access to each other\'s operational data (pricing, routes, passenger manifests).'),
    ('Security', 'A single shared password for all ministry users across all countries is insecure. Each country needs an individual super admin with email-based authentication and password recovery.'),
    ('No Feedback Mechanism', 'Passengers had no way to submit feedback, suggestions, or bug reports to the platform administrators.'),
    ('No Notification System', 'Agencies had no way to broadcast announcements (promotions, schedule changes) to passengers, and passengers had no way to track which announcements they had read.'),
]
for title, desc in problems:
    p = doc.add_paragraph()
    r = p.add_run(f'{title}: ')
    r.bold = True
    p.add_run(desc)

# ═══════════════════ 3. OBJECTIVES ═══════════════════

doc.add_heading('3. Objectives', level=1)

doc.add_heading('3.1 Primary Objectives', level=2)
primary = [
    'Develop a multi-country bus ticketing platform covering all 54 African nations',
    'Implement a language system supporting 11 African and international languages',
    'Create per-country payment provider integration (20+ mobile money providers)',
    'Build a Ministry of Transport approval workflow for agency registration',
    'Design a fully responsive interface accessible on all device sizes',
]
for p in primary:
    doc.add_paragraph(p, style='List Bullet')

doc.add_heading('3.2 Secondary Objectives', level=2)
secondary = [
    'Normalise data storage and eliminate redundancy through SQLite migration',
    'Enforce privacy between competing agencies via session-aware filtering',
    'Generate e-tickets in both PNG image and PDF formats',
    'Support agency management of buses, routes, schedules, and bookings',
    'Implement a bilingual announcement system with automatic French translation',
    'Build a feedback system with email notifications to administrators',
    'Create a per-notification read tracking system using session cookies',
    'Implement one-time shared password for enhanced ministry security',
    'Provide interactive visual seat selection with 4 bus layout classes',
    'Develop an agency dashboard with revenue breakdown by route',
]
for s in secondary:
    doc.add_paragraph(s, style='List Bullet')

# ═══════════════════ 4. TOOLS & TECHNOLOGIES ═══════════════════

doc.add_heading('4. Tools and Technologies Used', level=1)

doc.add_heading('4.1 Backend', level=2)
t1 = doc.add_table(rows=7, cols=2)
t1.style = 'Light Grid Accent 1'
t1.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Technology', 'Purpose']):
    t1.rows[0].cells[i].text = h
    for p in t1.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
backends = [
    ('Python 3.10+', 'Primary programming language'),
    ('Flask 2.x', 'Web framework (routing, sessions, templating)'),
    ('SQLite 3', 'Database engine (WAL journal mode)'),
    ('Werkzeug', 'Password hashing (scrypt) and security utilities'),
    ('Pillow (PIL)', 'E-ticket PNG image generation'),
    ('xhtml2pdf', 'PDF ticket generation'),
    ('deep-translator', 'Google Translate API for auto-translation (no API key needed)'),
]
for i, (a, b) in enumerate(backends):
    t1.rows[i+1].cells[0].text = a
    t1.rows[i+1].cells[1].text = b

doc.add_heading('4.2 Frontend', level=2)
t2 = doc.add_table(rows=6, cols=2)
t2.style = 'Light Grid Accent 1'
t2.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Technology', 'Purpose']):
    t2.rows[0].cells[i].text = h
    for p in t2.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
frontends = [
    ('HTML5', 'Page structure'),
    ('CSS3 (vanilla)', 'All styling — no framework (custom responsive grid)'),
    ('JavaScript (vanilla)', 'Client-side interactivity (modals, navigation, seat picker)'),
    ('Jinja2', 'Server-side templating (Flask integrated)'),
    ('Font Awesome 6.5.1', 'Icon library (CDN)'),
    ('Google Fonts (Inter)', 'Typography'),
]
for i, (a, b) in enumerate(frontends):
    t2.rows[i+1].cells[0].text = a
    t2.rows[i+1].cells[1].text = b

doc.add_heading('4.3 Development Tools', level=2)
t3 = doc.add_table(rows=4, cols=2)
t3.style = 'Light Grid Accent 1'
t3.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Tool', 'Purpose']):
    t3.rows[0].cells[i].text = h
    for p in t3.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
devtools = [
    ('VS Code', 'Code editor'),
    ('Git', 'Version control'),
    ('PowerShell', 'Command-line interface'),
    ('python-dotenv', 'Environment variable management (.env file)'),
]
for i, (a, b) in enumerate(devtools):
    t3.rows[i+1].cells[0].text = a
    t3.rows[i+1].cells[1].text = b

# ═══════════════════ 5. SYSTEM ARCHITECTURE ═══════════════════

doc.add_heading('5. System Architecture', level=1)

doc.add_heading('5.1 High-Level Architecture', level=2)
doc.add_paragraph(
    'AFRI Trans follows a monolithic Flask application pattern with three distinct user portals. '
    'The application uses a shared services layer for translation, country management, payment '
    'providers, and session/authentication.'
)

arch_text = """  ┌──────────────────────────────────────────────────┐
  │                   AFRI Trans                         │
  ├──────────────────────────────────────────────────────┤
  │                                                      │
  │   ┌─────────────────┐  ┌──────────────┐  ┌─────────┐│
  │   │   Passenger App  │  │ Agency Portal│  │ Ministry││
  │   │                  │  │              │  │ Portal  ││
  │   │ • Search trips   │  │ • Dashboard  │  │• Oversight│
  │   │ • Book tickets   │  │ • Buses      │  │• Approve │
  │   │ • Pay online     │  │ • Routes     │  │• Monitor │
  │   │ • Pick seats     │  │ • Schedules  │  │• Reports │
  │   │ • View tickets   │  │ • Bookings   │  │         │
  │   │ • Feedback       │  │ • Manifests  │  │         │
  │   └─────────────────┘  └──────────────┘  └─────────┘│
  │                                                      │
  ├──────────────────────────────────────────────────────┤
  │              Shared Services Layer                   │
  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────────┐ │
  │  │i18n      │ │Country   │ │Payment │ │Session/Auth│ │
  │  │Engine    │ │Manager   │ │Gateway │ │Manager    │ │
  │  │(11 langs)│ │(54 ctrys)│ │(20+ pr)│ │+ Rate     │ │
  │  │          │ │          │ │        │ │ Limiter   │ │
  │  └──────────┘ └──────────┘ └────────┘ └───────────┘ │
  ├──────────────────────────────────────────────────────┤
  │                    Data Layer                        │
  │              ┌──────────────────────┐                │
  │              │   SQLite Database    │                │
  │              │ (13 tables, indexed) │                │
  │              └──────────────────────┘                │
  └──────────────────────────────────────────────────────┘"""

p = doc.add_paragraph()
r = p.add_run(arch_text)
r.font.name = 'Consolas'
r.font.size = Pt(7.5)

doc.add_heading('5.2 Request Flow', level=2)
doc.add_paragraph(
    'A typical booking request flows through the system as follows:'
)
flow_text = 'Passenger -> Search (country + cities) -> Pick Schedule -> Select Seat -> Enter Details -> Choose Payment -> Confirm -> Generate Ticket'
p = doc.add_paragraph()
r = p.add_run(flow_text)
r.font.name = 'Consolas'
r.font.size = Pt(10)

doc.add_heading('5.3 Rate Limiting Architecture', level=2)
doc.add_paragraph(
    'An in-memory rate limiter protects all login endpoints. Each IP address is tracked '
    'independently with a sliding window of 15 minutes. After 10 failed attempts, the IP is '
    'blocked temporarily. Successful login clears the attempt counter for that IP.'
)
p = doc.add_paragraph()
r = p.add_run(
    'login_attempts = defaultdict(list)\n'
    'RATE_LIMIT_WINDOW = 15 minutes\n'
    'RATE_LIMIT_MAX = 10 attempts per window'
)
r.font.name = 'Consolas'
r.font.size = Pt(9)

# ═══════════════════ 6. DATABASE DESIGN ═══════════════════

doc.add_heading('6. Database Design', level=1)

doc.add_heading('6.1 Schema Overview', level=2)
doc.add_paragraph(
    'The database uses SQLite with WAL (Write-Ahead Logging) journal mode for concurrent read/write '
    'performance. The schema contains 10 tables with proper foreign keys and ON DELETE CASCADE rules.'
)

doc.add_heading('agencies', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('name', 'TEXT NOT NULL'),
    ('phone', 'TEXT DEFAULT \'\''),
    ('email', 'TEXT DEFAULT \'\' — globally UNIQUE via partial index WHERE email != \'\''),
    ('country', 'TEXT NOT NULL'),
    ('password_hash', 'TEXT'),
    ('approved', 'INTEGER DEFAULT 0 — 0=pending, 1=approved'),
    ('rejection_reason', 'TEXT DEFAULT \'\''),
    ('approval_reason', 'TEXT DEFAULT \'\''),
    ('reset_token', 'TEXT — for password reset'),
    ('reset_token_expiry', 'TEXT'),
    ('created_at', 'TEXT NOT NULL'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('buses', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('agency_id', 'INTEGER REFERENCES agencies(id) ON DELETE CASCADE'),
    ('plate', 'TEXT NOT NULL — uppercase, unique per agency'),
    ('capacity', 'INTEGER NOT NULL — range 14–80'),
    ('bus_type', 'TEXT DEFAULT \'standard\' — \'standard\' or \'vip\''),
    ('status', 'TEXT DEFAULT \'available\' — \'available\' or \'busy\''),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('routes', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('agency_id', 'INTEGER REFERENCES agencies(id) ON DELETE CASCADE'),
    ('from_city', 'TEXT NOT NULL'),
    ('to_city', 'TEXT NOT NULL'),
    ('price', 'INTEGER NOT NULL'),
    ('duration', 'TEXT DEFAULT \'\''),
    ('luggage_enabled', 'INTEGER DEFAULT 0'),
    ('luggage_price_per_kg', 'INTEGER DEFAULT 0'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('schedules', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('route_id', 'INTEGER REFERENCES routes(id) ON DELETE CASCADE'),
    ('bus_id', 'INTEGER REFERENCES buses(id) ON DELETE CASCADE'),
    ('date', 'TEXT NOT NULL — ISO format YYYY-MM-DD'),
    ('time', 'TEXT NOT NULL — HH:MM format'),
    ('period', 'TEXT NOT NULL — \'morning\', \'afternoon\', or \'night\''),
    ('status', 'TEXT DEFAULT \'active\' — \'active\' or \'cancelled\''),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('bookings', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('schedule_id', 'INTEGER REFERENCES schedules(id) ON DELETE CASCADE'),
    ('passenger_name', 'TEXT NOT NULL'),
    ('passenger_phone', 'TEXT NOT NULL'),
    ('passenger_email', 'TEXT DEFAULT \'\''),
    ('seat_number', 'INTEGER'),
    ('reference', 'TEXT NOT NULL UNIQUE — auto-generated ref code'),
    ('paid', 'INTEGER DEFAULT 0'),
    ('payment_method', 'TEXT DEFAULT \'cash\''),
    ('status', 'TEXT DEFAULT \'pending\' — pending/confirmed/cancelled'),
    ('luggage_fee', 'INTEGER DEFAULT 0'),
    ('commission', 'INTEGER DEFAULT 0 — 1% of total, hidden from UI'),
    ('created_at', 'TEXT NOT NULL'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d
doc.add_paragraph(
    'Unique index: CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_seat ON bookings(schedule_id, seat_number) WHERE seat_number IS NOT NULL;'
)

doc.add_heading('announcements', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('agency_id', 'INTEGER REFERENCES agencies(id)'),
    ('message', 'TEXT NOT NULL — English version'),
    ('message_fr', 'TEXT DEFAULT \'\' — auto-translated French version'),
    ('badge', 'TEXT DEFAULT \'NEW\' — NEW/PROMO/UPDATE/GENERAL'),
    ('is_active', 'INTEGER DEFAULT 1'),
    ('created_at', 'TEXT NOT NULL'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d
doc.add_paragraph(
    'Migration: ALTER TABLE announcements ADD COLUMN message_fr TEXT DEFAULT \'\';'
)

doc.add_heading('feedback', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('name', 'TEXT DEFAULT \'\' — auto-detected from session'),
    ('role', 'TEXT DEFAULT \'user\' — user/agency/ministry'),
    ('message', 'TEXT NOT NULL'),
    ('created_at', 'TEXT NOT NULL'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('super_admins', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('email', 'TEXT NOT NULL'),
    ('password_hash', 'TEXT'),
    ('country_code', 'TEXT NOT NULL'),
    ('reset_token', 'TEXT'),
    ('reset_token_expiry', 'TEXT'),
    ('created_at', 'TEXT NOT NULL'),
    ('UNIQUE(email, country_code)', '— one super admin per email per country'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('commissions', level=3)
cols = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('agency_id', 'INTEGER REFERENCES agencies(id)'),
    ('booking_id', 'INTEGER REFERENCES bookings(id)'),
    ('amount', 'INTEGER NOT NULL — 1% of booking total'),
    ('created_at', 'TEXT NOT NULL'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('meta', level=3)
cols = [
    ('key', 'TEXT PRIMARY KEY — e.g. "migrated", "shared_pw_used_cm"'),
    ('value', 'TEXT'),
]
t = doc.add_table(rows=len(cols)+1, cols=2)
t.style = 'Light Grid Accent 1'
for i, h in enumerate(['Column', 'Type & Notes']):
    t.rows[0].cells[i].text = h
    for p in t.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
for i, (c, d) in enumerate(cols):
    t.rows[i+1].cells[0].text = c
    t.rows[i+1].cells[1].text = d

doc.add_heading('6.2 Entity Relationships', level=2)
er_text = """Agencies  1───* Buses         (one agency has many buses)
Agencies  1───* Routes        (one agency defines many routes)
Agencies  1───* Announcements (one agency creates many announcements)
Routes    1───* Schedules     (one route has many scheduled trips)
Buses     1───* Schedules     (one bus appears in many schedules)
Schedules 1───* Bookings      (one trip has many bookings)
Agencies  1───* Commissions   (one agency has many commission records)
Countries 1───* Super_Admins  (one country has one super admin)"""
p = doc.add_paragraph()
r = p.add_run(er_text)
r.font.name = 'Consolas'
r.font.size = Pt(9)

doc.add_heading('6.3 Migration from JSON to SQLite', level=2)
doc.add_paragraph(
    'The original implementation stored all data in a single JSON file (data.json). This caused '
    'several problems that were resolved by migrating to normalised SQLite:'
)
mig_table = doc.add_table(rows=6, cols=3)
mig_table.style = 'Light Grid Accent 1'
mig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Issue', 'JSON Storage', 'SQLite Solution']):
    mig_table.rows[0].cells[i].text = h
    for p in mig_table.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
mig_data = [
    ('ID Collisions', 'len(data[\'x\']) + 1 produced duplicates on delete', 'AUTOINCREMENT guarantees unique IDs'),
    ('Data Duplication', 'Passenger details repeated across bookings', 'Normalised passengers table'),
    ('Price Duplication', 'Route prices duplicated per schedule', 'Route prices stored once in routes table'),
    ('Orphan Records', 'Deleting an agency left orphan data', 'ON DELETE CASCADE cleans up children'),
    ('Concurrent Writes', 'Last writer wins, no transaction safety', 'WAL journal + per-connection transactions'),
]
for i, (a, b, c) in enumerate(mig_data):
    mig_table.rows[i+1].cells[0].text = a
    mig_table.rows[i+1].cells[1].text = b
    mig_table.rows[i+1].cells[2].text = c

# ═══════════════════ 7. FILE STRUCTURE ═══════════════════

doc.add_heading('7. Complete File Structure', level=1)

fs = """transport/
+-- app.py                      # Main Flask app: 48+ routes, context processors
+-- database.py                 # SQLite module: schema, CRUD, migration
+-- countries.json              # 54 African countries configuration
+-- generate_translations.py    # Auto-translate en.json -> 10 languages
+-- translate_announcements.py  # Back-fill French translations for announcements
+-- generate_readme_docx.py     # This document generator
+-- .env                        # SMTP credentials (gitignored)
+-- static/
|   +-- style.css               # All CSS: responsive, animations, components
|   +-- img/afritrans-logo.svg  # Brand logo
+-- templates/
|   +-- base.html               # Base layout (nav, footer, country modal, flash)
|   +-- index.html              # Homepage: hero, search, agencies, stats
|   +-- search.html             # Trip results grouped by period
|   +-- pick_seat.html          # Interactive seat map (pre-payment)
|   +-- seats.html              # Seat selection (post-payment)
|   +-- book.html               # Passenger details form
|   +-- payment.html            # Payment method selection
|   +-- ticket.html             # E-ticket display (HTML)
|   +-- ticket_pdf.html         # PDF template
|   +-- lookup.html             # Ticket lookup by reference
|   +-- notifications.html      # Announcements list with read tracking
|   +-- notification_detail.html# Single announcement view
|   +-- feedback.html           # Feedback submission form
|   +-- feedback_all.html       # Ministry: view all feedback
|   +-- agencies.html           # Browse all agencies
|   +-- agency_browse.html      # Single agency public page
|   +-- agency_dashboard.html   # Agency control panel
|   +-- agency_login.html       # Agency sign in
|   +-- agency_register.html    # Agency registration
|   +-- agency_buses.html       # Bus management
|   +-- agency_bus_form.html    # Add/edit bus
|   +-- agency_routes.html      # Route management
|   +-- agency_route_form.html  # Add/edit route
|   +-- agency_schedules.html   # Schedule management
|   +-- agency_schedule_form.html# Add/edit schedule
|   +-- agency_bookings.html    # Booking management
|   +-- agency_booking_reassign.html # Reassign booking
|   +-- agency_manifest.html    # Passenger manifest
|   +-- agency_announcements.html # Announcement management
|   +-- agency_forgot_password.html
|   +-- agency_reset_password.html
|   +-- agency_verify_code.html
|   +-- ministry_dashboard.html # Ministry national overview
|   +-- ministry_login.html     # 2-step ministry login
|   +-- ministry_relogin.html   # Set personal password (step 2)
|   +-- ministry_agencies.html  # Agency registry (approve/reject)
|   +-- ministry_bookings.html  # Cross-agency booking view
|   +-- ministry_forgot_password.html
|   +-- ministry_reset_password.html
|   +-- ministry_verify_code.html
+-- translations/
    +-- en.json                 # English source of truth (538+ keys)
    +-- fr.json                 # French (manually maintained)
    +-- ar.json                 # Arabic
    +-- pt.json                 # Portuguese
    +-- es.json                 # Spanish
    +-- sw.json                 # Swahili
    +-- am.json                 # Amharic
    +-- so.json                 # Somali
    +-- ti.json                 # Tigrinya
    +-- af.json                 # Afrikaans
    +-- zu.json                 # Zulu"""

p = doc.add_paragraph()
r = p.add_run(fs)
r.font.name = 'Consolas'
r.font.size = Pt(7)

# ═══════════════════ 8. FEATURES IMPLEMENTED ═══════════════════

doc.add_heading('8. Features Implemented', level=1)

doc.add_heading('8.1 Multi-Country Support (54 Countries)', level=2)
doc.add_paragraph(
    'All 54 African countries are configured in countries.json with: name, flag colours (3–6 hex values), '
    'local currency, currency code, major cities (8–18 per country), default language, supported languages, '
    'local mobile money providers, and VIP surcharge amount. Country switching is available via a globe icon '
    'in the navbar that opens a searchable modal grid showing all 54 countries with their flags.'
)

doc.add_heading('8.2 Internationalisation (11 Languages, 538+ Keys)', level=2)
doc.add_paragraph(
    'The platform supports 11 languages: English, French, Arabic, Portuguese, Swahili, Amharic, Somali, '
    'Tigrinya, Spanish, Afrikaans, and Zulu. All UI text is wrapped in _(\'text\') function calls. Each '
    'language has a JSON translation file. Missing keys fall back gracefully to English. The language '
    'switcher appears only when a country has 2+ supported languages. Country-switching auto-selects '
    'the country\'s default language.'
)

doc.add_heading('8.3 Passenger Booking Flow', level=2)
steps = [
    'Search: Passenger selects origin city, destination city, and travel date on the homepage search form',
    'Browse Results: Available trips displayed grouped by period (morning 05:00–11:59 / afternoon 12:00–16:59 / night 17:00–04:59) with agency name, bus plate, bus type, departure time, duration, price, and available seats count',
    'Pick Seat: Interactive seat map shows the bus layout (4 classes depending on capacity). Occupied seats are greyed out, available seats are green (standard) or gold (VIP). Selected seat turns blue with pricing display',
    'Enter Details: Passenger provides name, phone, optional email. Optional luggage if route supports it',
    'Payment: Country-specific mobile money providers displayed. Payment is simulated with transaction ID',
    'Ticket: E-ticket displayed with all details. Downloadable as PDF or PNG image',
    'Lookup: Passenger can retrieve ticket later via reference number',
]
for i, s in enumerate(steps):
    doc.add_paragraph(f'Step {i+1}: {s}', style='List Bullet')

doc.add_heading('8.4 Interactive Seat Selection (4 Layout Classes)', level=2)
doc.add_paragraph(
    'The seat layout system supports 4 bus configuration classes, determined dynamically by bus capacity:'
)
classes = [
    ('Class 1 (14–29 seats)', '3 columns: Left(1) + Aisle + Right(2). Compact mini-bus layout.'),
    ('Class 2 (30–40 seats)', '4 columns: Left(2) + Aisle + Right(2). Standard coach layout.'),
    ('Class 3 (41–60 seats)', '2+2+3 columns: Left(2) + Aisle + Centre(2) + Aisle + Right(3). Large coach.'),
    ('Class 4 (61–80 seats)', '4+3 columns: Left(4) + Aisle + Right(3). Max-capacity layout.'),
]
for name, desc in classes:
    p = doc.add_paragraph()
    r = p.add_run(f'{name}: ')
    r.bold = True
    p.add_run(desc)

doc.add_paragraph(
    'Each seat has a type: standard (green gradient) or VIP (gold gradient). VIP seats incur a '
    'per-country surcharge (e.g. 3,000 XAF in Cameroon, 500 KSh in Kenya). The bus body shows '
    'driver area, front entrance, walkway, rear exit, emergency exit markers, and toilet/storage '
    'area. A legend explains all seat states (Available, VIP, Taken, Your Selection). On seat '
    'selection, the page auto-scrolls to the booking button showing the total payable amount.'
)

doc.add_heading('8.5 Agency Portal (Complete Dashboard)', level=2)

agency_features = [
    'Dashboard: Stats cards (routes, buses, bookings, upcoming trips). Today\'s trips highlight card with route, period, time, bus, seat occupancy, and manifest link. Revenue breakdown by route with visual progress bars showing percentage share. Recent bookings table (last 8). Buses table with plate, type badge, seats, status badge. Routes table with pricing. Upcoming trips table with manifest access. Quick action buttons (Announce, Bookings, Schedule).',
    'Bus Management: Add new buses with plate number, capacity (14–80), type (standard/VIP). Edit existing buses. Toggle bus status manually. Buses auto-mark busy when assigned to a schedule and auto-revert to available when schedule cancelled.',
    'Route Management: Define city pairs with pricing, duration, optional luggage configuration (enabled/disabled, price per kg). Edit existing routes.',
    'Schedule Management: Create trips by assigning a route, bus, date, time, and period (morning/afternoon/night). Edit or cancel schedules. Cancelling a schedule auto-reverts the bus to available.',
    'Booking Management: View all bookings with filters. Cancel bookings. Reassign passengers to alternative trips (e.g. if a schedule is cancelled).',
    'Passenger Manifest: Generate and view passenger manifest for any scheduled trip showing all booked passengers with seat numbers.',
    'Announcements: Create announcements with badge type (NEW/PROMO/UPDATE/GENERAL). Messages auto-translate to French. Deactivate old announcements.',
    'Commission Visibility: Only the 1% rate is shown as an info badge. The actual commission amount is NEVER displayed to agencies.',
    'Registration Flow: Agency registers (name, email, password) -> Pending approval -> Ministry approves/rejects -> Agency becomes visible to passengers.',
]
for f in agency_features:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('8.6 Ministry of Transport Portal', level=2)
ministry_features = [
    '2-Step Login: Step 1 uses the shared password (Admin123 — one-time use only). Step 2 requires setting a personal email + password combination. After first use, the shared password is invalidated and subsequent visits skip straight to step 2.',
    'Dashboard: Stats grid showing registered agencies, pending approvals (with pulse animation when >0), total bookings, total revenue, commission info badge, active trips count. Fleet overview table (total buses, routes, schedules).',
    'Agency Registry: Full list of agencies with name, country, locations, bus/route/booking counts, status badges (Approved green, PENDING orange, Rejected red). Approve action with reason modal. Reject action with reason modal (reason stored permanently and shown to the rejected agency on their dashboard).',
    'Booking Records: Cross-agency view of all bookings within the minister\'s country with passenger details, route, schedule, payment status.',
]
for f in ministry_features:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('8.7 Bilingual Announcement System', level=2)
doc.add_paragraph(
    'Cameroon is bilingual (English and French). All agency announcements must be visible in the '
    'passenger\'s preferred language. The system handles this as follows:'
)
ann_features = [
    'When an agency creates an announcement, the message is auto-translated to French using Google Translate (via deep-translator library) and stored in the message_fr column',
    'The French translation is stored at creation time (not on-the-fly) to avoid repeated API calls on every page load',
    'The ann_msg(ann) helper function (injected via Flask context processor) returns the French message when the current language is French, otherwise returns English',
    'All templates use ann_msg(ann) instead of ann.message to display announcements',
    'A back-fill script (translate_announcements.py) translates all existing announcements that were created before the feature was implemented',
    'The get_announcements() function uses SELECT a.* so it automatically includes the new message_fr column',
]
for f in ann_features:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('8.8 Per-Notification Read Tracking', level=2)
doc.add_paragraph(
    'Passengers can see which announcements they have and haven\'t read yet. This is tracked '
    'without requiring user login:'
)
read_features = [
    'Read announcement IDs are stored in session[\'read_notification_ids\'] as a list',
    'When a passenger clicks "Read More" on an announcement, the ID is added to the list',
    'The navbar bell icon shows a red badge with the count of unread announcements (total announcements minus read IDs)',
    'In the notifications list, unread announcements show a blue dot indicator; read ones show a green checkmark with "Read" label',
    'Both /notifications and /notification/<id> pages use no-store, no-cache, must-revalidate cache headers to prevent stale data',
    'Logout clears the read_notification_ids list',
]
for f in read_features:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('8.9 Feedback System', level=2)
doc.add_paragraph(
    'A feedback form allows any user to submit suggestions, bug reports, or general comments:'
)
fb_features = [
    'Accessible via /feedback route from the navbar "Feedback" link',
    'The form has a single message field (textarea) — no manual name or role fields',
    'Name and role are auto-detected from the session if available: passenger (role: user), agency (role: agency, name from DB), ministry (role: ministry, name from session email)',
    'On submission, the feedback is stored in the feedback table and an email is sent to FEEDBACK_EMAIL (configured via .env) with the submitter\'s name, role, and message',
    'Ministry can view all feedback at /feedback/all (requires super_admin session)',
    'Feedback is listed newest-first with role badges (agency green, ministry red, user grey)',
    'Email sending uses Gmail SMTP with an app password via python-dotenv (.env file)',
]
for f in fb_features:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('8.10 E-Ticket Generation', level=2)
doc.add_paragraph('Tickets are generated in three formats:')
ticket_formats = [
    'HTML Ticket (/ticket/<ref>): Web page with all booking details, styled with country flag colours',
    'PNG Image (/ticket/<ref>/image): Rendered with Pillow (PIL). Features: country flag colours in header/footer, QR-style reference, route mapping, passenger details, seat number, VIP/Standard colour-coded badge, price breakdown with surcharges, validity period, agency and bus information',
    'PDF Document (/ticket/<ref>/pdf): Generated via xhtml2pdf from the HTML template, suitable for printing or email attachment',
]
for f in ticket_formats:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('8.11 Payment Providers (20+ Networks)', level=2)
doc.add_paragraph(
    '20 African mobile money and digital payment providers are configured per country:'
)
providers = [
    'MTN MoMo (Cameroon, Nigeria, Ghana, Côte d\'Ivoire, Uganda, Zambia, Rwanda, Benin)',
    'Orange Money (Francophone Africa: Senegal, Mali, Burkina Faso, etc.)',
    'M-Pesa (Kenya, Tanzania, DRC, Lesotho, Mozambique, Ghana, Ethiopia)',
    'Airtel Money (Kenya, Uganda, Rwanda, Zambia, Chad, DRC, Congo, Niger, Madagascar, Malawi, Tanzania, Gabon, Seychelles)',
    'EMOLA (Mozambique, Angola)',
    'EcoCash (Zimbabwe)',
    'Wave (Senegal, Côte d\'Ivoire)',
    'Telebirr (Ethiopia)',
    'Zaad (Somalia)',
    'Opay (Nigeria)',
    'Plus 10 more country-specific providers',
]
for p in providers:
    doc.add_paragraph(p, style='List Bullet')

doc.add_heading('8.12 Mobile Responsiveness', level=2)
doc.add_paragraph(
    'The interface is fully responsive with four breakpoints. The CSS uses custom properties (CSS '
    'variables for flag colours) and custom responsive utilities (no framework).'
)
resp_table = doc.add_table(rows=5, cols=3)
resp_table.style = 'Light Grid Accent 1'
resp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Breakpoint', 'Target', 'Key Changes']):
    resp_table.rows[0].cells[i].text = h
    for p in resp_table.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
resp_data = [
    ('1024px', 'Tablet / small laptop', 'Grid-4 collapses to 2 columns. Container padding reduced.'),
    ('768px', 'Tablet portrait / large phone', 'All grids -> single column. Hamburger nav appears. Hero padding reduced. Table min-width drops.'),
    ('480px', 'Phone', 'Country grid -> 1 column. Buttons/forms shrink. Negative margins for edge-to-edge scrolling. Seat size reduces to 30px.'),
    ('360px', 'Very small phone', 'Minimal padding. Smallest font sizes. Table min-width drops to 280px.'),
]
for i, (a, b, c) in enumerate(resp_data):
    resp_table.rows[i+1].cells[0].text = a
    resp_table.rows[i+1].cells[1].text = b
    resp_table.rows[i+1].cells[2].text = c

doc.add_paragraph()

doc.add_heading('8.13 Agency Privacy', level=2)
doc.add_paragraph(
    'Competing agencies cannot see each other\'s operational data. When an agency employee is '
    'logged in, all public-facing pages filter to show ONLY that agency\'s data. Direct URL '
    'access to competitor agency pages shows "Access denied." Regular passengers (not logged '
    'in as an agency) see all approved agencies. Ministry users see everything within their '
    'country scope.'
)

doc.add_heading('8.14 Bus Auto-Status Management', level=2)
doc.add_paragraph(
    'Buses have two states: available and busy. The system manages this automatically:'
)
bus_status = [
    'When add_schedule() is called, the assigned bus\'s status is set to "busy"',
    'When update_schedule() is called with status="cancelled", the bus reverts to "available"',
    'This prevents double-booking a bus on two schedules at the same time',
    'Agencies can still manually change bus status if needed',
]
for b in bus_status:
    doc.add_paragraph(b, style='List Bullet')

doc.add_heading('8.15 One-Time Shared Password', level=2)
doc.add_paragraph(
    'The default super admin shared password (Admin123) is a security vulnerability. The system '
    'implements a one-time-use mechanism:'
)
pw_features = [
    'On first visit to /ministry/login, the shared password form is shown. On successful entry, a flag (shared_pw_used_{country}) is set to "1" in the meta table',
    'On subsequent visits, the GET route checks the meta table and redirects straight to step 2 (personal email + password)',
    'The POST route on step 1 rejects the shared password if it has already been used',
    'Step 2 requires the super admin to set a personal email address and password. After this, login uses standard email+password authentication',
    'Password reset flows exist for both agencies and super admins with 8-digit verification codes sent via email',
]
for p in pw_features:
    doc.add_paragraph(p, style='List Bullet')

# ═══════════════════ 9. BUSINESS RULES ═══════════════════

doc.add_heading('9. Business Rules & Constraints', level=1)

rule_sections = [
    ('Commission', [
        '1% commission is calculated on the booking total (base price + VIP surcharge + luggage fee)',
        'Commission is deducted at source before the remaining 99% is attributed to the agency',
        'The commission amount in currency is NEVER displayed in any UI — not on agency dashboard, not on ministry dashboard',
        'Only the rate (1%) is shown as an informational badge: "Platform Commission (1%) / Deducted automatically per booking"',
        'Commission records are stored in the commissions table for platform owner reference',
    ]),
    ('Bus Constraints', [
        'Capacity: minimum 14 seats, maximum 80 seats (enforced in form validation)',
        'Two types: standard and VIP. VIP seats add the per-country surcharge to the base fare',
        'Bus plate numbers are uppercase and unique per agency',
        'Status auto-managed: busy when assigned to an active schedule, available when cancelled',
        'One email address = one agency globally (UNIQUE index on agencies.email)',
    ]),
    ('Schedule Constraints', [
        'Three periods: morning (05:00–11:59), afternoon (12:00–16:59), night (17:00–04:59)',
        'Each schedule must have a unique combination of route, bus, date, and time',
        'Only future schedules are shown in the agency dashboard',
        'Booking closes 15 minutes before departure time',
    ]),
    ('Booking Rules', [
        'A booking references exactly one schedule and one seat number',
        'Status flow: pending -> confirmed (on payment) or cancelled',
        'Reference number is auto-generated and globally unique (pattern: COUNTRY-XXXXXXX)',
        'Seats are unique per schedule — enforced by database-level partial unique index',
        'Passenger can look up ticket by reference without logging in',
        'Reassign feature allows moving a booking to a different schedule without losing payment',
        'Bookings auto-expire 24 hours after departure',
    ]),
    ('Security Rules', [
        'The shared password (Admin123) is invalidated after first successful super admin login',
        'All /agency/* routes are protected by get_agency_session() — redirects to login if invalid',
        'get_agency_session() validates that the agency still exists in the database on every call',
        'Stale agency_id is automatically removed from the session if the agency was deleted',
        'Rate limiting: 10 failed login attempts per 15-minute sliding window per IP address',
        'Successful login clears the IP\'s attempt counter',
        'Logout clears read_notification_ids and agency_id from session',
        'Password reset uses 8-digit code sent via email, with expiry time',
    ]),
    ('Notification Rules', [
        'Bell icon colour: #c62828 (red) for ALL countries — NOT the country\'s flag-2 colour',
        'Bell badge count = total active announcements minus IDs in read_notification_ids',
        'Both notification pages use no-store, no-cache, must-revalidate headers',
        'Blue dot = unread announcement; green checkmark + "Lire" label = read',
    ]),
    ('Translation Rules', [
        'en.json is the source of truth — all other languages are derivatives',
        'Missing keys fall back to English text automatically via _().get(text, text)',
        'French announcement translation is stored in message_fr column at creation time',
        'ann_msg(ann) returns French if lang=fr AND message_fr is non-empty, else English',
        'Language is stored in session[\'lang\'] and a cookie (365-day expiry)',
    ]),
    ('Agency Privacy Rules', [
        'When agency_id is in session, public pages filter to show only that agency\'s data',
        'Direct URL access to competitor agency pages is blocked with "Access denied"',
        'Ministry users see everything within their country scope',
        'Passengers (not logged in as agency) see all approved agencies',
    ]),
]
for title, rules in rule_sections:
    doc.add_heading(title, level=2)
    for r in rules:
        doc.add_paragraph(r, style='List Bullet')

# ═══════════════════ 10. IMPLEMENTATION DETAILS ═══════════════════

doc.add_heading('10. Implementation Details', level=1)

doc.add_heading('10.1 Key Code Patterns', level=2)

doc.add_heading('Translation Wrapper', level=3)
p = doc.add_paragraph()
r = p.add_run(
    "def _(text):\n"
    "    lang = get_current_lang()\n"
    "    t = load_translations(lang)\n"
    "    return t.get(text, text)  # Falls back to original English"
)
r.font.name = 'Consolas'
r.font.size = Pt(9)
doc.add_paragraph(
    'Note: for _ in range(...) shadows the _() function. In templates, use a different variable '
    'name for loop variables (e.g. for idx in range(...)).'
)

doc.add_heading('Context Processor (inject_globals)', level=3)
p = doc.add_paragraph()
r = p.add_run(
    "# Available in ALL templates:\n"
    "#   _()           - translation function\n"
    "#   current_lang  - 'en', 'fr', 'ar', etc.\n"
    "#   country       - current country config dict\n"
    "#   COUNTRIES     - all 54 countries\n"
    "#   cities        - current country's cities\n"
    "#   today         - today's date (ISO)\n"
    "#   ann_msg(ann)  - bilingual announcement display\n"
    "#   total_ann_count - unread announcements count\n"
    "#   read_ids      - set of read announcement IDs"
)
r.font.name = 'Consolas'
r.font.size = Pt(8)

doc.add_heading('Country-Scoped Query', level=3)
p = doc.add_paragraph()
r = p.add_run(
    "def _country_agencies():\n"
    "    code = session.get('country', 'cm')\n"
    "    agencies = get_approved_agencies_by_country(code)\n"
    "    if 'agency_id' in session:\n"
    "        agencies = [a for a in agencies if a['id'] == session['agency_id']]\n"
    "    return agencies"
)
r.font.name = 'Consolas'
r.font.size = Pt(9)

doc.add_heading('Bilingual Announcement Helper', level=3)
p = doc.add_paragraph()
r = p.add_run(
    "def ann_msg(ann):\n"
    "    msg = ann.get('message_fr') or ann.get('message', '')\n"
    "    if get_current_lang() != 'fr' or not ann.get('message_fr'):\n"
    "        return ann.get('message', '')\n"
    "    return msg"
)
r.font.name = 'Consolas'
r.font.size = Pt(9)

doc.add_heading('Bus Layout Algorithm', level=3)
doc.add_paragraph(
    'The bus layout is generated programmatically by the bus_layout() function in database.py. '
    'It supports 4 layout classes based on bus capacity. The layout returns a grid of rows with '
    'each cell containing a seat number, class (standard/vip), or special element (door, aisle). '
    'The template renders this grid as an interactive seat map with touch-friendly sizing.'
)

doc.add_heading('10.2 Complete Route Inventory', level=2)
doc.add_paragraph('The application has 48+ routes serving three user portals:')

route_summary = [
    ('Passenger Routes (12)', '/, /search, /pick-seat/<sid>, /book/<sid>, /payment/<bid>, /ticket/<bid>, /ticket/<bid>/pdf, /ticket/<bid>/image, /lookup, /feedback, /feedback/all, /notifications, /notification/<nid>'),
    ('Utility Routes (3)', '/lang/<lang>, /country/<code>, /agencies, /agency/<aid>'),
    ('Agency Routes (22)', '/agency/login, /agency/register, /agency/logout, /agency/dashboard, /agency/buses, /agency/buses/add, /agency/buses/<bid>/edit, /agency/routes, /agency/routes/add, /agency/routes/<rid>/edit, /agency/schedules, /agency/schedules/add, /agency/schedules/<sid>/edit, /agency/bookings, /agency/bookings/<bid>/reassign, /agency/manifest/<sid>, /agency/announcements, /agency/forgot-password, /agency/verify-code, /agency/reset-password'),
    ('Ministry Routes (11)', '/ministry/login, /ministry/relogin, /ministry/logout, /ministry/dashboard, /ministry/agencies, /ministry/bookings, /ministry/forgot-password, /ministry/verify-code, /ministry/reset-password'),
]
for title, desc in route_summary:
    p = doc.add_paragraph()
    r = p.add_run(f'{title}: ')
    r.bold = True
    p.add_run(desc)

doc.add_heading('10.3 Email Configuration', level=2)
doc.add_paragraph(
    'The application uses Gmail SMTP for sending emails (feedback notifications and password reset codes). '
    'Configuration is loaded from a .env file using python-dotenv:'
)
p = doc.add_paragraph()
r = p.add_run(
    'MAIL_USERNAME=your@gmail.com\n'
    'MAIL_PASSWORD=your-16-char-app-password\n'
    'MAIL_FROM=your@gmail.com\n'
    'FEEDBACK_EMAIL=your@gmail.com\n'
    'MAIL_SERVER=smtp.gmail.com\n'
    'MAIL_PORT=587'
)
r.font.name = 'Consolas'
r.font.size = Pt(9)

# ═══════════════════ 11. CHALLENGES ═══════════════════

doc.add_heading('11. Challenges and Solutions', level=1)

challenges = [
    ('Data Redundancy in JSON Storage',
     'The original data.json stored all data in a flat, denormalised structure. Passenger details were '
     'repeated across every booking, route prices were duplicated for every schedule, and ID generation '
     'using len(data[\'x\']) + 1 produced collisions when items were deleted. There was no referential '
     'integrity — deleting an agency left orphan data.',
     'Migrated to SQLite with a fully normalised schema. Seven tables with proper foreign keys '
     '(ON DELETE CASCADE), AUTOINCREMENT for collision-free IDs, WAL journal mode for concurrent '
     'write safety, and UNIQUE constraints to eliminate duplication. A migration function '
     '(migrate_from_json()) imports existing JSON data with idempotent execution tracking via the meta table.'),
    ('Multi-Language Translation Management',
     'Maintaining consistent translations across 11 languages with 538+ UI strings. Adding new UI '
     'text required updating all 11 files. Non-Latin scripts (Arabic, Amharic, Tigrinya) required '
     'special handling. The generate_translations.py script could time out when processing large batches.',
     'A generate_translations.py script reads en.json (source of truth) and regenerates all language '
     'files, adding missing keys. The _() function gracefully falls back to English when a key is '
     'missing. French is manually maintained as the primary bilingual target. For large batches, '
     'individual translation files can be edited manually.'),
    ('Agency Privacy',
     'Competing agencies should not know each other\'s pricing, routes, or operational data. Since '
     'the booking platform is public, any agency employee could browse as a passenger to view '
     'competitor information.',
     'Session-aware filtering in the _country_agencies() helper. When an agency_id is present in '
     'the session, all public pages filter to show only the logged-in agency\'s data. Direct URL '
     'access to competitor agency pages is explicitly blocked with authorisation checks.'),
    ('Concurrent Booking Race Conditions',
     'Two passengers could select the same seat simultaneously at payment time. Without proper '
     'locking, both bookings would succeed for the same seat.',
     'Three layers of protection: (1) Database-level partial unique index on (schedule_id, seat_number) '
     'WHERE seat_number IS NOT NULL. (2) Atomic booking function (add_booking_atomic) wraps seat '
     'selection + booking in a BEGIN IMMEDIATE transaction. (3) Atomic payment confirmation '
     '(confirm_booking_atomic) re-checks seat inside a transaction at payment time. If the seat '
     'was taken between selection and payment, the passenger is redirected to pick another seat.'),
    ('Concurrent Login and Rate Limiting',
     'The original login endpoints had no protection — an attacker could hammer login endpoints '
     'with unlimited rapid attempts, potentially brute-forcing passwords or overwhelming the server.',
     'An in-memory rate limiter was added to all login endpoints. Each IP address is tracked '
     'independently with a sliding window of 15 minutes. After 10 failed attempts, the IP is '
     'blocked with a user-friendly message. On successful login, the attempt counter is cleared.'),
    ('Shared Password Security',
     'Using Admin123 as a shared password across all countries is insecure. Any ministry user who '
     'knew the password could log in as any country\'s super admin.',
     'The shared password is now one-time-use. After the first successful login, a flag is set '
     'in the meta table (shared_pw_used_{country}). Step 2 forces the user to set a personal '
     'email + password. On subsequent visits, the shared password step is skipped entirely.'),
    ('Bilingual Announcement Translation',
     'Cameroon has two official languages (English and French). Announcements need to be visible '
     'in both languages. On-the-fly translation would hit the Google Translate API on every page '
     'load, which is slow and unreliable.',
     'The French translation is stored in a dedicated message_fr column at announcement creation '
     'time. The ann_msg() context processor selects the French or English version based on the '
     'user\'s language preference. A back-fill script handles existing announcements.'),
    ('Bell Icon Colour Inconsistency',
     'The bell icon colour was using var(--flag-2) which changed colour when switching countries. '
     'For example, in Cameroon it appeared red, but in Kenya it appeared white (on white background).',
     'The bell icon colour was hardcoded to #c62828 (consistent red) for all countries, ensuring '
     'the notification bell is always visible regardless of the country\'s flag colours.'),
    ('Missing Feedback System',
     'Passengers had no way to submit feedback, suggestions, or bug reports. There was no channel '
     'for users to communicate with the platform administrators.',
     'A complete feedback system was built: new feedback table in the database, /feedback route '
     '(GET form + POST submit with auto-detected name/role), email notification to administrators '
     'via SMTP, /feedback/all route for ministry to view all submissions, and a navbar link.'),
    ('Unclosed HTML Elements',
     'A missing </div> in the country modal caused the entire page footer to render inside the '
     'modal overlay (which had display: none), making the footer invisible.',
     'Systematic div-counting review of all templates. The issue was fixed by properly closing '
     'the modal container before the footer.'),
]
for title, problem, solution in challenges:
    doc.add_heading(title, level=2)
    p = doc.add_paragraph()
    r = p.add_run('Problem: ')
    r.bold = True
    p.add_run(problem)
    p2 = doc.add_paragraph()
    r2 = p2.add_run('Solution: ')
    r2.bold = True
    r2.font.color.rgb = RGBColor(0x00, 0x7A, 0x5E)
    p2.add_run(solution)

# ═══════════════════ 12. TESTING ═══════════════════

doc.add_heading('12. Testing and Results', level=1)

doc.add_heading('12.1 Testing Approach', level=2)
approaches = [
    'Manual browser testing across all 48+ routes and user flows (passenger, agency, ministry)',
    'Automated HTTP tests using Python http.client to verify route responses (HTTP 200)',
    'Database verification confirming migration accuracy and data integrity (record counts match)',
    'Responsive testing at all four breakpoints (1024, 768, 480, 360px)',
    'Concurrent booking testing by opening multiple browser tabs simultaneously',
]
for a in approaches:
    doc.add_paragraph(a, style='List Bullet')

doc.add_heading('12.2 Migration Results', level=2)
mig_res = doc.add_table(rows=7, cols=3)
mig_res.style = 'Light Grid Accent 1'
mig_res.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Entity', 'JSON Records', 'SQLite Records']):
    mig_res.rows[0].cells[i].text = h
    for p in mig_res.rows[0].cells[i].paragraphs:
        for r in p.runs: r.bold = True
mig_data = [
    ('Agencies', '7', '7'),
    ('Buses', '111', '111'),
    ('Routes', '9', '9'),
    ('Schedules', '11', '11'),
    ('Bookings', '18', '18'),
    ('Passengers (deduplicated)', 'N/A (repeated)', '7 unique'),
]
for i, (a, b, c) in enumerate(mig_data):
    mig_res.rows[i+1].cells[0].text = a
    mig_res.rows[i+1].cells[1].text = b
    mig_res.rows[i+1].cells[2].text = c

doc.add_heading('12.3 Key Test Results', level=2)
test_res = [
    'All routes return HTTP 200 with valid HTML content',
    'Database migration: 100% data integrity preserved (all records matched)',
    'Concurrent booking: unique index prevents double-booking at database level',
    'Rate limiting: blocks after 10 attempts, resets after 15 minutes, clears on success',
    'Responsive design: all pages functional at 360px, 480px, 768px, 1024px breakpoints',
    'Translation: all 538+ keys load without errors in all 11 languages',
    'Bilingual announcements: French and English display correctly based on language setting',
    'Email notifications: feedback submissions reach FEEDBACK_EMAIL via SMTP',
    'Commission hiding: amount never displayed in agency or ministry dashboards',
    'One-time password: Admin123 rejected after first use, redirects to step 2',
]
for t in test_res:
    doc.add_paragraph(t, style='List Bullet')

# ═══════════════════ 13. CONCLUSION ═══════════════════

doc.add_heading('13. Conclusion and Future Work', level=1)

doc.add_heading('13.1 Summary of Achievements', level=2)
achievements = [
    'Complete coverage of all 54 African countries with localised configuration (flag colours, currency, cities, languages, payment providers)',
    'Multilingual interface supporting 11 languages across 4 scripts (Latin, Arabic, Ge\'ez, Latin-extended) with 538+ translation keys',
    'Full booking lifecycle: search -> browse -> pick seat -> enter details -> pay -> e-ticket (HTML + PDF + PNG)',
    'Agency management portal with dashboard (revenue by route, recent bookings, today\'s trips), bus/route/schedule CRUD, booking management, passenger manifests, and bilingual announcements',
    'Ministry oversight with per-country login, agency approval/rejection workflow, cross-agency booking visibility, and national statistics dashboard',
    'Bilingual announcement system with automatic French translation via Google Translate, stored at creation time',
    'Per-notification read tracking using session cookies (no login required for passengers)',
    'Interactive visual seat selection with 4 bus layout classes, colour-coded (standard green, VIP gold, selected blue, taken grey)',
    'Responsive design with 4 breakpoints accessible on desktop, tablet, and mobile devices',
    'Data integrity through SQLite migration with normalised schema, foreign keys, unique constraints, and atomic transactions',
    'Competitor privacy preventing unauthorised data access between agencies',
    'Rate limiting on all login endpoints (10 attempts per 15 minutes per IP)',
    'One-time shared password (Admin123) with forced personal password setup',
    'Feedback system with email notifications to administrators',
    'Bus auto-status management (busy when scheduled, available when cancelled)',
    'Commission system (1%) with amount hidden from UI — rate only shown as badge',
    'Hardened session management: agency validation on every protected route, stale session cleanup, logout clears read tracking',
]
for a in achievements:
    doc.add_paragraph(a, style='List Bullet')

doc.add_heading('13.2 Future Improvements', level=2)

future = [
    ('Security Enhancements', [
        'Add CSRF protection to all forms',
        'Switch to HTTPS in production',
        'Implement Redis-backed rate limiter for multi-server deployments',
        'Add two-factor authentication for ministry users',
    ]),
    ('Code Quality', [
        'Refactor monolithic app.py into modular route blueprints (passenger, agency, ministry, api)',
        'Separate business logic from route handlers into service layer',
        'Add unit tests with pytest and integration tests with Selenium',
        'Add type hints throughout the codebase',
    ]),
    ('Real-Time Features', [
        'WebSocket-based real-time seat availability updates',
        'Live booking notifications for agencies via Server-Sent Events',
        'SMS booking confirmations via Africa\'s Talking API',
    ]),
    ('Payment Integration', [
        'Connect to real mobile money APIs (M-Pesa, MTN MoMo, Orange Money)',
        'Implement webhook-based payment confirmation',
        'Add payment receipt generation',
        'Support for card payments (Stripe/Paystack)',
    ]),
    ('Performance Optimisation', [
        'Add Redis caching for frequently accessed data (cities, agencies, routes)',
        'Implement database query optimisation with proper indexing',
        'Add CDN for static assets (Font Awesome, Google Fonts)',
        'Implement database connection pooling',
    ]),
    ('Additional Features', [
        'RTL (right-to-left) support for Arabic-language countries',
        'Mobile app (React Native or Flutter)',
        'Driver/operator mobile interface for manifest management',
        'Multi-trip and round-trip booking',
        'Loyalty/rewards programme for frequent passengers',
        'Bus tracking with GPS integration',
        'Automated translation for all 10 languages (currently French is manual, others are timed out)',
        'Custom error pages (404, 500)',
        'Agency analytics dashboard with CSV export and charts',
        'Booking history and trip history for passengers',
    ]),
]
for title, items in future:
    doc.add_heading(title, level=2)
    for item in items:
        doc.add_paragraph(item, style='List Bullet')

# ═══════════════════ END ═══════════════════

doc.add_paragraph()
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('— End of Report —')
r.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
r.font.size = Pt(12)

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run('Report prepared by TEH ADOLF BUOH — FERDSILINKS, BUEA — 2026')
r2.font.size = Pt(10)
r2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

output_path = os.path.join(os.path.dirname(__file__), 'AFRI_Trans_Internship_Report.docx')
doc.save(output_path)
print(f'Report saved to: {output_path}')
