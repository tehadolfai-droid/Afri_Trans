from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement
import os

doc = Document()

for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)

for i in range(1, 6):
    h = doc.styles[f'Heading {i}']
    h.font.color.rgb = RGBColor(0x00, 0x7A, 0x5E)

# Helper: add code block
def add_code(text, size=8):
    for line in text.strip().split('\n'):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.left_indent = Cm(1)
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

# Helper: add table with header and data
def add_table(headers, rows, col_widths=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Light Grid Accent 1'
    for i, h in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(10)
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = tbl.rows[r_idx + 1].cells[c_idx]
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(10)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in tbl.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph()

# Helper: screenshot placeholder
def add_screenshot_placeholder(caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    # Add a bordered box to represent the screenshot
    lines = [
        '+' + '-' * 60 + '+',
        '|' + ' ' * 60 + '|',
        '|' + f'  {caption}'.ljust(59) + '|',
        '|' + '  [Screenshot Placeholder]'.ljust(59) + '|',
        '|' + ' ' * 60 + '|',
        '+' + '-' * 60 + '+',
    ]
    for line in lines:
        pr = doc.add_paragraph()
        pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pr.paragraph_format.space_before = Pt(0)
        pr.paragraph_format.space_after = Pt(0)
        r = pr.add_run(line)
        r.font.name = 'Consolas'
        r.font.size = Pt(7)
        r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

# Helper: bold inline
def bold_line(label, text):
    p = doc.add_paragraph()
    r = p.add_run(label)
    r.bold = True
    if text:
        p.add_run(text)
    return p

# ═══════════════════ COVER PAGE ═══════════════════

for _ in range(6):
    doc.add_paragraph()

title = doc.add_heading('AFRI Trans', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in title.runs:
    run.font.size = Pt(52)
    run.font.color.rgb = RGBColor(0x00, 0x7A, 0x5E)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run('Multi-Country Inter-City Bus Ticketing Platform')
r.font.size = Pt(20)
r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub2.add_run('Complete System Documentation\nSpecification, Internship Report & User Guide')
r2.font.size = Pt(14)
r2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

info_lines = [
    'Presented by: TEH ADOLF BUOH (ADOLF.AI)',
    'Internship Period: June – July 2026',
    'Organisation: FERDSILINKS BUEA, CAMEROON',
    'Serving All 54 African Nations | 11 Languages | 20+ Payment Providers',
]
for line in info_lines:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(line)
    r.font.size = Pt(12)

doc.add_page_break()

# ═══════════════════ TABLE OF CONTENTS ═══════════════════

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
    'Appendix A: Full Route Inventory',
    'Appendix B: Translation Key Reference',
    'Appendix C: Country Configuration Reference',
    'Appendix D: References',
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
    'This document provides complete documentation of the AFRI Trans platform, including system '
    'architecture, database design, all implemented features, business rules, implementation details, '
    'and the challenges faced during development. It serves as both a technical specification document '
    'and an internship report covering the development period at Ferdsilink Buea, Cameroon.'
)

doc.add_heading('1.1 Background', level=2)
doc.add_paragraph(
    'Inter-city bus travel is the primary mode of transportation for millions of Africans. However, '
    'most bus booking systems are paper-based, fragmented by country, or operated by individual '
    'agencies with no centralised platform. This creates several problems:'
)
for b in [
    'Passengers must visit physical terminals to book tickets — no online booking available',
    'No way to compare prices across multiple agencies serving the same route',
    'Limited payment options, often cash-only with no digital payment integration',
    'No standardised ticketing or booking records — tickets are handwritten',
    'Language barriers across different regions of Africa (over 2,000 languages spoken)',
    'Regulatory gaps — no government oversight of bus agency operations',
    'No feedback mechanism for passengers to report issues or suggest improvements',
]:
    doc.add_paragraph(b, style='List Bullet')

doc.add_paragraph(
    'AFRI Trans aims to solve these problems by providing a single, multi-country platform where '
    'passengers can search, compare, book, and pay for bus tickets across any African country.'
)

doc.add_heading('1.2 UK English Convention', level=2)
doc.add_paragraph(
    'Throughout this project and document, UK English spelling is used exclusively. Key examples: '
    'colour (not color), organisation (not organization), normalised (not normalized), centre '
    '(not center), behaviour (not behavior), favour (not favor), licence (not license), programme '
    '(not program), defence (not defense). This convention applies to all UI text, code comments, '
    'and documentation.'
)

doc.add_heading('1.3 Document Structure', level=2)
doc.add_paragraph(
    'This document is organised into 13 main sections plus appendices. Sections 1–3 provide the '
    'project background and objectives. Sections 4–7 cover the technical architecture, database, '
    'and file structure. Section 8 details all implemented features. Sections 9–10 document business '
    'rules and implementation specifics. Sections 11–13 cover challenges, testing, and future work. '
    'The appendices provide comprehensive reference material including the complete route inventory, '
    'translation keys, and country configurations.'
)

# ═══════════════════ 2. PROBLEM STATEMENT ═══════════════════

doc.add_heading('2. Problem Statement', level=1)

problems = [
    ('Lack of Centralisation',
     'No single platform exists for booking bus tickets across multiple African countries. '
     'Passengers must interact with each agency separately, often requiring physical presence '
     'at bus terminals. There is no unified search, comparison, or booking experience.'),
    ('Language Barriers',
     'Africa has over 2,000 languages across 54 countries. A platform serving the continent '
     'must support multiple languages to be accessible to diverse populations. Currently 11 '
     'languages are supported, covering major language groups across West, East, North, '
     'Southern, and Central Africa.'),
    ('Currency and Payment Fragmentation',
     'Each country uses a different currency (e.g., XAF, XOF, NGN, KES, GHS, ZAR, EGP, MAD, '
     'ETB, TZS, UGX, RWF) with varying exchange rates. Each country also has different mobile '
     'money providers (M-Pesa, MTN MoMo, Orange Money, Airtel Money, etc.). A unified system '
     'must handle this complexity while displaying prices in the passenger\'s local currency.'),
    ('Regulatory Requirements',
     'Each country has its own Ministry of Transport that must approve and oversee agencies '
     'operating within its jurisdiction. The platform must support per-country government '
     'oversight with distinct approval workflows, registration tracking, and national statistics.'),
    ('Data Redundancy and Integrity',
     'Initial implementation used flat JSON file storage (data.json), leading to duplicate '
     'data, ID collisions when items were deleted, referential integrity issues, and no '
     'transaction safety for concurrent writes. A robust database solution was needed.'),
    ('Agency Privacy and Competition',
     'Competing agencies should not have access to each other\'s operational data including '
     'pricing strategies, route profitability, passenger manifests, and booking volumes. '
     'Since the booking platform is public, special mechanisms are needed to protect '
     'competitor privacy.'),
    ('Security Vulnerabilities',
     'A single shared password (Admin123) for all ministry users across all countries is '
     'insecure. Login endpoints had no rate limiting, leaving them vulnerable to brute-force '
     'attacks. No CSRF protection existed on forms. Session management lacked proper validation.'),
    ('No Feedback Mechanism',
     'Passengers had no way to submit feedback, suggestions, or bug reports to the platform '
     'administrators. Issues and feature requests had no formal channel for communication.'),
    ('No Notification System',
     'Agencies had no way to broadcast announcements (promotions, schedule changes, service '
     'updates) to passengers. Passengers had no way to see or track which announcements '
     'they had read.'),
    ('Concurrent Booking Conflicts',
     'Without proper locking mechanisms, two passengers could select and book the same seat '
     'simultaneously, leading to overbooking and passenger dissatisfaction at departure time.'),
]
for title, desc in problems:
    p = doc.add_paragraph()
    r = p.add_run(f'{title}: ')
    r.bold = True
    p.add_run(desc)

doc.add_page_break()

# ═══════════════════ 3. OBJECTIVES ═══════════════════

doc.add_heading('3. Objectives', level=1)

doc.add_heading('3.1 Primary Objectives', level=2)
for p in [
    'Develop a multi-country bus ticketing platform covering all 54 African nations with per-country localisation',
    'Implement a language system supporting 11 African and international languages (English, French, Arabic, Portuguese, Swahili, Amharic, Somali, Tigrinya, Spanish, Afrikaans, Zulu)',
    'Create per-country payment provider integration supporting 20+ African mobile money networks',
    'Build a Ministry of Transport approval workflow for agency registration with per-country scope',
    'Design a fully responsive interface accessible on desktop, tablet, and mobile devices',
]:
    doc.add_paragraph(p, style='List Bullet')

doc.add_heading('3.2 Secondary Objectives', level=2)
for s in [
    'Normalise data storage and eliminate redundancy through SQLite migration from JSON',
    'Enforce privacy between competing agencies via session-aware data filtering',
    'Generate e-tickets in three formats: HTML, PNG image (Pillow), and PDF (xhtml2pdf)',
    'Support agency management of buses, routes, schedules, bookings, and passenger manifests',
    'Implement a bilingual announcement system with automatic French translation for Cameroon',
    'Build a feedback system with email notifications to administrators via SMTP',
    'Create a per-notification read tracking system using session cookies (no login required)',
    'Implement one-time shared password (Admin123) for enhanced ministry security',
    'Provide interactive visual seat selection with 4 bus layout classes based on capacity',
    'Develop an agency dashboard with revenue breakdown by route and visual bar charts',
    'Implement rate limiting on all login endpoints (10 attempts per 15 minutes per IP)',
    'Add automatic bus status management (busy when scheduled, available when cancelled)',
]:
    doc.add_paragraph(s, style='List Bullet')

doc.add_page_break()

# ═══════════════════ 4. TOOLS & TECHNOLOGIES ═══════════════════

doc.add_heading('4. Tools and Technologies Used', level=1)

doc.add_heading('4.1 Backend Technologies', level=2)
add_table(
    ['Technology', 'Version', 'Purpose'],
    [
        ('Python', '3.10+', 'Primary programming language and runtime'),
        ('Flask', '2.x', 'Web framework (routing, sessions, templating, request handling)'),
        ('SQLite', '3.x (WAL mode)', 'Database engine — file-based, zero-configuration, transactional'),
        ('Werkzeug', '(Flask bundled)', 'Password hashing (scrypt), security utilities, debugger'),
        ('Pillow (PIL Fork)', '10.x', 'E-ticket PNG image generation with flag colours and QR-style refs'),
        ('xhtml2pdf', 'Latest', 'PDF ticket generation from HTML templates'),
        ('deep-translator', 'Latest', 'Google Translate API wrapper for auto-translation (no API key)'),
        ('python-dotenv', '1.x', 'Environment variable management (.env file for credentials)'),
        ('Jinja2', '(Flask bundled)', 'Server-side templating engine with template inheritance'),
    ]
)

doc.add_heading('4.2 Frontend Technologies', level=2)
add_table(
    ['Technology', 'Purpose'],
    [
        ('HTML5', 'Page structure with semantic elements'),
        ('CSS3 (Vanilla)', 'All styling — custom responsive grid system, CSS variables, animations, flexbox'),
        ('JavaScript (Vanilla)', 'Client-side interactivity — modals, navigation toggle, country search, seat picker'),
        ('Font Awesome 6.5.1', 'Icon library — navigation icons, status indicators, social links (CDN-loaded)'),
        ('Google Fonts (Inter)', 'Primary typeface — clean, modern, highly readable at all sizes'),
    ]
)

doc.add_heading('4.3 Development Tools', level=2)
add_table(
    ['Tool', 'Purpose'],
    [
        ('VS Code', 'Code editor with Python, Jinja2, and CSS extensions'),
        ('Git', 'Version control and change tracking'),
        ('PowerShell (Windows)', 'Command-line interface, script execution, automation'),
        ('SQLite Browser (DB Browser)', 'Database inspection and query testing'),
        ('Chrome DevTools', 'Responsive testing, network analysis, console debugging'),
        ('Postman / HTTPie', 'API route testing (GET/POST validation)'),
    ]
)

doc.add_heading('4.4 Development Environment', level=2)
doc.add_paragraph(
    'The application was developed on a Windows 11 machine running Python 3.10. The Flask development '
    'server was used for local testing with debug mode enabled. The database file (data.db) is created '
    'automatically on first run via the init_db() function in database.py.'
)
add_table(
    ['Component', 'Specification'],
    [
        ('Operating System', 'Windows 11'),
        ('Python', '3.10+'),
        ('Storage', 'SQLite (single file)'),
        ('Server', 'Flask development server (Werkzeug)'),
        ('Port', '5000 (default Flask)'),
        ('Static Files', 'Served directly from /static/ directory'),
        ('Templates', 'Jinja2 auto-reloading in debug mode'),
    ]
)

doc.add_page_break()

# ═══════════════════ 5. SYSTEM ARCHITECTURE ═══════════════════

doc.add_heading('5. System Architecture', level=1)

doc.add_heading('5.1 High-Level Architecture', level=2)
doc.add_paragraph(
    'AFRI Trans follows a monolithic Flask application pattern with three distinct user portals '
    '(Passenger, Agency, Ministry) sharing a common services layer and data layer. The monolithic '
    'approach was chosen deliberately for this project because:'
)
for reason in [
    'Single developer — simpler to develop, debug, and deploy without microservice overhead',
    'Shared session state — all portals share the same Flask session object seamlessly',
    'Consistent database access — all modules use the same database.py functions',
    'Simplified deployment — one process, one port, no inter-service communication needed',
]:
    doc.add_paragraph(reason, style='List Bullet')

doc.add_paragraph(
    'The architecture is organised into three layers:'
)

bold_line('Presentation Layer: ', 'Jinja2 templates render HTML/CSS/JavaScript for all three portals. '
    'Responsive CSS provides device-appropriate layouts across desktop, tablet, and mobile.')

bold_line('Application Layer: ', 'Flask route handlers in app.py process HTTP requests, enforce '
    'authentication/authorization, and coordinate business logic. Database operations are delegated '
    'to database.py functions.')

bold_line('Data Layer: ', 'SQLite database with 10+ tables stores all application data. The database '
    'module handles schema creation, CRUD operations, migrations, and connection management.')

doc.add_paragraph()
arch_text = (
    '  +========================================================+\n'
    '  |                    AFRI Trans                            |\n'
    '  +========================================================+\n'
    '  |                                                          |\n'
    '  |  +------------------+  +---------------+  +------------+ |\n'
    '  |  |  Passenger App   |  | Agency Portal |  | Ministry   | |\n'
    '  |  |                  |  |               |  | Portal     | |\n'
    '  |  | - Search trips   |  | - Dashboard   |  | - Overview | |\n'
    '  |  | - Book tickets   |  | - Buses/Routes|  | - Agencies | |\n'
    '  |  | - Pay online     |  | - Schedules   |  | - Approvals| |\n'
    '  |  | - Pick seats     |  | - Bookings    |  | - Bookings | |\n'
    '  |  | - View tickets   |  | - Manifests   |  | - Stats    | |\n'
    '  |  | - Feedback       |  | - Announc.    |  |            | |\n'
    '  |  | - Notifications  |  | - Pass. Reset |  | - Pass Reset| |\n'
    '  |  +------------------+  +---------------+  +------------+ |\n'
    '  |                                                          |\n'
    '  +--------------------- Shared Services -------------------+\n'
    '  |  +----------+  +----------+  +---------+  +-----------+ |\n'
    '  |  | i18n     |  | Country  |  | Payment |  | Auth/Sess | |\n'
    '  |  | Engine   |  | Manager  |  | Gateway |  | + Rate    | |\n'
    '  |  | 11 langs |  | 54 ctrys |  | 20+ pr. |  | Limiter   | |\n'
    '  |  +----------+  +----------+  +---------+  +-----------+ |\n'
    '  +----------------------------------------------------------+\n'
    '  |                     Data Layer                           |\n'
    '  |              +--------------------------+                 |\n'
    '  |              |  SQLite Database         |                 |\n'
    '  |              |  10+ tables, indexed,    |                 |\n'
    '  |              |  WAL journal mode        |                 |\n'
    '  |              +--------------------------+                 |\n'
    '  +----------------------------------------------------------+'
)
p = doc.add_paragraph()
r = p.add_run(arch_text)
r.font.name = 'Consolas'
r.font.size = Pt(7.5)

doc.add_heading('5.2 Request Flow', level=2)
doc.add_paragraph(
    'A typical booking request flows through the system as follows:'
)
flow_text = (
    'Passenger -> Search (country + cities + date)\n'
    '         -> Browse Results (grouped by period)\n'
    '         -> Select Schedule -> View Seat Map\n'
    '         -> Pick Seat -> Enter Passenger Details\n'
    '         -> Choose Payment Provider -> Confirm\n'
    '         -> Generate E-Ticket (HTML + PDF + PNG)\n'
    '         -> Lookup Later via Reference Number'
)
add_code(flow_text, size=9)

doc.add_heading('5.3 Session and Authentication Architecture', level=2)
doc.add_paragraph(
    'Flask sessions (signed cookies) manage user state across all three portals. '
    'The following session keys are used:'
)
add_table(
    ['Session Key', 'Type', 'Purpose'],
    [
        ('country', 'str', 'Currently selected country code (e.g., "cm", "ke")'),
        ('lang', 'str', 'Currently selected language code (e.g., "en", "fr")'),
        ('agency_id', 'int', 'Logged-in agency ID (None if not logged in)'),
        ('agency_name', 'str', 'Cached agency name for navbar display'),
        ('ministry_country', 'str', 'Logged-in ministry country scope'),
        ('super_admin_id', 'int', 'Logged-in super admin ID'),
        ('super_admin_email', 'str', 'Cached super admin email for display'),
        ('read_notification_ids', 'list', 'IDs of read announcements (per-notification tracking)'),
    ]
)

doc.add_paragraph(
    'Protected routes use decorator-style checks. For agencies, get_agency_session() validates '
    'that the agency_id in the session still corresponds to a valid database record. If the '
    'agency was deleted, the stale session entry is automatically removed and the user is '
    'redirected to login.'
)

doc.add_heading('5.4 Rate Limiting Architecture', level=2)
doc.add_paragraph(
    'An in-memory rate limiter protects all three login endpoints (/agency/login, '
    '/ministry/login, /ministry/relogin). Each IP address is tracked independently with '
    'a sliding window of 15 minutes:'
)
add_code(
    "login_attempts = defaultdict(list)\n"
    "RATE_LIMIT_WINDOW = 15  # minutes\n"
    "RATE_LIMIT_MAX = 10     # max attempts per window\n\n"
    "def is_rate_limited(ip):\n"
    "    now = datetime.now()\n"
    "    attempts = login_attempts[ip]\n"
    "    # Remove expired attempts outside the window\n"
    "    attempts[:] = [t for t in attempts\n"
    "                   if now - t < timedelta(minutes=RATE_LIMIT_WINDOW)]\n"
    "    if len(attempts) >= RATE_LIMIT_MAX:\n"
    "        return True, remaining_minutes\n"
    "    attempts.append(now)\n"
    "    return False, 0",
    size=8
)
doc.add_paragraph(
    'On successful login, the IP\'s attempt counter is cleared. The limiter uses an in-memory '
    'dictionary, which means it is per-process. In a multi-worker deployment (e.g., gunicorn), '
    'a Redis-backed solution would be needed for cross-process coordination.'
)

doc.add_page_break()

# ═══════════════════ 6. DATABASE DESIGN ═══════════════════

doc.add_heading('6. Database Design', level=1)

doc.add_heading('6.1 Schema Overview', level=2)
doc.add_paragraph(
    'The database uses SQLite with WAL (Write-Ahead Logging) journal mode for concurrent '
    'read/write performance. The schema contains 10 tables with proper foreign keys, '
    'ON DELETE CASCADE rules, and strategic indexes. Below is the complete schema '
    'documentation for every table.'
)

# agencies table
doc.add_heading('agencies', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique agency identifier'),
        ('name', 'TEXT', 'NOT NULL', 'Agency business name'),
        ('password', 'TEXT', 'NOT NULL', 'Scrypt-hashed password'),
        ('country', 'TEXT', 'NOT NULL DEFAULT \'cm\'', '2-letter ISO country code'),
        ('locations', 'TEXT', 'NOT NULL DEFAULT \'[]\'', 'JSON array of operating cities'),
        ('email', 'TEXT', 'DEFAULT \'\'', 'Admin email (unique when non-empty)'),
        ('phone', 'TEXT', 'DEFAULT \'\'', 'Contact phone number'),
        ('approved', 'INTEGER', 'DEFAULT 0', '0=pending, 1=approved'),
        ('rejection_reason', 'TEXT', 'DEFAULT \'\'', 'Reason if rejected by ministry'),
        ('approval_reason', 'TEXT', 'DEFAULT \'\'', 'Reason if approved by ministry'),
        ('reset_token', 'TEXT', '', 'Password reset verification token'),
        ('reset_token_expiry', 'TEXT', '', 'Token expiration timestamp'),
        ('created_at', 'TEXT', 'NOT NULL', 'ISO-format creation timestamp'),
    ]
)

# buses table
doc.add_heading('buses', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique bus identifier'),
        ('agency_id', 'INTEGER', 'REFERENCES agencies(id) ON DELETE CASCADE', 'Owner agency'),
        ('plate', 'TEXT', 'NOT NULL', 'Vehicle registration plate'),
        ('capacity', 'INTEGER', 'NOT NULL DEFAULT 71', 'Seat count (14–80 range)'),
        ('bus_type', 'TEXT', 'DEFAULT \'standard\'', '\'standard\' or \'vip\''),
        ('status', 'TEXT', 'DEFAULT \'available\'', '\'available\' or \'busy\''),
    ]
)

# routes table
doc.add_heading('routes', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique route identifier'),
        ('agency_id', 'INTEGER', 'REFERENCES agencies(id) ON DELETE CASCADE', 'Owner agency'),
        ('from_city', 'TEXT', 'NOT NULL', 'Origin city name'),
        ('to_city', 'TEXT', 'NOT NULL', 'Destination city name'),
        ('price', 'INTEGER', 'NOT NULL', 'Base fare in local currency'),
        ('duration', 'TEXT', 'DEFAULT \'\'', 'Travel time (e.g., "4 hours")'),
        ('luggage_enabled', 'INTEGER', 'DEFAULT 0', '1 if luggage service available'),
        ('luggage_price_per_kg', 'INTEGER', 'DEFAULT 0', 'Price per kg of luggage'),
    ]
)

# schedules table
doc.add_heading('schedules', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique schedule identifier'),
        ('route_id', 'INTEGER', 'REFERENCES routes(id) ON DELETE CASCADE', 'Associated route'),
        ('bus_id', 'INTEGER', 'REFERENCES buses(id) ON DELETE CASCADE', 'Assigned bus'),
        ('date', 'TEXT', 'NOT NULL', 'Departure date (YYYY-MM-DD)'),
        ('time', 'TEXT', 'NOT NULL', 'Departure time (HH:MM, 24h)'),
        ('period', 'TEXT', 'NOT NULL', '\'morning\', \'afternoon\', or \'night\''),
        ('status', 'TEXT', 'DEFAULT \'active\'', '\'active\' or \'cancelled\''),
    ]
)

# bookings table
doc.add_heading('bookings', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique booking identifier'),
        ('schedule_id', 'INTEGER', 'REFERENCES schedules(id) ON DELETE CASCADE', 'Associated trip'),
        ('passenger_id', 'INTEGER', 'REFERENCES passengers(id)', 'Passenger record'),
        ('seat_number', 'INTEGER', '', 'Assigned seat number'),
        ('booking_ref', 'TEXT', 'NOT NULL UNIQUE', 'Globally unique reference code'),
        ('paid', 'INTEGER', 'DEFAULT 0', '1 if payment completed'),
        ('status', 'TEXT', 'DEFAULT \'pending\'', '\'pending\', \'confirmed\', \'cancelled\''),
        ('payment_method', 'TEXT', '', 'Mobile money provider used'),
        ('transaction_id', 'TEXT', '', 'Payment transaction reference'),
        ('created_at', 'TEXT', 'NOT NULL', 'Booking creation timestamp'),
        ('luggage_weight', 'REAL', 'DEFAULT 0', 'Luggage weight in kg'),
        ('luggage_fee', 'INTEGER', 'DEFAULT 0', 'Total luggage charge'),
    ]
)
doc.add_paragraph(
    'Unique Index: CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_seat '
    'ON bookings(schedule_id, seat_number) WHERE seat_number IS NOT NULL;'
)

# passengers table
doc.add_heading('passengers', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique passenger identifier'),
        ('name', 'TEXT', 'NOT NULL', 'Passenger full name'),
        ('phone', 'TEXT', 'NOT NULL', 'Phone number'),
        ('id_number', 'TEXT', 'DEFAULT \'\'', 'Government ID number'),
        ('UNIQUE(phone, id_number)', '', '', 'Prevents duplicate passenger records'),
    ]
)

# announcements table
doc.add_heading('announcements', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique announcement identifier'),
        ('agency_id', 'INTEGER', 'REFERENCES agencies(id)', 'Creating agency'),
        ('message', 'TEXT', 'NOT NULL', 'English version of announcement'),
        ('message_fr', 'TEXT', 'DEFAULT \'\'', 'Auto-translated French version'),
        ('badge', 'TEXT', 'DEFAULT \'NEW\'', '\'NEW\', \'PROMO\', \'UPDATE\', \'GENERAL\''),
        ('is_active', 'INTEGER', 'DEFAULT 1', '1=active, 0=deactivated'),
        ('created_at', 'TEXT', 'NOT NULL', 'Creation timestamp'),
    ]
)

# feedback table
doc.add_heading('feedback', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique feedback identifier'),
        ('name', 'TEXT', 'DEFAULT \'\'', 'Auto-detected submitter name'),
        ('role', 'TEXT', 'DEFAULT \'user\'', '\'user\', \'agency\', \'ministry\''),
        ('message', 'TEXT', 'NOT NULL', 'Feedback content'),
        ('created_at', 'TEXT', 'NOT NULL', 'Submission timestamp'),
    ]
)

# super_admins table
doc.add_heading('super_admins', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique admin identifier'),
        ('email', 'TEXT', 'NOT NULL', 'Admin email address'),
        ('password_hash', 'TEXT', '', 'Scrypt-hashed password'),
        ('country_code', 'TEXT', 'NOT NULL', '2-letter ISO country code'),
        ('reset_token', 'TEXT', '', 'Password reset token'),
        ('reset_token_expiry', 'TEXT', '', 'Token expiry timestamp'),
        ('created_at', 'TEXT', 'NOT NULL', 'Account creation timestamp'),
        ('UNIQUE(email, country_code)', '', '', 'One admin per email per country'),
    ]
)

# commissions table
doc.add_heading('commissions', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT', 'Unique commission record'),
        ('agency_id', 'INTEGER', 'REFERENCES agencies(id)', 'Agency charged'),
        ('booking_id', 'INTEGER', 'REFERENCES bookings(id)', 'Source booking'),
        ('amount', 'INTEGER', 'NOT NULL', '1% of booking total'),
        ('created_at', 'TEXT', 'NOT NULL', 'Record creation timestamp'),
    ]
)

# meta table
doc.add_heading('meta', level=3)
add_table(
    ['Column', 'Type', 'Constraints', 'Description'],
    [
        ('key', 'TEXT', 'PRIMARY KEY', 'Config key (e.g., "migrated", "shared_pw_used_cm")'),
        ('value', 'TEXT', 'NOT NULL', 'Config value'),
    ]
)

doc.add_heading('6.2 Entity Relationship Diagram', level=2)
er_text = (
    'Agencies  1───* Buses          (one agency has many buses)\n'
    'Agencies  1───* Routes         (one agency defines many routes)\n'
    'Agencies  1───* Announcements  (one agency creates many announcements)\n'
    'Agencies  1───* Commissions    (one agency has many commission records)\n'
    'Routes    1───* Schedules      (one route has many scheduled trips)\n'
    'Buses     1───* Schedules      (one bus appears in many schedules)\n'
    'Schedules 1───* Bookings       (one trip has many bookings)\n'
    'Passengers 1───* Bookings      (one passenger can have many bookings)\n'
    'Countries 1───* Super_Admins   (one country has one super admin)'
)
add_code(er_text, size=9)

doc.add_heading('6.3 Migration from JSON to SQLite', level=2)
doc.add_paragraph(
    'The original implementation stored all data in a single JSON file (data.json). This caused '
    'several critical problems that were resolved by migrating to a normalised SQLite database:'
)
add_table(
    ['Issue', 'JSON Storage', 'SQLite Solution'],
    [
        ('ID Collisions', 'len(data[\'x\']) + 1 produced duplicates when items were deleted',
         'AUTOINCREMENT guarantees unique, monotonic IDs'),
        ('Passenger Data Duplication', 'Passenger details repeated across every booking',
         'Normalised passengers table with UNIQUE(phone, id_number)'),
        ('Route Price Duplication', 'Route prices duplicated for every schedule referencing them',
         'Route prices stored once in routes table, referenced by foreign key'),
        ('Orphan Records', 'Deleting an agency left orphan buses, routes, schedules, bookings',
         'ON DELETE CASCADE automatically removes all child records'),
        ('Concurrent Write Safety', 'Last writer wins — no transaction isolation',
         'WAL journal mode + IMMEDIATE transactions for atomicity'),
    ]
)
doc.add_paragraph(
    'The migration function (migrate_from_json()) reads the existing JSON file once and imports '
    'all data into the normalised SQLite structure. It tracks completion via a "migrated" key in '
    'the meta table to ensure idempotent execution — running the function multiple times does not '
    'duplicate data.'
)

doc.add_page_break()

# ═══════════════════ DEPLOYMENT GUIDE ═══════════════════

doc.add_heading('6.4 Deployment Guide', level=2)

doc.add_heading('Prerequisites', level=3)
add_table(
    ['Requirement', 'Version / Details'],
    [
        ('Python', '3.10 or higher'),
        ('Pip', 'Latest (for package installation)'),
        ('Operating System', 'Windows, Linux, or macOS'),
        ('Disk Space', 'Minimum 50 MB (application + database)'),
        ('SMTP Account', 'Gmail with App Password (for email features)'),
    ]
)

doc.add_heading('Step-by-Step Installation', level=3)
add_code(
    "# 1. Clone or copy the project\n"
    "git clone <repository-url> transport\n"
    "cd transport\n\n"
    "# 2. Install Python dependencies\n"
    "pip install flask pillow xhtml2pdf python-dotenv deep-translator\n\n"
    "# 3. Configure environment variables\n"
    "# Create .env file with:\n"
    "#   MAIL_USERNAME=your@gmail.com\n"
    "#   MAIL_PASSWORD=your-16-char-app-password\n"
    "#   FEEDBACK_EMAIL=your@gmail.com\n\n"
    "# 4. Initialise the database (first time only)\n"
    "python -c \"from database import init_db; init_db()\"\n\n"
    "# 5. Load country configuration\n"
    "python -c \"from database import migrate_from_json; migrate_from_json('countries.json')\"\n\n"
    "# 6. Start the Flask development server\n"
    "python app.py\n\n"
    "# 7. Open in browser\n"
    "# http://localhost:5000",
    size=8
)

doc.add_heading('First-Time Setup Checklist', level=3)
for item in [
    'Create a .env file with valid Gmail credentials (App Password for 2FA-enabled accounts)',
    'Initialise the database with init_db() — creates all tables automatically',
    'Load country data from countries.json',
    'Create a super admin account via the ministry login flow (step 1: Admin123, step 2: personal email + password)',
    'Register an agency account and log in to the agency portal',
    'Add buses, routes, and schedules from the agency dashboard',
    'Approve the agency via the ministry portal',
    'Search and book tickets as a passenger',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Production Deployment Considerations', level=3)
doc.add_paragraph('For production deployment, the following changes are recommended:')
add_table(
    ['Area', 'Development', 'Production'],
    [
        ('Web Server', 'Flask built-in (Werkzeug)', 'Gunicorn + Nginx (Linux) or Waitress + IIS (Windows)'),
        ('Database', 'SQLite (data.db)', 'PostgreSQL or MySQL (for higher concurrency)'),
        ('Session Storage', 'Signed cookies', 'Redis or database-backed sessions'),
        ('Rate Limiter', 'In-memory (per-process)', 'Redis (cross-process coordination)'),
        ('HTTPS', 'Not configured', 'Let\'s Encrypt SSL certificate + Nginx termination'),
        ('Static Files', 'Flask static folder', 'CDN or Nginx direct serving'),
        ('Environment Variables', '.env file', 'System environment variables or vault'),
        ('Error Monitoring', 'Flask debug mode', 'Sentry or custom logging with log rotation'),
        ('Secret Key', 'Hardcoded default', 'Generate with os.urandom(24), store in env'),
    ]
)

doc.add_page_break()

# ═══════════════════ 7. FILE STRUCTURE ═══════════════════

doc.add_heading('7. Complete File Structure', level=1)
doc.add_paragraph(
    'The project follows a standard Flask application layout with all application code in the '
    'root directory, templates in /templates/, static assets in /static/, and translations in '
    '/translations/. Below is the complete file structure as of July 2026.'
)

fs = (
    'transport/\n'
    '+-- app.py                         # Main Flask app: 48+ routes, 6 context processors\n'
    '+-- database.py                    # SQLite module: schema, CRUD, migration, helpers\n'
    '+-- countries.json                 # 54 African countries: flags, currencies, cities, providers\n'
    '+-- data.json                      # Original flat-file storage (legacy, migration source)\n'
    '+-- data.db                        # SQLite database (created by migration or init_db)\n'
    '+-- generate_translations.py       # Auto-translate en.json into 10 target languages\n'
    '+-- translate_announcements.py     # Back-fill message_fr for pre-existing announcements\n'
    '+-- generate_consolidated_report.py# This document generator\n'
    '+-- generate_readme_docx.py        # Legacy internship report generator\n'
    '+-- md_to_docx.py                  # Markdown-to-DOCX converter\n'
    '+-- .env                           # SMTP credentials (MAIL_USERNAME, MAIL_PASSWORD, etc.)\n'
    '+-- static/\n'
    '|   +-- style.css                  # All CSS: responsive grid, animations, components, utilities\n'
    '|   +-- img/\n'
    '|       +-- afritrans-logo.svg     # Brand logo (bus icon with text)\n'
    '+-- templates/\n'
    '|   +-- base.html                  # Base layout: nav, footer, country modal, flash messages\n'
    '|   +-- index.html                 # Homepage: hero, search card, agencies grid, stats\n'
    '|   +-- search.html                # Trip results grouped by period (morning/afternoon/night)\n'
    '|   +-- pick_seat.html             # Interactive seat map (pre-payment selection)\n'
    '|   +-- seats.html                 # Seat selection page (post-payment)\n'
    '|   +-- book.html                  # Passenger details form (name, phone, optional luggage)\n'
    '|   +-- payment.html               # Payment method selection (country-specific providers)\n'
    '|   +-- ticket.html                # E-ticket display (HTML format with flag colours)\n'
    '|   +-- ticket_pdf.html            # PDF-optimised ticket template\n'
    '|   +-- lookup.html                # Ticket lookup by reference number\n'
    '|   +-- notifications.html         # Announcements list with read tracking\n'
    '|   +-- notification_detail.html   # Single announcement detail view\n'
    '|   +-- feedback.html              # Feedback submission form\n'
    '|   +-- feedback_all.html          # Ministry: view all submitted feedback\n'
    '|   +-- agencies.html              # Browse all approved agencies\n'
    '|   +-- agency_browse.html         # Single agency public detail page\n'
    '|   +-- agency_dashboard.html      # Agency control panel: stats, revenue, recent bookings\n'
    '|   +-- agency_login.html          # Agency sign in\n'
    '|   +-- agency_register.html       # Agency registration form\n'
    '|   +-- agency_buses.html          # Bus list with status badges\n'
    '|   +-- agency_bus_form.html       # Add/edit bus form\n'
    '|   +-- agency_routes.html         # Route list with pricing\n'
    '|   +-- agency_route_form.html     # Add/edit route form\n'
    '|   +-- agency_schedules.html      # Schedule list with period grouping\n'
    '|   +-- agency_schedule_form.html  # Add/edit schedule form\n'
    '|   +-- agency_bookings.html       # Booking management with filters\n'
    '|   +-- agency_booking_reassign.html# Reassign booking to alternative trip\n'
    '|   +-- agency_manifest.html       # Passenger manifest for a trip\n'
    '|   +-- agency_announcements.html  # Announcement management with translation\n'
    '|   +-- agency_forgot_password.html# Password reset request\n'
    '|   +-- agency_reset_password.html # New password form\n'
    '|   +-- agency_verify_code.html    # 8-digit verification code entry\n'
    '|   +-- ministry_dashboard.html    # Ministry national overview dashboard\n'
    '|   +-- ministry_login.html        # 2-step ministry login (shared pw + personal)\n'
    '|   +-- ministry_relogin.html      # Set personal password after first login\n'
    '|   +-- ministry_agencies.html     # Agency registry: approve/reject with reasons\n'
    '|   +-- ministry_bookings.html     # Cross-agency booking view\n'
    '|   +-- ministry_forgot_password.html\n'
    '|   +-- ministry_reset_password.html\n'
    '|   +-- ministry_verify_code.html\n'
    '+-- translations/\n'
    '    +-- en.json                    # English source of truth (538+ translation keys)\n'
    '    +-- fr.json                    # French (manually maintained, fully translated)\n'
    '    +-- ar.json                    # Arabic (auto-generated + English fallback)\n'
    '    +-- pt.json                    # Portuguese (auto-generated + English fallback)\n'
    '    +-- es.json                    # Spanish (auto-generated + English fallback)\n'
    '    +-- sw.json                    # Swahili (auto-generated + English fallback)\n'
    '    +-- am.json                    # Amharic (auto-generated + English fallback)\n'
    '    +-- so.json                    # Somali (auto-generated + English fallback)\n'
    '    +-- ti.json                    # Tigrinya (auto-generated + English fallback)\n'
    '    +-- af.json                    # Afrikaans (auto-generated + English fallback)\n'
    '    +-- zu.json                    # Zulu (auto-generated + English fallback)'
)
add_code(fs, size=7)

doc.add_page_break()

# ═══════════════════ 8. FEATURES IMPLEMENTED ═══════════════════

doc.add_heading('8. Features Implemented', level=1)

doc.add_heading('8.1 Multi-Country Support (54 Countries)', level=2)
doc.add_paragraph(
    'All 54 African countries are configured in countries.json with comprehensive per-country '
    'localisation data. Each country record includes:'
)
for item in [
    'Country name (English) and 2-letter ISO code',
    'Flag colours — between 3 and 6 hex colour values for CSS variable injection',
    'Local currency symbol (e.g., FCFA, KSh, ZAR, EGP, NGN) and ISO code (e.g., XAF, KES, ZAR, EGP, NGN)',
    'Major cities — 8 to 18 cities per country for origin/destination selection',
    'Default language and list of supported languages for language toggle visibility',
    'Local mobile money payment providers and their display names',
    'VIP surcharge amount in local currency',
    'Booking reference prefix (e.g., CM for Cameroon, KE for Kenya)',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph('Example country configuration for Cameroon:')
add_code(
    "'cm': {\n"
    "    'name': 'Cameroon',\n"
    "    'flag_colors': ['#007a5e','#ce1126','#fcd116'],\n"
    "    'currency': 'FCFA',\n"
    "    'currency_code': 'XAF',\n"
    "    'ref_prefix': 'CM',\n"
    "    'cities': [\"Douala\",\"Yaoundé\",\"Bamenda\",\"Bafoussam\",\"Garoua\",\n"
    "              \"Maroua\",\"Ngaoundéré\",\"Bertoua\",\"Buea\",\"Limbe\",\n"
    "              \"Kumba\",\"Tiko\",\"Bota\",\"Mutengene\",\"Muyuka\",\"Bafang\"],\n"
    "    'lang': 'en',\n"
    "    'languages': ['en', 'fr'],\n"
    "    'providers': ['mtn_momo', 'orange_money'],\n"
    "    'vip_surcharge': 3000\n"
    "}",
    size=7
)

doc.add_paragraph(
    'Country switching is available via a globe icon in the navbar. Clicking it opens a searchable '
    'modal grid displaying all 54 countries with their flag colours as coloured bars. The user can '
    'search by country name and click to switch. On country switch, the language automatically '
    'changes to the country\'s default language.'
)

add_screenshot_placeholder('Figure 8.1a: Country selection modal showing all 54 African nations with flag colours')

doc.add_paragraph('The complete list of 54 supported countries with their currency and default language:')
add_table(
    ['#', 'Country', 'Code', 'Currency', 'Language', 'Cities'],
    [
        ('1', 'Algeria', 'dz', 'DZD', 'ar', 'Algiers, Oran, Constantine, Annaba, Blida, Tizi Ouzou'),
        ('2', 'Angola', 'ao', 'AOA', 'pt', 'Luanda, Huambo, Benguela, Lubango, Cabinda, Malanje'),
        ('3', 'Benin', 'bj', 'XOF', 'fr', 'Cotonou, Porto-Novo, Parakou, Abomey, Bohicon, Natitingou'),
        ('4', 'Botswana', 'bw', 'BWP', 'en', 'Gaborone, Francistown, Maun, Serowe, Kasane, Molepolole'),
        ('5', 'Burkina Faso', 'bf', 'XOF', 'fr', 'Ouagadougou, Bobo-Dioulasso, Koudougou, Ouahigouya, Banfora'),
        ('6', 'Burundi', 'bi', 'BIF', 'fr', 'Bujumbura, Gitega, Ngozi, Rumonge, Muyinga, Kayanza'),
        ('7', 'Cameroon', 'cm', 'XAF', 'en, fr', 'Douala, Yaoundé, Bamenda, Bafoussam, Garoua, Maroua, Buea'),
        ('8', 'Cape Verde', 'cv', 'CVE', 'pt', 'Praia, Mindelo, Santa Maria, São Filipe, Assomada'),
        ('9', 'CAR', 'cf', 'XAF', 'fr', 'Bangui, Bimbo, Berberati, Bambari, Bouar, Bossangoa'),
        ('10', 'Chad', 'td', 'XAF', 'fr', 'N\'Djamena, Moundou, Sarh, Abéché, Kélo, Koumra'),
        ('11', 'Comoros', 'km', 'KMF', 'ar', 'Moroni, Mutsamudu, Fomboni, Domoni, Iconi'),
        ('12', 'Congo', 'cg', 'XAF', 'fr', 'Brazzaville, Pointe-Noire, Dolisie, Nkayi, Owando, Ouesso'),
        ('13', 'Côte d\'Ivoire', 'ci', 'XOF', 'fr', 'Abidjan, Bouaké, Yamoussoukro, Korhogo, San-Pédro, Gagnoa'),
        ('14', 'DRC', 'cd', 'CDF', 'fr', 'Kinshasa, Lubumbashi, Kisangani, Goma, Bukavu, Mbuji-Mayi'),
        ('15', 'Djibouti', 'dj', 'DJF', 'ar', 'Djibouti City, Ali Sabieh, Tadjoura, Obock, Arta, Dikhil'),
        ('16', 'Egypt', 'eg', 'EGP', 'ar', 'Cairo, Alexandria, Giza, Luxor, Aswan, Sharm El Sheikh, Hurghada'),
        ('17', 'Equatorial Guinea', 'gq', 'XAF', 'es', 'Malabo, Bata, Ebebiyin, Aconibe, Mongomo, Evinayong'),
        ('18', 'Eritrea', 'er', 'ERN', 'ti', 'Asmara, Keren, Massawa, Assab, Mendefera, Barentu'),
        ('19', 'Eswatini', 'sz', 'SZL', 'en', 'Mbabane, Manzini, Big Bend, Malkerns, Nhlangano, Siteki'),
        ('20', 'Ethiopia', 'et', 'ETB', 'am', 'Addis Ababa, Dire Dawa, Bahir Dar, Gondar, Hawassa, Jimma'),
        ('21', 'Gabon', 'ga', 'XAF', 'fr', 'Libreville, Port-Gentil, Franceville, Oyem, Moanda, Lambaréné'),
        ('22', 'Gambia', 'gm', 'GMD', 'en', 'Banjul, Serrekunda, Brikama, Bakau, Farafenni, Barra'),
        ('23', 'Ghana', 'gh', 'GHS', 'en', 'Accra, Kumasi, Takoradi, Tamale, Cape Coast, Tema, Koforidua'),
        ('24', 'Guinea', 'gn', 'GNF', 'fr', 'Conakry, Kankan, Nzérékoré, Kindia, Labé, Mamou, Boké'),
        ('25', 'Guinea-Bissau', 'gw', 'XOF', 'pt', 'Bissau, Bafatá, Gabú, Bissorã, Bolama, Cacheu'),
        ('26', 'Kenya', 'ke', 'KES', 'en, sw', 'Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, Thika, Malindi'),
        ('27', 'Lesotho', 'ls', 'LSL', 'en', 'Maseru, Teyateyaneng, Mafeteng, Hlotse, Mohale\'s Hoek, Qacha\'s Nek'),
        ('28', 'Liberia', 'lr', 'LRD', 'en', 'Monrovia, Gbarnga, Buchanan, Harper, Voinjama, Zwedru'),
        ('29', 'Libya', 'ly', 'LYD', 'ar', 'Tripoli, Benghazi, Misrata, Sabha, Tobruk, Sirte, Zawiya'),
        ('30', 'Madagascar', 'mg', 'MGA', 'mg', 'Antananarivo, Toamasina, Antsirabe, Mahajanga, Fianarantsoa, Toliara'),
        ('31', 'Malawi', 'mw', 'MWK', 'en', 'Lilongwe, Blantyre, Mzuzu, Zomba, Karonga, Kasungu, Mangochi'),
        ('32', 'Mali', 'ml', 'XOF', 'fr', 'Bamako, Sikasso, Mopti, Koutiala, Ségou, Kayes, Gao'),
        ('33', 'Mauritania', 'mr', 'MRU', 'ar', 'Nouakchott, Nouadhibou, Kiffa, Kaédi, Zouérat, Atar, Rosso'),
        ('34', 'Mauritius', 'mu', 'MUR', 'en', 'Port Louis, Beau Bassin, Quatre Bornes, Curepipe, Vacoas, Phoenix'),
        ('35', 'Morocco', 'ma', 'MAD', 'ar', 'Casablanca, Rabat, Marrakech, Fes, Tangier, Agadir, Oujda'),
        ('36', 'Mozambique', 'mz', 'MZN', 'pt', 'Maputo, Beira, Nampula, Tete, Quelimane, Chimio, Pemba'),
        ('37', 'Namibia', 'na', 'NAD', 'en', 'Windhoek, Rundu, Walvis Bay, Swakopmund, Oshakati, Otjiwarongo'),
        ('38', 'Niger', 'ne', 'XOF', 'fr', 'Niamey, Zinder, Maradi, Tahoua, Agadez, Dosso, Diffa'),
        ('39', 'Nigeria', 'ng', 'NGN', 'en', 'Lagos, Abuja, Port Harcourt, Kano, Ibadan, Enugu, Kaduna, Benin City'),
        ('40', 'Rwanda', 'rw', 'RWF', 'en, fr', 'Kigali, Butare, Gisenyi, Ruhengeri, Gitarama, Kibungo'),
        ('41', 'São Tomé', 'st', 'STN', 'pt', 'São Tomé, Santo António, Neves, Trindade, Santana'),
        ('42', 'Senegal', 'sn', 'XOF', 'fr', 'Dakar, Touba, Thiès, Saint-Louis, Kaolack, Ziguinchor, Mbour'),
        ('43', 'Seychelles', 'sc', 'SCR', 'en', 'Victoria, Beau Vallon, Anse Royale, Cascade, Takamaka'),
        ('44', 'Sierra Leone', 'sl', 'SLL', 'en', 'Freetown, Bo, Kenema, Makeni, Koidu, Port Loko'),
        ('45', 'Somalia', 'so', 'SOS', 'so', 'Mogadishu, Hargeisa, Kismayo, Baidoa, Garowe, Bosaso, Beledweyne'),
        ('46', 'South Africa', 'za', 'ZAR', 'en, af, zu', 'Johannesburg, Cape Town, Durban, Pretoria, Port Elizabeth, Bloemfontein'),
        ('47', 'South Sudan', 'ss', 'SSP', 'en', 'Juba, Wau, Malakal, Bentiu, Bor, Yei, Rumbek'),
        ('48', 'Sudan', 'sd', 'SDG', 'ar', 'Khartoum, Omdurman, Port Sudan, Nyala, Kassala, El Obeid, Gadarif'),
        ('49', 'Tanzania', 'tz', 'TZS', 'en, sw', 'Dar es Salaam, Mwanza, Arusha, Dodoma, Mbeya, Zanzibar, Tanga'),
        ('50', 'Togo', 'tg', 'XOF', 'fr', 'Lomé, Sokodé, Kara, Kpalimé, Atakpamé, Dapaong, Tsévié'),
        ('51', 'Tunisia', 'tn', 'TND', 'ar', 'Tunis, Sfax, Sousse, Gabès, Bizerte, Kairouan, Gafsa'),
        ('52', 'Uganda', 'ug', 'UGX', 'en', 'Kampala, Gulu, Jinja, Mbale, Mbarara, Entebbe, Lira'),
        ('53', 'Zambia', 'zm', 'ZMW', 'en', 'Lusaka, Copperbelt, Livingstone, Kabwe, Ndola, Kitwe, Chipata'),
        ('54', 'Zimbabwe', 'zw', 'USD', 'en', 'Harare, Bulawayo, Chitungwiza, Mutare, Gweru, Kwekwe, Kadoma'),
    ],
    col_widths=[1, 3, 1.5, 2, 3, 6]
)

doc.add_heading('8.2 Internationalisation (11 Languages, 538+ Keys)', level=2)
doc.add_paragraph(
    'The platform supports 11 languages covering the major language groups across Africa:'
)
add_table(
    ['Code', 'Language', 'Script', 'Primary Countries'],
    [
        ('en', 'English', 'Latin', 'Nigeria, Ghana, Kenya, South Africa, Uganda, Tanzania, Zambia, Zimbabwe, etc.'),
        ('fr', 'French', 'Latin', 'Cameroon, Senegal, Côte d\'Ivoire, DRC, Mali, Burkina Faso, Niger, Benin, Togo, etc.'),
        ('ar', 'Arabic', 'Arabic', 'Egypt, Morocco, Algeria, Tunisia, Libya, Sudan, Mauritania'),
        ('pt', 'Portuguese', 'Latin', 'Angola, Mozambique, Cape Verde, Guinea-Bissau, São Tomé'),
        ('es', 'Spanish', 'Latin', 'Equatorial Guinea'),
        ('sw', 'Swahili', 'Latin', 'Tanzania, Kenya, Uganda, DRC, Rwanda, Burundi'),
        ('am', 'Amharic', 'Ge\'ez', 'Ethiopia'),
        ('so', 'Somali', 'Latin', 'Somalia, Djibouti, Ethiopia (Somali region)'),
        ('ti', 'Tigrinya', 'Ge\'ez', 'Eritrea, Ethiopia (Tigray region)'),
        ('af', 'Afrikaans', 'Latin', 'South Africa, Namibia'),
        ('zu', 'Zulu', 'Latin', 'South Africa'),
    ]
)

doc.add_heading('Translation Architecture', level=3)
doc.add_paragraph(
    'Each language has a dedicated JSON file in the /translations/ directory containing key-value '
    'pairs. The en.json file is the source of truth with 538+ keys covering every UI string in '
    'the application. The translation system works as follows:'
)
for item in [
    'All UI text is wrapped in _("text") function calls in Jinja2 templates',
    'The _() function loads the current language\'s JSON file and looks up the key',
    'If the key is missing in the target language, it falls back gracefully to the English text',
    'A language toggle is shown in the navbar only when the current country has 2+ supported languages',
    'Switching countries automatically switches to that country\'s default language',
    'Language preference is stored in session[\'lang\'] and a persistent cookie (365-day expiry)',
    'The generate_translations.py script auto-generates translation files from en.json using Google Translate',
    'French is manually maintained as the primary bilingual target for Cameroon',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.3 Passenger Booking Flow', level=2)
doc.add_paragraph(
    'The booking process follows a clear 7-step flow from search to e-ticket delivery. '
    'Each step builds on the previous one, with the passenger\'s selections preserved '
    'throughout the session.'
)

add_screenshot_placeholder('Figure 8.1: Homepage with search form, featured agencies, and statistics')

steps = [
    ('Search', 'Passenger selects origin city, destination city, and travel date on the homepage '
     'search form. The search form auto-fills with the current country\'s cities. A date picker '
     'limits selection to future dates (booking closes 15 min before departure).'),
    ('Browse Results', 'Available trips are displayed grouped by time period: Morning (05:00–11:59), '
     'Afternoon (12:00–16:59), and Night (17:00–04:59). Each trip card shows: agency name, bus plate, '
     'bus type (standard/VIP badge), departure time, travel duration, ticket price, and available '
     'seats count. Trips departing within 15 minutes are marked as "Closing Soon".'),
    ('Pick Seat', 'An interactive seat map shows the full bus layout with seat states: available '
     '(green), VIP (gold), taken (grey with person icon), and selected (blue). Clicking an '
     'available seat selects it and auto-scrolls to the booking button showing the total payable '
     'amount. VIP seats display the additional surcharge.'),
    ('Enter Details', 'Passenger provides: full name, phone number, and optional ID number. If the '
     'route supports luggage, an optional luggage weight field is shown with the per-kg price. '
     'If the passenger has booked before, their details are pre-filled.'),
    ('Payment', 'Country-specific mobile money providers are displayed as selectable options. '
     'For Cameroon: MTN MoMo and Orange Money. For Kenya: M-Pesa and Airtel Money. Payment is '
     'currently simulated with transaction ID generation. The total includes base fare + VIP '
     'surcharge (if applicable) + luggage fee (if applicable).'),
    ('Confirmation', 'The system re-checks seat availability inside a database transaction. If the '
     'seat was taken between selection and payment, the passenger is redirected to pick another '
     'seat. On success, the booking is confirmed with a unique reference number.'),
    ('E-Ticket', 'A full e-ticket is displayed with: passenger name, route (from → to), date and time, '
     'seat number, bus plate, agency name, price breakdown, payment method, transaction ID, and '
     'booking reference. The ticket is available in HTML, PDF (download), and PNG image formats. '
     'The passenger can also look up the ticket later via the reference number on the lookup page.'),
]
for i, (title, desc) in enumerate(steps):
    doc.add_heading(f'Step {i+1}: {title}', level=3)
    doc.add_paragraph(desc)

add_screenshot_placeholder('Figure 8.2: Interactive seat selection map with VIP/standard colour coding')

doc.add_heading('8.4 Interactive Seat Selection (4 Layout Classes)', level=2)
doc.add_paragraph(
    'The seat layout system supports 4 bus configuration classes, determined dynamically by '
    'bus capacity. Each class has a different column arrangement optimised for the bus size:'
)
add_table(
    ['Class', 'Capacity', 'Layout', 'Description'],
    [
        ('Class 1', '14–29 seats', 'Left(1) + Aisle + Right(2)', 'Compact mini-bus layout. 3 columns total. Suitable for small buses and shuttle services.'),
        ('Class 2', '30–40 seats', 'Left(2) + Aisle + Right(2)', 'Standard mid-size coach layout. 4 columns total. Common for regional routes.'),
        ('Class 3', '41–60 seats', 'Left(2) + Aisle + Centre(2) + Aisle + Right(3)', 'Large coach with centre walkway. 7 columns total. 2-2-3 configuration typical for inter-city buses.'),
        ('Class 4', '61–80 seats', 'Left(4) + Aisle + Right(3)', 'Max-capacity layout. 7 columns total. 4-3 configuration for maximum passenger capacity.'),
    ]
)
doc.add_paragraph(
    'Each seat has a type attribute: standard (green gradient background) or VIP (gold gradient '
    'background). VIP seats incur a per-country surcharge (e.g., 3,000 XAF in Cameroon, 500 KSh '
    'in Kenya, 50 ZAR in South Africa). The bus body visual includes: driver area (top), front '
    'entrance door, centre walkway, rear exit door, emergency exit markers, and toilet/storage '
    'area. A colour legend explains all seat states.'
)

doc.add_paragraph('Example: 71-seat layout (Class 4) visual representation:')
add_code(
    "Row 1:   [D][D][D] [ 1][ 2][ 3][ 4] | [ 5][ 6][ 7]  [E]\n"
    "Row 2:   [ ][ ][ ]  [ 8][ 9][10][11] | [12][13][14]  [ ]\n"
    "Row 3:   [ ][ ][ ]  [15][16][17][18] | [19][20][21]  [ ]\n"
    "...\n"
    "Row 14:  [ ][ ][ ]  [60][61][62][63] | [64][65][66]  [ ]\n"
    "Row 15:  [ ][ ][ ]  [67][68][69][70] | [71][E][E][E] [ ]\n"
    "                       [Driver]     [Door]",
    size=7
)
doc.add_paragraph(
    'D = Driver area, E = Emergency exit, numbers = seat positions, pipes = aisle. '
    'The layout is generated programmatically by the bus_layout() function in database.py.'
)

add_screenshot_placeholder('Figure 8.3: Full ticket view (HTML e-ticket with flag colours)')

doc.add_heading('8.5 Agency Portal', level=2)
doc.add_paragraph(
    'Agencies have a comprehensive dashboard for managing all aspects of their operations. '
    'The portal is accessible at /agency/* routes and requires agency login.'
)

doc.add_heading('Dashboard Overview', level=3)
doc.add_paragraph(
    'The agency dashboard (agency_dashboard.html) provides a complete operational overview:'
)
for item in [
    'Stats Cards: Total routes, total buses (with standard/VIP breakdown), total bookings, upcoming trips count',
    'Today\'s Trips: Highlight card showing today\'s schedules with route, period, time, bus plate, seat occupancy (booked/total), and a link to generate the passenger manifest',
    'Revenue by Route: Visual bar chart showing revenue contribution per route with percentage labels and colour-coded bars',
    'Recent Bookings: Table showing the last 8 bookings with passenger name, route, seat, status badge, and created-at timestamp',
    'Buses Table: All buses with plate number, type badge (standard/VIP), capacity, status badge (available/busy), and action buttons',
    'Routes Table: All routes with from→to, duration, price, luggage info, and edit button',
    'Upcoming Trips: Future schedules with manifest links and action buttons',
    'Quick Actions: Buttons for creating announcements, viewing all bookings, and adding schedules',
]:
    doc.add_paragraph(item, style='List Bullet')

add_screenshot_placeholder('Figure 8.4: Agency dashboard with revenue chart, stats cards, and recent bookings')

doc.add_heading('Bus Management', level=3)
for item in [
    'Add new buses: plate number (auto-uppercased), capacity (14–80, validated), type (standard/VIP)',
    'Edit existing buses: update any bus attribute',
    'Bus status toggling: manually set available/busy',
    'Auto-status management: bus is automatically set to "busy" when assigned to a schedule, and reverts to "available" when the schedule is cancelled',
    'Bus list: sortable table with type badges (standard=blue, VIP=gold), status badges (available=green, busy=red)',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Route Management', level=3)
for item in [
    'Define city pairs: select origin from agency locations, destination from other cities',
    'Set pricing: base fare in local currency (non-negative, validated)',
    'Set duration: travel time as text (e.g., "4 hours", "1 day")',
    'Configure luggage: enable/disable luggage service, set price per kg',
    'Edit existing routes: update any route attribute',
    'Route list: sortable table with pricing and luggage info',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Schedule Management', level=3)
for item in [
    'Create trips: assign a route + bus + date + time + period (morning/afternoon/night)',
    'Period auto-detection: time input automatically determines the period',
    'Only available buses are shown in the bus dropdown (busy buses are excluded)',
    'Edit schedules: change any schedule attribute',
    'Cancel schedules: sets status to "cancelled" and auto-reverts the bus to "available"',
    'Schedule list: grouped by period, filtered to future dates, with status badges',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Booking Management', level=3)
for item in [
    'View all bookings with passenger name, route, seat, status, payment method, and timestamp',
    'Cancel bookings: mark as cancelled, freeing the seat for rebooking',
    'Reassign bookings: move a passenger to a different trip without losing payment — useful when a schedule is cancelled',
    'Passenger manifest: generate and print a manifest for any scheduled trip showing all booked passengers with seat numbers',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Announcements', level=3)
for item in [
    'Create announcements with a message title and badge type (NEW/PROMO/UPDATE/GENERAL)',
    'Automatic French translation: message is translated to French using Google Translate and stored in message_fr column',
    'Deactivate old announcements: set is_active = 0 to hide from passengers',
    'Announcement list: all active and inactive announcements with status badges',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Commission Visibility', level=3)
doc.add_paragraph(
    'The 1% platform commission is handled transparently. The actual commission amount in '
    'currency is NEVER displayed in any agency or ministry UI. Only the rate (1%) is shown '
    'as an informational badge: "Platform Commission (1%) / Deducted automatically per booking". '
    'This prevents friction between the platform and agencies while maintaining transparency '
    'about the fee structure. The commission amount is stored in the commissions table for '
    'platform owner reference only.'
)

doc.add_heading('Registration Flow', level=3)
for item in [
    'Agency fills registration form: name, email, phone, country, operating locations, password',
    'System creates agency account with approved=0 (pending status)',
    'Agency is invisible to passengers until approved by the Ministry',
    'Ministry reviews and approves/rejects with a reason (stored permanently)',
    'On approval, agency receives a banner on their dashboard and becomes searchable to passengers',
    'On rejection, the rejection reason is displayed on the agency dashboard',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.6 Ministry of Transport Portal', level=2)
doc.add_paragraph(
    'Each country has its own scoped Ministry portal accessible at /ministry/* routes. '
    'The portal provides government oversight of all transport agencies operating in the country.'
)

doc.add_heading('2-Step Login Process', level=3)
for item in [
    'Step 1 — Shared Password: On first visit, the minister enters the shared password (Admin123). '
     'This is a ONE-TIME-USE credential. On successful entry, a flag (shared_pw_used_{country}) '
     'is set to "1" in the meta table.',
    'Step 2 — Personal Account Setup: The minister is redirected to set a personal email and '
     'password. After this, all future logins use step 2 directly.',
    'Subsequent Visits: The system checks the meta table and redirects straight to step 2, '
     'skipping the shared password form entirely.',
    'Security: The shared password POST route rejects attempts if the flag is already set, '
     'preventing any reuse of Admin123.',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Dashboard', level=3)
for item in [
    'Stats grid: registered agencies, pending approvals (with pulse animation when >0), total bookings, total revenue',
    'Commission info badge showing the 1% platform rate',
    'Active trips count for the current date',
    'Fleet overview: total buses, routes, and schedules across all agencies in the country',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('Agency Registry', level=3)
for item in [
    'Full list of all agencies in the minister\'s country',
    'Each row shows: agency name, country, locations, bus count, route count, booking count',
    'Status badges: approved (green), PENDING (orange with pulse), rejected (red)',
    'Approve action: opens a modal to enter approval reason (stored permanently, shown to agency)',
    'Reject action: opens a modal to enter rejection reason (stored permanently, shown to agency dashboard)',
]:
    doc.add_paragraph(item, style='List Bullet')

add_screenshot_placeholder('Figure 8.5: Ministry dashboard with stats grid and agency registry')

doc.add_heading('Booking Records', level=3)
doc.add_paragraph(
    'Cross-agency view of all bookings within the minister\'s country, showing: passenger name, '
    'phone, route, schedule, seat number, booking reference, payment status, and agency name. '
    'This allows the ministry to monitor booking activity across all operators.'
)

doc.add_heading('8.7 E-Ticket Generation (3 Formats)', level=2)
doc.add_paragraph(
    'Tickets are generated in three formats to support different use cases:'
)
add_table(
    ['Format', 'Route', 'Technology', 'Features'],
    [
        ('HTML', '/ticket/<ref>', 'Jinja2 template', 'Full web page with country flag colours, responsive layout, all booking details'),
        ('PNG Image', '/ticket/<ref>/image', 'Pillow (PIL)', 'Rendered graphics: flag colours in header/footer, QR-style reference, route map, VIP badge, price breakdown, seat layout'),
        ('PDF', '/ticket/<ref>/pdf', 'xhtml2pdf', 'Print-optimised layout, suitable for email attachment and mobile download'),
    ]
)
doc.add_paragraph(
    'The PNG ticket generation uses Pillow to draw a complete ticket image including: country '
    'flag colours in the header and footer, a QR-style reference number block, route mapping '
    '(from → to with arrow), passenger name and phone, seat number in large font, VIP/Standard '
    'badge with colour coding, price breakdown showing base fare, VIP surcharge, luggage fee, '
    'and total, validity period (departure date/time), and agency and bus information.'
)

doc.add_heading('8.8 Bilingual Announcement System', level=2)
doc.add_paragraph(
    'Cameroon is bilingual (English and French). All agency announcements must be visible in '
    'the passenger\'s preferred language. The system handles this through a dedicated architecture:'
)
for item in [
    'Auto-translation: When an agency creates an announcement, the message is automatically translated to French using Google Translate (via the deep-translator library) and stored in the message_fr column',
    'Storage at creation time: The French translation is stored at creation time (not on-the-fly) to avoid repeated API calls on every page load — this is critical for performance',
    'ann_msg() helper: A context processor function (injected via @app.context_processor) that returns the French message when the current language is French, otherwise returns English',
    'Template usage: All templates use ann_msg(ann) instead of ann.message to display announcements correctly in both languages',
    'Back-fill script: translate_announcements.py handles existing announcements that were created before the feature was implemented, ensuring no announcement is left untranslated',
    'Schema compatibility: get_announcements() uses SELECT a.* so it automatically includes the message_fr column without schema changes to existing queries',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.9 Per-Notification Read Tracking', level=2)
doc.add_paragraph(
    'Passengers can see which announcements they have and haven\'t read without requiring '
    'user login or account creation. This is achieved through session-based tracking:'
)
for item in [
    'Tracking mechanism: Read announcement IDs are stored in session[\'read_notification_ids\'] as a Python list',
    'Mark as read: When a passenger clicks "Read More" on an announcement in the notifications list, the announcement ID is added to the read list',
    'Unread count: The navbar bell icon displays a red badge (#c62828) with the count of unread announcements (total active announcements minus IDs in read_notification_ids)',
    'Visual indicators: In the notifications list, unread announcements show a blue dot indicator; read announcements show a green checkmark with "Lire" (French for "Read") label',
    'Cache prevention: Both /notifications and /notification/<id> pages use no-store, no-cache, must-revalidate HTTP cache headers to prevent stale notification data',
    'Logout cleanup: The logout function clears read_notification_ids from the session',
]:
    doc.add_paragraph(item, style='List Bullet')

add_screenshot_placeholder('Figure 8.6: Notifications page showing unread (blue dot) and read (green checkmark) announcements')

doc.add_heading('8.10 Feedback System', level=2)
doc.add_paragraph(
    'A feedback form allows any user to submit suggestions, bug reports, or general comments. '
    'The system was designed with simplicity in mind — a single message field with automatic '
    'role detection.'
)
for item in [
    'Access: Available at /feedback route, linked from the navbar as "Feedback"',
    'Form: Single message field (textarea) — no manual name or role fields required from the user',
    'Auto-detection: Name and role are automatically detected from the session:'
     ' passenger (role: "user", name: blank), agency (role: "agency", name from database),'
     ' ministry (role: "ministry", name from session email)',
    'Storage: Feedback is stored in the feedback table with name, role, message, and timestamp',
    'Email notification: On every submission, an email is sent to FEEDBACK_EMAIL (configured in .env)'
     ' via Gmail SMTP with the submitter\'s name, role, and message body',
    'Ministry view: Super admins can view all feedback at /feedback/all, listed newest-first with'
     ' role badges (agency=green, ministry=red, user=grey)',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.11 Payment Providers (20+ Networks)', level=2)
doc.add_paragraph(
    '20 African mobile money and digital payment providers are configured across the continent. '
    'Each country has its own set of providers based on local availability:'
)
add_table(
    ['Provider', 'Code', 'Active Countries'],
    [
        ('MTN MoMo', 'mtn_momo', 'Cameroon, Nigeria, Ghana, Côte d\'Ivoire, Uganda, Zambia, Rwanda, Benin'),
        ('Orange Money', 'orange_money', 'Cameroon, Senegal, Côte d\'Ivoire, Mali, Burkina Faso, Niger, Benin, Togo, Madagascar'),
        ('M-Pesa', 'mpesa', 'Kenya, Tanzania, DRC, Lesotho, Mozambique, Ghana, Ethiopia'),
        ('Airtel Money', 'airtel_money', 'Kenya, Uganda, Rwanda, Zambia, Chad, DRC, Congo, Niger, Madagascar, Malawi, Tanzania, Gabon, Seychelles'),
        ('EMOLA', 'emola', 'Mozambique, Angola'),
        ('EcoCash', 'ecocash', 'Zimbabwe'),
        ('Wave', 'wave', 'Senegal, Côte d\'Ivoire'),
        ('Telebirr', 'telebirr', 'Ethiopia'),
        ('Zaad', 'zaad', 'Somalia'),
        ('Opay', 'opay', 'Nigeria'),
        ('Paga', 'paga', 'Nigeria'),
        ('Tigo Pesa', 'tigo_pesa', 'Tanzania'),
        ('Halo Pesa', 'halo_pesa', 'Tanzania'),
        ('Equity', 'equity', 'Kenya'),
        ('Mobicash', 'mobicash', 'Tanzania'),
        ('FreeMoney', 'freemoney', 'Senegal'),
        ('Wari', 'wari', 'Senegal, Mali, Burkina Faso'),
        ('M-Pesa (Ghana)', 'mpesa_gh', 'Ghana'),
        ('Cassava', 'cassava', 'Ghana'),
        ('Spay', 'spay', 'Somalia'),
    ]
)
doc.add_paragraph(
    'Payment is currently simulated with transaction ID generation. In production, these would '
    'connect to real mobile money APIs via provider-specific SDKs or aggregate payment gateways.'
)

doc.add_heading('8.12 Mobile Responsiveness', level=2)
doc.add_paragraph(
    'The interface is fully responsive with four breakpoints. All CSS is vanilla (no framework) '
    'using CSS custom properties for flag colour theming and custom responsive utility classes.'
)
add_table(
    ['Breakpoint', 'Target Devices', 'Key Layout Changes'],
    [
        ('1024px', 'Tablets, small laptops', '4-column grids → 2-column. Container padding reduced. Nav items compacted.'),
        ('768px', 'Tablet portrait, large phones', 'All grids → single column. Hamburger navigation appears. Hero padding reduced. Table min-width drops for horizontal scroll.'),
        ('480px', 'Landscape phones', 'Country modal grid → 1 column. Buttons and form inputs shrink. Negative margins for edge-to-edge scrolling tables. Seat size reduces to 30px max-width.'),
        ('360px', 'Very small phones', 'Minimal padding. Smallest font sizes (clamp()). Table min-width drops to 280px. Everything optimised for one-handed use.'),
    ]
)

doc.add_paragraph('Key responsive features include:')
for item in [
    'Hamburger navigation toggle with smooth slide animation and click-outside-to-close',
    'All tables wrapped in scrollable containers with overflow-x: auto and sticky headers',
    'Fluid typography using clamp() for heading sizes',
    'Seat layout scales down proportionally on mobile with touch-friendly tap targets',
    'Nav language buttons arranged horizontally on mobile (not stacked)',
    'Dashboards use responsive stat grids (dash-stats, trip-row, trip-action classes)',
    'Bus layout adjusts column widths for smaller screens',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.13 Agency Privacy', level=2)
doc.add_paragraph(
    'Competing agencies cannot see each other\'s operational data. The privacy system uses '
    'session-aware filtering:'
)
for item in [
    'When an agency employee is logged in, all public-facing pages (homepage, search results, agency listings) filter to show ONLY that agency\'s data',
    'Direct URL access to competitor agency pages (e.g., /agency/browse/<id>) is blocked with an "Access denied" message when the session agency_id doesn\'t match',
    'Regular passengers (not logged in as an agency) continue to see all approved agencies',
    'Ministry users see everything within their country scope across all agencies',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.14 Bus Auto-Status Management', level=2)
doc.add_paragraph(
    'Buses have two operational states: "available" and "busy". The system manages transitions '
    'automatically to prevent scheduling conflicts:'
)
for item in [
    'Automatic busy: When add_schedule() creates a new schedule, the assigned bus\'s status is automatically set to "busy"',
    'Automatic available: When update_schedule() sets a schedule status to "cancelled", the bus automatically reverts to "available"',
    'Manual override: Agencies can still manually change bus status if needed through the bus management interface',
    'Visual indicator: Bus status is displayed as a coloured badge (available=green, busy=red) in all bus listings',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.15 One-Time Shared Password', level=2)
doc.add_paragraph(
    'The default super admin shared password (Admin123) presented a security vulnerability — '
    'anyone who knew it could access any country\'s ministry portal. The one-time-use mechanism '
    'eliminates this risk:'
)
for item in [
    'First visit: The GET route for /ministry/login checks the meta table for shared_pw_used_{country}. If not set, it shows the shared password form (step 1)',
    'On successful entry of Admin123: The flag shared_pw_used_{country} is set to "1" in the meta table. The user is redirected to step 2 to set a personal email and password',
    'Subsequent visits: The GET route checks the flag and redirects straight to step 2 (personal login), skipping the shared password form entirely',
    'Security enforcement: The POST route for step 1 explicitly rejects the shared password if the flag is already set, preventing any reuse even via direct POST requests',
    'Password recovery: Both agency and ministry users have complete password reset flows with 8-digit verification codes sent via email, with configurable expiry time',
]:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ═══════════════════ 9. BUSINESS RULES ═══════════════════

doc.add_heading('9. Business Rules & Constraints', level=1)

doc.add_heading('Commission Rules', level=2)
for r in [
    '1% commission is calculated on the booking total (base price + VIP surcharge + luggage fee)',
    'Commission is deducted at source before the remaining 99% is attributed to the agency',
    'The commission amount in currency is NEVER displayed in any UI — not on agency dashboard, not on ministry dashboard',
    'Only the rate (1%) is shown as an informational badge: "Platform Commission (1%) / Deducted automatically per booking"',
    'Commission records are stored in the commissions table for platform owner reference and financial reconciliation',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Bus Constraints', level=2)
for r in [
    'Capacity: minimum 14 seats, maximum 80 seats (enforced in form validation with error messages)',
    'Two types: standard and VIP. VIP seats add a per-country surcharge to the base fare',
    'Bus plate numbers are uppercased automatically and unique per agency',
    'Status auto-managed: busy when assigned to an active schedule, available when cancelled',
    'One email address = one agency globally (UNIQUE constraint enforced at database level)',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Schedule Constraints', level=2)
for r in [
    'Three periods: morning (05:00–11:59), afternoon (12:00–16:59), night (17:00–04:59)',
    'Each schedule must have a unique combination of route, bus, date, and time',
    'Only future schedules are shown in agency and ministry dashboards',
    'Booking closes 15 minutes before departure time (enforced in booking flow)',
    'Trips are auto-expired 2 hours after departure (marked as "completed")',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Booking Rules', level=2)
for r in [
    'A booking references exactly one schedule and one seat number',
    'Status flow: pending → confirmed (on payment) or cancelled',
    'Reference number is auto-generated and globally unique (pattern: COUNTRY-XXXXXXX where XXXXXXX is a random 7-character alphanumeric)',
    'Seats are unique per schedule — enforced by database-level partial unique index: CREATE UNIQUE INDEX idx_bookings_seat ON bookings(schedule_id, seat_number) WHERE seat_number IS NOT NULL',
    'Passenger can look up ticket by reference without logging in (public /lookup route)',
    'Reassign feature allows moving a booking to a different schedule without losing payment — preserves all booking details',
    'Bookings auto-expire 24 hours after departure (status set to "expired")',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Security Rules', level=2)
for r in [
    'The shared password (Admin123) is invalidated after first successful super admin login via meta table flag',
    'All /agency/* routes are protected by get_agency_session() — redirects to login if session missing or invalid',
    'get_agency_session() validates that the agency still exists in the database on every single call — removes stale session if agency was deleted',
    'Rate limiting: 10 failed login attempts per 15-minute sliding window per IP address on all login endpoints',
    'Successful login clears the IP\'s failed attempt counter',
    'Logout clears read_notification_ids and agency_id from session for complete session cleanup',
    'Password reset uses 8-digit verification code sent via email with configurable expiry',
    'Ministry logout clears super_admin_id and ministry_country from session',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Notification Rules', level=2)
for r in [
    'Bell icon colour: #c62828 (red) for ALL countries — NOT the country\'s flag-2 colour (this was a deliberate bug fix)',
    'Bell badge count = total active announcements minus IDs in read_notification_ids list',
    'Both /notifications and /notification/<id> pages use no-store, no-cache, must-revalidate HTTP cache headers',
    'Blue dot indicator = unread announcement; green checkmark + "Lire" label = read announcement',
    'Unread count is recalculated on every page load via the context processor',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Translation Rules', level=2)
for r in [
    'en.json is the source of truth — all other language JSON files are derivatives',
    'Missing keys in any language fall back to English text automatically via _().get(text, text)',
    'French announcement translation is stored in message_fr column at creation time — never on-the-fly',
    'ann_msg(ann) returns French version if current language is French AND message_fr is non-empty, otherwise returns English version',
    'Language preference is stored in session[\'lang\'] and a persistent cookie with 365-day expiry',
    'Language toggle is only visible when the current country has 2+ supported languages',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_heading('Agency Privacy Rules', level=2)
for r in [
    'When agency_id is in session, all public pages filter to show only that agency\'s data',
    'Direct URL access to competitor agency pages is blocked with "Access denied" authorisation message',
    'Ministry users see everything within their country scope across all agencies',
    'Regular passengers (no agency_id in session) see all approved agencies without restriction',
]:
    doc.add_paragraph(r, style='List Bullet')

doc.add_page_break()

# ═══════════════════ 10. IMPLEMENTATION DETAILS ═══════════════════

doc.add_heading('10. Implementation Details', level=1)

doc.add_heading('10.1 Key Code Patterns', level=2)

doc.add_heading('Translation Wrapper', level=3)
add_code(
    "def _(text):\n"
    "    lang = get_current_lang()\n"
    "    t = load_translations(lang)\n"
    "    return t.get(text, text)  # Falls back to original English if key missing",
    size=9
)
doc.add_paragraph(
    'Note: for _ in range(...) shadows the _() function in templates. Always use a different '
    'loop variable name such as for idx in range(...) or for i in range(...).'
)

doc.add_heading('Context Processor (inject_globals)', level=3)
add_code(
    "# Available in ALL templates:\n"
    "#   _()              - translation function\n"
    "#   current_lang     - 'en', 'fr', 'ar', etc.\n"
    "#   country          - current country config dict (flag colours, currency, etc.)\n"
    "#   COUNTRIES        - dictionary of all 54 countries\n"
    "#   cities           - current country's cities list\n"
    "#   today            - today's date in ISO format (YYYY-MM-DD)\n"
    "#   ann_msg(ann)     - bilingual announcement display helper\n"
    "#   total_ann_count  - count of unread announcements for bell badge\n"
    "#   read_ids         - set of read announcement IDs for template checks",
    size=8
)

doc.add_heading('Country-Scoped Query (Agency Privacy)', level=3)
add_code(
    "def _country_agencies():\n"
    "    code = session.get('country', 'cm')\n"
    "    agencies = get_approved_agencies_by_country(code)\n"
    "    if 'agency_id' in session:\n"
    "        agencies = [a for a in agencies if a['id'] == session['agency_id']]\n"
    "    return agencies",
    size=9
)

doc.add_heading('Bilingual Announcement Helper', level=3)
add_code(
    "def ann_msg(ann):\n"
    "    \"\"\"Return the appropriate language version of an announcement.\"\"\"\n"
    "    if get_current_lang() == 'fr' and ann.get('message_fr'):\n"
    "        return ann['message_fr']\n"
    "    return ann.get('message', '')",
    size=9
)

doc.add_heading('Atomic Booking with Race Condition Protection', level=3)
add_code(
    "def add_booking_atomic(schedule_id, passenger_id, seat_number, ...):\n"
    "    conn = get_db()\n"
    "    conn.execute('BEGIN IMMEDIATE')\n"
    "    try:\n"
    "        # Re-check seat availability inside the transaction\n"
    "        existing = conn.execute(\n"
    "            'SELECT id FROM bookings WHERE schedule_id=? AND seat_number=?',\n"
    "            (schedule_id, seat_number)).fetchone()\n"
    "        if existing:\n"
    "            conn.execute('ROLLBACK')\n"
    "            return False, 'Seat already taken'\n"
    "        # Insert booking\n"
    "        conn.execute('INSERT INTO bookings ...')\n"
    "        conn.execute('COMMIT')\n"
    "        return True, ref\n"
    "    except IntegrityError:\n"
    "        conn.execute('ROLLBACK')\n"
    "        return False, 'That seat was just taken by another passenger'",
    size=7
)

doc.add_heading('Rate Limiter', level=3)
add_code(
    "login_attempts = defaultdict(list)\n\n"
    "def is_rate_limited(ip):\n"
    "    now = datetime.now()\n"
    "    attempts = login_attempts[ip]\n"
    "    # Sliding window: keep only attempts within last 15 minutes\n"
    "    attempts[:] = [t for t in attempts\n"
    "                   if now - t < timedelta(minutes=15)]\n"
    "    if len(attempts) >= 10:\n"
    "        oldest = attempts[0]\n"
    "        wait = 15 - (now - oldest).total_seconds() / 60\n"
    "        return True, int(wait)\n"
    "    attempts.append(now)\n"
    "    return False, 0",
    size=8
)

doc.add_heading('Bus Auto-Status Management', level=3)
add_code(
    "# In add_schedule() — auto-set bus to busy\n"
    "def add_schedule(route_id, bus_id, date, time, period):\n"
    "    conn = get_db()\n"
    "    conn.execute('INSERT INTO schedules ...')\n"
    "    conn.execute('UPDATE buses SET status=\"busy\" WHERE id=?', (bus_id,))\n"
    "    conn.commit()\n\n"
    "# In update_schedule() — revert bus when cancelled\n"
    "def update_schedule(sid, status):\n"
    "    conn = get_db()\n"
    "    if status == 'cancelled':\n"
    "        bus_id = conn.execute(\n"
    "            'SELECT bus_id FROM schedules WHERE id=?', (sid,)).fetchone()[0]\n"
    "        conn.execute('UPDATE buses SET status=\"available\" WHERE id=?', (bus_id,))\n"
    "    conn.execute('UPDATE schedules SET status=? WHERE id=?', (status, sid))\n"
    "    conn.commit()",
    size=7
)

doc.add_heading('10.2 Complete Route Inventory', level=2)
doc.add_paragraph('The application has 48+ routes serving three user portals:')

add_table(
    ['Category', 'Count', 'Routes'],
    [
        ('Passenger', '13', '/, /search, /pick-seat/<sid>, /book/<sid>, /payment/<bid>, /confirm-payment/<bid>, /ticket/<ref>, /ticket/<ref>/pdf, /ticket/<ref>/image, /lookup, /feedback, /feedback/all, /notifications, /notification/<nid>'),
        ('Utility', '4', '/lang/<lang>, /country/<code>, /agencies, /agency/<aid>'),
        ('Agency', '22', '/agency/login, /agency/register, /agency/logout, /agency/dashboard, /agency/buses, /agency/buses/add, /agency/buses/<bid>/edit, /agency/routes, /agency/routes/add, /agency/routes/<rid>/edit, /agency/schedules, /agency/schedules/add, /agency/schedules/<sid>/edit, /agency/bookings, /agency/bookings/<bid>/reassign, /agency/manifest/<sid>, /agency/announcements, /agency/announcements/add, /agency/forgot-password, /agency/verify-code, /agency/reset-password'),
        ('Ministry', '11', '/ministry/login, /ministry/relogin, /ministry/logout, /ministry/dashboard, /ministry/agencies, /ministry/agencies/<aid>/approve, /ministry/agencies/<aid>/reject, /ministry/bookings, /ministry/forgot-password, /ministry/verify-code, /ministry/reset-password'),
    ]
)

doc.add_heading('10.3 Email Configuration', level=2)
doc.add_paragraph(
    'The application uses Gmail SMTP for sending email notifications (feedback submissions '
    'and password reset codes). Configuration is loaded from a .env file using python-dotenv:'
)
add_code(
    'MAIL_USERNAME=your@gmail.com\n'
    'MAIL_PASSWORD=your-16-char-app-password\n'
    'MAIL_FROM=your@gmail.com\n'
    'FEEDBACK_EMAIL=your@gmail.com\n'
    'MAIL_SERVER=smtp.gmail.com\n'
    'MAIL_PORT=587',
    size=9
)
doc.add_paragraph(
    'The .env file is excluded from version control via .gitignore. The load_dotenv() function '
    'is called at application startup in app.py. Gmail requires an "App Password" (16-character) '
    'when 2-factor authentication is enabled on the Google account.'
)

doc.add_heading('10.4 Bus Layout Algorithm', level=2)
doc.add_paragraph(
    'The bus_layout() function in database.py generates a 2D grid representing the bus interior. '
    'It takes the bus capacity and type (standard/VIP) and returns a list of rows, where each '
    'row contains cells. Each cell is either a seat (with number and type), a walkway, a door, '
    'or empty space. The layout supports 4 configuration classes based on capacity ranges '
    '(Class 1: 14–29, Class 2: 30–40, Class 3: 41–60, Class 4: 61–80 seats).'
)
doc.add_paragraph(
    'The algorithm works as follows: (1) Determine layout class from capacity, (2) Calculate '
    'number of rows based on seats per row, (3) Generate each row with seat numbers, aisles, '
    'and special elements, (4) Assign seat types — the last row and window seats are VIP for '
    'standard buses, or all seats are VIP for VIP buses.'
)

doc.add_heading('10.5 Session Management', level=2)
doc.add_paragraph(
    'Flask uses signed session cookies to maintain state across HTTP requests. The application '
    'stores the following in the session:'
)
add_table(
    ['Key', 'Type', 'Set When', 'Cleared When'],
    [
        ('country', 'str', 'Country switch, first visit', 'Logout (not needed — persists across sessions)'),
        ('lang', 'str', 'Language switch, country switch', 'Logout (not needed — persists across sessions)'),
        ('agency_id', 'int', 'Successful agency login', 'Agency logout, stale session cleanup'),
        ('agency_name', 'str', 'Successful agency login', 'Agency logout'),
        ('ministry_country', 'str', 'Successful ministry login', 'Ministry logout'),
        ('super_admin_id', 'int', 'Successful ministry login', 'Ministry logout'),
        ('super_admin_email', 'str', 'Successful ministry login', 'Ministry logout'),
        ('read_notification_ids', 'list', 'Viewing notification detail', 'Agency logout'),
    ]
)

doc.add_heading('10.6 Template Structure', level=2)
doc.add_paragraph(
    'All templates extend base.html which provides the common layout: navbar with country '
    'selector, language toggle, bell icon with unread badge, and Feedback link; footer with '
    'branding and links; country selection modal; flash message display area; and responsive '
    'meta tags and CSS/JS includes. Each portal template adds portal-specific navigation '
    '(agency sidebar links, ministry dashboard links) in its content block.'
)

doc.add_page_break()

# ═══════════════════ 11. CHALLENGES ═══════════════════

doc.add_heading('11. Challenges and Solutions', level=1)

challenges = [
    ('Data Redundancy in JSON Storage',
     'The original data.json stored all data in a flat, denormalised structure. Passenger details were '
     'repeated across every booking, route prices were duplicated for every schedule referencing them, '
     'and ID generation using len(data[\'x\']) + 1 produced collisions when items were deleted. Deleting '
     'an agency left orphan buses, routes, schedules, and bookings with no referential integrity.',
     'Migrated to SQLite with a fully normalised schema of 7+ tables with proper foreign keys '
     '(ON DELETE CASCADE), AUTOINCREMENT for collision-free IDs, WAL journal mode for concurrent '
     'write safety, and UNIQUE constraints on passenger phone+ID to eliminate duplication. '
     'A migration function (migrate_from_json()) imports existing JSON data into the new structure '
     'with idempotent execution tracking via the meta table.'),
    ('Multi-Language Translation Management',
     'Maintaining consistent translations across 11 languages with 538+ UI strings is labour-intensive. '
     'Adding new UI text required updating all 11 files. Non-Latin scripts (Arabic, Amharic, Tigrinya) '
     'required special handling. The generate_translations.py script could time out when processing '
     'large batches of new keys across all 10 non-English languages.',
     'The generate_translations.py script reads en.json (source of truth) and regenerates all language '
     'files by adding missing keys while preserving existing translations. The _() function gracefully '
     'falls back to English when a key is missing in any language file. French is manually maintained '
     'as the primary bilingual target for Cameroon. For large batches that time out, individual '
     'translation files can be edited manually or the batch can be split into smaller chunks.'),
    ('Agency Privacy',
     'Competing agencies should not know each other\'s pricing strategies, route profitability, '
     'passenger manifests, or booking volumes. Since the booking platform is public, any agency '
     'employee could browse the site as a regular passenger to view competitor information.',
     'Session-aware filtering in the _country_agencies() helper. When an agency_id is present in '
     'the session, all public pages (homepage, search, agency browser) filter to show only the '
     'logged-in agency\'s data. Direct URL access to competitor agency pages is explicitly blocked '
     'with an "Access denied" authorisation check. This provides privacy without requiring separate '
     '"admin" and "public" code paths.'),
    ('Concurrent Booking Race Conditions',
     'Two passengers could select the same seat simultaneously at payment time. Without proper '
     'locking, both bookings would succeed for the same seat, leading to overbooking and passenger '
     'dissatisfaction at departure time. This is the classic "race condition" problem that systems '
     'like Ticketmaster and airline booking systems face.',
     'Three layers of protection: (1) Database-level partial unique index on (schedule_id, seat_number) '
     'WHERE seat_number IS NOT NULL — this guarantees that even if two INSERT statements execute at '
     'the exact same microsecond, only one will succeed. (2) Atomic booking function (add_booking_atomic) '
     'wraps seat selection + booking creation in a BEGIN IMMEDIATE transaction, acquiring a write lock '
     'immediately. (3) Atomic payment confirmation (confirm_booking_atomic) re-checks seat availability '
     'inside a transaction at payment time, redirecting the passenger to pick again if the seat was '
     'taken between booking creation and payment.'),
    ('Concurrent Login and Rate Limiting',
     'The original login endpoints had no protection — an attacker could hammer /agency/login, '
     '/ministry/login, and /ministry/relogin with unlimited rapid attempts, potentially brute-forcing '
     'passwords or overwhelming the server with 500+ concurrent requests (the "Facebook question").',
     'An in-memory rate limiter was added to all three login endpoints. Each IP address is tracked '
     'independently with a sliding window of 15 minutes. After 10 failed attempts, the IP is blocked '
     'with a user-friendly message showing the remaining wait time. On successful login, the IP\'s '
     'attempt counter is cleared. The limiter uses a defaultdict(list) with datetime objects for '
     'efficient sliding window cleanup.'),
    ('Shared Password Security',
     'Using "Admin123" as a shared password across all 54 countries is a critical security '
     'vulnerability. Any ministry user who knew this password could log in as any country\'s '
     'super admin, accessing all agency data and performing approval/rejection actions.',
     'The shared password is now one-time-use. After the first successful login, a flag '
     '(shared_pw_used_{country}) is set to "1" in the meta table. Step 2 forces the user to '
     'set a personal email + password combination. All subsequent visits skip the shared '
     'password step entirely, and the POST route rejects the shared password if the flag is set.'),
    ('Bilingual Announcement Translation',
     'Cameroon has two official languages (English and French). Agency announcements need to be '
     'visible in both languages to serve all passengers. On-the-fly translation would hit the '
     'Google Translate API on every page load, which is slow, unreliable (API may throttle), '
     'and creates unnecessary external dependencies.',
     'The French translation is stored in a dedicated message_fr column at announcement creation '
     'time using the deep-translator library. The ann_msg() context processor selects the French '
     'or English version based on the user\'s language preference. A back-fill script '
     '(translate_announcements.py) handles all pre-existing announcements. This approach adds '
     '~1 second to announcement creation but eliminates API calls on every page view.'),
    ('Bell Icon Colour Inconsistency',
     'The notification bell icon colour was initially set using var(--flag-2), which dynamically '
     'changed based on the selected country\'s flag colours. In Cameroon the bell appeared as red, '
     'but in Kenya (where flag-2 is white) the bell became invisible against the light navbar '
     'background. This was a critical UI bug.',
     'The bell icon colour was hardcoded to #c62828 (a specific shade of red) for ALL countries, '
     'regardless of flag colours. This ensures the notification bell is always visible and '
     'consistent across all 54 country themes.'),
    ('Missing Feedback System',
     'The original platform had no channel for passengers, agencies, or ministry users to submit '
     'feedback, suggestions, or bug reports. There was no way for users to communicate issues '
     'to the platform administrators, making it impossible to improve the platform based on '
     'user input.',
     'A complete feedback system was built from scratch: a new feedback table in the database, '
     'a /feedback route with GET (form display) and POST (submission with auto-detected name/role), '
     'email notification to FEEDBACK_EMAIL via Gmail SMTP on every submission, a /feedback/all '
     'route for ministry to view all submissions with role badges, and a navbar "Feedback" link.'),
    ('Unclosed HTML Elements',
     'A missing </div> in the country modal caused the entire page footer to render inside the '
     'modal overlay (which had display: none by default). This made the footer completely '
     'invisible on all pages, and the bug was difficult to locate because the structure appeared '
     'correct at first glance.',
     'A systematic div-counting review of all templates was performed. The issue was identified '
     'as an unclosed modal container div and fixed by properly closing it before the footer '
     'block. A mental checklist was created to count opening vs. closing div tags when '
     'modifying template structures.'),
    ('Translation Auto-Generation Timeout',
     'The generate_translations.py script translates each key in en.json into 10 target languages '
     'using the deep-translator library. When processing 26+ new keys, the script timed out because '
     'it makes sequential API calls (26 keys × 10 languages = 260 API calls). Each call takes '
     '1–3 seconds, leading to total times exceeding 5 minutes.',
     'French translations were done manually to ensure quality. For the remaining 9 languages, '
     'English text was used as fallback (the _() function naturally falls back to English for '
     'missing keys). A future improvement would add batch processing with delays or use a '
     'translation API with batch support.'),
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

doc.add_page_break()

# ═══════════════════ 12. TESTING ═══════════════════

doc.add_heading('12. Testing and Results', level=1)

doc.add_heading('12.1 Testing Approach', level=2)
approaches = [
    'Manual browser testing across all 48+ routes and user flows for all three portals (passenger, agency, ministry)',
    'Automated HTTP tests using Python http.client to verify all routes return HTTP 200 with valid HTML content',
    'Database verification confirming migration accuracy and data integrity (all record counts matched)',
    'Responsive testing at all four breakpoints: 1024px (tablet), 768px (mobile), 480px (small phone), 360px (very small phone)',
    'Concurrent booking testing by opening multiple browser tabs simultaneously selecting the same seat',
    'Rate limiter testing by submitting rapid failed login attempts and verifying the block activates after 10',
    'Translation testing by switching between all 11 languages and verifying UI strings appear correctly',
    'Email notification testing by submitting feedback and confirming receipt at FEEDBACK_EMAIL',
]
for a in approaches:
    doc.add_paragraph(a, style='List Bullet')

doc.add_heading('12.2 Migration Results', level=2)
doc.add_paragraph(
    'The migration from JSON to SQLite successfully preserved all data with zero loss. '
    'Passenger records were deduplicated from repeated entries across 18 bookings into '
    '7 unique passenger records:'
)
add_table(
    ['Entity', 'JSON Records', 'SQLite Records', 'Status'],
    [
        ('Agencies', '7', '7', '100% preserved'),
        ('Buses', '111', '111', '100% preserved'),
        ('Routes', '9', '9', '100% preserved'),
        ('Schedules', '11', '11', '100% preserved'),
        ('Bookings', '18', '18', '100% preserved'),
        ('Passengers (deduplicated)', 'N/A (repeated in bookings)', '7 unique', 'Duplication eliminated'),
    ]
)

doc.add_heading('12.3 Key Test Results', level=2)
add_table(
    ['Test', 'Result', 'Notes'],
    [
        ('All routes return HTTP 200', 'PASS', '48+ routes verified with valid HTML content'),
        ('Database migration integrity', 'PASS', '100% data preserved; passengers deduplicated from ~18 to 7'),
        ('Concurrent booking prevention', 'PASS', 'Unique index prevents double-booking; atomic transaction catches race conditions'),
        ('Rate limiter (10 attempts/15 min)', 'PASS', 'Blocks after 10; resets after 15 min; clears on successful login'),
        ('Responsive design (4 breakpoints)', 'PASS', 'All pages functional at 360px, 480px, 768px, 1024px'),
        ('Translation (538+ keys, 11 languages)', 'PASS', 'All keys load without errors; missing keys fall back to English'),
        ('Bilingual announcements (FR/EN)', 'PASS', 'French and English display correctly based on language setting'),
        ('Email notifications (feedback)', 'PASS', 'Feedback submissions reach FEEDBACK_EMAIL via SMTP'),
        ('Commission amount hidden from UI', 'PASS', 'Amount never displayed in agency or ministry dashboards'),
        ('One-time shared password (Admin123)', 'PASS', 'Rejected after first use; redirected to step 2 on subsequent visits'),
        ('Bell icon colour (#c62828)', 'PASS', 'Consistent red across all 54 country themes'),
        ('Notification read tracking', 'PASS', 'Unread count updates correctly; blue dot/green check works'),
        ('Agency privacy filtering', 'PASS', 'Logged-in agencies see only their data; competitor URLs blocked'),
        ('Bus auto-status management', 'PASS', 'Bus set to busy on schedule creation; reverts on cancellation'),
        ('Logout session cleanup', 'PASS', 'Agency_id and read_notification_ids cleared on logout'),
        ('Password reset flow (8-digit code)', 'PASS', 'Verification code sent via email; expires after configured time'),
    ]
)

doc.add_heading('12.4 Bug Fixes Throughout Development', level=2)
add_table(
    ['Bug', 'Cause', 'Fix'],
    [
        ('Footer invisible on all pages', 'Missing </div> in country modal template', 'Systematic div-counting; closed modal container before footer'),
        ('Bell icon invisible on light-themed countries', 'var(--flag-2) used for bell colour', 'Hardcoded bell colour to #c62828 (red) for all countries'),
        ('Announcements not showing French text', 'message not updated to use message_fr column', 'Added ann_msg() context processor; updated all templates'),
        ('Agency notifications showing all agencies\' announcements', 'No agency_id filter in query', 'Added agency_id filter in get_announcements()'),
        ('404 error on agency dashboard after deleting an agency', 'Stale agency_id in session with no validation', 'get_agency_session() now checks DB existence on every call'),
        ('get_next_ref import error', 'New function added to database.py but not imported in app.py', 'Added from database import get_next_ref to app.py'),
        ('Redirect loop in ministry login after shared password use', 'Missing meta table check in GET route', 'Added is_shared_pw_used() check before showing step 1 form'),
        ('Notification unread count not updating after reading', 'No session tracking for read notifications', 'Added read_notification_ids list to session'),
        ('Schedule creation with unavailable (busy) bus', 'Bus dropdown showed all buses regardless of status', 'Filtered bus dropdown to show only "available" buses'),
    ]
)

doc.add_page_break()

# ═══════════════════ 13. CONCLUSION ═══════════════════

doc.add_heading('13. Conclusion and Future Work', level=1)

doc.add_heading('13.1 Summary of Achievements', level=2)
achievements = [
    'Complete coverage of all 54 African countries with localised configuration (flag colours, currency, cities, languages, payment providers)',
    'Multilingual interface supporting 11 languages across 4 scripts (Latin, Arabic, Ge\'ez, Latin-extended) with 538+ translation keys',
    'Full booking lifecycle: search → browse → pick seat → enter details → pay → e-ticket in HTML, PDF, and PNG formats',
    'Agency management portal with dashboard (revenue by route, recent bookings, today\'s trips), bus/route/schedule CRUD, booking management, passenger manifests, and bilingual announcements',
    'Ministry oversight with per-country 2-step login, agency approval/rejection workflow with permanent reasons, cross-agency booking visibility, and national statistics dashboard',
    'Bilingual announcement system with automatic French translation via Google Translate, stored at creation time for performance',
    'Per-notification read tracking using session cookies — no user login required for passengers to track their reading progress',
    'Interactive visual seat selection with 4 bus layout classes (Class 1–4 based on capacity), colour-coded (standard green, VIP gold, selected blue, taken grey)',
    'Responsive design with 4 breakpoints (1024, 768, 480, 360px) accessible on desktop, tablet, and mobile devices',
    'Data integrity through SQLite migration from flat JSON with normalised schema, foreign keys, unique constraints, atomic transactions, and WAL journal mode',
    'Competitor privacy preventing unauthorised data access between agencies via session-aware filtering',
    'Rate limiting on all login endpoints (10 attempts per 15 minutes per IP) with sliding window implementation',
    'One-time shared password (Admin123) with forced personal password setup on first login',
    'Feedback system with email notifications to administrators via Gmail SMTP',
    'Bus auto-status management (busy when scheduled, available when cancelled) preventing double-booking',
    'Commission system (1%) with amount hidden from all UI — rate only shown as informational badge',
    'Hardened session management: agency validation on every protected route, stale session cleanup, logout clears read tracking',
]
for a in achievements:
    doc.add_paragraph(a, style='List Bullet')

doc.add_heading('13.2 Future Improvements', level=2)

future_sections = [
    ('Security Enhancements', [
        'Add CSRF protection to all forms (currently not implemented)',
        'Switch to HTTPS in production deployment',
        'Implement Redis-backed rate limiter for multi-server / multi-worker deployments',
        'Add two-factor authentication (2FA) for ministry users',
        'Implement account lockout after N failed attempts (not just rate limiting)',
        'Add audit logging for all administrative actions (approve/reject, login, password changes)',
    ]),
    ('Code Quality and Architecture', [
        'Refactor monolithic app.py (~1500+ lines) into modular Flask blueprints (passenger, agency, ministry, api)',
        'Separate business logic from route handlers into a dedicated service layer',
        'Add comprehensive unit tests with pytest and integration tests with Selenium',
        'Add Python type hints throughout the entire codebase',
        'Implement proper error handling with custom error pages (404, 500, 403)',
        'Add API documentation with OpenAPI/Swagger for future mobile app integration',
    ]),
    ('Real-Time Features', [
        'WebSocket-based real-time seat availability updates (prevent stale seat maps)',
        'Live booking notifications for agencies via Server-Sent Events (SSE) or WebSockets',
        'SMS booking confirmations via Africa\'s Talking API or Twilio',
        'Real-time bus tracking with GPS integration for passengers',
    ]),
    ('Payment Integration', [
        'Connect to real mobile money APIs (M-Pesa Daraja API, MTN MoMo API, Orange Money API)',
        'Implement webhook-based payment confirmation (async payment flow)',
        'Add payment receipt generation with QR codes for verification',
        'Support for international card payments (Stripe, Paystack, Flutterwave)',
        'Implement payment refund flow for cancelled bookings',
    ]),
    ('Performance Optimisation', [
        'Add Redis caching for frequently accessed data (cities list, agencies list, translation files)',
        'Implement database query optimisation with composite indexes on frequently queried columns',
        'Add CDN for static assets (Font Awesome, Google Fonts)',
        'Implement database connection pooling for high-concurrency scenarios',
        'Consider PostgreSQL migration for production-scale deployments (row-level locking, better concurrency)',
    ]),
    ('Additional Features', [
        'RTL (right-to-left) layout support for Arabic-language countries',
        'Mobile application (React Native or Flutter) for native booking experience',
        'Driver/operator mobile interface for manifest management and seat scanning',
        'Multi-trip and round-trip booking in a single transaction',
        'Loyalty/rewards programme for frequent passengers with points accumulation',
        'Automated translation for all 10 languages (currently French is manual, others have English fallback for timed-out keys)',
        'Agency analytics dashboard with CSV/Excel export and interactive charts',
        'Booking history and trip history pages for returning passengers',
        'Social login (Google, Facebook) for passenger accounts',
        'Multi-language announcement creation (agencies write in both English and French)',
    ]),
]
for title, items in future_sections:
    doc.add_heading(title, level=2)
    for item in items:
        doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph()

# ═══════════════════ APPENDIX A ═══════════════════

doc.add_page_break()
doc.add_heading('Appendix A: Full Route Inventory', level=1)
doc.add_paragraph(
    'Complete list of all 48+ application routes organised by portal. '
    'Each route shows the HTTP method(s) supported and a brief description.'
)

add_table(
    ['Route', 'Methods', 'Portal', 'Description'],
    [
        ('/', 'GET', 'Passenger', 'Homepage with hero, search form, agencies grid, statistics'),
        ('/search', 'GET, POST', 'Passenger', 'Search trips by origin, destination, date'),
        ('/pick-seat/<sid>', 'GET, POST', 'Passenger', 'Interactive seat selection for a schedule'),
        ('/book/<sid>', 'GET, POST', 'Passenger', 'Passenger details and booking form'),
        ('/payment/<bid>', 'GET, POST', 'Passenger', 'Payment method selection and confirmation'),
        ('/confirm-payment/<bid>', 'POST', 'Passenger', 'Payment confirmation with seat re-check'),
        ('/ticket/<ref>', 'GET', 'Passenger', 'HTML e-ticket display'),
        ('/ticket/<ref>/pdf', 'GET', 'Passenger', 'PDF e-ticket download'),
        ('/ticket/<ref>/image', 'GET', 'Passenger', 'PNG e-ticket image download'),
        ('/lookup', 'GET, POST', 'Passenger', 'Ticket lookup by reference number'),
        ('/notifications', 'GET', 'Passenger', 'Announcements list with read tracking'),
        ('/notification/<nid>', 'GET', 'Passenger', 'Single announcement detail view'),
        ('/feedback', 'GET, POST', 'Passenger', 'Submit feedback (auto-detects name/role)'),
        ('/feedback/all', 'GET', 'Ministry', 'View all feedback submissions'),
        ('/lang/<lang>', 'GET', 'Utility', 'Switch language'),
        ('/country/<code>', 'GET', 'Utility', 'Switch country'),
        ('/agencies', 'GET', 'Passenger', 'Browse all approved agencies'),
        ('/agency/<aid>', 'GET', 'Passenger', 'Single agency public detail page'),
        ('/agency/login', 'GET, POST', 'Agency', 'Agency sign in with rate limiting'),
        ('/agency/register', 'GET, POST', 'Agency', 'Agency registration form'),
        ('/agency/logout', 'GET', 'Agency', 'Agency logout (clears session + read tracking)'),
        ('/agency/dashboard', 'GET', 'Agency', 'Agency control panel with stats and revenue chart'),
        ('/agency/buses', 'GET', 'Agency', 'Bus list with status badges'),
        ('/agency/buses/add', 'GET, POST', 'Agency', 'Add new bus'),
        ('/agency/buses/<bid>/edit', 'GET, POST', 'Agency', 'Edit existing bus'),
        ('/agency/routes', 'GET', 'Agency', 'Route list with pricing'),
        ('/agency/routes/add', 'GET, POST', 'Agency', 'Add new route'),
        ('/agency/routes/<rid>/edit', 'GET, POST', 'Agency', 'Edit existing route'),
        ('/agency/schedules', 'GET', 'Agency', 'Schedule list grouped by period'),
        ('/agency/schedules/add', 'GET, POST', 'Agency', 'Add new schedule'),
        ('/agency/schedules/<sid>/edit', 'GET, POST', 'Agency', 'Edit or cancel schedule'),
        ('/agency/bookings', 'GET', 'Agency', 'Booking management with filters'),
        ('/agency/bookings/<bid>/reassign', 'GET, POST', 'Agency', 'Reassign booking to alternative trip'),
        ('/agency/manifest/<sid>', 'GET', 'Agency', 'Passenger manifest for a trip'),
        ('/agency/announcements', 'GET', 'Agency', 'Announcement management list'),
        ('/agency/announcements/add', 'GET, POST', 'Agency', 'Create announcement (auto-translate to FR)'),
        ('/agency/forgot-password', 'GET, POST', 'Agency', 'Password reset request'),
        ('/agency/verify-code', 'GET, POST', 'Agency', 'Verify 8-digit reset code'),
        ('/agency/reset-password', 'GET, POST', 'Agency', 'Set new password'),
        ('/ministry/login', 'GET, POST', 'Ministry', '2-step login (shared pw + personal)'),
        ('/ministry/relogin', 'GET, POST', 'Ministry', 'Set personal password after first login'),
        ('/ministry/logout', 'GET', 'Ministry', 'Ministry logout'),
        ('/ministry/dashboard', 'GET', 'Ministry', 'National statistics dashboard'),
        ('/ministry/agencies', 'GET', 'Ministry', 'Agency registry with approve/reject actions'),
        ('/ministry/agencies/<aid>/approve', 'POST', 'Ministry', 'Approve agency with reason'),
        ('/ministry/agencies/<aid>/reject', 'POST', 'Ministry', 'Reject agency with reason'),
        ('/ministry/bookings', 'GET', 'Ministry', 'Cross-agency booking view'),
        ('/ministry/forgot-password', 'GET, POST', 'Ministry', 'Password reset request'),
        ('/ministry/verify-code', 'GET, POST', 'Ministry', 'Verify 8-digit reset code'),
        ('/ministry/reset-password', 'GET, POST', 'Ministry', 'Set new password'),
    ]
)

doc.add_page_break()

# ═══════════════════ APPENDIX B ═══════════════════

doc.add_heading('Appendix B: Translation Key Reference', level=1)
doc.add_paragraph(
    'The English translation file (en.json) contains 538+ keys organised by functional area. '
    'Below is a summary of the key categories and the number of keys in each. '
    'For the complete list, refer to the en.json file in the /translations/ directory.'
)

add_table(
    ['Category', 'Key Count', 'Description'],
    [
        ('Navigation', '~35', 'Navbar items, footer links, breadcrumbs, tab labels'),
        ('Homepage', '~25', 'Hero text, search labels, featured section, statistics'),
        ('Search Results', '~20', 'Trip cards, period headings, filters, sorting'),
        ('Seat Selection', '~30', 'Seat states (available/VIP/taken), layout labels, legend'),
        ('Booking Form', '~40', 'Passenger fields, luggage options, validation messages'),
        ('Payment', '~25', 'Provider names, payment status, confirmation messages'),
        ('E-Ticket', '~35', 'Ticket sections, labels, download options, print'),
        ('Agency Portal', '~80', 'Dashboard labels, CRUD forms, table headers, action buttons'),
        ('Ministry Portal', '~60', 'Dashboard, agency registry, approve/reject modals'),
        ('Notifications', '~20', 'Announcement badges, read/unread labels, timestamps'),
        ('Feedback', '~15', 'Form labels, submission messages, role badges'),
        ('Authentication', '~50', 'Login forms, registration, password reset, error messages'),
        ('General', '~60', 'Flash messages, error/404, loading states, empty states, buttons'),
        ('Country-Specific', '~25', 'Payment provider display names, currency labels, date formats'),
    ]
)

doc.add_page_break()

# ═══════════════════ APPENDIX C ═══════════════════

doc.add_heading('Appendix C: Country Configuration Reference', level=1)
doc.add_paragraph(
    'All 54 African countries are configured in countries.json. Each country entry includes '
    'the fields documented below. The configuration drives flag colour theming, currency display, '
    'city selection, language options, payment providers, and VIP pricing.'
)

add_table(
    ['Field', 'Type', 'Example', 'Description'],
    [
        ('name', 'string', '"Cameroon"', 'English country name'),
        ('flag_colors', 'array', '["#007a5e","#ce1126","#fcd116"]', '3–6 hex colour values for CSS variables'),
        ('currency', 'string', '"FCFA"', 'Local currency symbol/abbreviation'),
        ('currency_code', 'string', '"XAF"', 'ISO 4217 currency code'),
        ('ref_prefix', 'string', '"CM"', 'Booking reference prefix'),
        ('cities', 'array', '["Douala","Yaoundé",...]', '8–18 city names for origin/destination'),
        ('lang', 'string', '"en"', 'Default language code'),
        ('languages', 'array', '["en","fr"]', 'Supported language codes'),
        ('providers', 'array', '["mtn_momo","orange_money"]', 'Payment provider codes'),
        ('vip_surcharge', 'number', '3000', 'VIP seat surcharge in local currency'),
        ('flag_svg', 'string (base64)', '(omitted)', 'Base64-encoded SVG flag image (optional)'),
    ]
)

doc.add_paragraph()
doc.add_paragraph(
    'The country list includes all 54 UN-recognised African nations: Algeria, Angola, Benin, '
    'Botswana, Burkina Faso, Burundi, Cameroon, Cape Verde, Central African Republic, Chad, '
    'Comoros, Congo, Côte d\'Ivoire, Democratic Republic of the Congo, Djibouti, Egypt, '
    'Equatorial Guinea, Eritrea, Eswatini, Ethiopia, Gabon, Gambia, Ghana, Guinea, '
    'Guinea-Bissau, Kenya, Lesotho, Liberia, Libya, Madagascar, Malawi, Mali, Mauritania, '
    'Mauritius, Morocco, Mozambique, Namibia, Niger, Nigeria, Rwanda, São Tomé and Príncipe, '
    'Senegal, Seychelles, Sierra Leone, Somalia, South Africa, South Sudan, Sudan, Tanzania, '
    'Togo, Tunisia, Uganda, Zambia, Zimbabwe.'
)

doc.add_page_break()

# ═══════════════════ APPENDIX D: REFERENCES ═══════════════════

doc.add_heading('Appendix D: References', level=1)

references = [
    ('Flask Documentation', 'The Flask Web Framework. Pallets Project.', 'https://flask.palletsprojects.com/'),
    ('Python 3 Documentation', 'Python Software Foundation.', 'https://docs.python.org/3/'),
    ('SQLite Documentation', 'SQLite Consortium.', 'https://www.sqlite.org/docs.html'),
    ('Jinja2 Documentation', 'Template Engine. Pallets Project.', 'https://jinja.palletsprojects.com/'),
    ('Pillow (PIL Fork) Documentation', 'Python Imaging Library.', 'https://pillow.readthedocs.io/'),
    ('xhtml2pdf Documentation', 'PDF Generation from HTML.', 'https://xhtml2pdf.readthedocs.io/'),
    ('Werkzeug Documentation', 'WSGI Toolkit. Pallets Project.', 'https://werkzeug.palletsprojects.com/'),
    ('Font Awesome Icons', 'Icon Library. Fonticons, Inc.', 'https://fontawesome.com/'),
    ('Google Fonts (Inter)', 'Typography by Rasmus Andersson.', 'https://fonts.google.com/specimen/Inter'),
    ('deep-translator', 'Google Translate wrapper library.', 'https://github.com/nidhaloff/deep-translator'),
    ('python-dotenv', 'Environment variable loader.', 'https://github.com/theskumar/python-dotenv'),
    ('ISO 3166-1 Country Codes', 'International Organization for Standardization.', 'https://www.iso.org/iso-3166-country-codes.html'),
    ('African Languages Reference', 'Ethnologue: Languages of Africa. SIL International.', 'https://www.ethnologue.com/region/Africa'),
    ('Mobile Money in Africa', 'GSMA Mobile Money Report.', 'https://www.gsma.com/mobilemoney/'),
    ('Bus Seat Layout Standards', 'Industry standard configurations for inter-city transport in West and Central Africa.', 'N/A (industry knowledge)'),
    ('M-Pesa Daraja API', 'Safaricom payment API documentation.', 'https://developer.safaricom.co.ke/'),
    ('MTN MoMo API', 'MTN Mobile Money developer portal.', 'https://momodeveloper.mtn.com/'),
]

for title, desc, url in references:
    p = doc.add_paragraph()
    r = p.add_run(f'{title}: ')
    r.bold = True
    p.add_run(f'{desc}')
    if url != 'N/A (industry knowledge)':
        p2 = doc.add_paragraph()
        p2.paragraph_format.left_indent = Cm(1)
        r2 = p2.add_run(url)
        r2.font.color.rgb = RGBColor(0x00, 0x55, 0xCC)
        r2.font.size = Pt(10)

doc.add_paragraph()
doc.add_paragraph()

# ═══════════════════ END ═══════════════════

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('— End of Document —')
r.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
r.font.size = Pt(14)

doc.add_paragraph()

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run('Report prepared by TEH ADOLF BUOH (ADOLF.AI)\n'
                'Internship Period: June – July 2026\n'
                'Organisation: FERDSILINKS BUEA, CAMEROON\n'
                'AFRI Trans — Serving All 54 African Nations')
r2.font.size = Pt(11)
r2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

output_path = os.path.join(os.path.dirname(__file__), 'AFRI_Trans_Complete_Documentation.docx')
doc.save(output_path)
print(f'Document saved to: {output_path}')
