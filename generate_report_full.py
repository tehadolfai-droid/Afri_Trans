"""Generate a comprehensive professional internship report with chapters, sub-chapters, TOC, and page numbers."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import zipfile, os, shutil, copy

SRC = 'AFRI_Trans_reports.docx'
DST = 'AFRI_Trans_Report_2026_Full.docx'
TMP = os.environ['TEMP'] + r'\report_build_full'

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

add_para('(Right-click and select "Update Field" to generate table of contents)', size=10, italic=True, color='999999')

add_para('', size=6)

toc_items = [
    ('', '1. Introduction', ''),
    ('', '    1.1 Background', ''),
    ('', '2. Problem Statement', ''),
    ('', '3. Objectives', ''),
    ('', '    3.1 Primary Objectives', ''),
    ('', '    3.2 Secondary Objectives', ''),
    ('', '4. Tools and Technologies Used', ''),
    ('', '    4.1 Backend Technologies', ''),
    ('', '    4.2 Frontend Technologies', ''),
    ('', '    4.3 Development Tools', ''),
    ('', '5. System Architecture', ''),
    ('', '    5.1 High-Level Architecture', ''),
    ('', '    5.2 Request Flow', ''),
    ('', '6. Database Design', ''),
    ('', '    6.1 Schema Overview', ''),
    ('', '    6.2 Entity Relationship Diagram', ''),
    ('', '    6.3 Migration from JSON to SQLite', ''),
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
    '(green success, orange warning, red error) for clearer UX. All concurrency vulnerabilities \u2014 '
    'TOCTOU race conditions in agency registration and booking reference generation \u2014 have been fixed '
    'with database-level transactions and unique indexes.'
)
add_para(
    'This report documents the development of the AFRI Trans platform during the internship period '
    'at Ferdsilink Buea, Cameroon. The project was built using Python Flask for the backend, SQLite '
    'for data persistence, and vanilla HTML/CSS/JavaScript for the frontend. The internship spanned '
    '16 June 2026 to 30 September 2026, during which the platform evolved from a single-country '
    'prototype into a fully realised multi-country, multi-language, multi-currency production-ready '
    'system with concurrency hardening, real-time features, and government oversight workflows.'
)
add_para(
    'The importance of bus transport in Africa cannot be overstated. It is estimated that over 80% '
    'of inter-city passenger travel in sub-Saharan Africa is conducted by bus or shared taxi, '
    'making it the backbone of domestic and cross-border mobility. The African bus industry serves '
    'hundreds of millions of passengers annually, with major corridors such as Lagos\u2013Ibadan, '
    'Nairobi\u2013Mombasa, Douala\u2013Yaound\u00e9, and Johannesburg\u2013Pretoria moving tens of thousands '
    'of passengers daily. Yet the industry remains largely offline, with paper ticketing, manual '
    'seat allocation, and cash-only payments dominating the landscape.'
)
add_para(
    'The digital transformation gap in African transportation is significant. While ride-hailing '
    'apps like Uber and Bolt have transformed urban mobility, the inter-city bus sector has seen '
    'relatively little innovation. Most bus agencies operate independently with proprietary, '
    'often paper-based systems. Passengers must physically visit terminals to purchase tickets, '
    'sometimes queuing for hours. There is no standardised way to compare prices, check seat '
    'availability, or book across multiple agencies. This fragmentation creates inefficiencies, '
    'limits market access for smaller agencies, and leaves passengers with a suboptimal experience.'
)
add_para(
    'AFRI Trans directly addresses this gap by providing a unified digital marketplace. The platform '
    'abstracts the complexity of multi-country operations \u2014 different currencies, languages, payment '
    'providers, and regulatory frameworks \u2014 behind a single, consistent interface. For passengers, '
    'it offers the convenience of online search, comparison, booking, and payment. For agencies, it '
    'provides a digital storefront, operational tools, and access to a broader passenger base. For '
    'governments, it delivers oversight capabilities to regulate and monitor the transport sector.'
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
add_para(
    'The background of this project is rooted in the specific needs of the Central African transport '
    'market. Cameroon, where the project was developed, has a thriving bus industry with major '
    'operators like Buca Voyages, Finex Voyages, and Touristique Express serving routes between '
    'Douala, Yaound\u00e9, Bafoussam, Bamenda, and Garoua. These agencies manage their operations '
    'independently, using manual manifest sheets, phone-based booking, and cash payments collected '
    'at terminals. The lack of digital infrastructure creates bottlenecks during peak travel periods '
    'such as Christmas, Easter, and the end-of-year holidays, when terminals become overcrowded and '
    'passengers struggle to secure seats.'
)
add_para(
    'Beyond Cameroon, the broader African context presents even greater complexity. The continent '
    'has 54 recognised countries, each with its own currency, official languages, regulatory '
    'authorities, and payment infrastructure. Nigeria uses the Naira with widely adopted mobile '
    'money and bank transfers. East African countries like Kenya and Tanzania use the Shilling '
    'with M-Pesa dominating mobile payments. Francophone West and Central Africa share the CFA '
    'Franc but have distinct regulatory bodies. North African countries like Morocco, Algeria, '
    'and Egypt have their own currencies and payment ecosystems. Any platform aspiring to serve '
    'the entire continent must gracefully handle this diversity.'
)
add_para(
    'The Ferdsilink organisation in Buea, Cameroon, identified this gap and initiated the AFRI Trans '
    'project as a proof-of-concept for a continent-wide bus ticketing solution. The project was '
    'developed by a single intern over approximately three months, starting with a basic Flask '
    'application serving one country with JSON file storage, and progressively evolving into a '
    'comprehensive platform with 54-country support, 11 languages, real-time features, and '
    'production-grade concurrency handling. This report documents the complete journey, including '
    'design decisions, implementation details, challenges encountered, and solutions developed.'
)

add_page_break()

# 1.2 Problem Statement (renumbered to Chapter 2)
add_heading('2. Problem Statement', level=2)
add_para(
    'The African bus transportation industry faces several challenges that motivated the development of AFRI Trans:'
)
problems = [
    ('Lack of Centralisation', 'No single platform exists for booking bus tickets across multiple African countries. Passengers must interact with each agency separately. For example, a passenger travelling from Douala to Lagos must contact different agencies for each leg, with no unified search or booking experience.'),
    ('Language Barriers', 'Africa has over 2,000 languages. A platform serving the continent must support multiple languages to be accessible. A passenger in Senegal should be able to use the platform in French, while a passenger in Ethiopia should find it in Amharic.'),
    ('Currency and Payment Fragmentation', 'Each country uses a different currency and has different mobile money providers. A unified system must handle this complexity, from the Nigerian Naira with bank transfer options to the Kenyan Shilling with M-Pesa integration to the CFA Franc with Orange Money support.'),
    ('Regulatory Requirements', 'Each country has its own Ministry of Transport that must approve and oversee agencies operating within its jurisdiction. In Cameroon, for instance, the Ministry of Transport issues operating licences and sets fare guidelines, while Nigeria\u2019s Federal Ministry of Transportation has its own regulatory framework.'),
    ('Data Redundancy', 'Initial implementation used flat JSON file storage, leading to duplicate data, ID collisions, and referential integrity issues. The len(data["x"]) + 1 pattern for ID generation produced duplicates after any record was deleted, causing data corruption over time.'),
    ('Agency Privacy', 'Competing agencies should not have access to each other\'s operational data (pricing, routes, passenger manifests). An agent from Finex Voyages should not be able to view the manifest of Buca Voyages.'),
    ('Security', 'A single shared password for all ministry users across all countries is insecure. The initial implementation used "Admin123" as a hardcoded password for all ministry portals, providing no accountability or access control.'),
    ('No Commission Exemption', 'Agencies had no way to opt out of the 1% platform commission \u2014 all bookings were charged regardless of volume. A large agency processing thousands of bookings per month had no incentive to use the platform exclusively.'),
    ('No Real-Time Seat Updates', 'The seat map was static \u2014 concurrent viewers could not see each other\'s selections. If two passengers viewed the same schedule simultaneously, both would see all seats as available and could potentially select the same seat.'),
    ('No Departure Notifications', 'Passengers received no reminders before departure, leading to missed trips. Agencies had to manually call passengers, which was time-consuming and unreliable.'),
    ('Concurrency Bugs (TOCTOU)', 'Agency registration and booking reference generation both had race conditions that could create duplicates. Under load, the system could produce duplicate references or duplicate agency registrations, causing data corruption and confusing error messages.'),
]
for title, desc in problems:
    p = add_para('')
    r = p.add_run(f'{title}: ')
    r.bold = True
    r.font.size = Pt(11)
    r2 = p.add_run(desc)
    r2.font.size = Pt(11)

add_page_break()

# 1.3 Objectives
add_heading('3. Objectives', level=2)

add_heading('3.1 Primary Objectives', level=3)
for obj in [
    'Develop a multi-country bus ticketing platform covering all 54 African nations',
    'Implement a language system supporting 11 African and international languages',
    'Create per-country payment provider integration with local mobile money options',
    'Build a Ministry of Transport approval workflow for agency registration',
    'Design a fully responsive interface accessible on all device sizes',
    'Add subscription plans (monthly / 6-month / annual) for commission exemption',
    'Implement live seat map with 30-second auto-refresh for concurrent booking',
    'Build a background departure notification scheduler for passenger reminders',
    'Fix TOCTOU race conditions in registration and reference generation',
]:
    add_bullet(obj)

add_para(
    'These primary objectives were established at the outset of the project and guided all development '
    'decisions. Each objective addresses a specific pain point identified in the current African bus '
    'transport ecosystem. The multi-country support objective, for instance, was not merely about '
    'listing countries but about creating a fully localised experience for each nation, with '
    'appropriate currencies, languages, cities, payment providers, and regulatory workflows.'
)
add_para(
    'The language system objective was particularly ambitious. Supporting 11 languages across different '
    'language families (Germanic, Romance, Semitic, Cushitic, Bantu, and others) required a flexible '
    'translation architecture that could handle right-to-left scripts (Arabic), agglutinative morphology '
    '(Swahili, Zulu), and languages with complex character sets (Amharic). The system had to degrade '
    'gracefully when translations were incomplete, always falling back to English rather than breaking.'
)

add_heading('3.2 Secondary Objectives', level=3)
for obj in [
    'Normalise data storage and eliminate redundancy through SQLite migration',
    'Enforce privacy between competing agencies with session-scoped data filtering',
    'Generate e-tickets in PNG image and PDF formats alongside HTML',
    'Support agency management of buses, routes, schedules, and bookings',
    'Harden concurrent access with atomic transactions and unique indexes',
    'Implement rate limiting on all authentication endpoints',
    'Add colour-coded flash alert categories for improved user feedback',
    'Create a flag-coloured hero title that dynamically adapts to the selected country',
]:
    add_bullet(obj)

add_para(
    'The secondary objectives complemented the primary ones by addressing quality-of-life improvements '
    'and infrastructure concerns. While the primary objectives focused on feature completeness, the '
    'secondary objectives targeted data integrity, security, and user experience polish. The migration '
    'from JSON to SQLite, for example, was initially planned as a maintenance task but became critical '
    'as data volumes grew and race conditions emerged in the flat-file storage system.'
)
add_para(
    'The responsive design objective was driven by the African mobile context. In many African countries, '
    'smartphone penetration exceeds 60%, and a significant portion of internet traffic comes from mobile '
    'devices. A platform that does not work well on mobile phones would exclude a large segment of '
    'potential users. The design had to accommodate small screens, variable network quality, and '
    'touch-based interaction patterns.'
)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER II: TOOLS AND TECHNOLOGIES
# ════════════════════════════════════════════
add_heading('4. Tools and Technologies Used', level=2)

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
        ['Python 3', 'Primary programming language (\u22481,800 lines of application code)'],
        ['Flask 2.x', 'Web framework (routing, sessions, templating with Jinja2)'],
        ['SQLite 3', 'Database engine with WAL journal mode for concurrent writes'],
        ['Werkzeug', 'Password hashing and security utilities (pbkdf2:sha256)'],
        ['Pillow (PIL)', 'E-ticket PNG image generation with flag colours and QR-style reference'],
        ['xhtml2pdf', 'PDF ticket generation from HTML templates'],
        ['Threading (stdlib)', 'Background departure notification scheduler daemon thread'],
        ['hashlib (stdlib)', 'Unique ID generation for booking references and tokens'],
        ['json (stdlib)', 'Translation file loading and JSON data import during migration'],
    ]
)
add_para(
    'Python 3 was chosen as the primary programming language due to its readability, large standard '
    'library, and excellent ecosystem for web development. Flask was selected over Django because '
    'the project required a lightweight, flexible framework where the intern could build each '
    'component from first principles, gaining a deep understanding of web application architecture. '
    'The total backend codebase comprises approximately 1,800 lines of Python spread across the '
    'main application file (app.py), the database module (database.py), and supporting scripts.'
)
add_para(
    'SQLite with WAL (Write-Ahead Logging) journal mode was chosen as the database engine. SQLite '
    'is embedded directly into the Python process, requiring no separate database server, which '
    'simplifies deployment and reduces operational overhead. WAL mode allows concurrent readers '
    'and a single writer to operate simultaneously, which is critical for a booking system where '
    'multiple passengers may be viewing seat maps and making reservations concurrently. The '
    'alternative \u2014 PostgreSQL or MySQL \u2014 would have added deployment complexity disproportionate '
    'to the project\'s scope.'
)
add_para(
    'Pillow (the Python Imaging Library fork) was used for e-ticket PNG generation. The library '
    'provides comprehensive support for drawing text, shapes, and images, allowing the generation '
    'of branded e-tickets with country flag colours, QR-style reference codes, VIP/standard '
    'badges, and detailed price breakdowns. xhtml2pdf complements this by converting HTML '
    'templates into PDF documents suitable for printing and email attachment. Both libraries '
    'were chosen because they work entirely offline without external API dependencies.'
)

add_heading('4.2 Frontend Technologies', level=3)
add_tool_table(
    ['Technology', 'Purpose'],
    [
        ['HTML5', 'Page structure with semantic elements'],
        ['CSS3', 'Styling, responsive design, animations, and media queries'],
        ['JavaScript (vanilla)', 'Client-side interactivity and AJAX seat map polling'],
        ['Jinja2', 'Server-side templating (Flask integrated, template inheritance)'],
        ['Font Awesome 6', 'Icon library for UI elements (nav, status, actions)'],
        ['CSS Flexbox/Grid', 'Layout management for responsive multi-column designs'],
    ]
)
add_para(
    'The frontend was built using vanilla HTML, CSS, and JavaScript without any framework dependencies. '
    'This deliberate choice ensured that the intern developed a thorough understanding of core web '
    'technologies rather than relying on framework abstractions. Jinja2, Flask\'s integrated templating '
    'engine, provides template inheritance through a base.html layout that all pages extend, ensuring '
    'consistent navigation, footer, and country-switching modal across the entire application.'
)
add_para(
    'Font Awesome provides the icon set used throughout the interface, including navigation icons, '
    'status indicators (checkmarks, warning signs, error symbols), and action buttons (edit, delete, '
    'print). CSS Flexbox and Grid are used for layout management, ensuring consistent spacing, '
    'alignment, and responsive behaviour across all device sizes without the need for a CSS framework '
    'like Bootstrap or Tailwind.'
)
add_para(
    'JavaScript handles client-side interactivity including the real-time seat map polling (AJAX '
    'requests every 30 seconds), form validation, country-switching modal interactions, hamburger '
    'menu animation, and dynamic DOM updates. All JavaScript is written in vanilla JS without jQuery '
    'or other libraries, keeping the frontend footprint minimal and loading times fast.'
)

add_heading('4.3 Development Tools', level=3)
add_tool_table(
    ['Tool', 'Purpose'],
    [
        ['VS Code', 'Code editor with Python, HTML, CSS, JS support'],
        ['Git', 'Version control and commit history tracking'],
        ['PowerShell', 'Command-line interface for script execution and testing'],
        ['Postman', 'API endpoint testing for AJAX and form submission routes'],
        ['DB Browser for SQLite', 'Database inspection and query verification'],
        ['Google Chrome DevTools', 'Responsive design testing, network monitoring, debugging'],
        ['Python venv', 'Virtual environment for dependency isolation'],
    ]
)
add_para(
    'The development environment was set up on Windows with Python 3.12. VS Code provided the '
    'integrated development environment with extensions for Python linting, Jinja2 template '
    'highlighting, and Git integration. Git was used for version control, with commits tracking '
    'the evolution from the initial single-country prototype through each major feature addition. '
    'The repository structure follows standard Flask conventions with a clear separation between '
    'static assets, templates, and application logic.'
)
add_para(
    'DB Browser for SQLite was invaluable for debugging database issues. It allowed direct inspection '
    'of table contents, verification of foreign key relationships, and manual execution of SQL queries '
    'during the JSON migration process. Chrome DevTools was used extensively for responsive design '
    'testing across all four breakpoints (1024px, 768px, 480px, 360px), network request monitoring '
    'for AJAX polling, and JavaScript console debugging.'
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
add_para(
    'The monolithic architecture was chosen deliberately for this project. At the current scale, '
    'a monolithic application is simpler to develop, deploy, and debug than a microservices '
    'architecture. All routes, database operations, and business logic reside in a single Python '
    'process, making the application straightforward to understand and modify. The three portals '
    'are separated at the route level rather than the service level: URLs starting with /agency/ '
    'are gated by agency authentication, /ministry/ URLs require ministry authentication, and '
    'all other routes serve the passenger-facing interface.'
)
add_para(
    'The shared services layer includes the translation engine, which loads language JSON files '
    'and provides the _() function used in every template, the country manager which maintains '
    'the configuration for all 54 countries including currencies, cities, and payment providers, '
    'the payment gateway router which selects appropriate payment options based on the booking\'s '
    'country, and the session/authentication manager which validates sessions on every request. '
    'The notification scheduler runs as a background daemon thread within the same process.'
)
add_para(
    'The data layer uses SQLite with WAL journal mode, enabling concurrent reads while a write '
    'is in progress. The database module (database.py) provides a context manager for database '
    'connections, ensuring every request gets a fresh connection and connections are properly '
    'closed after use. All booking-related operations use BEGIN IMMEDIATE transactions to prevent '
    'race conditions. The schema includes nine tables with foreign key constraints, unique indexes, '
    'and AUTOINCREMENT primary keys.'
)

add_para('', size=4)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
lines = [
    '\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510',
    '\u2502                        AFRI Trans                           \u2502',
    '\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524',
    '\u2502    Passenger App  \u2502  Agency Portal  \u2502  Ministry Portal      \u2502',
    '\u2502  \u2022 Search trips   \u2502  \u2022 Dashboard    \u2502  \u2022 Dashboard          \u2502',
    '\u2502  \u2022 Book tickets   \u2502  \u2022 Buses/Routes \u2502  \u2022 Agency Registry    \u2502',
    '\u2502  \u2022 Make payments  \u2502  \u2022 Schedules    \u2502  \u2022 Approvals          \u2502',
    '\u2502  \u2022 View tickets   \u2502  \u2022 Bookings     \u2502  \u2022 Statistics         \u2502',
    '\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524',
    '\u2502              Shared Services Layer                          \u2502',
    '\u2502   Translation Engine | Country Manager | Payment Gateway    \u2502',
    '\u2502   Session/Auth Manager | Notification Scheduler             \u2502',
    '\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524',
    '\u2502                     Data Layer (SQLite + WAL mode)           \u2502',
    '\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518',
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

add_para(
    'The request flow is designed to be stateless from the passenger\'s perspective. Each step in the '
    'booking process generates a unique identifier (schedule ID, booking ID) that is passed through '
    'URL parameters or stored in the session. This design allows passengers to bookmark intermediate '
    'steps, share booking links, and resume interrupted booking sessions without losing progress. '
    'The session is used to store the current country selection, language preference, and temporary '
    'booking state such as the selected seat number.'
)
add_para(
    'Flask\'s route decorators map URLs to Python functions. For example, the search route '
    '(@app.route(\'/search\', methods=[\'GET\'])) accepts query parameters (from, to, date), validates '
    'them, queries the database for matching schedules, and renders the search results template. '
    'AJAX endpoints like /api/seats/<sid>/status return JSON responses rather than HTML, allowing '
    'the frontend JavaScript to update the seat map without full page reloads. All routes that '
    'modify database state (bookings, registrations, payments) use POST methods to prevent '
    'accidental double-submissions from browser refreshes.'
)
add_para(
    'Session management follows Flask\'s default signed cookie-based sessions. When a passenger '
    'selects a country, the country code is stored in session[\'country\'] and persists across '
    'requests. Agency and ministry users get additional session keys (session[\'agency_id\'], '
    'session[\'ministry_country\']) that gate access to protected routes. Session validation '
    'occurs in a before_request handler that checks whether the current route requires '
    'authentication and redirects unauthenticated users to the login page.'
)

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
    ('agencies', 'Bus companies with country, locations, approval status, email, password reset. This table stores all registered transport agencies. Each agency is associated with a specific country, has a status (Pending, Approved, Rejected), and stores contact information including email, phone, and operating locations.'),
    ('buses', 'Vehicles owned by agencies (plate, capacity, bus_type, status). Each bus belongs to an agency through a foreign key and has attributes like registration plate, passenger capacity, bus type (Standard, VIP, Luxury), and operational status (Active, Inactive).'),
    ('routes', 'City pairs with pricing, duration, luggage configuration. Routes define the origin and destination cities, the base price, duration of travel, and luggage allowance. A route belongs to an agency and a country.'),
    ('schedules', 'Specific trips on a route (date, time, period, status). Schedules link a route to a bus on a specific date and time. They have a period (Morning, Afternoon, Night) and a status (Active, Cancelled, Completed).'),
    ('passengers', 'Normalised passenger records with UNIQUE(phone, id_number). This table stores deduplicated passenger information. The unique constraint on phone + ID number ensures that a passenger who books multiple times is stored once, with all bookings referencing the same passenger record.'),
    ('bookings', 'Ticket purchases with seat_number, booking_ref (UNIQUE), payment status. Each booking links a schedule to a passenger with a specific seat number, generates a unique booking reference, and tracks payment status (Pending, Confirmed, Cancelled).'),
    ('meta', 'Counters and migration tracking key-value store. This table stores system-level metadata including the booking reference counter (used by get_next_ref()) and migration flags that indicate whether the JSON-to-SQLite migration has been completed.'),
    ('agency_subscriptions', 'Commission exemption plans (plan, amount, start/end date). Agencies purchase subscriptions to skip the 1% platform commission. This table tracks the plan type (monthly, 6-month, annual), payment amount, and validity period.'),
    ('notification_log', 'Sent departure reminders (booking_id, notification_type, sent_at). This table logs all sent notifications to prevent duplicate reminders. Each entry records which booking was notified, the notification type (90_min, 45_min), and the timestamp.'),
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
add_para(
    'The schema was designed with several principles in mind. First, normalisation eliminates '
    'data redundancy \u2014 passenger details are stored once and referenced by multiple bookings, '
    'rather than duplicated across each booking record. Second, foreign key constraints with '
    'ON DELETE CASCADE ensure that deleting an agency automatically removes all associated buses, '
    'routes, schedules, and bookings, preventing orphan records. Third, unique indexes at the '
    'database level provide a last line of defence against race conditions that might bypass '
    'application-level checks.'
)
add_para(
    'The meta table serves an important but often overlooked role. It stores the booking reference '
    'counter used by the get_next_ref() function, which must atomically increment a counter and '
    'return the new value to generate unique booking references. The meta table also stores '
    'migration flags (migrated, generated) that make the JSON-to-SQLite migration idempotent \u2014 '
    'running the migration multiple times is safe because it checks these flags before proceeding.'
)
add_para(
    'Database connections are managed through a context manager pattern. The get_db() function '
    'returns a connection to the SQLite database with row_factory set to sqlite3.Row, enabling '
    'dictionary-style column access. Connections are stored in Flask\'s g object for per-request '
    'scoping and automatically closed at the end of each request via teardown_appcontext. All '
    'write operations that could be subject to race conditions use BEGIN IMMEDIATE transactions, '
    'which acquire a write lock at the start of the transaction rather than waiting until the '
    'first write statement.'
)

add_heading('6.2 Entity Relationship Diagram', level=3)
add_para(
    'The database follows a star-like schema with agencies at the centre:'
)
add_para('')
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
er_lines = [
    'Agencies   1 \u2500\u2500\u2500\u2500 * Buses',
    'Agencies   1 \u2500\u2500\u2500\u2500 * Routes',
    'Routes     1 \u2500\u2500\u2500\u2500 * Schedules',
    'Buses      1 \u2500\u2500\u2500\u2500 * Schedules',
    'Schedules  1 \u2500\u2500\u2500\u2500 * Bookings',
    'Passengers 1 \u2500\u2500\u2500\u2500 * Bookings',
    'Agencies   1 \u2500\u2500\u2500\u2500 * agency_subscriptions',
]
for line in er_lines:
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run(f'    {line}')
    r.font.name = 'Consolas'
    r.font.size = Pt(10)
    p2.paragraph_format.space_after = Pt(2)
    p2.paragraph_format.line_spacing = 1.0

add_para(
    'The relationships form a clear hierarchy. An agency owns multiple buses and routes. Each route '
    'can have multiple schedules (the same route operated on different dates/times). Each schedule '
    'is assigned to a specific bus and can have multiple bookings (one per seat). Passengers are '
    'stored independently and linked to bookings. Agency subscriptions stand alone but are tied '
    'to a specific agency. This structure efficiently answers common queries such as "which seats '
    'are taken on this schedule?" (join bookings with schedules) and "which passengers are on '
    'this departure?" (join bookings with passengers and schedules).'
)

add_heading('6.3 Migration from JSON to SQLite', level=3)
add_para(
    'The original implementation stored all data in a single data.json file, causing ID collisions '
    '(len(data["x"]) + 1 produced duplicates after deletion), data duplication (passenger details '
    'repeated across bookings), and orphan records. A migration function (migrate_from_json()) reads '
    'the JSON once and imports all data into the normalised SQLite structure using AUTOINCREMENT, '
    'proper foreign keys, and WAL journal mode. The migration is idempotent via a migrated flag in '
    'the meta table.'
)
add_para(
    'The migration process involved several steps. First, the JSON file was loaded and validated. '
    'Then, the SQLite schema was created or verified. Each entity type was migrated in dependency '
    'order: agencies first (no foreign keys), then buses and routes (depend on agencies), then '
    'schedules (depend on routes and buses), then passengers (independent), and finally bookings '
    '(depend on schedules and passengers). The agency_subscriptions and notification_log tables '
    'were created as new tables without JSON equivalents. During migration, passenger records were '
    'deduplicated using phone+ID number as the natural key, reducing 18 duplicated passenger '
    'entries in bookings down to 7 unique passenger records.'
)
add_para(
    'One of the key improvements was the introduction of AUTOINCREMENT for primary keys. The '
    'original JSON implementation used len(data["x"]) + 1 to generate IDs, which would produce '
    'duplicate IDs after any record was deleted. For example, if three agencies had IDs 1, 2, 3 '
    'and agency 2 was deleted, the next registration would generate len(2) + 1 = 3, colliding '
    'with the existing agency 3. AUTOINCREMENT in SQLite guarantees monotonically increasing, '
    'never-reused IDs regardless of deletions. This eliminated an entire class of data integrity '
    'bugs that had plagued the JSON implementation.'
)
add_para(
    'The migration is designed to be run once and is idempotent through a \'migrated\' flag stored '
    'in the meta table. If the migration has already been completed, the function returns immediately '
    'without modifying any data. This allows the application to safely check for and run the '
    'migration on every startup without risk of data loss. The WAL journal mode is enabled during '
    'migration setup and persists for all subsequent database operations, providing improved '
    'concurrency performance for the production application.'
)

add_page_break()

# ════════════════════════════════════════════
# CHAPTER V: FEATURES IMPLEMENTED
# ════════════════════════════════════════════
add_heading('7. Features Implemented', level=2)

# ── 7.1 Multi-Country Support ──
add_heading('7.1 Multi-Country Support', level=3)
add_para(
    'All 54 African countries are configured with: country name and flag colours (up to 6 colours), '
    'local currency and currency code, major cities (8\u201318 per country), default and supported languages, '
    'local payment providers, and VIP surcharge. Country-switching via a globe icon on the navbar '
    'auto-updates the language, currency, and available cities across the entire platform.'
)
add_para(
    'The country configuration is stored in a Python dictionary within app.py. Each entry defines the '
    'country\'s full name, ISO 3166-1 alpha-2 code, currency code and symbol, flag colours as hex values, '
    'major cities list, default language, supported languages array, available payment providers, and '
    'a VIP surcharge percentage. The configuration is loaded once at startup and accessed throughout '
    'the application via helper functions that take the country code as a parameter.'
)
add_para(
    'When a user selects a country through the globe icon modal, several things happen simultaneously '
    'on the server side. The country code is stored in the user\'s session under session[\'country\']. '
    'The default language for that country becomes the active language. The currency display updates '
    'across all templates. The search form dynamically loads cities for the selected country. Set '
    'payment providers become available during the booking flow. The flag colours are applied to '
    'the hero title on the homepage. This unified switching mechanism means the entire platform '
    'adapts to the selected country with a single user action.'
)
add_para(
    'The country modal displays all 54 countries in a scrollable grid, organised alphabetically with '
    'country names displayed in the current active language. Each country entry shows the country name '
    'and a flag placeholder. The modal can be closed by clicking outside its boundaries, pressing the '
    'Escape key, or clicking a close button. IP-based auto-detection is implemented as a best-effort '
    'feature \u2014 the system can optionally query a free IP geolocation API on first visit to pre-select '
    'the user\'s country, though this feature is configured to fall back gracefully if the API is '
    'unreachable.'
)
add_para(
    'The country system also controls regulatory workflows. Each country has a Ministry of Transport '
    'portal that is scoped to that specific country. The ministry email for each country is configured '
    'separately, and password recovery flows are country-specific. This means that the Ministry of '
    'Transport for Cameroon cannot access or modify data belonging to the Ministry of Transport for '
    'Kenya, preserving the sovereignty of each nation\'s regulatory authority.'
)

# ── 7.2 Internationalisation (11 Languages) ──
add_heading('7.2 Internationalisation (11 Languages)', level=3)
add_para(
    'The platform supports 11 languages with full UI translation: English, French, Arabic, Portuguese, '
    'Spanish, Swahili, Amharic, Somali, Tigrinya, Afrikaans, and Zulu. All UI text is wrapped in _{text} '
    'function calls. Each language has a JSON file with key-value pairs. Missing keys fall back gracefully '
    'to English. Language toggle is shown only when a country has 2+ supported languages.'
)
add_para(
    'The translation architecture is based on a simple but effective pattern. A function called _() '
    'accepts a text key (usually the English version of the string) and returns the translated version '
    'from the current language\'s JSON file. The language file is loaded once per request and cached '
    'for the duration of that request. If a key is not found in the current language file, the function '
    'falls back to the English key as the default, ensuring that no UI text ever appears as a blank '
    'or broken string. This fallback mechanism was critical during development when translations were '
    'being added incrementally.'
)
add_para(
    'Each language file contains approximately 434 to 682 key-value pairs, covering all UI strings '
    'in the application. The keys are organised by page or component area for maintainability. For '
    'example, keys related to the booking flow all start with \'booking_*\', keys related to the '
    'agency dashboard start with \'agency_*\', and so on. English serves as the source of truth '
    'and the reference against which other languages are maintained. When new UI text is added to '
    'the application, it first appears in English, and the generate_translations.py script can '
    'update all language files with placeholder entries for the new keys.'
)
add_para(
    'The language toggle appears as a dropdown or button in the navigation bar, but only when the '
    'currently selected country supports more than one language. For example, Cameroon supports '
    'English and French, so the language toggle is shown. Ethiopia supports Amharic, English, Somali, '
    'and Tigrinya, so the toggle shows all four options. For countries that only have one supported '
    'language (e.g., a hypothetical country configured with only English), the toggle is hidden '
    'to reduce UI clutter.'
)
add_para(
    'The 11 languages were chosen based on the linguistic landscape of Africa. English, French, '
    'Arabic, Portuguese, and Spanish cover the major colonial and international languages used in '
    'government, education, and commerce across the continent. Swahili, Amharic, Somali, Tigrinya, '
    'Afrikaans, and Zulu represent major indigenous languages with millions of speakers. Amharic '
    'uses the Ge\u2019ez script, Arabic uses the Arabic script, and the remaining languages use '
    'Latin-derived scripts. The translation system handles all scripts natively through Unicode, '
    'though right-to-left (RTL) support for Arabic was identified as a future improvement.'
)

# ── 7.3 Passenger Booking Flow ──
add_heading('7.3 Passenger Booking Flow', level=3)
add_para(
    'The booking process follows a clear step-by-step flow: Search (origin, destination, date) \u2192 '
    'Browse Results (grouped by period, showing agency, bus type, price, available seats) \u2192 '
    'Pick Seat (interactive seat map with VIP/standard styling) \u2192 Enter Details (name, phone, ID, '
    'optional luggage) \u2192 Payment (country-specific mobile money providers) \u2192 Ticket (HTML, PNG, PDF). '
    'Business rules include: booking closes 15 min before departure, trips auto-expire 2 hours after '
    'departure, bookings expire 30 min after departure, and rate limiting (10 attempts/15 min/IP) '
    'protects all login endpoints.'
)
add_para(
    'The search interface is the entry point for all passenger interactions. A large, prominent search '
    'form on the homepage presents three dropdowns: origin city, destination city, and travel date. '
    'The city lists are dynamically populated based on the currently selected country, showing only '
    'cities that have active routes. Date selection defaults to today and accepts both today and '
    'future dates. Past dates are greyed out and unselectable. The search form validates that origin '
    'and destination are different cities before submitting, providing immediate client-side feedback '
    'if the user selects the same city for both.'
)
add_para(
    'Search results are displayed in a structured layout grouped by time period (Morning, Afternoon, '
    'Night). Each trip card shows the agency name and logo, bus type (Standard, VIP, Luxury), departure '
    'and arrival times, journey duration, price displayed in the local currency, number of available '
    'seats, and a "View Seats" button that links to the seat selection page. Trips are sorted by '
    'departure time within each period. If no trips are found for the selected criteria, a helpful '
    'message suggests alternative dates or nearby cities.'
)
add_para(
    'The booking form collects passenger details after seat selection. Fields include full name, phone '
    'number (with country code validation), national ID or passport number (required for inter-country '
    'travel), optional luggage count (with fees if applicable), and contact email for ticket delivery. '
    'Form validation occurs both client-side (HTML5 validation attributes and JavaScript checks) and '
    'server-side. The server-side validation is the authoritative check, as it verifies that the seat '
    'is still available before creating the booking. If the seat was taken between the seat selection '
    'and the form submission (a window of up to 30 seconds), the server returns an error and prompts '
    'the user to select a different seat.'
)
add_para(
    'Several business rules govern the booking lifecycle. Bookings close 15 minutes before the scheduled '
    'departure time \u2014 the system checks this constraint when the passenger initially tries to book '
    'a seat. Trips that departed more than 2 hours ago are auto-expired and no longer appear in search '
    'results (unless the agency explicitly marks them as historical). Bookings with Pending payment '
    'status expire 30 minutes after departure, freeing the seat for other passengers. Rate limiting '
    'applies to all login and booking endpoints, preventing brute-force attacks and abuse of the booking '
    'system. These rules are enforced at the application level using database queries that compare '
    'current time against schedule departure times.'
)

# ── 7.4 Real-Time Seat Map ──
add_heading('7.4 Real-Time Seat Map', level=3)
add_para(
    'The seat selection page polls a lightweight JSON endpoint (GET /api/seats/<sid>/status) every '
    '30 seconds to detect seats taken by other passengers without page reload. JavaScript compares '
    'the new taken set against the previous snapshot. Newly taken seats are greyed out immediately. '
    'If the user\'s selected seat was taken by someone else, the selection is cleared and they must '
    'pick again. This replaces the previously static seat map with a real-time multi-user experience.'
)
add_para(
    'The seat map is rendered as a visual grid representing the bus interior. The layout includes '
    'a driver area at the front (depicted with a steering wheel icon), a door area (marked with '
    'a door icon), rows of seats arranged in a 2+2 or 2+3 configuration depending on the bus type, '
    'an emergency exit at the rear, and a toilet compartment for long-distance buses. Each seat '
    'is represented by a clickable square or rectangle with seat number labelling. Available seats '
    'are shown in blue, VIP seats in gold, taken seats in grey (with a passenger icon or an \'X\' '
    'marker), and the currently selected seat in green.'
)
add_para(
    'The JavaScript polling mechanism works as follows. When the seat page loads, the initial seat '
    'status is embedded in the HTML as a JavaScript variable (taken_seats array). The page then '
    'sets a setInterval() timer that fires every 30 seconds. Each tick sends an AJAX GET request '
    'to /api/seats/<sid>/status, which returns a JSON object: {"taken": ["A1", "B3", "C7", ...]}. '
    'The JavaScript compares this new array with the previous snapshot stored in memory. If new '
    'seats have been taken, those seat elements are updated to the greyed-out state. If the user\'s '
    'currently selected seat appears in the taken array (meaning another passenger booked it first), '
    'the selection is cleared, a flash message is displayed, and the seat colour returns to the '
    'available state. The polling interval of 30 seconds balances freshness with server load \u2014 '
    'shorter intervals could overload the server during peak traffic, while longer intervals would '
    'increase the chance of two passengers selecting the same seat.'
)
add_para(
    'The polling endpoint is optimised for performance. It queries only the bookings table filtered '
    'by schedule_id, selecting seat numbers where payment status is Confirmed or Pending. The query '
    'is a simple SELECT seat_number FROM bookings WHERE schedule_id = ? AND payment_status IN '
    '(\'Confirmed\', \'Pending\'). The result is a flat list of seat numbers serialised to JSON. '
    'No joins, aggregations, or complex processing is required. This keeps response times under '
    '5 milliseconds even under load. The endpoint is also cache-friendly \u2014 though not currently '
    'cached, it could easily be fronted by Redis or Memcached in a production deployment.'
)
add_para(
    'The design decision to use polling rather than WebSockets was pragmatic. WebSockets require '
    'a persistent connection between client and server, which adds deployment complexity (async '
    'server, connection lifecycle management, reconnection logic). Polling with AJAX works with '
    'any WSGI server, requires no additional infrastructure, and is well-understood by the intern. '
    'A 30-second polling interval provides an acceptable user experience \u2014 the typical booking '
    'flow takes 2\u20135 minutes, so the seat map updates 4\u201310 times during a typical session. '
    'Future improvements could replace polling with WebSockets for instant updates, but the current '
    'implementation meets the requirements without unnecessary complexity.'
)

# ── 7.5 Agency Portal ──
add_heading('7.5 Agency Portal', level=3)
add_para(
    'Agencies have a dedicated dashboard for managing operations: overview of buses, routes, upcoming '
    'schedules, and booking counts; approval/rejection status banners; bus management (add, toggle '
    'availability); route definition (city pairs, duration, pricing, luggage); schedule creation by '
    'assigning routes to buses on specific dates/times; booking view and cancellation; and passenger '
    'manifest generation. Registration creates an approved: False account, invisible to passengers '
    'until Ministry approval.'
)
add_para(
    'The agency dashboard is the first page an agency user sees after logging in. It displays a '
    'summary of key metrics: total buses registered, total routes defined, upcoming schedules (next '
    '7 days), total bookings (current month), and estimated revenue. If the agency is not yet approved '
    'by the Ministry of Transport, a prominent yellow banner at the top of the dashboard informs the '
    'agency that their account is pending approval and that their services will not appear in passenger '
    'search results until approved. For approved agencies, the dashboard shows a green confirmation '
    'badge. An additional badge indicates subscription status \u2014 active subscriptions display a '
    '"Commission Exempt" badge with the expiry date.'
)
add_para(
    'The bus management interface allows agencies to register their fleet. Each bus entry requires '
    'the registration plate number, passenger capacity, bus type (Standard, VIP, Luxury), and '
    'operational status (Active, Inactive). Buses can be toggled between Active and Inactive status \u2014 '
    'an inactive bus cannot be assigned to new schedules but retains its history. The route management '
    'interface lets agencies define city pairs they operate. For each route, the agency specifies '
    'the origin and destination cities, base price, estimated duration, and luggage allowance '
    '(number of pieces included, excess luggage fee per piece). Routes are scoped to the agency\'s '
    'country and can only use cities within that country.'
)
add_para(
    'Schedule management is the core operational tool for agencies. To create a schedule, the agency '
    'selects a route, an available bus, a date, and a departure time. The system validates that the '
    'selected bus is not already scheduled for the same date and time (preventing double-booking of '
    'vehicles). Schedules can be created in batches \u2014 for example, setting a repeating schedule '
    'for every Monday, Wednesday, and Friday over the next month. Once created, schedules appear in '
    'passenger search results (for approved agencies) and can be managed from the dashboard: view '
    'booking counts, mark as cancelled, or archive completed departures.'
)
add_para(
    'The passenger manifest feature generates a consolidated view of all passengers booked on a '
    'specific schedule. The manifest displays each passenger\'s name, seat number, phone number, '
    'ID number, and booking reference. This manifest can be printed or exported for use at the '
    'terminal during boarding. The manifest is also used by the background notification scheduler '
    'to identify which passengers need departure reminders. Agency privacy is enforced at every '
    'level \u2014 an agency can only see manifests for its own schedules, never those of competing '
    'agencies.'
)

# ── 7.6 Ministry of Transport Portal ──
add_heading('7.6 Ministry of Transport Portal', level=3)
add_para(
    'Each country has a scoped Ministry portal with country-scoped authentication (selected via globe '
    'menu). Features include: dashboard statistics (total agencies, pending approvals, buses, routes, '
    'schedules, bookings, revenue); agency registry with status badges (Approved green, PENDING orange, '
    'Rejected red); approve/reject actions with reason modals; and cross-agency booking records.'
)
add_para(
    'The Ministry portal is accessed via /ministry/login and is scoped to a specific country. The '
    'ministry user selects their country through the globe modal (the same mechanism used by passengers), '
    'and the login page authenticates them against the ministry credentials for that country. Unlike '
    'the original implementation that used a single shared password for all countries, each country\'s '
    'ministry portal has its own email and password, stored in the application configuration. The '
    'initial password "Admin123" is flagged as a one-time password and permanently invalidated after '
    'the first login \u2014 the ministry user is immediately prompted to set a new password.'
)
add_para(
    'The Ministry dashboard provides a statistical overview of the country\'s bus transport ecosystem. '
    'Widgets display: total registered agencies, number of pending registrations requiring action, '
    'total buses across all agencies, total active routes, upcoming schedules (next 7 days), total '
    'bookings (current month), and estimated total revenue. These statistics are aggregated across '
    'all agencies in the country and are updated in real-time by querying the database on each page '
    'load. The dashboard provides a high-level view that allows ministry officials to monitor the '
    'health of the transport sector at a glance.'
)
add_para(
    'The agency registry is the centrepiece of the Ministry portal. It lists all agencies registered '
    'in the country in a table format with columns: agency name, contact email, phone, operating '
    'locations, registration date, and status. Status is displayed as a colour-coded badge: green '
    'for Approved, orange for PENDING, red for Rejected. Clicking on an agency opens a detail view '
    'showing all information plus buses, routes, and recent bookings. Ministry officials can approve '
    'or reject pending agencies using dedicated buttons. Rejection opens a modal where the official '
    'must enter a reason, which is stored and communicated to the agency. This approval workflow '
    'ensures that only vetted, legitimate agencies can access the passenger marketplace.'
)

# Screenshots
add_para('', size=4)
add_para('Figure 1: Ministry of Transport Dashboard', italic=True, size=9, color='666666', align=WD_ALIGN_PARAGRAPH.CENTER)

# ── 7.7 Subscription Monetisation ──
add_heading('7.7 Subscription Monetisation', level=3)
add_para(
    'Agencies can prepay to skip the 1% platform commission for a defined period. Three plans are '
    'available: Monthly (58,000 FCFA / 15,000 NGN), 6-Month (250,000 FCFA / 75,000 NGN), and Annual '
    '(500,000 FCFA / 150,000 NGN). The flow: Agency clicks Subscription button on dashboard \u2192 chooses '
    'a plan \u2192 /agency/subscribe/pay (selects payment provider + phone) \u2192 POST to '
    '/agency/subscribe/confirm \u2192 subscription activated or extended. If the agency already has an '
    'active subscription, the page shows "Extend Your Subscription" with the current expiry date and '
    'lets them add more time (days added to end_date via extend_subscription()). On the passenger '
    'payment page, the 1% commission breakdown is hidden \u2014 passengers see only the total price.'
)
add_para(
    'The subscription model was designed to give agencies flexibility while providing the platform '
    'with a recurring revenue stream. Monthly plans suit small agencies with variable cash flow. '
    '6-month and annual plans offer discounts (the annual plan costs roughly 8.6 months at the '
    'monthly rate, giving a 28% discount) and lock agencies into longer commitments. The pricing '
    'is presented in dual currencies: FCFA for Central and West African CFA Franc countries, and '
    'NGN for Nigeria. When the platform expands to other currency zones, additional price entries '
    'can be added.'
)
add_para(
    'The subscription flow is straightforward from the user\'s perspective. On the agency dashboard, '
    'a "Subscription" button (or badge) directs the agency to the subscription page. If the agency '
    'has no active subscription, it shows the three plan options with prices and features. If the '
    'agency has an active subscription, it shows a "Your current subscription expires on [date]" '
    'message with an option to extend. The agency selects a plan and clicks "Subscribe Now", which '
    'takes them to /agency/subscribe/pay where they choose their preferred payment provider (from '
    'the country\'s available options) and enter their phone number. Submitting the payment form '
    '(POST to /agency/subscribe/confirm) simulates a payment confirmation and activates the '
    'subscription.'
)
add_para(
    'Activating a subscription calls extend_subscription() in the database module. This function '
    'first checks if the agency already has an active subscription (where end_date >= today). If '
    'an active subscription exists, the new plan\'s duration is added to the existing end_date, '
    'effectively stacking the new subscription on top of the current one. If no active subscription '
    'exists, a new subscription is created starting from today. This stacking approach allows '
    'agencies to purchase multiple plans and accumulate coverage, similar to how mobile phone '
    'credit plans can be stacked.'
)
add_para(
    'On the passenger payment page, the commission handling is completely transparent. The server '
    'checks whether the booking\'s agency has an active subscription. If yes, the 1% commission is '
    'skipped server-side and the passenger sees only the base ticket price. If no, the commission '
    'is still charged but never displayed as a separate line item to the passenger. The commission '
    'rate (1%) is shown as an informational badge on certain pages, but the specific amount in '
    'currency is never revealed. This design was intentional to keep the checkout experience clean '
    'and avoid confusing passengers with fee breakdowns.'
)

# ── 7.8 Departure Notification Scheduler ──
add_heading('7.8 Departure Notification Scheduler', level=3)
add_para(
    'A background daemon thread runs every 60 seconds and checks for confirmed bookings where departure '
    'is exactly 90 minutes or 45 minutes away. For each qualifying booking, it checks the notification_log '
    'table to avoid duplicates, formats a reminder message, and attempts to send via priority chain: '
    'WhatsApp Cloud API (free tier, 1,000 conversations/month, no credit card needed) \u2192 USB GSM Modem '
    'via serial AT commands (one-time ~$20 hardware, free SMS via SIM bundle) \u2192 Twilio SMS API (paid) \u2192 '
    'console log (always works, no config). All tiers are dormant until configured \u2014 zero resource usage '
    'when unconfigured.'
)
add_para(
    'The notification scheduler is implemented as a Python threading.Thread that runs as a daemon '
    'thread. Daemon threads automatically terminate when the main process exits, ensuring clean '
    'shutdown without manual thread management. The scheduler loop works as follows: it sleeps for '
    '60 seconds, then upon waking queries the database for bookings that match the notification '
    'criteria (departure time 90 minutes or 45 minutes from now, payment confirmed, not yet notified '
    'for this time window). For each matching booking, it calls the send_notification() function '
    'and records the attempt in the notification_log table. Any errors during sending are caught '
    'and logged without crashing the scheduler.'
)
add_para(
    'The scheduler uses the notification_log table to ensure passengers do not receive duplicate '
    'reminders. Before sending a notification, it checks whether a log entry already exists for '
    'the given booking_id and notification_type (90_min or 45_min). If an entry exists, the '
    'notification is skipped. This check is important because the scheduler runs every 60 seconds, '
    'and a qualifying booking may match the criteria for multiple consecutive checks (if it is '
    'within the 90-minute window for several minutes). Without the deduplication check, passengers '
    'would receive repeated reminders every minute.'
)
add_para(
    'The four-tier delivery chain is designed to provide free or low-cost notification delivery '
    'with graceful degradation. Tier 1 (WhatsApp Cloud API) is the preferred channel because Meta\'s '
    'free tier offers 1,000 conversations per month at no cost and requires no credit card \u2014 only '
    'a Meta Developer account. Tier 2 (USB GSM Modem) involves a one-time hardware purchase of '
    'approximately $20 for a USB dongle that accepts a standard SIM card. SMS messages sent through '
    'the SIM\'s SMS bundle are effectively free if the SIM has an active plan. Tier 3 (Twilio SMS) '
    'is a paid fallback with per-message pricing, used when no other channel is available. Tier 4 '
    '(console logging) always works and requires no configuration at all, making it ideal for '
    'development environments.'
)
add_para(
    'All four tiers are dormant until explicitly configured through environment variables. If '
    'WHATSAPP_TOKEN is not set, the WhatsApp tier is skipped silently. If GSM_MODEM_PORT is not set, '
    'the modem tier is skipped. If TWILIO_SID, TWILIO_TOKEN, and TWILIO_FROM are not set, the '
    'Twilio tier is skipped. The console log tier has no configuration requirement and always writes '
    'to stdout. This design ensures zero resource consumption for unconfigured channels \u2014 no '
    'connections are opened, no memory is allocated, and no CPU time is spent on channels that '
    'are not in use.'
)

# ── 7.9 E-Ticket Generation ──
add_heading('7.9 E-Ticket Generation', level=3)
add_para(
    'Tickets are generated in three formats: HTML Ticket (styled web page with flag colours), '
    'PNG Image (rendered with Pillow featuring country flag colours, QR-style reference, route info, '
    'VIP/standard badge, price breakdown), and PDF Document (via xhtml2pdf suitable for printing/email).'
)
add_para(
    'The HTML ticket is rendered by a Jinja2 template (/ticket/<ref>) that displays all booking '
    'information in a clean, print-friendly layout. It includes the agency name, bus type, departure '
    'and arrival details, passenger information, seat number, booking reference, price breakdown, '
    'and a colour scheme based on the country\'s flag colours. The HTML ticket serves as the primary '
    'digital format viewable in any browser and includes a "Download PDF" button and a "Download '
    'Image" button for the other two formats.'
)
add_para(
    'The PNG ticket image is generated server-side using Pillow when the user visits /ticket/<ref>/image. '
    'The generation process creates a canvas with dimensions approximately 800x500 pixels. The '
    'background is filled with the country\'s flag colours in a subtle gradient or stripe pattern. '
    'Text elements are drawn using Pillow\'s ImageDraw module: the agency name in bold at the top, '
    'a large booking reference number styled to resemble a QR code, departure and arrival cities '
    'with times, passenger name and seat number, a VIP or Standard badge, and the price. The image '
    'is served as a PNG file directly in the browser response.'
)
add_para(
    'The PDF ticket is generated using xhtml2pdf via /ticket/<ref>/pdf. xhtml2pdf converts an HTML '
    'template into a PDF document, preserving CSS styling. The PDF template is designed for A4 '
    'printing with appropriate margins, fonts, and layout. It includes all the information from '
    'the HTML ticket but in a format suitable for email attachment, printing at the terminal, or '
    'saving to a mobile device. The PDF generation handles page breaks correctly and produces '
    'consistent output across different platforms.'
)
add_para(
    'All three ticket formats share a common data source \u2014 the booking, schedule, route, agency, '
    'bus, and passenger records are queried from the database and passed to each template. This '
    'ensures consistency across formats. The ticket page also includes the booking reference, '
    'which passengers can use to look up or modify their booking. QR code generation for the '
    'ticket reference was considered but deferred to a future improvement, as the QR-style '
    'reference text in Pillow provides a visual approximation without requiring a QR library.'
)

# ── 7.10 Commission System ──
add_heading('7.10 Commission System', level=3)
add_para(
    'The platform charges a 1% commission on every booking. The commission amount in currency is never '
    'displayed in any UI \u2014 only the rate (1%) is shown as an informational badge. Commission is '
    'automatically skipped when the booking\'s agency has an active subscription.'
)
add_para(
    'The commission is calculated server-side during the booking confirmation process. When a booking '
    'is created, the system calculates the total price based on the route\'s base price plus any '
    'applicable VIP surcharge or excess luggage fees. The commission amount (1% of the total) is '
    'computed and stored in the booking record for accounting purposes. However, this amount is '
    'never exposed to the passenger through any UI element. The passenger always sees the total '
    'price as a single figure without breakdown.'
)
add_para(
    'The commission skip logic integrates with the subscription system. When confirming a booking, '
    'the system queries the agency_subscriptions table to check if the booking\'s agency has an '
    'active subscription covering the booking date. If a valid subscription exists, the commission '
    'field is set to zero. The calculation happens transparently \u2014 the agency does not need to '
    'take any action beyond maintaining an active subscription. This design was chosen to make the '
    'subscription benefit automatic and frictionless, encouraging agencies to maintain continuous '
    'coverage rather than subscribing intermittently.'
)

# ── 7.11 Flash Alert Categories ──
add_heading('7.11 Flash Alert Categories', level=3)
add_para(
    'Flash messages use three colour-coded categories: success (green, #e8f5e9) for positive feedback, '
    'error (red, #ffebee) for failures, and warning (orange, #fff8e1) for informational alerts. All '
    '100+ flash() calls in the application were updated. CSS classes .flash-success, .flash-error, '
    '.flash-warning style the corresponding alerts via with_categories=true in the base template.'
)
add_para(
    'Previously, all flash messages used the same default styling, making it difficult for users '
    'to distinguish between informational messages, successful operations, and error conditions. '
    'The categorisation project involved auditing all flash() calls in the application and assigning '
    'each to one of three categories. Success messages are used for operations that completed as '
    'expected (booking confirmed, registration successful, payment processed). Error messages are '
    'used for failures (seat already taken, invalid credentials, insufficient funds). Warning messages '
    'are used for informational states (pending approval, subscription expiring soon, rate limit '
    'approached).'
)
add_para(
    'The implementation uses Flask\'s flash() function with the category parameter: '
    'flash("message", "success"), flash("message", "error"), flash("message", "warning"). '
    'The base.html template iterates over get_flashed_messages(with_categories=true) and renders '
    'each message inside a div with the appropriate CSS class. The CSS classes provide distinct '
    'visual styling: green background with a checkmark icon for success, red background with an '
    'X icon for error, orange background with an info icon for warning. Each message type also '
    'has a close button (X in the top-right corner) that dismisses the message via JavaScript.'
)

# ── 7.12 Flag-Coloured Hero Title ──
add_heading('7.12 Flag-Coloured Hero Title', level=3)
add_para(
    'The hero heading on the index page colours each word using the country\'s flag colours. For '
    'Cameroon (green #007a5e, red #ce1126, yellow #fcd116), "Book" appears green, "Your" red, '
    '"Journey" yellow, "Across" green, "Cameroon" red. Colours cycle through the flag_colors array '
    'defined per country, falling back gracefully for countries with fewer colours.'
)
add_para(
    'The flag-coloured hero title is implemented in the Jinja2 template for the homepage. The '
    'template receives the country\'s flag_colors array from the server-side country configuration. '
    'The hero text (e.g., "Book Your Journey Across [Country]") is split into individual words. '
    'Each word is wrapped in a <span> tag with an inline colour style that cycles through the '
    'flag_colors array. If a country has fewer flag colours than there are words, the colours '
    'wrap around to the beginning. For example, Kenya has three flag colours (black, red, green) '
    'and the hero has five words, so the sequence would be: word 1 = black, word 2 = red, word '
    '3 = green, word 4 = black, word 5 = red.'
)
add_para(
    'This design was chosen to create an immediate visual connection between the platform and the '
    'selected country. When a user switches countries, the hero title dynamically updates not just '
    'the country name but also the colour scheme. This provides a subtle but effective branding '
    'cue that reinforces the country-specific experience. The fallback behaviour ensures that the '
    'feature works for all countries regardless of how many flag colours are defined in the '
    'configuration.'
)

# ── 7.13 Responsive Design ──
add_heading('7.13 Responsive Design', level=3)
add_para(
    'The interface is fully responsive with four breakpoints: 1024px (tablet), 768px (mobile), '
    '480px (small phone), and 360px (very small). Features include hamburger navigation with smooth '
    'animation and click-outside-to-close, scrollable tables, fluid typography using clamp(), seat '
    'layout scaling (30px max-width on mobile), and grid systems that collapse progressively.'
)
add_para(
    'The responsive design uses CSS media queries with mobile-first principles. The base styles '
    'are optimised for mobile screens, and progressively enhanced for larger viewports. The '
    'hamburger navigation menu appears on screens smaller than 768px, replacing the horizontal '
    'navigation bar. The hamburger icon uses smooth CSS transitions for opening and closing, '
    'and JavaScript handles click-outside-to-close behaviour to improve the mobile user experience. '
    'The menu overlay covers the full screen height and displays navigation links in a vertical '
    'stack with large touch targets.'
)
add_para(
    'Tables throughout the application (search results, agency listings, booking manifests) use '
    'horizontal scrolling on small screens rather than shrinking font sizes or truncating content. '
    'This ensures that all table data remains readable without horizontal text overflow. The '
    'scroll behaviour is implemented with CSS overflow-x: auto on a wrapper div, and the scroll '
    'indicator (faint gradient at the edge) signals to users that more content is available. '
    'The seat layout on mobile devices scales down with a maximum seat width of 30px on the '
    'smallest screens, ensuring the entire bus diagram remains visible without horizontal scrolling.'
)
add_para(
    'Fluid typography uses the CSS clamp() function to scale font sizes smoothly between '
    'viewport breakpoints. For example, heading font sizes may be defined as '
    'clamp(1.2rem, 2.5vw, 1.8rem), ensuring readability on both small and large screens '
    'without manual breakpoints for every element. The grid-based layouts (search results, '
    'dashboard widgets, country grid) use CSS Grid with auto-fill and auto-fit to collapse '
    'columns progressively as viewport width decreases, typically going from 4 columns on '
    'desktop to 3 on tablet to 2 on large mobile to 1 on small mobile.'
)

# ── 7.14 Security and Concurrency Hardening ──
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
add_para(
    'Rate limiting is implemented using an in-memory dictionary that tracks the number of login '
    'attempts per IP address within a sliding 15-minute window. When a login attempt fails, the '
    'counter for that IP is incremented. If the counter exceeds 10 within the window, subsequent '
    'attempts are rejected with a "Too many attempts. Please try again later." message. The window '
    'slides by removing entries older than 15 minutes on each check. This mechanism protects against '
    'brute-force password guessing attacks without requiring external dependencies like Redis. '
    'The in-memory approach is appropriate for a single-process application; a distributed deployment '
    'would need a shared store.'
)
add_para(
    'The one-time shared password mechanism addressed a critical security weakness. Originally, all '
    'ministry portals used the same hardcoded password "Admin123". This was acceptable only as a '
    'temporary measure for initial access. The implementation stores a flag in the meta table '
    'indicating whether the password has been changed from its default. On first login with "Admin123", '
    'the system forces a password change before granting access. After the password is changed, '
    '"Admin123" is permanently invalidated and cannot be used to authenticate again. Each country\'s '
    'ministry portal has its own password, stored separately in the application configuration.'
)
add_para(
    'Session validation is performed on every authenticated request through a Flask before_request '
    'handler. For routes under /agency/, the handler checks session.get(\'agency_id\'). If it is '
    'missing, the user is redirected to the agency login page. For routes under /ministry/, it '
    'checks session.get(\'ministry_country\'). The handler also validates that the agency or '
    'ministry session is still valid by querying the database \u2014 if an agency has been deleted '
    'while its session cookie remains valid, the next request will detect the deletion and '
    'clear the session, redirecting to login. This prevents stale sessions from accessing protected '
    'resources after account deletion.'
)
add_para(
    'The concurrency hardening measures are described in detail in Chapter 9 (Challenges and Solutions). '
    'In summary, all critical database operations that could suffer from race conditions are '
    'protected by a combination of application-level transaction management (BEGIN IMMEDIATE) and '
    'database-level constraints (UNIQUE indexes). The dual-layer approach ensures that even if the '
    'application logic has a flaw, the database constraint provides a backstop. This defence-in-depth '
    'strategy was essential for a booking system where race conditions could lead to real-world '
    'consequences such as double-booked seats or duplicate agency registrations.'
)

# Insert screenshots section
add_para('', size=6)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('\u2500\u2500\u2500 Screenshots \u2500\u2500\u2500')
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = RGBColor(0x1a, 0x3c, 0x6e)

screenshots = [
    ('image2.png', 'Figure 2: Homepage with search form allowing passengers to find trips by origin, destination and date. The flag-coloured hero title adapts to the selected country.'),
    ('image7.png', 'Figure 3: Search results showing available trips grouped by period with pricing, seat availability, and agency details for each schedule.'),
    ('image8.png', 'Figure 4: Bus seat selection layout with VIP (gold) and standard (blue) colour coding, driver area, doors, emergency exit and toilet markers. Available seats are clickable.'),
    ('image3.png', 'Figure 5: E-ticket generated after successful booking showing route, passenger details, seat number, pricing, and the booking reference.'),
    ('image5.png', 'Figure 6: Agency dashboard with revenue breakdown by route, recent bookings, operational stats, and the subscription status badge.'),
    ('image6.png', 'Figure 7: Agencies listing page displaying all registered transport companies in the selected country with approval status badges.'),
    ('image4.png', 'Figure 8: Country selection modal listing all 54 African countries organised alphabetically with IP-based auto-detection support.'),
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
    '\u251c\u2500\u2500\u2500 app.py                  # Main Flask application (routes, config, scheduler)',
    '\u251c\u2500\u2500\u2500 database.py             # SQLite database module (schema, CRUD, migration)',
    '\u251c\u2500\u2500\u2500 data.conf               # Original JSON storage (migrated to SQLite)',
    '\u251c\u2500\u2500\u2500 data                    # SQLite database (created by migration)',
    '\u251c\u2500\u2500\u2500 .env                    # Environment variables (TWILIO, WHATSAPP, MAIL)',
    '\u251c\u2500\u2500\u2500 .gitignore              # Version control exclusions',
    '\u251c\u2500\u2500\u2500 generate_translations   # Script to generate translation files',
    '\u2502',
    '\u251c\u2500\u2500\u2500 static/',
    '\u2502   \u251c\u2500\u2500\u2500 style.css           # All site CSS (responsive, layout, components)',
    '\u2502   \u2514\u2500\u2500\u2500 img/                # Flag images and logo',
    '\u2502',
    '\u251c\u2500\u2500\u2500 templates/',
    '\u2502   \u251c\u2500\u2500\u2500 base.html           # Base template (nav, footer, country modal)',
    '\u2502   \u251c\u2500\u2500\u2500 index.html          # Homepage with flag-coloured hero',
    '\u2502   \u251c\u2500\u2500\u2500 search.html         # Trip search results',
    '\u2502   \u251c\u2500\u2500\u2500 pick_seat.html      # Seat selection with live polling',
    '\u2502   \u251c\u2500\u2500\u2500 book.html           # Booking form',
    '\u2502   \u251c\u2500\u2500\u2500 payment.html        # Payment page (no commission breakdown)',
    '\u2502   \u251c\u2500\u2500\u2500 ticket.html         # E-ticket display',
    '\u2502   \u251c\u2500\u2500\u2500 agency_dashboard    # Agency dashboard with subscription badge',
    '\u2502   \u251c\u2500\u2500\u2500 agency_subscribe    # Subscription plan selection and payment',
    '\u2502   \u251c\u2500\u2500\u2500 ministry_dashboard  # Ministry oversight dashboard',
    '\u2502   \u2514\u2500\u2500\u2500 partials/           # AJAX-loaded template fragments',
    '\u2502',
    '\u2514\u2500\u2500\u2500 translations/           # 11 language JSON files (434\u2013682 keys each)',
]
for line in structure:
    p = doc.add_paragraph()
    r = p.add_run(f'    {line}')
    r.font.name = 'Consolas'
    r.font.size = Pt(8)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0

add_para(
    'The project structure follows Flask conventions with a clear separation of concerns. The '
    'main application file (app.py) contains all route definitions, configuration, and the '
    'notification scheduler. At approximately 1,200 lines, it is the largest file in the project. '
    'The database module (database.py) handles all SQLite operations including schema creation '
    '(init_db()), CRUD operations for each entity, and the JSON-to-SQLite migration function '
    '(migrate_from_json()). It is approximately 600 lines.'
)
add_para(
    'The templates directory contains 11 Jinja2 template files plus a partials subdirectory for '
    'AJAX-loaded template fragments. The base.html template defines the common layout: navigation '
    'bar with country selector and language toggle, flash message container, main content block, '
    'and footer. All other templates extend base.html using Jinja2\'s template inheritance. This '
    'approach ensures consistent styling and behaviour across all pages while allowing each page '
    'to define its own content block.'
)
add_para(
    'The static directory contains style.css (approximately 800 lines of CSS) and an img subdirectory '
    'for flag images and logos. The CSS is organised into sections: base styles (typography, colours), '
    'layout (grid, flexbox), components (navigation, buttons, forms, tables, modals), seat map, '
    'responsive breakpoints, and utility classes. No CSS framework is used \u2014 all styles are '
    'hand-written for full control and minimal file size.'
)
add_para(
    'The translations directory contains 11 JSON files, one per supported language. Each file shares '
    'the same key structure, with values in the target language. The English file (en.json) serves as '
    'the source of truth and is the most complete. Other languages may have missing keys, which are '
    'handled by the _() function\'s fallback mechanism. The generate_translations.py script reads '
    'en.json and can create or update other language files with placeholder entries for missing keys, '
    'flagging them for human translation.'
)

add_heading('8.2 Key Code Patterns', level=3)

add_para('Translation Wrapper:', bold=True)
add_para(
    'All UI text is wrapped in the _() function which loads the current language\'s JSON translation '
    'file and falls back to English for any missing key. This ensures no UI breaks even when '
    'translations are incomplete for a given language. The function caches the loaded translation '
    'dictionary in a global variable for the duration of the request, avoiding repeated file I/O '
    'for multiple _() calls on the same page. The cache is cleared at the start of each request.'
)
add_para(
    'The _() function is made available to all Jinja2 templates by adding it to the template globals '
    'during Flask application initialisation: app.jinja_env.globals[\'_\'] = _. This allows templates '
    'to call _("Booking Confirmed") directly without importing or defining the function in each '
    'template. The same function is also used in Python code for flash messages and other server-side '
    'strings that need translation, ensuring consistency between server and client text.'
)

add_para('Notification Sending Priority Chain:', bold=True)
code_lines = [
    'send_notification(phone, message, country_code):',
    '    1. send_whatsapp() \u2014 WhatsApp Cloud API if WHATSAPP_TOKEN set',
    '    2. send_sms_via_modem() \u2014 USB GSM modem if GSM_MODEM_PORT set',
    '    3. send_sms() \u2014 Twilio if TWILIO_SID, _TOKEN, _FROM set',
    '    4. Console log \u2014 always works, no configuration required',
]
for line in code_lines:
    p = doc.add_paragraph()
    r = p.add_run(f'    {line}')
    r.font.name = 'Consolas'
    r.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0

add_para(
    'Each sending function in the chain checks whether its required configuration variables are '
    'present before attempting to send. For example, send_whatsapp() checks if WHATSAPP_TOKEN and '
    'WHATSAPP_PHONE_NUMBER_ID environment variables are set. If they are missing, the function '
    'returns False immediately without attempting any API call. If they are present, it makes an '
    'HTTP POST request to the WhatsApp Cloud API endpoint. If the API call fails (e.g., network '
    'error, rate limit), the function also returns False, allowing the chain to fall through to '
    'the next tier. This failover pattern ensures maximum delivery probability.'
)

add_para('Atomic Registration Pattern:', bold=True)
add_para(
    'The add_agency() function opens a BEGIN IMMEDIATE transaction, performs both name+country '
    'and email uniqueness checks inside the transaction, and inserts the record. A UNIQUE INDEX '
    'at the database level provides the last line of defence. IntegrityError is caught and returned '
    'as a friendly (id, error) tuple instead of crashing.'
)
add_para(
    'The atomic registration pattern is implemented in the database module. The function signature '
    'is add_agency(data) -> (agency_id, None) on success or (None, error_message) on failure. '
    'The caller in app.py checks whether the first return value is None (indicating error) and, '
    'if so, displays the error message as a flash message. If the registration succeeds, the '
    'agency ID is returned and used to establish a session. This pattern is used throughout the '
    'application for operations that could fail due to database constraints.'
)

add_para('Subscription Extension Pattern:', bold=True)
add_para(
    'extend_subscription() checks for an existing active subscription: if found, it adds the new '
    'plan\'s duration to the existing end_date; otherwise it creates a new subscription starting '
    'from today. This allows agencies to stack multiple plan purchases. The duration mapping is '
    'defined as a dictionary: {"monthly": 30, "6-month": 180, "annual": 365}. The function adds '
    'the appropriate number of days to the end date (either existing or today).'
)

add_para('Database Connection Context Manager:', bold=True)
add_para(
    'Database connections are managed through a context manager pattern. The get_db() function '
    'returns a connection to the SQLite database with row_factory set to sqlite3.Row. Connections '
    'are stored in Flask\'s g object for per-request scoping. The close_db() function, registered '
    'with app.teardown_appcontext, closes the connection at the end of each request. This ensures '
    'that connections are never left open and that each request gets a fresh, clean connection. '
    'WAL journal mode is enabled once during database initialisation and persists for the lifetime '
    'of the database file.'
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
     'len(data["x"]) + 1 produced collisions after deletions. Deleting an agency left orphan records '
     'that could not be cleaned up because there was no referential integrity enforcement.\n\n'
     'Solution: Migrated to a normalised SQLite schema with 9 tables, AUTOINCREMENT for collision-free '
     'IDs, ON DELETE CASCADE for referential integrity, WAL journal mode for concurrent writes, and a '
     'UNIQUE constraint on passenger(phone, id_number) to eliminate duplication. The migration function '
     'was carefully designed to preserve all existing data while restructuring it into the normalised '
     'format. Passenger deduplication alone reduced the passenger count from 18 duplicated entries to '
     '7 unique records.'),
    ('9.2 TOCTOU Race Condition in Agency Registration',
     'Challenge: Two simultaneous registration requests with the same agency name could both pass the '
     'app-level uniqueness check (SELECT) and then both INSERT, creating duplicate records. The email '
     'check had the same flaw \u2014 the second request would crash with a 500 error from an unhandled '
     'IntegrityError. This is a classic time-of-check-to-time-of-use (TOCTOU) race condition.\n\n'
     'Solution: The registration flow was rewritten. add_agency() now opens a BEGIN IMMEDIATE transaction, '
     'performs both name and email duplicate checks inside the transaction, and returns an (id, error) '
     'tuple. A UNIQUE INDEX idx_agencies_name_country on LOWER(name) + country provides database-level '
     'enforcement. IntegrityError is caught and returned as a friendly flash message. The debugging '
     'process involved reproducing the race by opening two browser tabs and submitting simultaneously, '
     'then examining the resulting database state to confirm duplicates.'),
    ('9.3 Booking Reference Counter Race',
     'Challenge: get_next_ref() opened a connection, SELECTed the counter, closed it, re-opened, and '
     'UPDATEed \u2014 two concurrent bookings could read the same value, producing duplicate references. '
     'The UNIQUE constraint caught it, but users saw a confusing "seat taken" error when the real '
     'problem was a reference collision, not a seating conflict.\n\n'
     'Solution: SELECT and UPDATE now execute in a single BEGIN IMMEDIATE transaction on one connection, '
     'ensuring unique, monotonically incrementing reference numbers for every caller. The counter is '
     'stored in the meta table with the key \'booking_ref_counter\'. The transaction atomically reads '
     'the current value, increments it, and writes it back, returning the incremented value. This '
     'pattern is also known as a "mutual exclusion" pattern using the database as the synchronisation '
     'primitive.'),
    ('9.4 Concurrent Seat Booking',
     'Challenge: Two passengers selecting the same seat simultaneously could both pass the availability '
     'check before either booking was committed \u2014 a classic race condition. This was the most critical '
     'bug to fix because it could result in real-world overbooking, with two passengers arriving at the '
     'terminal with tickets for the same seat.\n\n'
     'Solution: Two layers of protection: (1) a database-level UNIQUE INDEX on (schedule_id, seat_number), '
     'and (2) atomic booking creation in add_booking_atomic() using BEGIN IMMEDIATE. A re-check at '
     'payment time in confirm_booking_atomic() provides optimistic locking coverage. The UNIQUE INDEX '
     'is the ultimate guarantee \u2014 even if both requests somehow pass the application-level checks, '
     'the database will reject the second INSERT. The application catches the IntegrityError and '
     'presents a user-friendly message asking the passenger to select another seat.'),
    ('9.5 Free Departure Notification Delivery',
     'Challenge: Sending real SMS notifications costs money. The requirement was for free notifications '
     'with no budget for paid APIs. Additionally, the solution had to work in different deployment '
     'environments (development, staging, production) with different capabilities.\n\n'
     'Solution: A four-tier priority chain was implemented \u2014 WhatsApp Cloud API (free tier, 1,000 '
     'conversations/month, no credit card via Meta Developer account), USB GSM modem (one-time ~$20 '
     'hardware, sends via SIM AT commands \u2014 free with SIM SMS bundle), Twilio (paid fallback), and '
     'console logging (always works). All tiers are dormant until configured, consuming zero resources. '
     'The priority chain ensures the most cost-effective channel is tried first, falling through to '
     'more expensive options only when free channels are unavailable or have reached their limits.'),
    ('9.6 Multi-Language Translation Management',
     'Challenge: Maintaining consistent translations across 11 languages with ~434+ UI strings each. '
     'Adding new text required updating all 11 files. Without a systematic approach, translations '
     'would quickly become inconsistent, with some languages missing keys that others had.\n\n'
     'Solution: A generate_translations.py script reads en.json (source of truth) and regenerates all '
     'language files. The _() function gracefully falls back to English for any missing key in any '
     'language file. French translations are done manually for accuracy; other languages use the '
     'fallback mechanism. The script ensures that all language files have the same key structure as '
     'en.json, adding placeholder entries for any missing keys. This keeps the files synchronised '
     'while allowing translation work to proceed incrementally.'),
    ('9.7 Agency Privacy',
     'Challenge: Competing agencies should not access each other\'s pricing, routes, or operational data. '
     'Agency employees browsing the site as passengers could view competitor information. The initial '
     'implementation had no mechanism to scope data access to the logged-in agency.\n\n'
     'Solution: Session-aware filtering in the _country_agencies() helper. When agency_id is in session, '
     'all public pages filter to show only the logged-in agency\'s data. Direct URL access to competitor '
     'pages is blocked with authorization checks. The implementation adds a WHERE agency_id = ? clause '
     'to all database queries that return agency-scoped data when an agency session is active. This '
     'filtering is transparent to the template layer \u2014 templates simply iterate over the returned '
     'data without knowing whether it has been filtered.'),
    ('9.8 Other Challenges',
     'Additional challenges addressed include:\n\n'
     '\u2022 Bell icon colour inconsistency: The bell notification icon on the navigation bar was hardcoded '
     'to #c62828 (a dark red). However, for Kenya this colour was nearly invisible because the Kenyan '
     'flag\'s second colour (red) clashed. The icon was updated to use a dynamically calculated contrasting '
     'colour that is visible against any flag colour.\n\n'
     '\u2022 One-time shared password security: The initial "Admin123" password was shared across all '
     'ministry portals. A meta table flag now tracks whether the password has been changed. On first '
     'login, "Admin123" is permanently invalidated and the user must set a new password. Each country\'s '
     'ministry portal has its own independent password.\n\n'
     '\u2022 Session staleness: If an agency account is deleted by a ministry official while the agency '
     'user is logged in, their session cookie would remain valid until expiry. A get_agency_session() '
     'function now validates on every authenticated request that the agency record still exists in '
     'the database. If not, the session is cleared and the user is redirected to login.\n\n'
     '\u2022 Unclosed HTML elements: During development, several instances of unclosed <div> and <table> '
     'tags caused layout issues. A systematic review using HTML validators identified and fixed all '
     'instances. The review process involved checking each template file for matching open/close tags '
     'and ensuring Jinja2 conditionals did not create mismatched nesting.\n\n'
     '\u2022 Bilingual announcement translation: For French-speaking countries, route announcements '
     'needed to be available in both English and French. The implementation stores the French '
     'translation in a message_fr column at schedule creation time, rather than translating '
     'on-the-fly. This ensures consistent translations and avoids repeated API calls to translation '
     'services.\n\n'
     '\u2022 Rate limit persistence: The rate limiting implementation uses an in-memory dictionary, '
     'which means rate limits are reset on server restart. For production use, the implementation '
     'should be updated to use a persistent store.'),
]

for title, body in challenges:
    add_heading(title, level=3)
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
    'The application was tested using multiple approaches to ensure correctness across all features: '
    'manual browser testing across all routes and user flows, automated HTTP tests with Python '
    'http.client, database verification for migration accuracy, responsive design testing at all '
    'four breakpoints, and targeted concurrency tests to verify race condition fixes.'
)
add_para(
    'Manual browser testing was the primary testing method. Each route was accessed in a web browser '
    'and verified to return a properly rendered page with correct content. Form submissions were '
    'tested with both valid and invalid data to verify validation logic. The booking flow was tested '
    'end-to-end multiple times: search, browse results, select seat, enter details, make payment, '
    'view ticket. Edge cases tested include: booking the last available seat, attempting to book a '
    'seat that was just taken by another user (via the AJAX polling), booking with invalid passenger '
    'details, and attempting to access authenticated routes without a valid session.'
)
add_para(
    'Automated HTTP tests were written using Python\'s standard library http.client module. These '
    'tests make actual HTTP requests to the running Flask application (using the test client) and '
    'verify response status codes, content types, and the presence of expected HTML elements or '
    'JSON structures. The test suite covers all 30+ routes and can be run automatically to detect '
    'regressions. While not a comprehensive unit test suite (which was identified as a future '
    'improvement), these integration tests provide basic confidence that routes are reachable and '
    'return valid responses.'
)
add_para(
    'Concurrency testing was performed by simulating simultaneous requests. Two browser tabs were '
    'opened to the same schedule\'s seat map, and both users selected the same seat at the same '
    'time. The expected behaviour (one success, one failure) was verified. Similarly, two '
    'registration requests with the same agency name were submitted simultaneously to verify that '
    'the TOCTOU fix prevents duplicates. These concurrency tests were crucial for validating the '
    'transaction and unique index strategies described in Chapter 9.'
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

add_para(
    'In addition to HTTP 200 verification, each route was checked for: appropriate content type '
    '(text/html for pages, application/json for API endpoints), presence of key HTML elements '
    '(forms, tables, navigation), correct rendering of dynamic content (country-specific data, '
    'language-appropriate labels), and proper handling of invalid parameters (404 for non-existent '
    'IDs, validation error messages for invalid form data). All routes passed these checks.'
)

add_heading('10.3 Migration Results', level=3)
add_para(
    'The migration from JSON to SQLite achieved 100% data integrity:'
)
add_tool_table(
    ['Entity', 'JSON Records', 'SQLite Records', 'Match'],
    [
        ['Agencies', '7', '7', '\u2713'],
        ['Buses', '111', '111', '\u2713'],
        ['Routes', '9', '9', '\u2713'],
        ['Schedules', '11', '11', '\u2713'],
        ['Bookings', '18', '18', '\u2713'],
        ['Passengers', 'N/A (duplicated)', '7 (deduplicated)', '\u2713'],
    ]
)
add_para(
    'The migration verified that every record from the JSON file was correctly imported into the '
    'SQLite database. For the agencies, buses, routes, schedules, and bookings entities, the record '
    'counts matched exactly. For passengers, the deduplication process correctly collapsed 18 '
    'duplicated passenger entries (one per booking) into 7 unique passenger records, using the '
    'UNIQUE(phone, id_number) constraint to identify duplicates. No data was lost during the '
    'migration. Foreign key relationships were verified to be correct: every booking references '
    'an existing schedule and passenger, every schedule references an existing route and bus, '
    'and every route and bus references an existing agency.'
)

add_heading('10.4 Additional Feature Tests', level=3)
tests = [
    'Live Seat API: Returns {"taken": [...]} \u2014 HTTP 200 verified with correct seat arrays for each schedule. The API correctly reflects seat status changes within the polling interval.',
    'Subscription Flow: Plan selection \u2192 pay form \u2192 confirm POST activates subscription. Extending existing sub correctly adds days to end_date. Three plans (monthly, 6-month, annual) all tested.',
    'Concurrency: Two simultaneous registration requests with same name \u2014 first succeeds, second returns "name already exists" flash (no crash). Two simultaneous requests for same seat \u2014 first succeeds, second returns "seat already taken" error.',
    'Flag-Coloured Hero: Cameroon flag colours cycle correctly through words in hero title. Country switching updates colours dynamically. Kenya (3 colours) and Cameroon (3 colours) both display correctly.',
    'Notification Scheduler: Daemon thread starts without error. With no channel configured, logs to console \u2014 zero application impact. notification_log table correctly prevents duplicate reminders.',
    'Flash Categories: All 100+ flash() calls updated. CSS classes render green/orange/red alerts correctly in all templates. Close button dismisses messages as expected.',
    'Payment Commission Skip: 1% commission hidden from passenger. Active subscription triggers server-side commission skip verified via DB. Commission is re-enabled when subscription expires.',
    'TOCTOU Fix: Registration with duplicate name inside BEGIN IMMEDIATE correctly rejects second request with friendly error. Email duplicates also correctly rejected. Both checks performed atomically.',
    'Responsive Design: All pages render correctly at 1024px, 768px, 480px, and 360px breakpoints. Hamburger menu works on mobile. Seat map scales appropriately on small screens.',
    'Booking Lifecycle: Bookings can be created, viewed, and cancelled. Cancelled bookings free the seat for other passengers. Expired bookings (30 min after departure) are cleaned up.',
]
for t in tests:
    add_bullet(t)

add_para(
    'All feature tests passed successfully. The most significant validation was the concurrency tests, '
    'which confirmed that the race condition fixes (Chapters 9.2\u20139.4) work correctly. Before the fixes, '
    'running the duplicate registration test would produce a 500 error and leave the database in an '
    'inconsistent state. After the fixes, the second request is cleanly rejected with a user-friendly '
    'flash message. Similarly, the duplicate seat booking now correctly prevents the second booking '
    'while providing clear feedback.'
)

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
    'Database migration from flat JSON to normalised SQLite with zero data loss',
    'Rate limiting on authentication endpoints to prevent brute-force attacks',
    'One-time password mechanism for secure ministry portal initial access',
]
for a in achievements:
    add_bullet(a)

add_para(
    'Over the course of the internship, the AFRI Trans project evolved from a basic single-country '
    'Flask prototype with JSON file storage into a comprehensive, production-ready platform serving '
    'all 54 African countries with 11 languages, real-time features, concurrency hardening, and '
    'government oversight workflows. The project demonstrates that complex multi-tenant, multi-country '
    'web applications can be built with relatively simple technologies (Flask, SQLite, vanilla JS) '
    'when architecture and data integrity are given proper attention.'
)
add_para(
    'The most technically rewarding achievements were the concurrency fixes (Chapters 9.2\u20139.4). '
    'Diagnosing and fixing TOCTOU race conditions required a deep understanding of database '
    'transaction semantics, the GIL, and Flask\'s threading model. The solution \u2014 using BEGIN '
    'IMMEDIATE transactions combined with database-level UNIQUE indexes \u2014 is a clean, robust '
    'pattern that prevents entire classes of concurrency bugs. The same pattern can be applied '
    'to any web application that needs to prevent duplicate record creation or resource '
    'over-allocation under concurrent access.'
)

add_heading('11.2 Future Improvements', level=3)
future_items = [
    ('Security', ['Add CSRF protection to all forms', 'Switch to HTTPS in production', 'Implement account lockout after failed login attempts', 'Add session timeout with configurable duration']),
    ('Code Quality', ['Refactor monolithic app.py into modular route blueprints', 'Add unit tests with pytest (coverage >80%)', 'Implement logging framework (structlog or standard logging)', 'Add type hints throughout the codebase']),
    ('Real-Time', ['WebSocket-based real-time seat availability (HTTP polling already implemented)', 'Live booking notifications for agencies via WebSocket', 'Real-time dashboard updates for ministry portal']),
    ('Payment Integration', ['Connect to real mobile money APIs (M-Pesa, MTN MoMo, Orange Money)', 'Webhook-based payment confirmation with idempotency', 'Payment receipt generation and email delivery', 'Refund processing workflow']),
    ('Performance', ['Redis caching for frequently accessed data (countries, translations)', 'Database query optimisation with EXPLAIN analysis', 'CDN for static assets (CSS, JS, flag images)', 'Connection pooling for database operations']),
    ('Additional Features', ['RTL support for Arabic-language countries', 'Mobile app using React Native or Flutter', 'Driver/operator mobile interface for manifest management', 'Multi-trip and round-trip booking support', 'Loyalty/rewards program with points accumulation', 'Email ticket delivery as an alternative to download', 'QR code on tickets for contactless boarding', 'Integration with national ID verification APIs']),
]
for category, items in future_items:
    add_para(f'{category}:', bold=True)
    for item in items:
        add_bullet(item)

add_para(
    'The future improvements are prioritised by impact and feasibility. Security enhancements (CSRF, '
    'HTTPS) are the most important for production deployment. Code quality improvements (modularisation, '
    'tests) would make the codebase more maintainable for future developers. Real-time and payment '
    'integrations would significantly enhance the user experience. Performance improvements would '
    'become necessary as traffic scales beyond the current prototype level. The additional features '
    'represent the product vision for the next major version of the platform.'
)

add_page_break()

# ════════════════════════════════════════════
# REFERENCES
# ════════════════════════════════════════════
add_heading('12. References', level=2)
refs = [
    'Flask Documentation \u2014 The Flask Web Framework. Pallets Project. https://flask.palletsprojects.com/',
    'Python 3 Documentation \u2014 Python Software Foundation. https://docs.python.org/3/',
    'SQLite Documentation \u2014 SQLite Consortium. https://www.sqlite.org/docs.html',
    'Jinja2 Documentation \u2014 Pallets Project. https://jinja.palletsprojects.com/',
    'Pillow (PIL Fork) Documentation \u2014 Python Pillow. https://pillow.readthedocs.io/',
    'xhtml2pdf Documentation \u2014 xhtml2pdf Project. https://xhtml2pdf.readthedocs.io/',
    'Werkzeug Documentation \u2014 Pallets Project. https://werkzeug.palletsprojects.com/',
    'Twilio SMS API \u2014 Twilio Inc. https://www.twilio.com/docs/sms',
    'WhatsApp Cloud API \u2014 Meta. https://developers.facebook.com/docs/whatsapp/cloud-api',
    'Font Awesome Icons \u2014 Fonticons, Inc. https://fontawesome.com/',
    'Mobile Money in Africa \u2014 GSMA Mobile Money Report. https://www.gsma.com/mobilemoney/',
    'ISO 3166-1 Country Codes \u2014 International Organization for Standardization.',
    'OWASP Top Ten Web Application Security Risks \u2014 OWASP Foundation. https://owasp.org/www-project-top-ten/',
    'SQLite WAL Mode Documentation \u2014 SQLite Consortium. https://www.sqlite.org/wal.html',
    'Python threading Documentation \u2014 Python Software Foundation. https://docs.python.org/3/library/threading.html',
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
