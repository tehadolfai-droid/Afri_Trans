"""Update AFRI_Trans_Updated_v2.docx with latest session changes:
- Contact Agency feature
- WhatsApp floating widget
- WhatsApp field + phone codes in registration
- Email required & globally unique
- 24h ticket validity removed
- Country switch clears auth
- Feedback role detection fix
"""

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

PATH = r'C:\Users\EYE INFORMATIQUE\OneDrive\Desktop\transport\AFRI_Trans_Updated_v2.docx'
doc = Document(PATH)

# ── helpers ──

def make_p_elem(text='', style='Normal', bold=False):
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

def make_heading_elem(text, level=3):
    return make_p_elem(text, f'Heading {level}')

def make_bullet_elem(text):
    return make_p_elem(text, 'List Bullet')

def make_bold_para_elem(label, text):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'Normal')
    pPr.append(pStyle)
    p.append(pPr)
    r1 = OxmlElement('w:r')
    rPr1 = OxmlElement('w:rPr')
    b1 = OxmlElement('w:b')
    rPr1.append(b1)
    r1.append(rPr1)
    t1 = OxmlElement('w:t')
    t1.text = label
    r1.append(t1)
    p.append(r1)
    r2 = OxmlElement('w:r')
    t2 = OxmlElement('w:t')
    t2.text = text
    r2.append(t2)
    p.append(r2)
    return p

def insert_all_after(ref_elem, elements):
    prev = ref_elem
    for elem in elements:
        prev.addnext(elem)
        prev = elem

def find_elem_by_text(text_fragment):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            return p._p
    return None

# ── New content builders ──

def build_contact_agency_section():
    elems = []
    elems.append(make_heading_elem('7.18 Contact Agency System', 3))
    elems.append(make_p_elem(
        'Passengers can now contact transport agencies directly through the platform. This feature '
        'addresses real-world scenarios such as missed buses, rebooking arrangements, and general '
        'inquiries \u2014 all without exposing agency email addresses publicly.'))
    for ca in [
        'Two-way contact: /contact-agency/<ref> form on the ticket page sends an email to the agency with passenger details, ticket ref, route, and message',
        'WhatsApp floating widget: green button fixed at bottom-right of every page, opens a searchable dropdown listing all agencies with WhatsApp numbers',
        'Clicking an agency in the widget opens wa.me/<number> with a pre-filled greeting message in the user\'s language',
        'API endpoint /api/agencies returns approved agencies with WhatsApp numbers as JSON for the frontend widget',
        'Agencies set their WhatsApp number during registration \u2014 country code auto-detected and prefixed (e.g. +237 for Cameroon)',
        'Client-side and server-side validation prevents entering the country code manually; only the local number is accepted',
        'Phone dial codes added to all 54 countries in the COUNTRIES dict for accurate auto-prefixing',
    ]:
        elems.append(make_bullet_elem(ca))
    return elems

def build_email_uniqueness_section():
    elems = []
    elems.append(make_heading_elem('7.19 Global Email Uniqueness', 3))
    elems.append(make_p_elem(
        'One email address can now only register one agency globally across all 54 countries. '
        'Previously, the email field was optional and only checked per-country, allowing duplicate '
        'registrations with the same email in different countries.'))
    for eu in [
        'Email field made required in agency registration (previously optional)',
        'get_agency_by_email_global() checks all countries before allowing registration',
        'Unique database index enforces no duplicate non-empty emails at the database level',
        'Email passed directly to add_agency() INSERT instead of a separate UPDATE call',
        'Registration form updated with "One email = one agency globally" notice',
        'Existing duplicate emails in the database remain but new registrations are blocked',
    ]:
        elems.append(make_bullet_elem(eu))
    return elems

def build_ticket_expiry_change():
    elems = []
    elems.append(make_heading_elem('7.20 Ticket Expiry Policy Change', 3))
    elems.append(make_p_elem(
        'The ticket validity period was changed from "24 hours after departure" to "valid only for '
        'the specific departure time". If a passenger misses the bus, the ticket expires immediately '
        'and they must book and pay for a new journey.'))
    for te in [
        'booking_valid_until() function removed \u2014 replaced with booking_has_departed() which compares departure time to current time',
        'is_expired logic simplified: ticket is expired if departure time has passed or status is "expired"',
        'All UI references to "Valid 24h after departure" replaced with "Valid for this departure only"',
        'PNG ticket image no longer shows 24h validity text \u2014 shows "EXPIRED TICKET" if departed',
        'Agency bookings list removes the "Valid until" display for each booking',
        'Translation keys updated in both en.json and fr.json',
    ]:
        elems.append(make_bullet_elem(te))
    return elems

def build_auth_clear_section():
    elems = []
    elems.append(make_heading_elem('7.21 Country Switch Session Clear', 3))
    elems.append(make_p_elem(
        'Switching countries via the globe icon now clears all authentication sessions. This prevents '
        'confusion where a ministry or agency session from one country leaked into another country\'s context.'))
    for ac in [
        'set_country() route now pops agency_id, ministry, ministry_1fa, ministry_country, super_admin_id, super_admin_email, and read_notification_ids from session',
        'Feedback page now checks session.get(\'ministry\') in addition to super_admin_id to accurately detect ministry role',
        'feedback_all access control also checks both ministry and super_admin_id flags',
        'Login page now displays the current country prominently so users know which country they are logging into',
    ]:
        elems.append(make_bullet_elem(ac))
    return elems

def build_challenges_v3():
    elems = []
    # 9.15
    elems.append(make_heading_elem('9.15 No Passenger-to-Agency Contact Channel', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'Passengers had no way to contact transport agencies directly if they missed the bus, needed '
        'to reschedule, or had inquiries. The ticket showed only the agency name with no phone, email, '
        'or contact button.'))
    elems.append(make_bold_para_elem('Solution: ',
        'A two-pronged contact system: (1) /contact-agency/<ref> form on the ticket page that emails '
        'the agency with full passenger and journey details, and (2) a floating WhatsApp widget on every '
        'page with a searchable list of all agencies that have registered a WhatsApp number.'))
    # 9.16
    elems.append(make_heading_elem('9.16 Duplicate Email Registration Across Countries', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'The email field was optional during agency registration and only checked per-country. This '
        'allowed registering agencies in different countries with the same email address, defeating '
        'the "one email = one agency" policy.'))
    elems.append(make_bold_para_elem('Solution: ',
        'Email made a required field with global uniqueness validation via get_agency_by_email_global(). '
        'A unique database index enforces no duplicate non-empty emails. The add_agency() function now '
        'accepts email directly in the INSERT statement rather than a separate UPDATE.'))
    # 9.17
    elems.append(make_heading_elem('9.17 Stale Ministry Session After Country Switch', 3))
    elems.append(make_bold_para_elem('Problem: ',
        'Switching countries via the globe icon preserved the ministry session (super_admin_id). '
        'The feedback page showed "(Ministry)" role even when the user was not actively logged into '
        'the ministry portal, because the stale flag remained in the session cookie.'))
    elems.append(make_bold_para_elem('Solution: ',
        'set_country() now clears all auth-related session keys (ministry, agency_id, super_admin_id, etc.). '
        'The feedback route now checks session.get(\'ministry\') in addition to super_admin_id for accurate '
        'role detection.'))
    return elems

def build_test_results_v3():
    elems = []
    elems.append(make_p_elem('Additional tests from the latest development cycle:'))
    for tr in [
        'Contact Agency form: email sent to agency correctly with passenger name, ref, route, and message',
        'WhatsApp widget: fetches agencies from /api/agencies, search filters correctly, opens correct wa.me link',
        'WhatsApp registration validation: rejects country code entry, auto-prefixes with correct dial code per country',
        'Email uniqueness: same email rejected across different countries during registration',
        'Ticket expiry: ticket shows "Valid for this departure only" and "EXPIRED" after departure time',
        'Country switch clears auth: agency_id, ministry, super_admin_id all removed from session on switch',
        'Feedback role detection: no longer shows "Ministry" due to stale super_admin_id from previous login',
        'Login page country indicator: clearly displays which country login is searching within',
    ]:
        elems.append(make_bullet_elem(tr))
    return elems

def build_achievements_v3():
    elems = []
    for ach in [
        'Contact Agency system: email-based contact form on ticket page linking passengers to agencies',
        'WhatsApp floating widget: bottom-right widget on every page with searchable agency list and instant WhatsApp chat',
        'WhatsApp number validation: per-country phone code auto-detection with client and server validation',
        '54 phone dial codes added to COUNTRIES dict for accurate WhatsApp number prefixing',
        'Global email uniqueness enforcement: one email = one agency worldwide, no exceptions',
        'Ticket expiry simplified: valid only for departure time, no 24-hour buffer period',
        'Country switch auth clearing: switching countries now fully logs out from all portals',
        'Accurate feedback role detection: checks full ministry auth session, not just stale super_admin flag',
    ]:
        elems.append(make_bullet_elem(ach))
    return elems

# ── Find insertion points ──

p_7_dot_17 = find_elem_by_text('7.17 IP Geolocation')
p_9_dot_14 = find_elem_by_text('9.14 Country Auto-Detection')
p_10_dot_5 = find_elem_by_text('10.5 Latest Feature Test Results')
p_11_dot_1 = find_elem_by_text('11.1 Summary of Achievements')

print(f"Found 7.17: {p_7_dot_17 is not None}")
print(f"Found 9.14: {p_9_dot_14 is not None}")
print(f"Found 10.5: {p_10_dot_5 is not None}")
print(f"Found 11.1: {p_11_dot_1 is not None}")

if p_7_dot_17 is not None:
    print("Inserting new features after 7.17...")
    all_new_features = (build_contact_agency_section() +
                        build_email_uniqueness_section() +
                        build_ticket_expiry_change() +
                        build_auth_clear_section())
    insert_all_after(p_7_dot_17, all_new_features)

if p_9_dot_14 is not None:
    print("Inserting new challenges after 9.14...")
    insert_all_after(p_9_dot_14, build_challenges_v3())

if p_10_dot_5 is not None:
    print("Appending to 10.5 test results...")
    # Find the last bullet in 10.5 and insert after it
    # Simple approach: insert after the 10.5 heading's content, but we'll just insert
    # after a known feature bullet
    marker = find_elem_by_text('IP geolocation auto-detect')
    if marker:
        insert_all_after(marker, [make_p_elem('')] + build_test_results_v3())
    else:
        # fallback: after 10.5 heading
        insert_all_after(p_10_dot_5, build_test_results_v3())

if p_11_dot_1 is not None:
    print("Adding achievements after 11.1...")
    # Find last bullet in achievements and add after
    ach_marker = find_elem_by_text('IP geolocation auto-detect')
    if ach_marker:
        insert_all_after(ach_marker, [make_p_elem('')] + build_achievements_v3())
    else:
        insert_all_after(p_11_dot_1, build_achievements_v3())

# ── Save ──

doc.save(PATH)
chars = sum(len(p.text) for p in doc.paragraphs)
tbls = len(doc.tables)
print(f'\nSaved: {PATH}')
print(f'Paragraphs: {len(doc.paragraphs)}, Tables: {tbls}, Chars: {chars}')
print(f'Est. pages: {chars//3500 + tbls//2}')
