"""Generate a professional internship report with chapters, sub-chapters, TOC, and page numbers."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import zipfile, os, shutil, copy

SRC = 'AFRI_Trans_reports.docx'
DST = 'AFRI_Trans_Report_2026.docx'
TMP = os.environ['TEMP'] + r'\report_build'

# ── 0. Extract images from source ──
if os.path.exists(TMP): shutil.rmtree(TMP)
with zipfile.ZipFile(SRC) as z:
    z.extractall(TMP)

IMG_DIR = os.path.join(TMP, 'word/media')

# ── 1. Create document ──
doc = Document()
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(4)
style.paragraph_format.line_spacing = 1.15

# Heading styles matching original document
h1 = doc.styles['Heading 1']
h1.font.name = 'Calibri'
h1.font.size = Pt(14)
h1.font.bold = True
h1.font.color.rgb = RGBColor(0x36, 0x5F, 0x91)
h1.paragraph_format.space_before = Pt(24)
h1.paragraph_format.space_after = Pt(0)

h2 = doc.styles['Heading 2']
h2.font.name = 'Calibri'
h2.font.size = Pt(13)
h2.font.bold = True
h2.font.color.rgb = RGBColor(0x4F, 0x81, 0xBD)
h2.paragraph_format.space_before = Pt(10)
h2.paragraph_format.space_after = Pt(0)

h3 = doc.styles['Heading 3']
h3.font.name = 'Calibri'
h3.font.size = Pt(11)
h3.font.bold = True
h3.font.color.rgb = RGBColor(0x4F, 0x81, 0xBD)
h3.paragraph_format.space_before = Pt(10)
h3.paragraph_format.space_after = Pt(0)

def add_heading(text, level=1):
    return doc.add_heading(text, level=level)

def add_para(text, bold=False, italic=False, size=11, color=None, align=None, space_after=4):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color: run.font.color.rgb = RGBColor(*bytes.fromhex(color))
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_bullet(text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 0.63)
    return p

def add_img(img_name, width=Inches(5.5), caption=''):
    """Insert image from extracted media folder."""
    path = os.path.join(IMG_DIR, img_name)
    if not os.path.exists(path):
        print(f'WARNING: {img_name} not found')
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=width)
    if caption:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(caption)
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

def add_page_break():
    doc.add_page_break()

# ── Helper: Add section break with page number style ──
def add_section_break():
    new_section = doc.add_section()
    new_section.page_width = Cm(21)
    new_section.page_height = Cm(29.7)
    new_section.top_margin = Cm(2.54)
    new_section.bottom_margin = Cm(2.54)
    new_section.left_margin = Cm(2.54)
    new_section.right_margin = Cm(2.54)
    return new_section

# ════════════════════════════════════════════
# TITLE PAGE
# ════════════════════════════════════════════
add_page_break()
for _ in range(4):
    add_para('', size=11)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('INTERNSHIP REPORT')
run.bold = True
run.font.size = Pt(26)
run.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

add_para('', size=8)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('AFRI Trans')
run.bold = True
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(0x2d, 0x5f, 0x8a)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Multi-Country Bus Ticketing Platform')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

add_para('', size=20)

# Add cover logos
for fn in ['image1.png', 'image2.png', 'image3.png']:
    add_img(fn, width=Inches(1.8))

add_para('', size=16)

info_lines = [
    ('Presented by', 'TEH ADOLF BUOH'),
    ('Internship Period', '16 June 2026 – 30 September 2026'),
    ('Organization', 'FERDSILINK BUEA, CAMEROON'),
    ('Supervisor', '________________________'),
]
for label, value in info_lines:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(f'{label}:  ')
    r1.bold = True
    r1.font.size = Pt(12)
    r2 = p.add_run(value)
    r2.font.size = Pt(12)

add_para('', size=16)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('2026')
run.bold = True
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

add_page_break()

# ════════════════════════════════════════════
# TABLE OF CONTENTS
# ════════════════════════════════════════════
add_heading('Table of Contents', level=1)

# Insert Word TOC field
p = doc.add_paragraph()
run = p.add_run()
fld_char1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
fld_code = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>')
fld_char2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
fld_char3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
run._element.append(fld_char1)
run._element.append(fld_code)
run._element.append(fld_char2)
run._element.append(fld_char3)

# Add placeholder text that reveals after TOC update
add_para('(Right-click and select "Update Field" to generate table of contents)', size=10, italic=True, color='999999')

# Also add a manual TOC listing as fallback
add_para('', size=6)

toc_items = [
    ('', '1. Introduction', ''),
    ('', '    1.1 Background', ''),
    ('', '    1.2 Problem Statement', ''),
    ('', '    1.3 Objectives', ''),
    ('', '        1.3.1 Primary Objectives', ''),
    ('', '        1.3.2 Secondary Objectives', ''),
    ('', '4. Tools and Technologies Used', ''),
    ('', '    2.1 Backend Technologies', ''),
    ('', '    2.2 Frontend Technologies', ''),
    ('', '    2.3 Development Tools', ''),
    ('', '5. System Architecture', ''),
    ('', '    3.1 High-Level Architecture', ''),
    ('', '    3.2 Request Flow', ''),
    ('', '6. Database Design', ''),
    ('', '    4.1 Schema Overview', ''),
    ('', '    4.2 Entity Relationship Diagram', ''),
    ('', '    4.3 Migration from JSON to SQLite', ''),
    ('', '7. Features Implemented', ''),
    ('', '    7.1 Multi-Country Support', ''),
    ('', '    7.2 Internationalisation (11 Languages)', ''),
    ('', '    7.3 Passenger Booking Flow', ''),
    ('', '    7.4 Real-Time Seat Map', ''),
    ('', '    7.5 Agency Portal', ''),
    ('', '    7.6 Ministry of Transport Portal', ''),
    ('', '    7.7 Subscription Monetisation', ''),
    ('', '    7.8 Departure Notification Scheduler', ''),
    ('', '    7.9 E-Ticket Generation', ''),
    ('', '    7.10 Commission System', ''),
    ('', '    7.11 Flash Alert Categories', ''),
    ('', '    7.12 Flag-Coloured Hero Title', ''),
    ('', '    7.13 Responsive Design', ''),
    ('', '    7.14 Security & Concurrency Hardening', ''),
    ('', '    8.1 Project Structure', ''),
    ('', '    8.2 Key Code Patterns', ''),
    ('', '9. Challenges and Solutions', ''),
    ('', '    9.1 Data Redundancy in JSON Storage', ''),
    ('', '    9.2 TOCTOU Race Conditions', ''),
    ('', '    9.3 Booking Reference Counter Race', ''),
    ('', '    9.4 Concurrent Seat Booking', ''),
    ('', '    9.5 Free Departure Notification Delivery', ''),
    ('', '    9.6 Multi-Language Translation Management', ''),
    ('', '    9.7 Agency Privacy', ''),
    ('', '    9.8 Other Challenges', ''),
    ('', '10. Testing and Results', ''),
    ('', '11. Conclusion and Future Work', ''),
    ('', '    11.1 Summary of Achievements', ''),
    ('', '    11.2 Future Improvements', ''),
    ('', 'References', ''),
]
for _, item, _ in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(item)
    r.font.size = Pt(10)
    if item and not item.startswith('    '):
        r.bold = True

add_page_break()

# ════════════════════════════════════════════
# CHAPTER I: INTRODUCTION
# ════════════════════════════════════════════
add_heading('1. Introduction', level=2)

add_para(
    'AFRI Trans is a web-based bus ticketing platform designed to serve all 54 African countries. '
    'The platform connects passengers with bus agencies through a unified booking system, while also '
    'providing administrative portals for agencies and government transport ministries. The system '
    'supports multiple languages, local currencies, country-specific payment providers, and per-country '
    'ministry oversight workflows.'
)
add_para(
    'Beyond core booking, AFRI Trans includes a subscription monetisation model where agencies prepay '
    'to skip the 1% platform commission, a live seat map with real-time polling so multiple passengers '
    'see seat availability update in sync, and a background departure notification scheduler that '
    'reminds passengers 90 and 45 minutes before departure. Flash messages use colour-coded categories '
    '(green success, orange warning, red error) for clearer UX. All concurrency vulnerabilities — '
    'TOCTOU race conditions in agency registration and booking reference generation — have been fixed '
    'with database-level transactions and unique indexes.'
)
add_para(
    'This report documents the development of the AFRI Trans platform during the internship period '
    'at Ferdsilink Buea, Cameroon. The project was built using Python Flask for the backend, SQLite '
    'for data persistence, and vanilla HTML/CSS/JavaScript for the frontend.'
)

# 1.1 Background
add_heading('1.1 Background', level=3)
add_para(
    'Inter-city bus travel is the primary mode of transportation for millions of Africans. However, '
    'most bus booking systems are paper-based, fragmented by country, or operated by individual '
    'agencies with no centralised platform. This creates several problems:'
)
for item in [
    'Passengers must visit physical terminals to book tickets',
    'No way to compare prices across multiple agencies',
    'Limited payment options, often cash-only',
    'No standardised ticketing or booking records',
    'Agencies lacked subscription-based commission exemption',
    'No real-time seat availability across concurrent users',
]:
    add_bullet(item)
add_para(
    'AFRI Trans aims to solve these problems by providing a single, multi-country platform where '
    'passengers can search, compare, book, and pay for bus tickets across any African country.'
)

# 1.2 Problem Statement
add_page_break()
add_heading('2. Problem Statement', level=2)
add_para(
    'The African bus transportation industry faces several challenges that motivated the development of AFRI Trans:'
)
problems = [
    ('Lack of Centralisation', 'No single platform exists for booking bus tickets across multiple African countries. Passengers must interact with each agency separately.'),
    ('Language Barriers', 'Africa has over 2,000 languages. A platform serving the continent must support multiple languages to be accessible.'),
    ('Currency and Payment Fragmentation', 'Each country uses a different currency and has different mobile money providers. A unified system must handle this complexity.'),
    ('Regulatory Requirements', 'Each country has its own Ministry of Transport that must approve and oversee agencies operating within its jurisdiction.'),
    ('Data Redundancy', 'Initial implementation used flat JSON file storage, leading to duplicate data, ID collisions, and referential integrity issues.'),
    ('Agency Privacy', 'Competing agencies should not have access to each other\'s operational data (pricing, routes, passenger manifests).'),
    ('Security', 'A single shared password for all ministry users across all countries is insecure.'),
    ('No Commission Exemption', 'Agencies had no way to opt out of the 1% platform commission — all bookings were charged regardless of volume.'),
    ('No Real-Time Seat Updates', 'The seat map was static — concurrent viewers could not see each other\'s selections.'),
    ('No Departure Notifications', 'Passengers received no reminders before departure, leading to missed trips.'),
    ('Concurrency Bugs (TOCTOU)', 'Agency registration and booking reference generation both had race conditions that could create duplicates.'),
]
for title, desc in problems:
    p = add_para('')
    r = p.add_run(f'{title}: ')
    r.bold = True
    r.font.size = Pt(11)
    r2 = p.add_run(desc)
    r2.font.size = Pt(11)

# 1.3 Objectives
add_page_break()
add_heading('3. Objectives', level=2)

add_heading('3.1 Primary Objectives', level=3)
for obj in [
    'Develop a multi-country bus ticketing platform covering all 54 African nations',
    'Implement a language system supporting 11 African and international languages',
    'Create per-country payment provider integration',
    'Build a Ministry of Transport approval workflow for agency registration',
    'Design a fully responsive interface accessible on all device sizes',
    'Add subscription plans (monthly / 6-month / annual) for commission exemption',
    'Implement live seat map with 30-second auto-refresh for concurrent booking',
    'Build a background departure notification scheduler for passenger reminders',
    'Fix TOCTOU race conditions in registration and reference generation',
]:
    add_bullet(obj)

add_heading('3.2 Secondary Objectives', level=3)
for obj in [
    'Normalise data storage and eliminate redundancy through SQLite migration',
    'Enforce privacy between competing agencies',
    'Generate e-tickets in PNG image and PDF formats',
    'Support agency management of buses, routes, schedules, and bookings',
    'Harden concurrent access with atomic transactions and unique indexes',
]:
    add_bullet(obj)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER II: TOOLS AND TECHNOLOGIES
# ════════════════════════════════════════════
add_heading('4. Tools and Technologies Used', level=2)

# Tables for tools
def add_tool_table(headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Light Grid Accent 1'
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10)
    for row_data in rows:
        row = table.add_row()
        for i, val in enumerate(row_data):
            cell = row.cells[i]
            cell.text = val
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)

add_heading('4.1 Backend Technologies', level=3)
add_tool_table(
    ['Technology', 'Purpose'],
    [
        ['Python 3', 'Primary programming language'],
        ['Flask 2.x', 'Web framework (routing, sessions, templating)'],
        ['SQLite 3', 'Database engine with WAL journal mode'],
        ['Werkzeug', 'Password hashing and security utilities'],
        ['Pillow', 'E-ticket PNG image generation'],
        ['xhtml2pdf', 'PDF ticket generation'],
        ['Threading', 'Background departure notification scheduler'],
    ]
)

add_heading('4.2 Frontend Technologies', level=3)
add_tool_table(
    ['Technology', 'Purpose'],
    [
        ['HTML5', 'Page structure'],
        ['CSS3', 'Styling and responsive design'],
        ['JavaScript', 'Client-side interactivity and AJAX polling'],
        ['Jinja2', 'Server-side templating (Flask integrated)'],
        ['Font Awesome', 'Icon library'],
    ]
)

add_heading('4.3 Development Tools', level=3)
add_tool_table(
    ['Tool', 'Purpose'],
    [
        ['VS Code', 'Code editor'],
        ['Git', 'Version control'],
        ['PowerShell', 'Command-line interface'],
        ['Postman', 'API endpoint testing'],
    ]
)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER III: SYSTEM ARCHITECTURE
# ════════════════════════════════════════════
add_heading('5. System Architecture', level=2)

add_heading('5.1 High-Level Architecture', level=3)
add_para(
    'AFRI Trans follows a monolithic Flask application pattern with three distinct user portals: '
    'Passenger App, Agency Portal, and Ministry of Transport Portal. A shared services layer handles '
    'translation, country management, payment gateway routing, and session authentication. The data '
    'layer is a normalised SQLite database with per-request connections and WAL journal mode.'
)

# Architecture diagram placeholder
add_para('', size=4)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
lines = [
    '┌─────────────────────────────────────────────────────────────┐',
    '│                        AFRI Trans                           │',
    '├─────────────────────────────────────────────────────────────┤',
    '│    Passenger App  │  Agency Portal  │  Ministry Portal      │',
    '│  • Search trips   │  • Dashboard    │  • Dashboard          │',
    '│  • Book tickets   │  • Buses/Routes │  • Agency Registry    │',
    '│  • Make payments  │  • Schedules    │  • Approvals          │',
    '│  • View tickets   │  • Bookings     │  • Statistics         │',
    '├─────────────────────────────────────────────────────────────┤',
    '│              Shared Services Layer                          │',
    '│   Translation Engine | Country Manager | Payment Gateway    │',
    '│   Session/Auth Manager | Notification Scheduler             │',
    '├─────────────────────────────────────────────────────────────┤',
    '│                     Data Layer (SQLite + WAL mode)           │',
    '└─────────────────────────────────────────────────────────────┘',
]
for line in lines:
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run(line)
    r.font.name = 'Consolas'
    r.font.size = Pt(7)
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.0

add_heading('5.2 Request Flow', level=3)
add_para(
    'A typical booking request flows through the system as follows:'
)
steps = [
    'Passenger enters search criteria (origin, destination, date)',
    'System queries schedules joined with routes, buses, agencies',
    'Results display available trips with pricing and seat availability',
    'Passenger selects a trip and views interactive seat map',
    'System shows real-time seat availability via AJAX polling',
    'Passenger selects seat and enters personal details',
    'Payment form presents country-specific mobile money providers',
    'Booking is created atomically with seat lock via BEGIN IMMEDIATE',
    'E-ticket generated in HTML, PNG, and PDF formats',
    'Background scheduler sends departure reminders at 90 min and 45 min',
]
for step in steps:
    add_bullet(step)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER IV: DATABASE DESIGN
# ════════════════════════════════════════════
add_heading('6. Database Design', level=2)

add_heading('6.1 Schema Overview', level=3)
add_para(
    'The database was initially implemented using flat JSON storage (data.json) and later migrated '
    'to a normalised SQLite database (data.db). The schema consists of nine tables:'
)

schema_tables = [
    ('agencies', 'Bus companies with country, locations, approval status, email, password reset'),
    ('buses', 'Vehicles owned by agencies (plate, capacity, bus_type, status)'),
    ('routes', 'City pairs with pricing, duration, luggage configuration'),
    ('schedules', 'Specific trips on a route (date, time, period, status)'),
    ('passengers', 'Normalised passenger records with UNIQUE(phone, id_number)'),
    ('bookings', 'Ticket purchases with seat_number, booking_ref (UNIQUE), payment status'),
    ('meta', 'Counters and migration tracking key-value store'),
    ('agency_subscriptions', 'Commission exemption plans (plan, amount, start/end date)'),
    ('notification_log', 'Sent departure reminders (booking_id, notification_type, sent_at)'),
]
for name, desc in schema_tables:
    p = add_para('')
    r = p.add_run(f'{name}: ')
    r.bold = True
    r.font.size = Pt(10)
    r2 = p.add_run(desc)
    r2.font.size = Pt(10)

add_para(
    'Key database constraints include a UNIQUE INDEX on bookings(schedule_id, seat_number) to '
    'prevent double-booking, a UNIQUE INDEX idx_agencies_name_country on agencies(name, country) '
    'to prevent duplicate registrations, and a UNIQUE INDEX idx_agencies_email for global email '
    'uniqueness. All foreign keys use ON DELETE CASCADE for referential integrity.'
)

add_heading('6.2 Entity Relationship Diagram', level=3)
add_para(
    'The database follows a star-like schema with agencies at the centre:'
)
add_para('')
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
er_lines = [
    'Agencies   1 ──── * Buses',
    'Agencies   1 ──── * Routes',
    'Routes     1 ──── * Schedules',
    'Buses      1 ──── * Schedules',
    'Schedules  1 ──── * Bookings',
    'Passengers 1 ──── * Bookings',
    'Agencies   1 ──── * agency_subscriptions',
]
for line in er_lines:
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run(f'    {line}')
    r.font.name = 'Consolas'
    r.font.size = Pt(10)
    p2.paragraph_format.space_after = Pt(2)
    p2.paragraph_format.line_spacing = 1.0

add_heading('6.3 Migration from JSON to SQLite', level=3)
add_para(
    'The original implementation stored all data in a single data.json file, causing ID collisions '
    '(len(data["x"]) + 1 produced duplicates after deletion), data duplication (passenger details '
    'repeated across bookings), and orphan records. A migration function (migrate_from_json()) reads '
    'the JSON once and imports all data into the normalised SQLite structure using AUTOINCREMENT, '
    'proper foreign keys, and WAL journal mode. The migration is idempotent via a migrated flag in '
    'the meta table.'
)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER V: FEATURES IMPLEMENTED
# ════════════════════════════════════════════
add_heading('7. Features Implemented', level=2)

add_heading('7.1 Multi-Country Support', level=3)
add_para(
    'All 54 African countries are configured with: country name and flag colours (up to 6 colours), '
    'local currency and currency code, major cities (8–18 per country), default and supported languages, '
    'local payment providers, and VIP surcharge. Country-switching via a globe icon on the navbar '
    'auto-updates the language, currency, and available cities across the entire platform.'
)

add_heading('7.2 Internationalisation (11 Languages)', level=3)
add_para(
    'The platform supports 11 languages with full UI translation: English, French, Arabic, Portuguese, '
    'Spanish, Swahili, Amharic, Somali, Tigrinya, Afrikaans, and Zulu. All UI text is wrapped in _{text} '
    'function calls. Each language has a JSON file with key-value pairs. Missing keys fall back gracefully '
    'to English. Language toggle is shown only when a country has 2+ supported languages.'
)

add_heading('7.3 Passenger Booking Flow', level=3)
add_para(
    'The booking process follows a clear step-by-step flow: Search (origin, destination, date) → '
    'Browse Results (grouped by period, showing agency, bus type, price, available seats) → '
    'Pick Seat (interactive seat map with VIP/standard styling) → Enter Details (name, phone, ID, '
    'optional luggage) → Payment (country-specific mobile money providers) → Ticket (HTML, PNG, PDF). '
    'Business rules include: booking closes 15 min before departure, trips auto-expire 2 hours after '
    'departure, bookings expire 30 min after departure, and rate limiting (10 attempts/15 min/IP) '
    'protects all login endpoints.'
)

add_heading('7.4 Real-Time Seat Map', level=3)
add_para(
    'The seat selection page polls a lightweight JSON endpoint (GET /api/seats/<sid>/status) every '
    '30 seconds to detect seats taken by other passengers without page reload. JavaScript compares '
    'the new taken set against the previous snapshot. Newly taken seats are greyed out immediately. '
    'If the user\'s selected seat was taken by someone else, the selection is cleared and they must '
    'pick again. This replaces the previously static seat map with a real-time multi-user experience.'
)

add_heading('7.5 Agency Portal', level=3)
add_para(
    'Agencies have a dedicated dashboard for managing operations: overview of buses, routes, upcoming '
    'schedules, and booking counts; approval/rejection status banners; bus management (add, toggle '
    'availability); route definition (city pairs, duration, pricing, luggage); schedule creation by '
    'assigning routes to buses on specific dates/times; booking view and cancellation; and passenger '
    'manifest generation. Registration creates an approved: False account, invisible to passengers '
    'until Ministry approval.'
)

add_heading('7.6 Ministry of Transport Portal', level=3)
add_para(
    'Each country has a scoped Ministry portal with country-scoped authentication (selected via globe '
    'menu). Features include: dashboard statistics (total agencies, pending approvals, buses, routes, '
    'schedules, bookings, revenue); agency registry with status badges (Approved green, PENDING orange, '
    'Rejected red); approve/reject actions with reason modals; and cross-agency booking records.'
)

# Screenshots
add_para('', size=4)
add_para('Figure 1: Ministry of Transport Dashboard', italic=True, size=9, color='666666', align=WD_ALIGN_PARAGRAPH.CENTER)

add_heading('7.7 Subscription Monetisation', level=3)
add_para(
    'Agencies can prepay to skip the 1% platform commission for a defined period. Three plans are '
    'available: Monthly (58,000 FCFA / 15,000 NGN), 6-Month (250,000 FCFA / 75,000 NGN), and Annual '
    '(500,000 FCFA / 150,000 NGN). The flow: Agency clicks Subscription button on dashboard → chooses '
    'a plan → /agency/subscribe/pay (selects payment provider + phone) → POST to '
    '/agency/subscribe/confirm → subscription activated or extended. If the agency already has an '
    'active subscription, the page shows "Extend Your Subscription" with the current expiry date and '
    'lets them add more time (days added to end_date via extend_subscription()). On the passenger '
    'payment page, the 1% commission breakdown is hidden — passengers see only the total price.'
)

add_heading('7.8 Departure Notification Scheduler', level=3)
add_para(
    'A background daemon thread runs every 60 seconds and checks for confirmed bookings where departure '
    'is exactly 90 minutes or 45 minutes away. For each qualifying booking, it checks the notification_log '
    'table to avoid duplicates, formats a reminder message, and attempts to send via priority chain: '
    'WhatsApp Cloud API (free tier, 1,000 conversations/month, no credit card needed) → USB GSM Modem '
    'via serial AT commands (one-time ~$20 hardware, free SMS via SIM bundle) → Twilio SMS API (paid) → '
    'console log (always works, no config). All tiers are dormant until configured — zero resource usage '
    'when unconfigured.'
)

add_heading('7.9 E-Ticket Generation', level=3)
add_para(
    'Tickets are generated in three formats: HTML Ticket (styled web page with flag colours), '
    'PNG Image (rendered with Pillow featuring country flag colours, QR-style reference, route info, '
    'VIP/standard badge, price breakdown), and PDF Document (via xhtml2pdf suitable for printing/email).'
)

add_heading('7.10 Commission System', level=3)
add_para(
    'The platform charges a 1% commission on every booking. The commission amount in currency is never '
    'displayed in any UI — only the rate (1%) is shown as an informational badge. Commission is '
    'automatically skipped when the booking\'s agency has an active subscription.'
)

add_heading('7.11 Flash Alert Categories', level=3)
add_para(
    'Flash messages use three colour-coded categories: success (green, #e8f5e9) for positive feedback, '
    'error (red, #ffebee) for failures, and warning (orange, #fff8e1) for informational alerts. All '
    '100+ flash() calls in the application were updated. CSS classes .flash-success, .flash-error, '
    '.flash-warning style the corresponding alerts via with_categories=true in the base template.'
)

add_heading('7.12 Flag-Coloured Hero Title', level=3)
add_para(
    'The hero heading on the index page colours each word using the country\'s flag colours. For '
    'Cameroon (green #007a5e, red #ce1126, yellow #fcd116), "Book" appears green, "Your" red, '
    '"Journey" yellow, "Across" green, "Cameroon" red. Colours cycle through the flag_colors array '
    'defined per country, falling back gracefully for countries with fewer colours.'
)

add_heading('7.13 Responsive Design', level=3)
add_para(
    'The interface is fully responsive with four breakpoints: 1024px (tablet), 768px (mobile), '
    '480px (small phone), and 360px (very small). Features include hamburger navigation with smooth '
    'animation and click-outside-to-close, scrollable tables, fluid typography using clamp(), seat '
    'layout scaling (30px max-width on mobile), and grid systems that collapse progressively.'
)

add_heading('7.14 Security and Concurrency Hardening', level=3)
add_para(
    'Several security and concurrency measures were implemented: rate limiting on all login endpoints '
    '(10 attempts per 15 minutes per IP), one-time shared password mechanism (Admin123 permanently '
    'invalidated after first use), atomic booking with BEGIN IMMEDIATE + unique index on '
    '(schedule_id, seat_number), TOCTOU-free agency registration using in-transaction uniqueness '
    'checks, atomic get_next_ref with single-connection SELECT+UPDATE, per-country super admin '
    'emails with password recovery, session validation on every authenticated request, and '
    'database-level UNIQUE indexes at multiple levels.'
)

# Insert screenshots section
add_para('', size=6)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('─── Screenshots ───')
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

screenshots = [
    ('image2.png', 'Figure 2: Homepage with search form allowing passengers to find trips by origin, destination and date.'),
    ('image7.png', 'Figure 3: Search results showing available trips grouped by period with pricing and seat availability.'),
    ('image8.png', 'Figure 4: Bus seat selection layout with VIP (gold) and standard (blue) colour coding, driver area, doors, emergency exit and toilet markers.'),
    ('image3.png', 'Figure 5: E-ticket generated after successful booking showing route, passenger details, seat number and pricing.'),
    ('image5.png', 'Figure 6: Agency dashboard with revenue breakdown by route, recent bookings, and operational stats.'),
    ('image6.png', 'Figure 7: Agencies listing page displaying all registered transport companies in the selected country.'),
    ('image4.png', 'Figure 8: Country selection modal listing all 54 African countries with IP-based auto-detection.'),
]
for fn, caption in screenshots:
    add_para('', size=4)
    add_img(fn, width=Inches(5.2), caption=caption)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER VI: IMPLEMENTATION DETAILS
# ════════════════════════════════════════════
add_heading('8. Implementation Details', level=2)

add_heading('8.1 Project Structure', level=3)
add_para(
    'The project follows a standard Flask application structure with the following key directories and files:'
)

structure = [
    'transport/',
    '├── app.py                  # Main Flask application (routes, config, scheduler)',
    '├── database.py             # SQLite database module (schema, CRUD, migration)',
    '├── data.conf               # Original JSON storage (migrated to SQLite)',
    '├── data                    # SQLite database (created by migration)',
    '├── .env                    # Environment variables (TWILIO, WHATSAPP, MAIL)',
    '├── .gitignore              # Version control exclusions',
    '├── generate_translations   # Script to generate translation files',
    '│',
    '├── static/',
    '│   ├── style.css           # All site CSS (responsive, layout, components)',
    '│   └── img/                # Flag images and logo',
    '│',
    '├── templates/',
    '│   ├── base.html           # Base template (nav, footer, country modal)',
    '│   ├── index.html          # Homepage with flag-coloured hero',
    '│   ├── search.html         # Trip search results',
    '│   ├── pick_seat.html      # Seat selection with live polling',
    '│   ├── book.html           # Booking form',
    '│   ├── payment.html        # Payment page (no commission breakdown)',
    '│   ├── ticket.html         # E-ticket display',
    '│   ├── agency_dashboard    # Agency dashboard with subscription badge',
    '│   ├── agency_subscribe    # Subscription plan selection and payment',
    '│   ├── ministry_dashboard  # Ministry oversight dashboard',
    '│   └── partials/           # AJAX-loaded template fragments',
    '│',
    '└── translations/           # 11 language JSON files (682 keys each)',
]
for line in structure:
    p = doc.add_paragraph()
    r = p.add_run(f'    {line}')
    r.font.name = 'Consolas'
    r.font.size = Pt(8)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0

add_heading('8.2 Key Code Patterns', level=3)

add_para('Translation Wrapper:', bold=True)
add_para(
    'All UI text is wrapped in the _() function which loads the current language\'s JSON translation '
    'file and falls back to English for any missing key. This ensures no UI breaks even when '
    'translations are incomplete for a given language.'
)

add_para('Notification Sending Priority Chain:', bold=True)
code_lines = [
    'send_notification(phone, message, country_code):',
    '    1. send_whatsapp() — WhatsApp Cloud API if WHATSAPP_TOKEN set',
    '    2. send_sms_via_modem() — USB GSM modem if GSM_MODEM_PORT set',
    '    3. send_sms() — Twilio if TWILIO_SID, _TOKEN, _FROM set',
    '    4. Console log — always works, no configuration required',
]
for line in code_lines:
    p = doc.add_paragraph()
    r = p.add_run(f'    {line}')
    r.font.name = 'Consolas'
    r.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0

add_para('Atomic Registration Pattern:', bold=True)
add_para(
    'The add_agency() function opens a BEGIN IMMEDIATE transaction, performs both name+country '
    'and email uniqueness checks inside the transaction, and inserts the record. A UNIQUE INDEX '
    'at the database level provides the last line of defence. IntegrityError is caught and returned '
    'as a friendly (id, error) tuple instead of crashing.'
)

add_para('Subscription Extension Pattern:', bold=True)
add_para(
    'extend_subscription() checks for an existing active subscription: if found, it adds the new '
    'plan\'s duration to the existing end_date; otherwise it creates a new subscription starting '
    'from today. This allows agencies to stack multiple plan purchases.'
)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER VII: CHALLENGES AND SOLUTIONS
# ════════════════════════════════════════════
add_heading('9. Challenges and Solutions', level=2)

challenges = [
    ('9.1 Data Redundancy in JSON Storage',
     'Challenge: The original data.json stored all data in a flat, denormalised structure. Passenger '
     'details were repeated across bookings, route prices were duplicated, and ID generation using '
     'len(data["x"]) + 1 produced collisions after deletions. Deleting an agency left orphan records.\n\n'
     'Solution: Migrated to a normalised SQLite schema with 9 tables, AUTOINCREMENT for collision-free '
     'IDs, ON DELETE CASCADE for referential integrity, WAL journal mode for concurrent writes, and a '
     'UNIQUE constraint on passenger(phone, id_number) to eliminate duplication.'),

    ('9.2 TOCTOU Race Condition in Agency Registration',
     'Challenge: Two simultaneous registration requests with the same agency name could both pass the '
     'app-level uniqueness check (SELECT) and then both INSERT, creating duplicate records. The email '
     'check had the same flaw — the second request would crash with a 500 error from an unhandled '
     'IntegrityError.\n\n'
     'Solution: The registration flow was rewritten. add_agency() now opens a BEGIN IMMEDIATE transaction, '
     'performs both name and email duplicate checks inside the transaction, and returns an (id, error) '
     'tuple. A UNIQUE INDEX idx_agencies_name_country on LOWER(name) + country provides database-level '
     'enforcement. IntegrityError is caught and returned as a friendly flash message.'),

    ('9.3 Booking Reference Counter Race',
     'Challenge: get_next_ref() opened a connection, SELECTed the counter, closed it, re-opened, and '
     'UPDATEed — two concurrent bookings could read the same value, producing duplicate references. '
     'The UNIQUE constraint caught it, but users saw a confusing "seat taken" error.\n\n'
     'Solution: SELECT and UPDATE now execute in a single BEGIN IMMEDIATE transaction on one connection, '
     'ensuring unique, monotonically incrementing reference numbers for every caller.'),

    ('9.4 Concurrent Seat Booking',
     'Challenge: Two passengers selecting the same seat simultaneously could both pass the availability '
     'check before either booking was committed — a classic race condition.\n\n'
     'Solution: Two layers of protection: (1) a database-level UNIQUE INDEX on (schedule_id, seat_number), '
     'and (2) atomic booking creation in add_booking_atomic() using BEGIN IMMEDIATE. A re-check at '
     'payment time in confirm_booking_atomic() provides optimistic locking coverage.'),

    ('9.5 Free Departure Notification Delivery',
     'Challenge: Sending real SMS notifications costs money. The requirement was for free notifications '
     'with no budget for paid APIs.\n\n'
     'Solution: A four-tier priority chain was implemented — WhatsApp Cloud API (free tier, 1,000 '
     'conversations/month, no credit card via Meta Developer account), USB GSM modem (one-time ~$20 '
     'hardware, sends via SIM AT commands — free with SIM SMS bundle), Twilio (paid fallback), and '
     'console logging (always works). All tiers are dormant until configured, consuming zero resources.'),

    ('9.6 Multi-Language Translation Management',
     'Challenge: Maintaining consistent translations across 11 languages with ~434+ UI strings each. '
     'Adding new text required updating all 11 files.\n\n'
     'Solution: A generate_translations.py script reads en.json (source of truth) and regenerates all '
     'language files. The _() function gracefully falls back to English for any missing key in any '
     'language file. French translations are done manually for accuracy; other languages use the '
     'fallback mechanism.'),

    ('9.7 Agency Privacy',
     'Challenge: Competing agencies should not access each other\'s pricing, routes, or operational data. '
     'Agency employees browsing the site as passengers could view competitor information.\n\n'
     'Solution: Session-aware filtering in the _country_agencies() helper. When agency_id is in session, '
     'all public pages filter to show only the logged-in agency\'s data. Direct URL access to competitor '
     'pages is blocked with authorization checks.'),

    ('9.8 Other Challenges',
     'Additional challenges addressed include: bell icon colour inconsistency (hardcoded to #c62828 '
     'instead of per-country flag-2 which was invisible in Kenya), one-time shared password security '
     '(Admin123 permanently invalidated after first use via meta table flags), session staleness '
     '(agencies deleted mid-session caught by get_agency_session() validation), unclosed HTML elements '
     '(systematic div-counting review), and bilingual announcement translation (French stored in '
     'message_fr column at creation time, not translated on-the-fly).'),
]

for title, body in challenges:
    add_heading(title, level=3)
    # Split on \n\n for separate paragraphs
    parts = body.split('\n\n')
    for part in parts:
        add_para(part.strip())

add_page_break()

# ════════════════════════════════════════════
# CHAPTER VIII: TESTING AND RESULTS
# ════════════════════════════════════════════
add_heading('10. Testing and Results', level=2)

add_heading('10.1 Testing Approach', level=3)
add_para(
    'The application was tested using: manual browser testing across all routes and user flows, '
    'automated HTTP tests with Python http.client, database verification for migration accuracy, '
    'responsive design testing at all four breakpoints, and targeted concurrency tests.'
)

add_heading('10.2 Route Verification', level=3)
add_para('All 30+ routes were verified to return HTTP 200 with valid HTML content:')
routes_list = [
    ('/', 'Homepage with agency listing and hero section'),
    ('/search?from=X&to=Y&date=Z', 'Trip search results with pricing'),
    ('/schedule/<sid>/seats-preview', 'Seat selection with interactive map'),
    ('/schedule/<sid>/book', 'Booking form with passenger details'),
    ('/booking/<bid>/payment', 'Payment provider options'),
    ('/booking/<bid>/payment (POST)', 'Payment confirmation (simulated)'),
    ('/ticket/<ref>', 'E-ticket with all details'),
    ('/ticket/<ref>/pdf', 'PDF ticket download'),
    ('/ticket/<ref>/image', 'PNG ticket image'),
    ('/api/seats/<sid>/status', 'JSON seat status (real-time polling)'),
    ('/agency/dashboard', 'Agency dashboard with subscription badge'),
    ('/agency/subscribe', 'Subscription plan selection'),
    ('/agency/subscribe/pay', 'Subscription payment form'),
    ('/ministry/agencies', 'Agency registry with status badges'),
    ('/api/booking/confirm (POST)', 'AJAX booking creation'),
]
for route, desc in routes_list:
    p = add_para('')
    r = p.add_run(f'{route}: ')
    r.bold = True
    r.font.size = Pt(9)
    r2 = p.add_run(desc)
    r2.font.size = Pt(9)

add_heading('10.3 Migration Results', level=3)
add_para(
    'The migration from JSON to SQLite achieved 100% data integrity:'
)
add_tool_table(
    ['Entity', 'JSON Records', 'SQLite Records', 'Match'],
    [
        ['Agencies', '7', '7', '✓'],
        ['Buses', '111', '111', '✓'],
        ['Routes', '9', '9', '✓'],
        ['Schedules', '11', '11', '✓'],
        ['Bookings', '18', '18', '✓'],
        ['Passengers', 'N/A (duplicated)', '7 (deduplicated)', '✓'],
    ]
)

add_heading('10.4 Additional Feature Tests', level=3)
tests = [
    'Live Seat API: Returns {"taken": [...]} — HTTP 200 verified with correct seat arrays.',
    'Subscription Flow: Plan selection → pay form → confirm POST activates subscription. Extending existing sub correctly adds days to end_date.',
    'Concurrency: Two simultaneous registration requests with same name — first succeeds, second returns "name already exists" flash (no crash).',
    'Flag-Coloured Hero: Cameroon flag colours cycle correctly through words in hero title. Country switching updates colours dynamically.',
    'Notification Scheduler: Daemon thread starts without error. With no channel configured, logs to console — zero application impact.',
    'Flash Categories: All 100+ flash() calls updated. CSS classes render green/orange/red alerts correctly in all templates.',
    'Payment Commission Skip: 1% commission hidden from passenger. Active subscription triggers server-side commission skip verified via DB.',
    'TOCTOU Fix: Registration with duplicate name inside BEGIN IMMEDIATE correctly rejects second request with friendly error.',
]
for t in tests:
    add_bullet(t)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER IX: CONCLUSION AND FUTURE WORK
# ════════════════════════════════════════════
add_heading('11. Conclusion and Future Work', level=2)

add_heading('11.1 Summary of Achievements', level=3)
add_para(
    'The AFRI Trans platform successfully delivers a multi-country bus ticketing system with the following '
    'achievements:'
)
achievements = [
    'Complete coverage of all 54 African countries with localised configuration',
    'Multilingual interface supporting 11 languages across different scripts',
    'Full booking lifecycle from search through payment to e-ticket delivery',
    'Agency management with registration, scheduling, subscription, and operations',
    'Government oversight with per-country ministry approval workflows',
    'Real-time seat map with 30-second AJAX polling for concurrent multi-user booking',
    'Background departure notification scheduler with four-tier delivery chain',
    'Subscription monetisation model with extendable plans for commission exemption',
    'Responsive design accessible on desktop, tablet, and mobile devices',
    'Data integrity through normalised SQLite schema with foreign keys and unique indexes',
    'Concurrency hardening with atomic transactions and TOCTOU-free registration',
    'Competitor privacy preventing unauthorised data access between agencies',
    'Colour-coded flash messaging for clearer user feedback',
]
for a in achievements:
    add_bullet(a)

add_heading('11.2 Future Improvements', level=3)
future_items = [
    ('Security', ['Add CSRF protection to all forms', 'Switch to HTTPS in production']),
    ('Code Quality', ['Refactor monolithic app.py into modular route blueprints', 'Add unit tests with pytest']),
    ('Real-Time', ['WebSocket-based real-time seat availability (HTTP polling already implemented)', 'Live booking notifications for agencies']),
    ('Payment Integration', ['Connect to real mobile money APIs (M-Pesa, MTN MoMo, Orange Money)', 'Webhook-based payment confirmation']),
    ('Performance', ['Redis caching for frequently accessed data', 'Database query optimisation', 'CDN for static assets']),
    ('Additional Features', ['RTL support for Arabic-language countries', 'Mobile app (React Native or Flutter)', 'Driver/operator mobile interface for manifest management', 'Multi-trip and round-trip booking', 'Loyalty/rewards program']),
]
for category, items in future_items:
    add_para(f'{category}:', bold=True)
    for item in items:
        add_bullet(item)

add_page_break()

# ════════════════════════════════════════════
# REFERENCES
# ════════════════════════════════════════════
add_heading('12. References', level=2)
refs = [
    'Flask Documentation — The Flask Web Framework. Pallets Project. https://flask.palletsprojects.com/',
    'Python 3 Documentation — Python Software Foundation. https://docs.python.org/3/',
    'SQLite Documentation — SQLite Consortium. https://www.sqlite.org/docs.html',
    'Jinja2 Documentation — Pallets Project. https://jinja.palletsprojects.com/',
    'Pillow (PIL Fork) Documentation — Python Pillow. https://pillow.readthedocs.io/',
    'xhtml2pdf Documentation — xhtml2pdf Project. https://xhtml2pdf.readthedocs.io/',
    'Werkzeug Documentation — Pallets Project. https://werkzeug.palletsprojects.com/',
    'Twilio SMS API — Twilio Inc. https://www.twilio.com/docs/sms',
    'WhatsApp Cloud API — Meta. https://developers.facebook.com/docs/whatsapp/cloud-api',
    'Font Awesome Icons — Fonticons, Inc. https://fontawesome.com/',
    'Mobile Money in Africa — GSMA Mobile Money Report. https://www.gsma.com/mobilemoney/',
    'ISO 3166-1 Country Codes — International Organization for Standardization.',
]
for i, ref in enumerate(refs, 1):
    p = add_para('')
    r = p.add_run(f'[{i}] {ref}')
    r.font.size = Pt(10)

# ════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════
doc.save(DST)
print(f'=== Report saved to {DST} ===')
print(f'Size: {os.path.getsize(DST)} bytes')
