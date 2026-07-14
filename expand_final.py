"""Expand original AFRI_Trans_reports.docx matching its exact writing style."""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from lxml import etree
import os, shutil, zipfile

SRC = 'AFRI_Trans_reports.docx'
DST = 'AFRI_Trans_Report_2026.docx'
TMP = os.environ['TEMP'] + '/report_build'

if os.path.exists(TMP): shutil.rmtree(TMP)
with zipfile.ZipFile(SRC) as z:
    z.extractall(TMP)
IMG_DIR = os.path.join(TMP, 'word/media')

shutil.copy(SRC, DST)
doc = Document(DST)
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
body = doc.element.body

def make_para(text, bold=False, italic=False, size=11, color=None, space_after=4):
    p = etree.SubElement(body, W + 'p')
    pPr = etree.SubElement(p, W + 'pPr')
    spacing = etree.SubElement(pPr, W + 'spacing')
    spacing.set(W + 'after', str(space_after * 20))
    spacing.set(W + 'line', '276')
    spacing.set(W + 'lineRule', 'auto')
    for rp in [etree.SubElement(p, W + 'rPr'), etree.SubElement(etree.SubElement(p, W + 'r'), W + 'rPr')]:
        rFonts = etree.SubElement(rp, W + 'rFonts')
        rFonts.set(W + 'ascii', 'Calibri')
        rFonts.set(W + 'hAnsi', 'Calibri')
        sz = etree.SubElement(rp, W + 'sz')
        sz.set(W + 'val', str(size * 2))
        if bold: etree.SubElement(rp, W + 'b')
        if italic: etree.SubElement(rp, W + 'i')
        if color:
            c = etree.SubElement(rp, W + 'color')
            c.set(W + 'val', color.lstrip('#'))
    t = etree.SubElement(etree.SubElement(p, W + 'r'), W + 't')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p

def insert_after(ref_p, new_elem):
    ref_p._element.addnext(new_elem)

def find_para(text_fragment):
    for i, p in enumerate(doc.paragraphs):
        if text_fragment in p.text:
            return i, p
    return None, None

def expand_section(section_title, new_paras, max_lookahead=50):
    idx, ref_p = find_para(section_title)
    if idx is None:
        print(f'  NOT FOUND: {section_title}')
        return False
    end_idx = idx
    for j in range(idx + 1, min(idx + max_lookahead, len(doc.paragraphs))):
        txt = doc.paragraphs[j].text.strip()
        if not txt: continue
        if doc.paragraphs[j].style and 'Heading' in doc.paragraphs[j].style.name:
            break
        if (txt[0].isdigit() and '. ' in txt[:5]) and txt.count('.') <= 2:
            break
        end_idx = j
    ref_p2 = doc.paragraphs[end_idx]
    for new_p in reversed(new_paras):
        insert_after(ref_p2, new_p)
    print(f'  EXPANDED: {section_title}')
    return True

print('Expanding original report with matched writing style...\n')

# ===== SECTION 7.18 Flash Alert Categories =====
expand_section('7.18 Flash Alert Categories', [
    make_para('Flash messages throughout the platform now use three colour-coded categories instead of a single style: success (green, #e8f5e9) for positive feedback, error (red, #ffebee) for failures, and warning (orange, #fff8e1) for informational alerts. The base template renders each category using the corresponding CSS class (.flash-success, .flash-error, .flash-warning) defined in style.css with appropriate colours, icons, and animation.'),
    make_para('Success alerts indicate booking confirmation, successful payment, agency approval, profile updates, and subscription activation. Error alerts indicate booking failure, payment decline, incorrect login, expired sessions, and database errors. Warning alerts indicate seat no longer available, rate limiting, session expiry, and action confirmations.'),
    make_para('All 100+ flash() calls in the application were updated to use with_categories=true. A close button (x) dismisses alerts with a smooth fade-out animation. Success and warning alerts auto-dismiss after 10 seconds. Error alerts require manual dismissal.'),
])

# ===== SECTION 7.19 Subscription Monetisation =====
expand_section('7.19 Subscription Monetisation', [
    make_para('Agencies can prepay to skip the 1% platform commission for a defined period. Three plans are available: Monthly (58,000 FCFA / 15,000 NGN), 6-Month (250,000 FCFA / 75,000 NGN), and Annual (500,000 FCFA / 150,000 NGN).'),
    make_para('The flow: Agency clicks Subscription button on dashboard -> chooses a plan -> /agency/subscribe/pay (selects payment provider + phone) -> POST to /agency/subscribe/confirm -> subscription activated or extended. If the agency already has an active subscription, the page shows "Extend Your Subscription" with the current expiry date and lets them add more time via extend_subscription() which adds plan days to the existing end_date.'),
    make_para('On the passenger payment page, the 1% commission breakdown is hidden. Passengers see only the total price. The commission skip happens server-side: when a booking is made for an agency with an active subscription, the 1% deduction is skipped entirely, and the agency receives 100% of the fare.'),
])

# ===== SECTION 7.20 Flag-Coloured Hero Title =====
expand_section('7.20 Flag-Coloured Hero Title', [
    make_para('The hero heading on the index page now colours each word using the country flag colours. For Cameroon (green #007a5e, red #ce1126, yellow #fcd116), "Book" appears green, "Your" red, "Journey" yellow, "Across" green, "Cameroon" red. The colours cycle through the flag_colors array defined per country, falling back gracefully for countries with fewer colours.'),
    make_para('The template splits the title into words using Jinja2 split() filter. Each word gets an inline style: color: country.flag_colors[loop.index0 % len(flag_colors)]. No JavaScript is needed. The colouring is rendered server-side and appears immediately on page load.'),
])

# ===== SECTION 7.21 Live Seat Map with Auto-Refresh =====
expand_section('7.21 Live Seat Map', [
    make_para('The seat selection page (pick_seat.html) polls a lightweight JSON endpoint every 30 seconds to detect seats taken by other passengers without page reload. JavaScript compares the new taken set against the previous snapshot. Newly taken seats are greyed out immediately. If the user selected seat was taken by someone else, the selection is cleared and they must pick again.'),
    make_para('The endpoint GET /api/seats/<sid>/status returns {"taken": [2, 7, 15, ...]} from a simple SQL query. A typical response is 150 bytes. Bandwidth usage is about 5 bytes/second per user, negligible for thousands of concurrent users.'),
])

# ===== SECTION 7.22 Departure Notification Scheduler =====
expand_section('7.22 Departure Notification Scheduler', [
    make_para('A background daemon thread runs every 60 seconds and checks for confirmed bookings where departure is exactly 90 minutes or 45 minutes away. It queries the database with a JOIN across schedules, bookings, passengers, routes, buses, and agencies to build the full reminder context.'),
    make_para('Before sending, the system checks the notification_log table to avoid duplicate sends. After a successful send, a record is inserted. This guarantees each passenger gets exactly one 90-minute and one 45-minute reminder per booking.'),
    make_para('The system attempts to send via priority chain: WhatsApp Cloud API (free tier, 1,000 conversations/month, no credit card needed) -> USB GSM Modem (one-time ~$20 hardware, free SMS via SIM bundle) -> Twilio SMS (paid) -> console log (always works, no config). All channels are dormant until configured, consuming zero resources when unconfigured.'),
    make_para('The format_phone() helper normalises numbers to international format by prepending the country code (+237 for Cameroon, +254 for Kenya) when needed.'),
])

# ===== SECTION 7.23 Concurrency Hardening =====
expand_section('7.23 Concurrency Hardening', [
    make_para('Two critical race conditions were fixed using SQLite transaction semantics and database-level constraints.'),
    make_para('Agency Registration: add_agency() now opens a BEGIN IMMEDIATE transaction and performs both uniqueness checks inside the transaction. A UNIQUE INDEX idx_agencies_name_country on LOWER(name) + country provides database-level enforcement. IntegrityError is caught and returned as a friendly error instead of a 500 crash.'),
    make_para('Booking Reference: get_next_ref() now uses a single BEGIN IMMEDIATE transaction for both SELECT and UPDATE operations. This prevents concurrent callers from reading the same counter value. References are now guaranteed unique and monotonically incrementing.'),
])

# ===== 9.15 TOCTOU Race Condition =====
expand_section('9.15 TOCTOU Race Condition in Agency Registration', [
    make_para('Challenge: Two simultaneous registration requests with the same agency name could both pass the app-level uniqueness check (SELECT) and then both INSERT, creating duplicate records. The same flaw existed for email uniqueness.'),
    make_para('Solution: The entire registration flow was rewritten. add_agency() now opens a BEGIN IMMEDIATE transaction, checks both name+country and email uniqueness inside the transaction, and inserts the record. A UNIQUE INDEX provides the last line of defence. IntegrityError is caught and returned as a friendly (id, error) tuple instead of crashing.'),
])

# ===== 9.16 Booking Reference Counter Race =====
expand_section('9.16 Booking Reference Counter Race', [
    make_para('Challenge: get_next_ref() opened a connection, SELECTed the counter, closed it, re-opened, and UPDATEed. Two concurrent bookings could read the same value, producing duplicate references. The UNIQUE constraint caught it, but users saw a confusing error.'),
    make_para('Solution: SELECT and UPDATE now execute in a single BEGIN IMMEDIATE transaction on one connection, ensuring unique, monotonically incrementing reference numbers for every caller.'),
])

# ===== 9.17 Free Departure Notification Delivery =====
expand_section('9.17 Free Departure Notification Delivery', [
    make_para('Challenge: SMS notifications cost money. The requirement was for free notifications with no budget for paid APIs.'),
    make_para('Solution: A four-tier priority chain was implemented: WhatsApp Cloud API (free tier, 1,000 conversations/month, no credit card), USB GSM modem (one-time ~$20 hardware, free SMS via SIM bundle), Twilio (paid fallback), and console logging (always works). All tiers are dormant until configured, consuming zero resources.'),
])

print('\n=== Saving expanded report ===')
doc.save(DST)
import os
size = os.path.getsize(DST)
chars = sum(len(p.text) for p in doc.paragraphs)
print(f'Saved: {DST}')
print(f'Size: {size:,} bytes')
print(f'Paragraphs: {len(doc.paragraphs)}')
print(f'Characters: {chars:,}')
print(f'Original chars: 52,393')
print(f'Growth: {((chars/52393)-1)*100:.0f}%')
