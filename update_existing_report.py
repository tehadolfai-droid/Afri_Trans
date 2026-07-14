"""Update AFRI_Trans_Report_Updated.docx with all work done today.

Strategy: Find key heading paragraphs by text match, then insert new content
after them using XML-level operations on the document body.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from copy import deepcopy
import os

ORIG_PATH = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\INTERNSHIP_REPORT.docx'
OUT_PATH = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\AFRI_Trans_Updated_v2.docx'
import shutil, os
if os.path.exists(OUT_PATH):
    os.remove(OUT_PATH)
shutil.copy2(ORIG_PATH, OUT_PATH)
doc = Document(OUT_PATH)
body = doc.element.body

# ── helpers ──────────────────────────────────────────────

def make_p_elem(text='', style='Normal', bold=False):
    """Create a <w:p> element with given text and style."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style)
    pPr.append(pStyle)
    p.append(pPr)
    if text:
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if bold:
            b = OxmlElement('w:b')
            rPr.append(b)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.text = text
        r.append(t)
        p.append(r)
    return p

def make_heading_elem(text, level=2):
    return make_p_elem(text, f'Heading {level}')

def make_bullet_elem(text):
    return make_p_elem(text, 'List Bullet')

def make_bold_para_elem(label, text):
    """Paragraph with bold label followed by normal text."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'Normal')
    pPr.append(pStyle)
    p.append(pPr)
    # Bold part
    r1 = OxmlElement('w:r')
    rPr1 = OxmlElement('w:rPr')
    b1 = OxmlElement('w:b')
    rPr1.append(b1)
    r1.append(rPr1)
    t1 = OxmlElement('w:t')
    t1.text = label
    r1.append(t1)
    p.append(r1)
    # Normal part
    r2 = OxmlElement('w:r')
    t2 = OxmlElement('w:t')
    t2.text = text
    r2.append(t2)
    p.append(r2)
    return p

def insert_after(ref_p, new_elem):
    """Insert new_elem after ref_p in the document body."""
    ref_p.addnext(new_elem)

def find_heading(text, start=0):
    """Find paragraph index by heading text."""
    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith('Heading') and p.text.strip() == text:
            if i >= start:
                return i
    return None

def find_para_containing(text, start=0):
    for i, p in enumerate(doc.paragraphs):
        if text in p.text:
            if i >= start:
                return i
    return None

print("Scanning document structure...")

# ── Insertion points ─────────────────────────────────────

# We'll work with XML elements directly. Find key paragraphs by text.

# For each insertion point, we need the <w:p> element to insert after.
# We'll collect them first, then insert.

insertions = []  # list of (after_paragraph_text_contains, elements_to_insert)

# 1. After "7.9 Payment Providers" → add 7.10–7.15
# 2. After "8.3 Bus Layout Algorithm" → add 8.4–8.6
# 3. After "9.7 Concurrent Seat Booking" → add 9.8–9.13
# 4. After "10.4 Screenshots" → add 10.5
# 5. Before "11.2 Future Improvements" → add new achievements

# ── Helper to build feature sections ─────────────────────

def build_feedback_section():
    elems = []
    elems.append(make_heading_elem('7.10 Feedback System', 3))
    elems.append(make_p_elem(
        'A feedback form allows any user to submit suggestions, bug reports, or general comments. '
        'The system was designed with simplicity in mind \u2014 a single message field with automatic '
        'role detection based on the user\'s current session state.'))
    for fb in [
        'Accessible via /feedback route from the navbar "Feedback" link',
        'Single message textarea \u2014 no manual name or role fields required from the user',
        'Name and role auto-detected from session: passenger (role: user), agency (role: agency, name from DB), ministry (role: ministry, name from session email)',
        'Feedback stored in dedicated feedback table with name, role, message, and timestamp columns',
        'Email notification sent to FEEDBACK_EMAIL via Gmail SMTP on every submission with submitter details',
        'Ministry can view all feedback at /feedback/all (requires super_admin session), listed newest-first with role badges',
        '.env configuration: MAIL_USERNAME, MAIL_PASSWORD, FEEDBACK_EMAIL loaded via python-dotenv',
    ]:
        elems.append(make_bullet_elem(fb))
    return elems

def build_bilingual_section():
    elems = []
    elems.append(make_heading_elem('7.11 Bilingual Announcement System', 3))
    elems.append(make_p_elem(
        'Cameroon is bilingual (English and French). All agency announcements must be visible in '
        'the passenger\'s preferred language. The system handles this through a dedicated architecture:'))
    for ba in [
        'message_fr column added to announcements table to store the French translation',
        'add_announcement() auto-translates message to French via Google Translate and stores in message_fr',
        'French translation stored at creation time (not on-the-fly) to avoid repeated API calls on every page load',
        'ann_msg(ann) helper via Flask @app.context_processor \u2014 returns French if lang=fr and message_fr exists, else English',
        'All templates updated to use ann_msg(ann) instead of ann.message for announcement display',
        'Back-fill script (translate_announcements.py) handles all pre-existing announcements',
        'get_announcements() uses SELECT a.* so it automatically includes message_fr column',
    ]:
        elems.append(make_bullet_elem(ba))
    return elems

def build_notification_section():
    elems = []
    elems.append(make_heading_elem('7.12 Per-Notification Read Tracking', 3))
    elems.append(make_p_elem(
        'Passengers can track which announcements they have read without requiring user login '
        'or account creation. This is achieved through session-based tracking:'))
    for nt in [
        'Read announcement IDs stored in session[\'read_notification_ids\'] as a Python list',
        'Clicking "Read More" on an announcement adds its ID to the read list',
        'Navbar bell icon shows red badge (#c62828) with count of unread announcements (total minus read IDs)',
        'Unread announcements show a blue dot indicator; read ones show a green checkmark with "Lire" label',
        'Both /notifications and /notification/<id> pages use no-store, no-cache, must-revalidate cache headers',
        'Logout clears read_notification_ids from session for complete cleanup',
        'Bell icon colour hardcoded to #c62828 (red) for ALL countries \u2014 not var(--flag-2) which caused invisibility',
        'Bell icon removed from homepage cards and search results \u2014 only navbar bell remains',
    ]:
        elems.append(make_bullet_elem(nt))
    return elems

def build_sharedpw_section():
    elems = []
    elems.append(make_heading_elem('7.13 One-Time Shared Password (Admin123)', 3))
    elems.append(make_p_elem(
        'The default super admin shared password (Admin123) presented a security vulnerability. '
        'The one-time-use mechanism eliminates this risk:'))
    for pw in [
        'is_shared_pw_used() and mark_shared_pw_used() functions manage the flag via meta table (key: shared_pw_used_{country})',
        'First visit: GET /ministry/login shows shared password form (step 1) if flag not set',
        'On successful Admin123 entry: flag set to "1" in meta table; user redirected to step 2 (personal email + password)',
        'Subsequent visits: GET route checks flag and redirects straight to step 2, skipping shared password form',
        'POST route on step 1 rejects shared password if flag is already set \u2014 prevents any reuse',
        'Step 2: /ministry/relogin for setting personal email and password',
        'Password reset flows for agencies and super admins use 8-digit verification codes via email',
    ]:
        elems.append(make_bullet_elem(pw))
    return elems

def build_commission_section():
    elems = []
    elems.append(make_heading_elem('7.14 Commission System (1% Platform Fee)', 3))
    elems.append(make_p_elem(
        'The platform charges a 1% commission on every booking. The system handles this transparently:'))
    for co in [
        '1% commission calculated on booking total (base price + VIP surcharge + luggage fee)',
        'Commission deducted at source before remaining 99% is attributed to the agency',
        'Commission amount in currency is NEVER displayed in any UI \u2014 not on agency or ministry dashboards',
        'Only the rate (1%) shown as informational badge: "Platform Commission (1%) / Deducted automatically per booking"',
        'Commission records stored in commissions table for platform owner reference',
        'This prevents friction between platform and agencies while maintaining fee transparency',
    ]:
        elems.append(make_bullet_elem(co))
    return elems

def build_busstatus_section():
    elems = []
    elems.append(make_heading_elem('7.15 Bus Auto-Status Management', 3))
    elems.append(make_p_elem(
        'Buses have two operational states: "available" and "busy". The system manages transitions automatically:'))
    for bs in [
        'add_schedule() sets the assigned bus status to "busy" automatically',
        'update_schedule() with status="cancelled" reverts the bus to "available"',
        'Agencies can still manually change bus status through the bus management interface',
        'Bus status displayed as coloured badge (available=green, busy=red) in all listings',
        'Prevents double-booking the same bus on two schedules simultaneously',
    ]:
        elems.append(make_bullet_elem(bs))
    return elems

def build_translation_keys_section():
    elems = []
    elems.append(make_heading_elem('7.16 Translation System Enhancements', 3))
    elems.append(make_p_elem(
        'The translation system was expanded with new keys covering the ministry and super admin '
        'login flows, plus several UI improvements:'))
    for tk in [
        '26 new translation keys added to en.json for ministry pages (dashboard, agency registry, approve/reject modals, booking oversight, password reset)',
        '8 new translation keys added for the super admin login flow (step 1 shared password form, step 2 personal account setup, error messages, validation hints)',
        'All 34 new keys manually translated to French in fr.json for accurate bilingual support',
        'generate_translations.py timed out when auto-translating 26+ keys across 10 languages (260 API calls) — French done manually, other languages received English fallback via _().get(text, text)',
        'The _() function fallback mechanism ensures no UI breaks even when translation keys are missing in any language file',
        'A future improvement would add batch processing with delays between API calls to prevent timeout',
    ]:
        elems.append(make_bullet_elem(tk))
    return elems

def build_autodetect_section():
    elems = []
    elems.append(make_heading_elem('7.17 IP Geolocation — Auto-Detect Country', 3))
    elems.append(make_p_elem(
        'On first visit, the platform automatically detects the user\'s country via IP geolocation '
        'and selects the appropriate country, language, and currency \u2014 no manual switching needed:'))
    for ad in [
        'Uses ip-api.com (free, no API key required) to look up the user\'s IP address on the very first HTTP request',
        'Runs server-side in a @app.before_request handler \u2014 executes once, then the session stores the choice',
        'No browser permission needed \u2014 works even if the user has disabled GPS/location services',
        'If the detected country is in the platform\'s 54-country list, it is auto-selected along with its default language',
        'If geolocation fails (VPN, API timeout, unrecognised country), defaults to Cameroon (cm) with English',
        'The user can always override via the globe icon country switcher \u2014 manual selection always takes priority',
        'Country names appear in the selected language (e.g. "\u0627\u0644\u0643\u0627\u0645\u064a\u0631\u0648\u0646" in Arabic) \u2014 standard UN-recognised names understood locally',
    ]:
        elems.append(make_bullet_elem(ad))
    return elems

def build_email_config():
    elems = []
    elems.append(make_heading_elem('8.4 Email Configuration (SMTP)', 3))
    elems.append(make_p_elem(
        'The application uses Gmail SMTP for sending email notifications (feedback submissions '
        'and password reset codes). Configuration is loaded from a .env file using python-dotenv:'))
    elems.append(make_p_elem(
        'MAIL_USERNAME=your@gmail.com\n'
        'MAIL_PASSWORD=your-16-char-app-password\n'
        'MAIL_FROM=your@gmail.com\n'
        'FEEDBACK_EMAIL=your@gmail.com\n'
        'MAIL_SERVER=smtp.gmail.com\n'
        'MAIL_PORT=587'))
    elems.append(make_p_elem(
        'The .env file is excluded from version control. Gmail requires an "App Password" (16 chars) '
        'when 2FA is enabled. load_dotenv() is called at app startup in app.py.'))
    return elems

def build_session_mgmt():
    elems = []
    elems.append(make_heading_elem('8.5 Session Management', 3))
    elems.append(make_p_elem(
        'Flask signed cookies manage user state across all three portals. Key session keys and their purposes:'))
    for ss in [
        'country (str) \u2014 currently selected country code (e.g. "cm", "ke")',
        'lang (str) \u2014 currently selected language code (e.g. "en", "fr")',
        'agency_id (int) \u2014 logged-in agency ID; None if not logged in',
        'agency_name (str) \u2014 cached agency name for navbar display',
        'ministry_country (str) \u2014 logged-in ministry country scope',
        'super_admin_id (int) \u2014 logged-in super admin ID',
        'super_admin_email (str) \u2014 cached email for display',
        'read_notification_ids (list) \u2014 IDs of read announcements for per-notification tracking',
    ]:
        elems.append(make_bullet_elem(ss))
    elems.append(make_p_elem(
        'Protected routes use get_agency_session() which validates that the agency_id in the session '
        'corresponds to a valid database record on every call. If the agency was deleted, the stale '
        'session entry is removed and the user is redirected to login. Logout clears both agency_id '
        'and read_notification_ids for complete session cleanup.'))
    return elems

def build_mobile_responsive():
    elems = []
    elems.append(make_heading_elem('8.6 Mobile Responsiveness Implementation', 3))
    elems.append(make_p_elem(
        'The responsive CSS uses custom utility classes and four breakpoints. Key responsive features implemented:'))
    for mr in [
        'fs-s \u2014 small font size utility for mobile screens',
        'max-w-780 \u2014 max-width constraint class for search cards',
        'dash-header, dash-title \u2014 dashboard heading responsive scaling',
        'dash-stats \u2014 responsive stat grid with auto-fill columns',
        'trip-row, trip-action \u2014 trip card mobile stacking on small screens',
        'lang-group \u2014 horizontal language buttons on mobile (not stacked)',
        'Hamburger nav with smooth animation and click-outside-to-close',
        'Seat size reduces to 30px max-width on screens under 480px',
        'Bus layout shows driver area, doors, emergency exit, toilet markers',
    ]:
        elems.append(make_bullet_elem(mr))
    return elems

def build_challenges():
    elems = []
    # 9.8
    elems.append(make_heading_elem('9.8 Missing Feedback System', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'The original platform had no channel for users to submit feedback, suggestions, or bug reports. '
        'There was no communication channel between users and platform administrators.'))
    elems.append(make_bold_para_elem('Solution: ',
        'A complete feedback system was built: new feedback table, /feedback GET+POST route with auto-detected '
        'name/role, email notification via Gmail SMTP, /feedback/all for ministry review, and navbar link.'))
    # 9.9
    elems.append(make_heading_elem('9.9 Bell Icon Colour Inconsistency', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'The bell icon used var(--flag-2) which changed colour per country. In Kenya (flag-2 = white), '
        'the bell became invisible against the light navbar \u2014 a critical UI bug.'))
    elems.append(make_bold_para_elem('Solution: ',
        'Bell colour hardcoded to #c62828 (red) for ALL countries. Bell icon removed from homepage cards '
        'and search results \u2014 only navbar bell remains.'))
    # 9.10
    elems.append(make_heading_elem('9.10 One-Time Shared Password Security', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'Using "Admin123" as a shared password across all 54 countries was a critical vulnerability. '
        'Anyone who knew it could access any country\'s ministry portal.'))
    elems.append(make_bold_para_elem('Solution: ',
        'A one-time-use mechanism was implemented via meta table flags. After first use, Admin123 is '
        'permanently invalidated and the user must set a personal email + password combination.'))
    # 9.11
    elems.append(make_heading_elem('9.11 Bilingual Announcement Translation', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'Cameroon is bilingual (English/French). On-the-fly translation would hit Google Translate API '
        'on every page load \u2014 slow, unreliable, and creates excessive external dependencies.'))
    elems.append(make_bold_para_elem('Solution: ',
        'French translation stored in message_fr column at creation time via deep-translator. ann_msg() '
        'context processor selects language version. Back-fill script handles pre-existing announcements.'))
    # 9.12
    elems.append(make_heading_elem('9.12 Session Staleness and Logout Cleanup', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'Deleted agencies left stale agency_id in session causing 404 errors. Logout did not clear '
        'read_notification_ids. Missing get_next_ref import caused 500 error.'))
    elems.append(make_bold_para_elem('Solution: ',
        'get_agency_session() validates DB existence on every call; auto-removes stale session. Logout '
        'clears both agency_id and read_notification_ids. Missing import added to app.py.'))
    # 9.13
    elems.append(make_heading_elem('9.13 Translation Auto-Generation Timeout', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'generate_translations.py timed out processing 26+ new keys across 10 languages (260 API calls).'))
    elems.append(make_bold_para_elem('Solution: ',
        'French done manually for accuracy. Remaining 9 languages use English fallback via _().get(text, text).'))
    # 9.14
    elems.append(make_heading_elem('9.14 Country Auto-Detection Accuracy', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'Users had to manually select their country from the globe icon menu on every new device or after '
        'clearing cookies. This added friction to the first-time user experience, especially for non-technical '
        'users who may not understand country flags or language codes.'))
    elems.append(make_bold_para_elem('Solution: ',
        'IP geolocation via ip-api.com (free, no API key) runs server-side on the very first HTTP request. '
        'It requires no browser permission and works even if GPS/location is disabled. The detected country '
        'is stored in the session, so it only runs once. If the API fails or the country is not in our list, '
        'it defaults to Cameroon. The user can always override via the globe icon.'))
    return elems

def build_test_results():
    elems = []
    elems.append(make_heading_elem('10.5 Latest Feature Test Results', 3))
    elems.append(make_p_elem('Additional tests conducted after implementing the latest features:'))
    for tr in [
        'Feedback system: auto-detected name/role stored correctly; email reaches FEEDBACK_EMAIL',
        'Bilingual announcements: French and English display correctly based on language setting',
        'Notification read tracking: blue dot/green checkmark updates; unread count recalculates correctly',
        'One-time shared password: Admin123 rejected after first use; redirects to personal login',
        'Commission hiding: amount never visible in agency or ministry dashboards',
        'Bus auto-status: busy on schedule creation, available on cancellation',
        'Session hardening: stale agency_id removed; logout clears all session data',
        'Bell icon: #c62828 consistent across all 54 country themes',
        'Mobile responsive: all pages functional at 360px/480px/768px/1024px breakpoints',
        'Seat selection: VIP/standard labels, smooth scroll, pricing updates correctly',
        'Agency dashboard: revenue bars render with correct percentage; today\'s trips highlight card shows route, period, bus, occupancy; stat grid responsive',
        'Email SMTP: feedback notifications sent successfully via Gmail App Password',
        'Agency announcements: extends base.html correctly (fixed from non-existent agency_base.html)',
        'Seat selection UX: VIP/standard labels display with price; smooth scroll on click; total payable updates; mobile 30px seats',
        'Dashboard stat grid: dash-stats auto-fill columns; trip-row/trip-action mobile stacking; dash-header/dash-title responsive scaling',
        'IP geolocation auto-detect: detects country on first visit without browser permission; falls back to Cameroon if API fails',
    ]:
        elems.append(make_bullet_elem(tr))
    return elems

def build_new_achievements():
    elems = []
    for ach in [
        'Feedback system with email notifications to administrators via Gmail SMTP',
        'Bilingual announcement system with automatic French translation, stored at creation time',
        'Per-notification read tracking using session cookies \u2014 no user login required for passengers',
        'One-time shared password (Admin123) with forced personal password setup on first login',
        'Commission system (1%) with amount hidden from all UI \u2014 rate only shown as badge',
        'Bus auto-status management (busy when scheduled, available when cancelled)',
        'Hardened session management: agency validation on every call, stale cleanup, logout clears all',
        'Mobile responsive custom utility classes, hamburger nav, stacked trip rows, resizable seats',
        'Interactive seat selection with VIP/standard labels, smooth scroll, total payable display',
        'Agency dashboard: revenue by route with bar chart, recent bookings, today\'s trips highlight',
        'Email SMTP configuration via .env with python-dotenv for credential management',
        'Translation system expansion: 26 new ministry keys + 8 new super admin login keys added to en.json and manually translated to French',
        'Interactive seat selection UX: VIP/standard class labels with pricing, smooth scroll on selection, total payable display, mobile-optimised 30px seats',
        'IP geolocation auto-detect: detects user country on first visit via ip-api.com, no browser permission needed, works with GPS off',
    ]:
        elems.append(make_bullet_elem(ach))
    return elems

# ── Locate insertion points ──────────────────────────────

def find_elem_by_text(text_fragment):
    """Find the XML element of a paragraph containing the given text."""
    for p in doc.paragraphs:
        if text_fragment in p.text:
            return p._p
    return None

# We'll insert in REVERSE order so earlier indices stay valid.
# Order: finish from bottom of doc upward.

insertion_points = []

# Find reference paragraphs
p_7_dot_9 = find_elem_by_text('7.9 Payment Providers')
p_8_dot_3 = find_elem_by_text('8.3 Bus Layout Algorithm')
p_9_dot_7 = find_elem_by_text('9.7 Concurrent Seat Booking')
p_10_dot_4 = find_elem_by_text('10.4 Screenshots')
p_11_dot_1 = find_elem_by_text('11.1 Summary of Achievements')
p_11_dot_2 = find_elem_by_text('11.2 Future Improvements')

# Check which ones were found
print(f"Found 7.9: {p_7_dot_9 is not None}")
print(f"Found 8.3: {p_8_dot_3 is not None}")
print(f"Found 9.7: {p_9_dot_7 is not None}")
print(f"Found 10.4: {p_10_dot_4 is not None}")
print(f"Found 11.1: {p_11_dot_1 is not None}")
print(f"Found 11.2: {p_11_dot_2 is not None}")

def insert_all_after(ref_elem, elements):
    """Insert multiple elements after ref_elem in correct order.
    addnext inserts right after ref, so we need to insert in reverse order
    to maintain the desired sequence, OR chain them.
    """
    prev = ref_elem
    for elem in elements:
        prev.addnext(elem)
        prev = elem

# ── Perform insertions ──────────────────

if p_7_dot_9 is not None:
    print("Inserting new features after 7.9...")
    all_features = (build_feedback_section() + build_bilingual_section() +
                    build_notification_section() + build_sharedpw_section() +
                    build_commission_section() + build_busstatus_section() +
                    build_translation_keys_section() + build_autodetect_section())
    insert_all_after(p_7_dot_9, all_features)

if p_8_dot_3 is not None:
    print("Inserting implementation details after 8.3...")
    all_impl = build_email_config() + build_session_mgmt() + build_mobile_responsive()
    insert_all_after(p_8_dot_3, all_impl)

if p_9_dot_7 is not None:
    print("Inserting new challenges after 9.7...")
    all_challenges = build_challenges()
    insert_all_after(p_9_dot_7, all_challenges)

if p_10_dot_4 is not None:
    print("Inserting new test results after 10.4...")
    all_tests = build_test_results()
    insert_all_after(p_10_dot_4, all_tests)

if p_11_dot_1 is not None:
    print("Inserting new achievements after 11.1...")
    all_achievements = build_new_achievements()
    insert_all_after(p_11_dot_1, all_achievements)

# ── Fix UK spelling ──────────────────────────────────────

uk_map = {
    'Organization:': 'Organisation:',
    'Normalize': 'Normalise',
    'Normalized': 'Normalised',
    'Standardized': 'Standardised',
    'Centralization': 'Centralisation',
    'Customizing': 'Customising',
    'Internationalization': 'Internationalisation',
}

for p in doc.paragraphs:
    for run in p.runs:
        for old, new in uk_map.items():
            if old in run.text:
                run.text = run.text.replace(old, new)

# ── Save ─────────────────────────────────────────────────

doc.save(OUT_PATH)
print(f'\nSaved to: {OUT_PATH}')

# Count
chars = sum(len(p.text) for p in doc.paragraphs)
tbls = len(doc.tables)
print(f'Paragraphs: {len(doc.paragraphs)}')
print(f'Tables: {tbls}')
print(f'Chars: {chars}')
print(f'Est. pages: {chars//3500 + tbls//2}')
