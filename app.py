from dotenv import load_dotenv
load_dotenv()
from collections import defaultdict
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash, send_file, make_response
from datetime import datetime, date, timedelta
import json, os, random, string, io, smtplib, ssl, urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from xhtml2pdf import pisa
from PIL import Image, ImageDraw, ImageFont
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    init_db, migrate_from_json, get_db,
    get_agencies, get_agency, get_agencies_by_country, get_approved_agencies_by_country,
    add_agency, update_agency, get_approved_agencies_contact,
    get_agency_by_email, get_agency_by_reset_token,
    get_buses_by_agency, get_bus, add_bus, update_bus, get_agency_bus_count,
    get_routes_by_agency, get_route, add_route,
    get_schedule, add_schedule, update_schedule, get_schedules_by_route_ids, get_all_routes, get_schedules, get_bookings_by_schedule_ids,
    get_bookings, get_booking, get_booking_by_ref, get_booking_seat_numbers,
    add_booking_atomic, update_booking, confirm_booking_atomic, get_next_ref,
    get_upcoming_bookings, notification_sent, log_notification,
    add_commission, get_total_commission, get_commission_summary_by_agency, get_commissions_for_booking,
    add_subscription, get_active_subscription, has_active_subscription, extend_subscription,
    add_announcement, get_announcements, deactivate_announcement,
    is_shared_pw_used, mark_shared_pw_used,
    get_super_admin_by_email, get_super_admin_by_country, add_super_admin, update_super_admin,
    get_super_admin_by_reset_token,
    add_feedback, get_all_feedback,
    get_all_agencies, get_all_subscriptions, get_total_commission_global,
    get_subscription_prices, set_subscription_price,
    add_trip_report, get_trip_report, get_trip_reports_by_agency, get_trip_report_count, cleanup_old_trip_reports, expire_unpaid_bookings,
)

app = Flask(__name__)
app.secret_key = 'afritrans-secret-2026'
app.permanent_session_lifetime = timedelta(days=15)

# ── Email Configuration (set env vars or edit directly) ──
MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_FROM     = os.environ.get('MAIL_FROM', MAIL_USERNAME)
FEEDBACK_EMAIL = os.environ.get('FEEDBACK_EMAIL', 'tehadolfai@gmail.com')

def send_email(to_email, subject, body_html):
    """Send an HTML email via SMTP. Returns True on success, False on failure."""
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print('[EMAIL] SMTP not configured — set MAIL_USERNAME and MAIL_PASSWORD env vars')
        return False
    msg = MIMEMultipart('alternative')
    msg['From'] = MAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html'))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls(context=ctx)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())
        print(f'[EMAIL] Sent to {to_email}')
        return True
    except Exception as e:
        print(f'[EMAIL] Failed to send to {to_email}: {e}')
        return False

# ── WhatsApp / SMS Notification Scheduler ──
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN', '')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID', '')
TWILIO_SID = os.environ.get('TWILIO_SID', '')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN', '')
TWILIO_FROM = os.environ.get('TWILIO_FROM', '')

def format_phone(phone, country_code='cm'):
    """Normalize phone to international format."""
    phone = phone.strip()
    if phone.startswith('+'):
        return phone
    pcode = COUNTRIES.get(country_code, {}).get('phone_code', '')
    return '+' + pcode + phone

def send_whatsapp(phone, message):
    """Send via WhatsApp Cloud API (Meta) — free 1000 conversations/month."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return False
    url = f'https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages'
    headers = {'Authorization': f'Bearer {WHATSAPP_TOKEN}', 'Content-Type': 'application/json'}
    data = {
        'messaging_product': 'whatsapp',
        'to': phone.lstrip('+'),
        'type': 'text',
        'text': {'body': message}
    }
    try:
        req = urllib.request.Request(url, json.dumps(data).encode(), headers)
        resp = urllib.request.urlopen(req, timeout=10)
        print(f'[WhatsApp] Sent to {phone}: {message}')
        return True
    except Exception as e:
        print(f'[WhatsApp] Error for {phone}: {e}')
        return False

def send_sms(phone, message):
    """Send SMS via Twilio."""
    if not TWILIO_SID or not TWILIO_TOKEN or not TWILIO_FROM:
        return False
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM, to=phone)
        print(f'[SMS] Sent to {phone}: {message}')
        return True
    except Exception as e:
        print(f'[SMS] Twilio error for {phone}: {e}')
        return False

# GSM Modem serial port (USB dongle with SIM). Set env var or auto-detect.
GSM_MODEM_PORT = os.environ.get('GSM_MODEM_PORT', '')  # e.g. COM3 /dev/ttyUSB0
GSM_MODEM_BAUD = int(os.environ.get('GSM_MODEM_BAUD', '115200'))

def send_sms_via_modem(phone, message):
    """Send SMS via USB GSM modem (AT commands) — free if SIM has SMS bundle."""
    if not GSM_MODEM_PORT:
        return False
    try:
        import serial
        ser = serial.Serial(GSM_MODEM_PORT, GSM_MODEM_BAUD, timeout=5)
        ser.write(b'AT+CMGF=1\r')
        import time; time.sleep(0.5)
        ser.write(f'AT+CMGS="{phone}"\r'.encode())
        time.sleep(0.5)
        ser.write(message.encode() + b'\x1A')
        time.sleep(2)
        ser.close()
        print(f'[GSM Modem] Sent to {phone}: {message}')
        return True
    except Exception as e:
        print(f'[GSM Modem] Error: {e}')
        return False

def send_notification(phone, message, country_code='cm'):
    """Send: WhatsApp (free) → GSM Modem (free) → Twilio SMS → console."""
    phone = format_phone(phone, country_code)
    if send_whatsapp(phone, message):
        return True
    if send_sms_via_modem(phone, message):
        return True
    if send_sms(phone, message):
        return True
    print(f'[NOTIFICATION] (log only) To {phone}: {message}')
    return True

def send_departure_reminders():
    """Check for upcoming departures and send notifications."""
    for mins in (90, 45):
        bookings = get_upcoming_bookings(mins)
        for bk in bookings:
            ntype = f'departure_{mins}min'
            if notification_sent(bk['id'], ntype):
                continue
            msg = _('Reminder: Your trip {from_city} → {to_city} on {agency_name} departs at {time}. Seat {seat}. Ref: {ref}.').format(
                from_city=bk['from_city'], to_city=bk['to_city'],
                agency_name=bk['agency_name'], time=bk['stime'],
                seat=bk['seat_number'], ref=bk['booking_ref']
            )
            send_notification(bk['phone'], msg, bk['agency_country'])
            log_notification(bk['id'], ntype)

def sms_scheduler_loop():
    """Background thread that runs departure checks every 60s."""
    import time
    with app.app_context():
        while True:
            try:
                send_departure_reminders()
            except Exception as e:
                print(f'[SMS Scheduler] Error: {e}')
            time.sleep(60)

import threading
threading.Thread(target=sms_scheduler_loop, daemon=True).start()

# ── Rate Limiter (in-memory, per IP) ──
login_attempts = defaultdict(list)
RATE_LIMIT_WINDOW = 15  # minutes
RATE_LIMIT_MAX = 10     # max attempts per window

def is_rate_limited(ip):
    now = datetime.now()
    attempts = login_attempts[ip]
    attempts[:] = [t for t in attempts if now - t < timedelta(minutes=RATE_LIMIT_WINDOW)]
    if len(attempts) >= RATE_LIMIT_MAX:
        return True, round(RATE_LIMIT_WINDOW - (now - attempts[0]).total_seconds() / 60)
    attempts.append(now)
    return False, 0

# ── IP Geolocation — auto-detect country on first visit ──
def _detect_country_by_ip():
    """Detect user's country via IP geolocation. Returns 2-letter code or None."""
    try:
        req = urllib.request.Request(
            'http://ip-api.com/json/',
            headers={'User-Agent': 'AFRI Trans/1.0'},
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
        if data.get('status') == 'success':
            code = data['countryCode'].lower()
            if code in COUNTRIES:
                return code
    except Exception:
        pass
    return None

@app.before_request
def auto_set_country():
    """On first visit, detect country by IP and auto-select it."""
    if 'country' not in session:
        detected = _detect_country_by_ip()
        if detected:
            session['country'] = detected
            c = COUNTRIES[detected]
            session['lang'] = c['lang']
        else:
            session['country'] = 'cm'
            session['lang'] = 'en'

# ── Translation Engine ──
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
_translations_cache = {}

def load_translations(lang):
    if lang in _translations_cache:
        return _translations_cache[lang]
    path = os.path.join(TRANSLATIONS_DIR, f'{lang}.json')
    if not os.path.exists(path):
        path = os.path.join(TRANSLATIONS_DIR, 'en.json')
    with open(path, 'r', encoding='utf-8') as f:
        _translations_cache[lang] = json.load(f)
    return _translations_cache[lang]

def get_current_lang():
    return session.get('lang', request.cookies.get('lang', 'en'))

def _(text):
    lang = get_current_lang()
    t = load_translations(lang)
    return t.get(text, text)

@app.context_processor
def inject_globals():
    country_code = session.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    all_anns = get_announcements(active_only=True, country=country_code)
    all_ann_ids = [a['id'] for a in all_anns]
    unread_count = len(all_anns)
    def ann_msg(ann):
        lang = get_current_lang()
        LANG_COL = {
            'fr': 'message_fr', 'ar': 'message_ar', 'pt': 'message_pt',
            'sw': 'message_sw', 'am': 'message_am', 'so': 'message_so',
            'ti': 'message_ti', 'es': 'message_es', 'af': 'message_af',
            'zu': 'message_zu',
        }
        if lang == 'en':
            return ann.get('message', '')
        col = LANG_COL.get(lang)
        if col and ann.get(col):
            return ann[col]
        return ann.get('message', '')
    def flag_emoji(code):
        if not code or len(code) != 2: return ''
        return chr(127462 + ord(code[0]) - 97) + chr(127462 + ord(code[1]) - 97)
    return dict(_=_, current_lang=get_current_lang(), ann_msg=ann_msg, cities=c['cities'], country=c, country_code=country_code, COUNTRIES=COUNTRIES, today=date.today().isoformat(), country_languages=c.get('languages', ['en']), vip_surcharge=c.get('vip_surcharge', 3000), country_providers=get_country_providers(), total_ann_count=unread_count, all_ann_ids=all_ann_ids, flag_emoji=flag_emoji)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    name = ''
    role = 'user'
    if session.get('agency_id'):
        a = get_agency(session['agency_id'])
        if a: name, role = a['name'], 'agency'
    elif session.get('ministry') and session.get('super_admin_id'):
        name, role = session.get('super_admin_email', 'Ministry'), 'ministry'
    if request.method == 'POST':
        msg = request.form.get('message', '').strip()
        if msg:
            add_feedback(name, role, msg)
            body = f'''
            <h3>New Feedback Submission</h3>
            <p><strong>Name:</strong> {name or 'Guest'}</p>
            <p><strong>Role:</strong> {role}</p>
            <p><strong>Message:</strong></p>
            <blockquote style="padding:12px; background:#f5f5f5; border-left:4px solid #c62828;">{msg}</blockquote>
            '''
            send_email(FEEDBACK_EMAIL, 'AFRI Trans - New Feedback', body)
            flash(_('Thank you for your feedback!'), 'success')
        else:
            flash(_('Please write a message.'), 'error')
        return redirect(url_for('feedback'))
    return render_template('feedback.html', name=name, role=role)

@app.route('/feedback/all')
def feedback_all():
    if not session.get('ministry') or not session.get('super_admin_id'):
        flash(_('Access denied.'), 'error')
        return redirect(url_for('feedback'))
    all_fb = get_all_feedback()
    return render_template('feedback_all.html', feedbacks=all_fb)

@app.route('/lang/<lang>')
def set_lang(lang):
    if lang not in ('en', 'fr', 'ar', 'pt', 'sw', 'am', 'so', 'ti', 'es', 'af', 'zu'):
        lang = 'en'
    session['lang'] = lang
    resp = make_response(redirect(request.referrer or url_for('index')))
    resp.set_cookie('lang', lang, max_age=365*24*3600)
    return resp

@app.route('/set-country/<code>')
def set_country(code):
    if code not in COUNTRIES:
        code = 'cm'
    session['country'] = code
    # Clear auth sessions when switching country — you are not
    # the ministry/agency of a country you just switched to
    session.pop('agency_id', None)
    session.pop('ministry', None)
    session.pop('ministry_1fa', None)
    session.pop('ministry_country', None)
    session.pop('super_admin_id', None)
    session.pop('super_admin_email', None)
    session.pop('read_notification_ids', None)
    c = COUNTRIES[code]
    if c['lang'] != get_current_lang():
        return redirect(url_for('set_lang', lang=c['lang']))
    return redirect(request.referrer or url_for('index'))

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

CITIES = [
    "Yaoundé", "Douala", "Bafoussam", "Bamenda", "Garoua", "Maroua",
    "Ngaoundéré", "Buéa", "Limbé", "Kribi", "Bertoua", "Ebolowa",
    "Dschang", "Foumban", "Kumba", "Tiko", "Bafang", "Sangmélima"
]

COUNTRIES = {
    'cm': {'name': 'Cameroon', 'flag_colors': ['#007a5e','#ce1126','#fcd116'], 'currency': 'FCFA', 'currency_code': 'XAF', 'ref_prefix': 'CM', 'cities': ["Yaoundé","Douala","Bafoussam","Bamenda","Garoua","Maroua","Ngaoundéré","Buéa","Limbé","Kribi","Bertoua","Ebolowa","Dschang","Foumban","Kumba","Tiko","Bafang","Sangmélima"], 'lang': 'en', 'languages': ['en','fr'], 'providers': ['mtn_momo', 'orange_money'], 'phone_code': '237', 'vip_surcharge': 3000},
    'ng': {'name': 'Nigeria', 'flag_colors': ['#008751','#ffffff','#008751'], 'currency': '₦', 'currency_code': 'NGN', 'ref_prefix': 'NG', 'cities': ["Lagos","Abuja","Port Harcourt","Ibadan","Kano","Kaduna","Enugu","Aba","Jos","Benin City"], 'lang': 'en', 'languages': ['en'], 'providers': ['opay', 'palmpay', 'mtn_momo'], 'phone_code': '234', 'vip_surcharge': 5000},
    'gh': {'name': 'Ghana', 'flag_colors': ['#ef3340','#ffd100','#009739'], 'currency': '₵', 'currency_code': 'GHS', 'ref_prefix': 'GH', 'cities': ["Accra","Kumasi","Takoradi","Tamale","Cape Coast","Tema","Ho","Sunyani"], 'lang': 'en', 'languages': ['en'], 'providers': ['mtn_momo', 'vodafone_cash'], 'phone_code': '233', 'vip_surcharge': 30},
    'ke': {'name': 'Kenya', 'flag_colors': ['#000000','#ffffff','#bb0000','#ffffff','#006600'], 'currency': 'KSh', 'currency_code': 'KES', 'ref_prefix': 'KE', 'cities': ["Nairobi","Mombasa","Kisumu","Nakuru","Eldoret","Thika","Malindi","Nyeri"], 'lang': 'en', 'languages': ['en', 'sw'], 'providers': ['mpesa', 'airtel_money'], 'phone_code': '254', 'vip_surcharge': 500},
    'eg': {'name': 'Egypt', 'flag_colors': ['#c8102e','#ffffff','#000000'], 'currency': 'E£', 'currency_code': 'EGP', 'ref_prefix': 'EG', 'cities': ["Cairo","Alexandria","Giza","Luxor","Aswan","Sharm El Sheikh","Hurghada","Port Said","Suez","Mansoura"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['vodafone_cash', 'fawry'], 'phone_code': '20', 'vip_surcharge': 100},
    'ma': {'name': 'Morocco', 'flag_colors': ['#c1272d','#006233','#c1272d'], 'currency': 'MAD', 'currency_code': 'MAD', 'ref_prefix': 'MA', 'cities': ["Casablanca","Rabat","Marrakech","Fez","Tangier","Agadir","Meknes","Oujda","Kenitra","Tetouan"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '212', 'vip_surcharge': 50},
    'dz': {'name': 'Algeria', 'flag_colors': ['#006633','#ffffff','#d21034'], 'currency': 'DZD', 'currency_code': 'DZD', 'ref_prefix': 'DZ', 'cities': ["Algiers","Oran","Constantine","Annaba","Blida","Setif","Tlemcen","Mostaganem","Biskra","Tizi Ouzou"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['baridimob', 'mtn_momo'], 'phone_code': '213', 'vip_surcharge': 500},
    'tn': {'name': 'Tunisia', 'flag_colors': ['#e70013','#ffffff','#e70013'], 'currency': 'TND', 'currency_code': 'TND', 'ref_prefix': 'TN', 'cities': ["Tunis","Sfax","Sousse","Kairouan","Gabes","Bizerte","Ariana","Gafsa","Monastir","La Marsa"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '216', 'vip_surcharge': 10},
    'ly': {'name': 'Libya', 'flag_colors': ['#e70013','#000000','#239e46'], 'currency': 'LYD', 'currency_code': 'LYD', 'ref_prefix': 'LY', 'cities': ["Tripoli","Benghazi","Misrata","Tarhuna","Al Khums","Zawiya","Derna","Sabha","Tobruk","Zuwara"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '218', 'vip_surcharge': 10},
    'sd': {'name': 'Sudan', 'flag_colors': ['#d21034','#ffffff','#000000','#007229'], 'currency': 'SDG', 'currency_code': 'SDG', 'ref_prefix': 'SD', 'cities': ["Khartoum","Omdurman","Port Sudan","Kassala","El Obeid","Nyala","Wad Medani","Gedaref","Fasher","Dongola"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['mtn_momo', 'orange_money'], 'phone_code': '249', 'vip_surcharge': 1500},
    'mr': {'name': 'Mauritania', 'flag_colors': ['#d01c1f','#00a95c','#d01c1f'], 'currency': 'MRU', 'currency_code': 'MRU', 'ref_prefix': 'MR', 'cities': ["Nouakchott","Nouadhibou","Kiffa","Zouerate","Kaedi","Rosso","Atar","Selibaby","Tidjikja","Aleg"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '222', 'vip_surcharge': 200},
    'sn': {'name': 'Senegal', 'flag_colors': ['#00853f','#fdef42','#e31b23'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'SN', 'cities': ["Dakar","Thiès","Saint-Louis","Ziguinchor","Kaolack","Touba","Mbour","Louga","Tambacounda","Rufisque"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'wave'], 'phone_code': '221', 'vip_surcharge': 3000},
    'ci': {'name': "Côte d'Ivoire", 'flag_colors': ['#f77f00','#ffffff','#009e60'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'CI', 'cities': ["Abidjan","Yamoussoukro","Bouaké","Daloa","Korhogo","San-Pédro","Gagnoa","Man","Divo","Anyama"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo', 'wave'], 'phone_code': '225', 'vip_surcharge': 3000},
    'ml': {'name': 'Mali', 'flag_colors': ['#14b53a','#fcd116','#ce1126'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'ML', 'cities': ["Bamako","Timbuktu","Gao","Mopti","Koutiala","Segou","Kayes","Sikasso","Kati","Nioro"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '223', 'vip_surcharge': 3000},
    'ne': {'name': 'Niger', 'flag_colors': ['#e05206','#ffffff','#0db02b'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'NE', 'cities': ["Niamey","Zinder","Maradi","Agadez","Tahoua","Dosso","Tillaberi","Diffa","Birni N Konni","Gaya"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '227', 'vip_surcharge': 3000},
    'bf': {'name': 'Burkina Faso', 'flag_colors': ['#ef2b2d','#fcd116','#009e49'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'BF', 'cities': ["Ouagadougou","Bobo-Dioulasso","Koudougou","Banfora","Ouahigouya","Dédougou","Fada N'Gourma","Tenkodogo","Réo","Houndé"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '226', 'vip_surcharge': 3000},
    'gn': {'name': 'Guinea', 'flag_colors': ['#ce1126','#fcd116','#009460'], 'currency': 'GNF', 'currency_code': 'GNF', 'ref_prefix': 'GN', 'cities': ["Conakry","Nzérékoré","Kankan","Kindia","Labe","Guéckédou","Mamou","Fria","Boké","Siguiri"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '224', 'vip_surcharge': 3000},
    'bj': {'name': 'Benin', 'flag_colors': ['#008751','#fcd116','#e8112d'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'BJ', 'cities': ["Porto-Novo","Cotonou","Parakou","Djougou","Bohicon","Abomey","Natitingou","Lokossa","Ouidah","Kandi"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '229', 'vip_surcharge': 3000},
    'tg': {'name': 'Togo', 'flag_colors': ['#d21034','#ffffff','#006a4e','#ffce00'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'TG', 'cities': ["Lomé","Sokodé","Kara","Atakpamé","Kpalimé","Bassar","Tsévié","Aného","Mango","Dapaong"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '228', 'vip_surcharge': 3000},
    'sl': {'name': 'Sierra Leone', 'flag_colors': ['#1eb53a','#ffffff','#0072c6'], 'currency': 'SLL', 'currency_code': 'SLL', 'ref_prefix': 'SL', 'cities': ["Freetown","Bo","Kenema","Makeni","Koidu","Port Loko","Kabala","Pujehun","Bonthe","Kailahun"], 'lang': 'en', 'languages': ['en'], 'providers': ['mtn_momo', 'orange_money'], 'phone_code': '232', 'vip_surcharge': 30},
    'lr': {'name': 'Liberia', 'flag_colors': ['#ef3340','#ffffff','#00205b'], 'currency': 'LRD', 'currency_code': 'LRD', 'ref_prefix': 'LR', 'cities': ["Monrovia","Gbarnga","Buchanan","Harper","Zwedru","Greenville","Tubmanburg","Voinjama","Robertsport","Bensonville"], 'lang': 'en', 'languages': ['en'], 'providers': ['mtn_momo', 'orange_money'], 'phone_code': '231', 'vip_surcharge': 300},
    'gm': {'name': 'Gambia', 'flag_colors': ['#ce1126','#ffffff','#0c1c8c','#3a7728'], 'currency': 'GMD', 'currency_code': 'GMD', 'ref_prefix': 'GM', 'cities': ["Banjul","Serekunda","Brikama","Bakau","Farafenni","Lamin","Basse Santa Su","Gunjur","Kuntaur","Janjanbureh"], 'lang': 'en', 'languages': ['en'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '220', 'vip_surcharge': 50},
    'gw': {'name': 'Guinea-Bissau', 'flag_colors': ['#ce1126','#fcd116','#009739'], 'currency': 'FCFA', 'currency_code': 'XOF', 'ref_prefix': 'GW', 'cities': ["Bissau","Bafatá","Gabú","Bissorã","Bolama","Cacheu","Catió","Bubaque","Mansoa","Farim"], 'lang': 'pt', 'languages': ['pt', 'en'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '245', 'vip_surcharge': 3000},
    'cv': {'name': 'Cape Verde', 'flag_colors': ['#003da5','#ffffff','#ef3340','#ffffff','#ffd100'], 'currency': 'CVE', 'currency_code': 'CVE', 'ref_prefix': 'CV', 'cities': ["Praia","Mindelo","Santa Maria","São Filipe","Assomada","Tarrafal","Porto Novo","Ribeira Grande","Pedra Badejo","São Domingos"], 'lang': 'pt', 'languages': ['pt', 'en'], 'providers': ['emola', 'mpesa'], 'phone_code': '238', 'vip_surcharge': 300},
    'td': {'name': 'Chad', 'flag_colors': ['#002664','#fecb00','#c60c30'], 'currency': 'FCFA', 'currency_code': 'XAF', 'ref_prefix': 'TD', 'cities': ["N'Djamena","Moundou","Sarh","Abeche","Kelo","Am Timan","Doba","Pala","Bongor","Mongo"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '235', 'vip_surcharge': 3000},
    'cf': {'name': 'Central African Republic', 'flag_colors': ['#003082','#ffffff','#289728','#ffce00','#d21034'], 'currency': 'FCFA', 'currency_code': 'XAF', 'ref_prefix': 'CF', 'cities': ["Bangui","Bimbo","Berbérati","Bambari","Bouar","Bossangoa","Bria","Nola","Kaga-Bandoro","Sibut"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '236', 'vip_surcharge': 3000},
    'ga': {'name': 'Gabon', 'flag_colors': ['#009e60','#fcd116','#3a75c4'], 'currency': 'FCFA', 'currency_code': 'XAF', 'ref_prefix': 'GA', 'cities': ["Libreville","Port-Gentil","Franceville","Oyem","Moanda","Mouila","Lambaréné","Tchibanga","Koulamoutou","Makokou"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '241', 'vip_surcharge': 3000},
    'cg': {'name': 'Congo', 'flag_colors': ['#009543','#fcd116','#dc241f'], 'currency': 'FCFA', 'currency_code': 'XAF', 'ref_prefix': 'CG', 'cities': ["Brazzaville","Pointe-Noire","Dolisie","Nkayi","Ouesso","Madingou","Sibiti","Impfondo","Gamboma","Owando"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '242', 'vip_surcharge': 3000},
    'cd': {'name': 'DR Congo', 'flag_colors': ['#007fff','#f7d618','#ce1021'], 'currency': 'CDF', 'currency_code': 'CDF', 'ref_prefix': 'CD', 'cities': ["Kinshasa","Lubumbashi","Mbuji-Mayi","Kananga","Kisangani","Bukavu","Tshikapa","Kolwezi","Likasi","Goma"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mpesa', 'airtel_money'], 'phone_code': '243', 'vip_surcharge': 5000},
    'gq': {'name': 'Equatorial Guinea', 'flag_colors': ['#3e9a00','#ffffff','#e8112d'], 'currency': 'FCFA', 'currency_code': 'XAF', 'ref_prefix': 'GQ', 'cities': ["Malabo","Bata","Mongomo","Ebebiyín","Aconibe","Añisoc","Luba","Evinayong","Nsok","Bicurga"], 'lang': 'es', 'languages': ['es', 'en'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '240', 'vip_surcharge': 3000},
    'st': {'name': 'São Tomé and Príncipe', 'flag_colors': ['#d21034','#12ad2b','#ffce00','#12ad2b'], 'currency': 'STN', 'currency_code': 'STN', 'ref_prefix': 'ST', 'cities': ["São Tomé","Santo António","Neves","Trindade","Santana","Guadalupe","São João dos Angolares","Caldeiras","Ribeira Afonso","Monte Mário"], 'lang': 'pt', 'languages': ['pt', 'en'], 'providers': ['emola', 'mpesa'], 'phone_code': '239', 'vip_surcharge': 150},
    'rw': {'name': 'Rwanda', 'flag_colors': ['#00a3d9','#fad201','#20603d'], 'currency': 'RWF', 'currency_code': 'RWF', 'ref_prefix': 'RW', 'cities': ["Kigali","Butare","Gisenyi","Ruhengeri","Gitarama","Cyangugu","Byumba","Kibungo","Nyanza","Rwamagana"], 'lang': 'en', 'languages': ['en','fr'], 'providers': ['mtn_momo', 'airtel_money'], 'phone_code': '250', 'vip_surcharge': 3000},
    'bi': {'name': 'Burundi', 'flag_colors': ['#1eb53a','#ce1126','#ffffff'], 'currency': 'BIF', 'currency_code': 'BIF', 'ref_prefix': 'BI', 'cities': ["Gitega","Bujumbura","Ngozi","Ruyigi","Kayanza","Bururi","Rutana","Muramvya","Makamba","Cibitoke"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '257', 'vip_surcharge': 3000},
    'ug': {'name': 'Uganda', 'flag_colors': ['#d90000','#fcd116','#000000'], 'currency': 'UGX', 'currency_code': 'UGX', 'ref_prefix': 'UG', 'cities': ["Kampala","Gulu","Mbarara","Jinja","Mbale","Masaka","Lira","Soroti","Arua","Fort Portal"], 'lang': 'en', 'languages': ['en', 'sw'], 'providers': ['mtn_momo', 'airtel_money'], 'phone_code': '256', 'vip_surcharge': 5000},
    'tz': {'name': 'Tanzania', 'flag_colors': ['#1eb53a','#fcd116','#000000','#00a3dd'], 'currency': 'TZS', 'currency_code': 'TZS', 'ref_prefix': 'TZ', 'cities': ["Dodoma","Dar es Salaam","Mwanza","Arusha","Mbeya","Tanga","Morogoro","Zanzibar City","Kigoma","Tabora"], 'lang': 'sw', 'languages': ['sw', 'en'], 'providers': ['mpesa', 'tigo_pesa', 'airtel_money'], 'phone_code': '255', 'vip_surcharge': 5000},
    'et': {'name': 'Ethiopia', 'flag_colors': ['#009a44','#fedd00','#ef3340'], 'currency': 'ETB', 'currency_code': 'ETB', 'ref_prefix': 'ET', 'cities': ["Addis Ababa","Dire Dawa","Mekelle","Adama","Gondar","Hawassa","Bahir Dar","Jimma","Dessie","Jijiga"], 'lang': 'am', 'languages': ['am', 'en'], 'providers': ['telebirr', 'mpesa'], 'phone_code': '251', 'vip_surcharge': 150},
    'so': {'name': 'Somalia', 'flag_colors': ['#4189dd','#ffffff','#4189dd'], 'currency': 'SOS', 'currency_code': 'SOS', 'ref_prefix': 'SO', 'cities': ["Mogadishu","Hargeisa","Kismayo","Baidoa","Galkayo","Merca","Bosaso","Beledweyne","Jowhar","Berbera"], 'lang': 'so', 'languages': ['so', 'en'], 'providers': ['zaad', 'evc_plus'], 'phone_code': '252', 'vip_surcharge': 5000},
    'dj': {'name': 'Djibouti', 'flag_colors': ['#6ab2e6','#ffffff','#12ad2b'], 'currency': 'DJF', 'currency_code': 'DJF', 'ref_prefix': 'DJ', 'cities': ["Djibouti City","Ali Sabieh","Tadjoura","Obock","Dikhil","Arta","Holhol","Yoboki","Randa","Loyada"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['orange_money', 'evc_plus'], 'phone_code': '253', 'vip_surcharge': 300},
    'ss': {'name': 'South Sudan', 'flag_colors': ['#000000','#ffffff','#007f2e','#ce1126','#0f47af'], 'currency': 'SSP', 'currency_code': 'SSP', 'ref_prefix': 'SS', 'cities': ["Juba","Wau","Malakal","Bor","Yei","Rumbek","Aweil","Torit","Bentiu","Kapoeta"], 'lang': 'en', 'languages': ['en'], 'providers': ['mtn_momo', 'orange_money'], 'phone_code': '211', 'vip_surcharge': 5000},
    'er': {'name': 'Eritrea', 'flag_colors': ['#12ad2b','#4189dd','#ce1126'], 'currency': 'ERN', 'currency_code': 'ERN', 'ref_prefix': 'ER', 'cities': ["Asmara","Keren","Massawa","Assab","Mendefera","Barentu","Decamhare","Mitsiwa","Nakfa","Tessenei"], 'lang': 'ti', 'languages': ['ti', 'en'], 'providers': ['mtn_momo', 'orange_money'], 'phone_code': '291', 'vip_surcharge': 50},
    'sc': {'name': 'Seychelles', 'flag_colors': ['#003f87','#fcd116','#d21034','#ffffff','#007f2e'], 'currency': 'SCR', 'currency_code': 'SCR', 'ref_prefix': 'SC', 'cities': ["Victoria","Praslin","La Digue","Beau Vallon","Anse Royale","Baie Sainte Anne","Takamaka","Anse Boileau","Port Glaud","Cascade"], 'lang': 'en', 'languages': ['en','fr'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '248', 'vip_surcharge': 50},
    'km': {'name': 'Comoros', 'flag_colors': ['#009739','#ffd100','#ffffff','#ef3340','#003da5'], 'currency': 'KMF', 'currency_code': 'KMF', 'ref_prefix': 'KM', 'cities': ["Moroni","Mutsamudu","Fomboni","Domoni","Mitsamiouli","Ouani","Moya","Simboa","Miringoni","Iconi"], 'lang': 'ar', 'languages': ['ar'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '269', 'vip_surcharge': 1000},
    'mu': {'name': 'Mauritius', 'flag_colors': ['#ce1126','#003f87','#fcd116','#009e60'], 'currency': 'MUR', 'currency_code': 'MUR', 'ref_prefix': 'MU', 'cities': ["Port Louis","Beau Bassin","Quatre Bornes","Curepipe","Vacoas","Triolet","Goodlands","Mahebourg","Moka","Flacq"], 'lang': 'en', 'languages': ['en'], 'providers': ['mpesa', 'orange_money'], 'phone_code': '230', 'vip_surcharge': 200},
    'mg': {'name': 'Madagascar', 'flag_colors': ['#ffffff','#ce1126','#009e60'], 'currency': 'MGA', 'currency_code': 'MGA', 'ref_prefix': 'MG', 'cities': ["Antananarivo","Toamasina","Antsirabe","Mahajanga","Fianarantsoa","Toliara","Antsiranana","Nosy Be","Morondava","Sambava"], 'lang': 'fr', 'languages': ['fr'], 'providers': ['mvola', 'orange_money'], 'phone_code': '261', 'vip_surcharge': 3000},
    'za': {'name': 'South Africa', 'flag_colors': ['#de3831','#ffffff','#007a4d','#002395','#ffb612','#000000'], 'currency': 'R', 'currency_code': 'ZAR', 'ref_prefix': 'ZA', 'cities': ["Johannesburg","Cape Town","Durban","Pretoria","Port Elizabeth","Bloemfontein","East London","Pietermaritzburg","Nelspruit","Rustenburg"], 'lang': 'en', 'languages': ['en', 'af', 'zu'], 'providers': ['snapsan', 'zapper'], 'phone_code': '27', 'vip_surcharge': 200},
    'ao': {'name': 'Angola', 'flag_colors': ['#ce1126','#000000','#ffd100'], 'currency': 'AOA', 'currency_code': 'AOA', 'ref_prefix': 'AO', 'cities': ["Luanda","Huambo","Lobito","Benguela","Lubango","Malanje","Namibe","Soyo","Uíge","Mbanza Congo"], 'lang': 'pt', 'languages': ['pt', 'en'], 'providers': ['emola', 'mpesa'], 'phone_code': '244', 'vip_surcharge': 3000},
    'mz': {'name': 'Mozambique', 'flag_colors': ['#009e60','#ffffff','#000000','#fcd116','#ce1126'], 'currency': 'MZN', 'currency_code': 'MZN', 'ref_prefix': 'MZ', 'cities': ["Maputo","Beira","Nampula","Chimoio","Quelimane","Tete","Xai-Xai","Pemba","Inhambane","Lichinga"], 'lang': 'pt', 'languages': ['pt', 'en'], 'providers': ['mpesa', 'emola'], 'phone_code': '258', 'vip_surcharge': 300},
    'zm': {'name': 'Zambia', 'flag_colors': ['#198a00','#ce1126','#000000','#e87a00'], 'currency': 'ZMW', 'currency_code': 'ZMW', 'ref_prefix': 'ZM', 'cities': ["Lusaka","Ndola","Kitwe","Livingstone","Kabwe","Chingola","Mufulira","Luanshya","Chipata","Kasama"], 'lang': 'en', 'languages': ['en'], 'providers': ['mtn_momo', 'airtel_money'], 'phone_code': '260', 'vip_surcharge': 50},
    'zw': {'name': 'Zimbabwe', 'flag_colors': ['#009739','#fce300','#ef3340','#000000','#ffffff'], 'currency': 'ZWG', 'currency_code': 'ZWG', 'ref_prefix': 'ZW', 'cities': ["Harare","Bulawayo","Chitungwiza","Mutare","Gweru","Kwekwe","Masvingo","Marondera","Kadoma","Victoria Falls"], 'lang': 'en', 'languages': ['en'], 'providers': ['ecocash', 'telecash'], 'phone_code': '263', 'vip_surcharge': 20},
    'mw': {'name': 'Malawi', 'flag_colors': ['#000000','#ce1126','#339e35'], 'currency': 'MWK', 'currency_code': 'MWK', 'ref_prefix': 'MW', 'cities': ["Lilongwe","Blantyre","Mzuzu","Zomba","Karonga","Kasungu","Mangochi","Salima","Nkhotakota","Mchinji"], 'lang': 'en', 'languages': ['en'], 'providers': ['mtn_momo', 'airtel_money'], 'phone_code': '265', 'vip_surcharge': 3000},
    'bw': {'name': 'Botswana', 'flag_colors': ['#75aadb','#ffffff','#000000'], 'currency': 'BWP', 'currency_code': 'BWP', 'ref_prefix': 'BW', 'cities': ["Gaborone","Francistown","Maun","Molepolole","Serowe","Selibe Phikwe","Kanye","Mochudi","Lobatse","Ramotswa"], 'lang': 'en', 'languages': ['en'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '267', 'vip_surcharge': 30},
    'na': {'name': 'Namibia', 'flag_colors': ['#003580','#ffffff','#ce1126','#ffffff','#009543'], 'currency': 'NAD', 'currency_code': 'NAD', 'ref_prefix': 'NA', 'cities': ["Windhoek","Rundu","Walvis Bay","Swakopmund","Oshakati","Otjiwarongo","Tsumeb","Keetmanshoop","Katima Mulilo","Grootfontein"], 'lang': 'en', 'languages': ['en'], 'providers': ['snapsan', 'orange_money'], 'phone_code': '264', 'vip_surcharge': 50},
    'ls': {'name': 'Lesotho', 'flag_colors': ['#00209f','#ffffff','#009543'], 'currency': 'LSL', 'currency_code': 'LSL', 'ref_prefix': 'LS', 'cities': ["Maseru","Teyateyaneng","Maputsoe","Leribe","Mafeteng","Mohale's Hoek","Butha-Buthe","Qacha's Nek","Quthing","Mokhotlong"], 'lang': 'en', 'languages': ['en'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '266', 'vip_surcharge': 50},
    'sz': {'name': 'Eswatini', 'flag_colors': ['#003da5','#fcd116','#ce1126','#fcd116','#003da5'], 'currency': 'SZL', 'currency_code': 'SZL', 'ref_prefix': 'SZ', 'cities': ["Mbabane","Manzini","Big Bend","Malkerns","Nhlangano","Siteki","Piggs Peak","Hluti","Simunye","Lobamba"], 'lang': 'en', 'languages': ['en'], 'providers': ['orange_money', 'mtn_momo'], 'phone_code': '268', 'vip_surcharge': 30},
}

# Subscription pricing per currency (monthly / semiannual / annual)
SUBSCRIPTION_PRICES = {
    'XAF': {'monthly': 58000, 'semiannual': 250000, 'annual': 500000},
    'XOF': {'monthly': 58000, 'semiannual': 250000, 'annual': 500000},
    'NGN': {'monthly': 15000, 'semiannual': 75000, 'annual': 150000},
}

PERIODS = [
    {"key": "morning", "label": "Morning", "range": "06:00 - 12:00", "icon": "fa-cloud-sun"},
    {"key": "afternoon", "label": "Afternoon", "range": "12:00 - 18:00", "icon": "fa-sun"},
    {"key": "night", "label": "Night", "range": "18:00 - 23:00", "icon": "fa-moon"}
]

PERIOD_TR = {'Morning': 'Morning', 'Afternoon': 'Afternoon', 'Night': 'Night'}

def gen_ref():
    n = get_next_ref()
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    country_code = session.get('country', 'cm')
    prefix = COUNTRIES.get(country_code, COUNTRIES['cm'])['ref_prefix']
    return f"{prefix}-{letters}-{n:04d}"

def period_key(time_str):
    h = int(time_str.split(':')[0])
    if h < 12: return 'morning'
    if h < 18: return 'afternoon'
    return 'night'

def auto_expire_trips():
    db = get_db()
    now = datetime.now()
    changed = False
    for s in db.execute("SELECT * FROM schedules WHERE status = 'active'").fetchall():
        try:
            sdt = datetime.strptime(f"{s['date']} {s['time']}", "%Y-%m-%d %H:%M")
        except (ValueError, KeyError):
            continue
        if now - sdt > timedelta(hours=2):
            db.execute("UPDATE schedules SET status = 'completed' WHERE id = ?", (s['id'],))
            changed = True
    for s in db.execute("SELECT * FROM schedules WHERE status = 'completed'").fetchall():
        try:
            sdt = datetime.strptime(f"{s['date']} {s['time']}", "%Y-%m-%d %H:%M")
        except (ValueError, KeyError):
            continue
        if now - sdt > timedelta(hours=48):
            db.execute("UPDATE buses SET status = 'available' WHERE id = ?", (s['bus_id'],))
            changed = True
    for bk in db.execute("SELECT * FROM bookings WHERE status IN ('confirmed', 'pending')").fetchall():
        s = db.execute("SELECT * FROM schedules WHERE id = ?", (bk['schedule_id'],)).fetchone()
        if not s: continue
        try:
            sdt = datetime.strptime(f"{s['date']} {s['time']}", "%Y-%m-%d %H:%M")
        except (ValueError, KeyError):
            continue
        if now > sdt + timedelta(hours=24):
            db.execute("UPDATE bookings SET status = 'expired' WHERE id = ?", (bk['id'],))
            changed = True
    if changed:
        db.commit()
    db.close()

def booking_has_departed(schedule):
    try:
        dep = datetime.strptime(f"{schedule['date']} {schedule['time']}", "%Y-%m-%d %H:%M")
        return datetime.now() > dep
    except (ValueError, KeyError):
        return True

def currency_filter(v):
    country_code = session.get('country', 'cm')
    sym = COUNTRIES.get(country_code, COUNTRIES['cm'])['currency']
    return f"{int(v):,} {sym}"
app.jinja_env.filters['currency'] = currency_filter

# ── Payment Provider Definitions ──
PAYMENT_PROVIDERS = {
    'mtn_momo': {'name': 'MTN MoMo', 'icon': 'fa-mobile-screen', 'color': 'var(--flag-3)'},
    'orange_money': {'name': 'Orange Money', 'icon': 'fa-mobile-screen', 'color': '#e65100'},
    'mpesa': {'name': 'M-Pesa', 'icon': 'fa-mobile-screen', 'color': '#00a3d9'},
    'tigo_pesa': {'name': 'Tigo Pesa', 'icon': 'fa-mobile-screen', 'color': '#d21034'},
    'airtel_money': {'name': 'Airtel Money', 'icon': 'fa-mobile-screen', 'color': '#ce1126'},
    'emola': {'name': 'EMOLA', 'icon': 'fa-mobile-screen', 'color': '#ce1126'},
    'vodafone_cash': {'name': 'Vodafone Cash', 'icon': 'fa-mobile-screen', 'color': '#e70013'},
    'ecocash': {'name': 'EcoCash', 'icon': 'fa-mobile-screen', 'color': '#009e60'},
    'wave': {'name': 'Wave', 'icon': 'fa-mobile-screen', 'color': '#009e60'},
    'telebirr': {'name': 'Telebirr', 'icon': 'fa-mobile-screen', 'color': '#078930'},
    'zaad': {'name': 'Zaad', 'icon': 'fa-mobile-screen', 'color': '#4189dd'},
    'evc_plus': {'name': 'EVC Plus', 'icon': 'fa-mobile-screen', 'color': '#4189dd'},
    'opay': {'name': 'Opay', 'icon': 'fa-mobile-screen', 'color': '#008751'},
    'palmpay': {'name': 'PalmPay', 'icon': 'fa-mobile-screen', 'color': '#0072c6'},
    'fawry': {'name': 'Fawry', 'icon': 'fa-mobile-screen', 'color': '#d21034'},
    'baridimob': {'name': 'BaridiMob', 'icon': 'fa-mobile-screen', 'color': '#006233'},
    'snapsan': {'name': 'SnapScan', 'icon': 'fa-mobile-screen', 'color': '#002395'},
    'zapper': {'name': 'Zapper', 'icon': 'fa-mobile-screen', 'color': '#003da5'},
    'mvola': {'name': 'MVola', 'icon': 'fa-mobile-screen', 'color': '#ce1126'},
    'telecash': {'name': 'Telecash', 'icon': 'fa-mobile-screen', 'color': '#fcd116'},
}

def get_vip_surcharge(bus=None):
    if bus and bus.get('vip_price') is not None:
        return int(bus['vip_price'])
    country_code = session.get('country', 'cm')
    return COUNTRIES.get(country_code, COUNTRIES['cm']).get('vip_surcharge', 3000)

def get_country_providers():
    country_code = session.get('country', 'cm')
    codes = COUNTRIES.get(country_code, COUNTRIES['cm']).get('providers', ['mtn_momo', 'orange_money'])
    return [{'code': c, **PAYMENT_PROVIDERS.get(c, {'name': c, 'icon': 'fa-mobile-screen', 'color': '#888'})} for c in codes]

def bus_layout(bus_type='standard', capacity=71):
    cls = 'vip' if bus_type == 'vip' else 'std'
    rows, n = [], 1

    # ── Minibus (14-20 seats): 1+2 Asymmetric, Offset Side Aisle ──
    if capacity <= 20:
        PER_ROW = 3  # 1 left + 2 right per row
        reg = capacity // PER_ROW
        rem = capacity % PER_ROW
        if rem == 0:
            reg -= 1
            rem = PER_ROW
        for _ in range(reg):
            rows.append([
                {'n': n, 'c': cls},
                None,
                {'n': n+1, 'c': cls}, {'n': n+2, 'c': cls},
            ])
            n += PER_ROW
        left = (rem + 2) // 3
        middle = rem - left
        last = [{'n': n + i, 'c': cls} for i in range(left)]
        last.append(None)
        for i in range(middle):
            last.append({'n': n + left + i, 'c': cls})
        while len(last) < 4:
            last.append(None)
        rows.append(last)
        return rows

    # ── Midi-Bus (22-35 seats): 2+2 Narrow Centre ──
    if capacity <= 35:
        PER_ROW = 4
        reg = capacity // PER_ROW
        rem = capacity % PER_ROW
        if rem == 0:
            reg -= 1
            rem = PER_ROW
        for _ in range(reg):
            rows.append([
                {'n': n, 'c': cls}, {'n': n+1, 'c': cls},
                None,
                {'n': n+2, 'c': cls}, {'n': n+3, 'c': cls},
            ])
            n += PER_ROW
        left = (rem + 1) // 2
        right = rem - left
        last = [{'n': n + i, 'c': cls} for i in range(left)]
        last.append({'door': 'rear_exit'})
        for i in range(right):
            last.append({'n': n + left + i, 'c': cls})
        while len(last) < 5:
            last.append(None)
        rows.append(last)
        return rows

    # ── Standard Coach (36-52 seats): 2+2 Symmetric, Sunken Centre ──
    if capacity <= 52:
        PER_ROW = 4
        reg = capacity // PER_ROW
        rem = capacity % PER_ROW
        if rem == 0:
            reg -= 1
            rem = PER_ROW
        for _ in range(reg):
            rows.append([
                {'n': n, 'c': cls}, {'n': n+1, 'c': cls},
                None,
                {'n': n+2, 'c': cls}, {'n': n+3, 'c': cls},
            ])
            n += PER_ROW
        left = (rem + 1) // 2
        right = rem - left
        last = [{'n': n + i, 'c': cls} for i in range(left)]
        last.append({'door': 'rear_exit'})
        for i in range(right):
            last.append({'n': n + left + i, 'c': cls})
        while len(last) < 5:
            last.append(None)
        rows.append(last)
        return rows

    # ── High-Cap Coach (53-80 seats): 3+2 Layout, Standard Centre ──
    PER_ROW = 5  # 3 left + 2 right
    reg = capacity // PER_ROW
    rem = capacity % PER_ROW
    if rem == 0:
        reg -= 1
        rem = PER_ROW
    for _ in range(reg):
        rows.append([
            {'n': n, 'c': cls}, {'n': n+1, 'c': cls}, {'n': n+2, 'c': cls},
            None,
            {'n': n+3, 'c': cls}, {'n': n+4, 'c': cls},
            None,
        ])
        n += PER_ROW
    left = (rem + 1) // 2
    right = rem - left
    last = [{'n': n + i, 'c': cls} for i in range(left)]
    for _ in range(left, 3):
        last.append(None)
    last.append(None)
    for i in range(right):
        last.append({'n': n + left + i, 'c': cls})
    for _ in range(right, 2):
        last.append(None)
    last.append({'door': 'rear_exit'})
    rows.append(last)
    return rows

def _grid_config(layout):
    cols = len(layout[0]) if layout else 5
    if cols == 4:
        grid_style = '1fr 24px 1fr 1fr'
    elif cols == 7:
        grid_style = '1fr 1fr 1fr 24px 1fr 1fr 1fr'
    else:
        grid_style = '1fr 1fr 24px 1fr 1fr'
    return cols, grid_style

def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def ticket_image(bk, s, route, bus, agency, period_label, is_expired=False, country=None):
    W, H = 580, 820
    if country:
        FLAG1 = _hex_to_rgb(country['flag_colors'][0])
        FLAG2 = _hex_to_rgb(country['flag_colors'][1])
        FLAG3 = _hex_to_rgb(country['flag_colors'][2])
        CURR_SYM = country['currency']
        CNAME = country['name']
        vs = bus.get('vip_price') if bus and bus.get('vip_price') is not None else country.get('vip_surcharge', 3000)
    else:
        FLAG1 = (0, 122, 94)
        FLAG2 = (206, 17, 38)
        FLAG3 = (252, 209, 22)
        CURR_SYM = 'FCFA'
        CNAME = 'Cameroon'
        vs = bus.get('vip_price') if bus and bus.get('vip_price') is not None else 3000
    WHITE = (255, 255, 255)
    DARK = (26, 26, 46)
    LGRAY = (248, 249, 250)
    GRAY = (136, 136, 136)
    LIGHT = (238, 238, 238)
    try:
        fb = ImageFont.truetype("arialbd.ttf", 26)
        fb2 = ImageFont.truetype("arialbd.ttf", 20)
        fb3 = ImageFont.truetype("arialbd.ttf", 14)
        fn = ImageFont.truetype("arial.ttf", 14)
        fs = ImageFont.truetype("arial.ttf", 11)
        fxs = ImageFont.truetype("arial.ttf", 10)
        fseat = ImageFont.truetype("arialbd.ttf", 34)
        fref = ImageFont.truetype("arialbd.ttf", 22)
    except:
        fb = fb2 = fb3 = fn = fs = fxs = fseat = fref = ImageFont.load_default()

    img = Image.new('RGB', (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    xm = 20

    draw.rounded_rectangle([5, 5, W-5, H-5], radius=16, outline=FLAG1, width=3)

    draw.rectangle([8, 8, W-8, 90], fill=(0, 0, 0))
    draw.rounded_rectangle([8, 8, W-8, 95], radius=14, fill=(0, 0, 0))
    draw.rectangle([8, 18, W-8, 90], fill=(0, 0, 0))

    fw, fh = 8, 18
    yf = 16
    for i, c in enumerate([FLAG1, FLAG2, FLAG3]):
        draw.rectangle([W//2 - 18 + i*10, yf, W//2 - 18 + i*10 + 8, yf+fh], fill=c)

    draw.text((W//2, 42), "AFRI Trans", fill=WHITE, font=fb, anchor="mt")
    draw.text((W//2, 66), "E-TICKET \u2022 OFFICIAL", fill=(200,200,200), font=fxs, anchor="mt")

    rx, ry, rw, rh = W//2 - 90, 76, 180, 40
    draw.rounded_rectangle([rx, ry, rx+rw, ry+rh], radius=10, fill=(0, 20, 0), outline=FLAG1, width=2)
    draw.text((W//2, ry+7), "REFERENCE", fill=(160, 200, 160), font=fxs, anchor="mt")
    draw.text((W//2, ry+24), bk['booking_ref'], fill=FLAG3, font=fref, anchor="mt")

    ys = 120
    for i, c in enumerate([FLAG1, FLAG2, FLAG3]):
        draw.rectangle([8 + (W-16)//3*i, ys, 8 + (W-16)//3*(i+1), ys+5], fill=c)

    y = ys + 20
    draw.text((xm, y), "DEPARTURE", fill=GRAY, font=fxs)
    draw.text((xm, y+14), route['from'], fill=DARK, font=fb2)
    draw.text((W-xm, y), "ARRIVAL", fill=GRAY, font=fxs, anchor="rt")
    draw.text((W-xm, y+14), route['to'], fill=DARK, font=fb2, anchor="rt")
    draw.text((W//2, y+14), "\u2192", fill=FLAG2, font=fb2, anchor="mt")

    y = y + 44
    draw.rounded_rectangle([xm, y, W-xm, y+34], radius=10, fill=LGRAY)
    info_text = f"Date: {s['date']}     Time: {s['time']}     {period_label}"
    draw.text((W//2, y+17), info_text, fill=DARK, font=fn, anchor="mt")

    y = y + 48
    for dx in range(0, W-2*xm, 8):
        if (dx//8) % 2 == 0:
            draw.rectangle([xm+dx, y, xm+dx+5, y+1], fill=LIGHT)

    y += 16
    draw.text((xm, y), "PASSENGER", fill=GRAY, font=fxs)
    draw.text((xm, y+14), bk['passenger_name'], fill=DARK, font=fb3)
    draw.text((W-xm, y), "PHONE", fill=GRAY, font=fxs, anchor="rt")
    draw.text((W-xm, y+14), bk['phone'], fill=DARK, font=fb3, anchor="rt")

    y = y + 46
    draw.text((xm, y), "SEAT", fill=GRAY, font=fxs)
    seat_text = str(bk['seat_number'])
    draw.text((xm, y+14), seat_text, fill=FLAG1, font=fseat)

    if bus['bus_type'] == 'vip':
        bx = xm + 60
        draw.rounded_rectangle([bx, y+18, bx+50, y+36], radius=6, fill=(255,248,225))
        draw.text((bx+25, y+27), "VIP", fill=(230,81,0), font=fxs, anchor="mt")
    else:
        bx = xm + 60
        draw.rounded_rectangle([bx, y+18, bx+70, y+36], radius=6, fill=(232,245,233))
        draw.text((bx+35, y+27), "STANDARD", fill=(46,125,50), font=fxs, anchor="mt")

    draw.text((W-xm, y), "AMOUNT PAID", fill=GRAY, font=fxs, anchor="rt")
    is_vip = bus['bus_type'] == 'vip'
    luggage_fee = bk.get('luggage_fee', 0)
    total = route['price'] + (vs if is_vip else 0) + luggage_fee
    draw.text((W-xm, y+14), f"{total:,} {CURR_SYM}", fill=DARK, font=fb2, anchor="rt")
    breakdown_parts = []
    if is_vip:
        breakdown_parts.append(f"base {route['price']:,} + VIP {vs:,}")
    if luggage_fee:
        breakdown_parts.append(f"luggage {luggage_fee:,}")
    if breakdown_parts:
        draw.text((W-xm, y+38), f"({' + '.join(breakdown_parts)} {CURR_SYM})", fill=(230,81,0) if (is_vip or luggage_fee) else GRAY, font=fxs, anchor="rt")

    y = y + (80 if breakdown_parts else 50)
    for dx in range(0, W-2*xm, 8):
        if (dx//8) % 2 == 0:
            draw.rectangle([xm+dx, y, xm+dx+5, y+1], fill=LIGHT)

    y += 16
    draw.text((xm, y), "AGENCY", fill=GRAY, font=fxs)
    draw.text((xm, y+14), agency['name'], fill=DARK, font=fb3)
    draw.text((W-xm, y), "BUS", fill=GRAY, font=fxs, anchor="rt")
    draw.text((W-xm, y+14), f"{bus['plate']} ({bus['bus_type'].upper()})", fill=DARK, font=fb3, anchor="rt")

    y += 38
    if is_expired:
        draw.text((xm, y), "EXPIRED TICKET", fill=FLAG2, font=fs)

    yf = H - 66
    draw.rectangle([8, yf-2, W-8, H-8], fill=LGRAY)
    draw.rounded_rectangle([8, yf-2, W-8, H-8], radius=14, fill=LGRAY)
    draw.rectangle([8, yf-2, W-8, H-20], fill=LGRAY)
    for dx in range(0, W-16, 8):
        if (dx//8) % 2 == 0:
            draw.rectangle([8+dx, yf-2, 8+dx+5, yf-1], fill=LIGHT)

    yf += 10
    meta = f"{s['time']}  |  {s['date']}  |  Seat {bk['seat_number']}"
    draw.text((W//2, yf), meta, fill=GRAY, font=fs, anchor="mt")
    draw.text((W//2, yf+20), "Show this ticket to the driver before boarding.", fill=(85,85,85), font=fn, anchor="mt")
    draw.text((W//2, yf+40), f"Booked on {bk['created_at']}  \u2022  AFRI Trans {CNAME}", fill=(170,170,170), font=fxs, anchor="mt")

    yb = H - 6
    for i, c in enumerate([FLAG1, FLAG2, FLAG3]):
        draw.rectangle([8 + (W-16)//3*i, yb-5, 8 + (W-16)//3*(i+1), yb-1], fill=c)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def seed():
    init_db()
    migrate_from_json()

seed()

# ============================================================
# PASSENGER ROUTES
# ============================================================

@app.before_request
def expire_old_trips():
    auto_expire_trips()

def _country_agencies():
    code = session.get('country', 'cm')
    agencies = get_approved_agencies_by_country(code)
    # When logged in as an agency, hide competitors — only show your own
    if 'agency_id' in session:
        agencies = [a for a in agencies if a['id'] == session['agency_id']]
    return agencies

@app.route('/')
def index():
    all_anns = get_announcements(active_only=True, country=session.get('country', 'cm'))
    anns_by_agency = {}
    for ann in all_anns:
        anns_by_agency.setdefault(ann['agency_id'], []).append(ann)
    return render_template('index.html', today=date.today().isoformat(), agencies=_country_agencies(), anns_by_agency=anns_by_agency)

@app.route('/search')
def search():
    return redirect(url_for('index'))

@app.route('/notifications')
def notifications():
    anns = get_announcements(active_only=True, country=session.get('country', 'cm'))
    resp = make_response(render_template('notifications.html', announcements=anns))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/notification/<int:nid>')
def notification_detail(nid):
    all_anns = get_announcements(active_only=True, country=session.get('country', 'cm'))
    ann = next((a for a in all_anns if a['id'] == nid), None)
    if not ann:
        return _('Announcement not found or has been removed.'), 404
    agency = get_agency(ann['agency_id'])
    resp = make_response(render_template('notification_detail.html', ann=ann, agency=agency))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/agencies')
def browse_agencies():
    agencies_info = []
    for a in _country_agencies():
        buses = len(get_buses_by_agency(a['id']))
        routes = get_routes_by_agency(a['id'])
        route_ids = [r['id'] for r in routes]
        active_trips = len([s for s in get_schedules_by_route_ids(route_ids) if s['status'] == 'active'])
        agencies_info.append({'agency': a, 'buses': buses, 'routes': len(routes), 'active_trips': active_trips})
    return render_template('agencies.html', agencies=agencies_info)

@app.route('/agency/<int:aid>/browse')
def browse_agency(aid):
    agency = get_agency(aid)
    if not agency: flash(_('Agency not found.'), 'error'); return redirect(url_for('index'))
    if not agency.get('approved', False): flash(_('Agency not yet approved by Ministry of Transport.'), 'warning'); return redirect(url_for('index'))
    if agency.get('country', 'cm') != session.get('country', 'cm'):
        flash(_('Agency not available in this country.'), 'error'); return redirect(url_for('index'))
    # Agencies cannot spy on competitors' data
    if 'agency_id' in session and session['agency_id'] != aid:
        flash(_('Access denied — you can only view your own agency profile.'), 'error'); return redirect(url_for('index'))
    routes = get_routes_by_agency(aid)
    buses = get_buses_by_agency(aid)
    route_ids = [r['id'] for r in routes]
    today_str = date.today().isoformat()
    all_schedules = get_schedules_by_route_ids(route_ids)
    all_bookings = get_bookings()
    schedules = []
    for s in all_schedules:
        if s['status'] != 'active': continue
        if s['date'] < today_str: continue
        route = next((r for r in routes if r['id'] == s['route_id']), None)
        bus = next((b for b in buses if b['id'] == s['bus_id']), None)
        taken = len([bk for bk in all_bookings if bk['schedule_id'] == s['id'] and bk['paid'] and bk['status'] == 'confirmed'])
        schedules.append({'id': s['id'], 'route': route, 'bus': bus, 'date': s['date'], 'time': s['time'], 'period': s['period'], 'booked': taken, 'capacity': bus['capacity'] if bus else 0})
    announcements = get_announcements(aid)
    return render_template('agency_browse.html', agency=agency, routes=routes, buses=buses, schedules=schedules, periods=PERIODS, announcements=announcements)

# ── Pick Seat Before Payment ──
@app.route('/schedule/<int:sid>/seats-preview')
def pick_seat(sid):
    return redirect(url_for('index'))

@app.route('/schedule/<int:sid>/book', methods=['GET', 'POST'])
def book(sid):
    return redirect(url_for('index'))

# ── Payment ──
@app.route('/booking/<int:bid>/payment', methods=['GET', 'POST'])
def payment(bid):
    bk = get_booking(bid)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('index'))
    if bk['paid']:
        return redirect(url_for('ticket', ref=bk['booking_ref']))
    s = get_schedule(bk['schedule_id'])
    route = get_route(s['route_id']) if s else None
    bus = get_bus(s['bus_id']) if s else None
    agency = get_agency(route['agency_id']) if route else None
    vs = get_vip_surcharge(bus)
    price = (route['price'] + vs) if bus and bus['bus_type'] == 'vip' else route['price'] if route else 0
    luggage_fee = bk.get('luggage_fee', 0)
    total_price = price + luggage_fee
    valid_providers = [p['code'] for p in get_country_providers()]
    if request.method == 'POST':
        provider = request.form.get('provider', '')
        phone = request.form.get('phone', '').strip()
        if provider not in valid_providers or not phone:
            flash(_('Please select a payment method and enter your phone number.'), 'error')
            return render_template('payment.html', bk=bk, s=s, route=route, bus=bus, agency=agency, price=price, luggage_fee=luggage_fee, total_price=total_price)
        tx_id = f"TXN-{bk['booking_ref']}-{random.randint(1000,9999)}"
        ok, err = confirm_booking_atomic(bid, provider, tx_id)
        if err == 'seat_taken':
            flash(_('Sorry, seat was taken by another passenger. Please rebook from the homepage.'), 'error')
            return redirect(url_for('index'))
        if not ok:
            flash(_('Payment failed: {}').format(err), 'error')
            return render_template('payment.html', bk=bk, s=s, route=route, bus=bus, agency=agency, price=price, luggage_fee=luggage_fee, total_price=total_price)
        # Record 1% platform commission (skip if agency has active subscription)
        if ok and agency and not has_active_subscription(agency['id']):
            commission = max(1, round(total_price * 0.01))
            country_code = session.get('country', 'cm')
            curr = COUNTRIES.get(country_code, COUNTRIES['cm'])['currency_code']
            add_commission(bid, agency['id'], commission, curr)
        return redirect(url_for('ticket', ref=bk['booking_ref']))
    return render_template('payment.html', bk=bk, s=s, route=route, bus=bus, agency=agency, price=price, luggage_fee=luggage_fee, total_price=total_price)

@app.route('/booking/<int:bid>/seats', methods=['GET', 'POST'])
def seats(bid):
    bk = get_booking(bid)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('index'))
    if not bk['paid']: return redirect(url_for('payment', bid=bid))
    return redirect(url_for('ticket', ref=bk['booking_ref']))

@app.route('/ticket/<ref>')
def ticket(ref):
    bk = get_booking_by_ref(ref)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('index'))
    s = get_schedule(bk['schedule_id'])
    route = get_route(s['route_id']) if s else None
    bus = get_bus(s['bus_id']) if s else None
    agency = get_agency(route['agency_id']) if route else None
    period_label = next((p['label'] for p in PERIODS if p['key'] == s['period']), s['period']) if s else ''
    vs = get_vip_surcharge(bus)
    price = (route['price'] + vs) if bus and bus['bus_type'] == 'vip' else route['price'] if route else 0
    luggage_fee = bk.get('luggage_fee', 0)
    total_price = price + luggage_fee
    is_expired = bk.get('status') == 'expired' or (s and booking_has_departed(s))
    return render_template('ticket.html', bk=bk, s=s, route=route, bus=bus, agency=agency, period_label=period_label, price=price, luggage_fee=luggage_fee, total_price=total_price, is_expired=is_expired)

@app.route('/ticket/<ref>/pdf')
def ticket_pdf(ref):
    bk = get_booking_by_ref(ref)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('index'))
    s = get_schedule(bk['schedule_id'])
    route = get_route(s['route_id']) if s else None
    bus = get_bus(s['bus_id']) if s else None
    agency = get_agency(route['agency_id']) if route else None
    period_label = next((p['label'] for p in PERIODS if p['key'] == s['period']), s['period']) if s else ''
    vs = get_vip_surcharge(bus)
    price = (route['price'] + vs) if bus and bus['bus_type'] == 'vip' else route['price'] if route else 0
    luggage_fee = bk.get('luggage_fee', 0)
    total_price = price + luggage_fee
    is_expired = bk.get('status') == 'expired' or (s and booking_has_departed(s))
    html = render_template('ticket_pdf.html', bk=bk, s=s, route=route, bus=bus, agency=agency, period_label=period_label, price=price, luggage_fee=luggage_fee, total_price=total_price, is_expired=is_expired)
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf)
    pdf.seek(0)
    return send_file(pdf, mimetype='application/pdf', as_attachment=True, download_name=f'ticket_{ref}.pdf')

@app.route('/ticket/<ref>/image')
def ticket_image_route(ref):
    bk = get_booking_by_ref(ref)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('index'))
    s = get_schedule(bk['schedule_id'])
    route = get_route(s['route_id']) if s else None
    bus = get_bus(s['bus_id']) if s else None
    agency = get_agency(route['agency_id']) if route else None
    period_label = next((p['label'] for p in PERIODS if p['key'] == s['period']), s['period']) if s else ''
    is_expired = bk.get('status') == 'expired' or (s and booking_has_departed(s))
    country_code = session.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    buf = ticket_image(bk, s, route, bus, agency, period_label, is_expired=is_expired, country=c)
    return send_file(buf, mimetype='image/png')

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if request.method == 'POST':
        ref = request.form.get('ref', '').strip().upper()
        if ref: return redirect(url_for('ticket', ref=ref))
        flash(_('Enter a booking reference.'), 'error')
    return render_template('lookup.html')

# ── Accordion Booking ──
@app.route('/book')
def booking_accordion():
    return redirect(url_for('index'))

@app.route('/api/booking/search', methods=['POST'])
def booking_search():
    fr = request.form.get('from', '')
    to = request.form.get('to', '')
    d = request.form.get('date', '')
    country_agencies = _country_agencies()
    country_agency_ids = {a['id'] for a in country_agencies}
    all_routes = get_all_routes()
    all_schedules = get_schedules()
    all_buses_cache = {}
    results = []
    if fr and to and d:
        for s in all_schedules:
            if s['status'] != 'active': continue
            route = next((r for r in all_routes if r['id'] == s['route_id']), None)
            if not route or route['from'].lower() != fr.lower() or route['to'].lower() != to.lower(): continue
            if s['date'] != d: continue
            bus = all_buses_cache.get(s['bus_id']) or get_bus(s['bus_id'])
            all_buses_cache[s['bus_id']] = bus
            agency = next((a for a in country_agencies if a['id'] == route['agency_id']), None)
            if not agency: continue
            taken = get_booking_seat_numbers(s['id'])
            available = (bus['capacity'] if bus else 0) - len(taken)
            results.append({'schedule': s, 'route': route, 'bus': bus, 'agency': agency, 'available': available, 'taken': sorted(taken)})
    grouped = {}
    for t in results:
        p = t['schedule']['period']
        if p not in grouped: grouped[p] = []
        grouped[p].append(t)
    html = render_template('partials/search_results.html', grouped=grouped, results=results, fr=fr, to=to, d=d, periods=PERIODS)
    return {'html': html}

@app.route('/api/booking/seats/<int:sid>')
def booking_seats(sid):
    s = get_schedule(sid)
    if not s: return {'html': '<div class="card text-center" style="padding:30px;color:#c62828;">' + _('Schedule not found.') + '</div>'}
    if s['status'] != 'active': return {'html': '<div class="card text-center" style="padding:30px;color:#c62828;">' + _('This trip is no longer active.') + '</div>'}
    route = get_route(s['route_id'])
    bus = get_bus(s['bus_id'])
    agency = get_agency(route['agency_id']) if route else None
    taken = get_booking_seat_numbers(s['id'])
    layout = bus_layout(bus['bus_type'] if bus else 'standard', bus['capacity'] if bus else 71)
    cols, grid_style = _grid_config(layout)
    vs = get_vip_surcharge(bus)
    html = render_template('partials/seat_layout.html', s=s, route=route, bus=bus, agency=agency, taken=taken, layout=layout, cols=cols, grid_style=grid_style, vip_surcharge=vs)
    return {'html': html, 'ctx': {'taken': sorted(taken), 'basePrice': route['price'] if route else 0, 'isVip': bus['bus_type'] == 'vip' if bus else False, 'vipSurcharge': vs, 'sid': sid}}

@app.route('/api/booking/form/<int:sid>')
def booking_form(sid):
    s = get_schedule(sid)
    if not s: return {'html': '<div class="card text-center" style="padding:30px;color:#c62828;">' + _('Schedule not found.') + '</div>'}
    route = get_route(s['route_id'])
    bus = get_bus(s['bus_id'])
    agency = get_agency(route['agency_id']) if route else None
    selected_seat = request.args.get('seat')
    if selected_seat and (not selected_seat.isdigit() or int(selected_seat) < 1):
        selected_seat = None
    vs = get_vip_surcharge(bus)
    base_price = route['price'] + (vs if bus and bus['bus_type'] == 'vip' else 0) if route else 0
    luggage_enabled = route.get('luggage_enabled', False) if route else False
    luggage_ppkg = route.get('luggage_price_per_kg', 0) if route else 0
    html = render_template('partials/passenger_form.html', s=s, route=route, bus=bus, agency=agency, selected_seat=selected_seat, vip_surcharge=vs)
    return {'html': html, 'ctx': {'basePrice': base_price, 'ppkg': luggage_ppkg, 'luggageEnabled': luggage_enabled}}

@app.route('/api/booking/confirm', methods=['POST'])
def booking_confirm():
    sid = request.form.get('sid', '').strip()
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    id_number = request.form.get('id_number', '').strip()
    seat_str = request.form.get('seat', '').strip()
    has_luggage = request.form.get('has_luggage') == 'on'
    luggage_weight = request.form.get('luggage_weight', '0').strip()
    if not sid or not sid.isdigit():
        return {'ok': False, 'error': _('Invalid schedule.')}
    sid = int(sid)
    if not name or not phone or not id_number:
        return {'ok': False, 'error': _('Please fill in your name, phone number, and ID number.')}
    s = get_schedule(sid)
    if not s: return {'ok': False, 'error': _('Schedule not found.')}
    try:
        dep = datetime.strptime(f"{s['date']} {s['time']}", "%Y-%m-%d %H:%M")
    except (ValueError, KeyError):
        return {'ok': False, 'error': _('Invalid schedule.')}
    if datetime.now() > dep:
        return {'ok': False, 'error': _('This trip has already departed.')}
    if dep - datetime.now() < timedelta(minutes=15):
        return {'ok': False, 'error': _('Too close to departure — booking closed (less than 15 min).')}
    route = get_route(s['route_id'])
    luggage_enabled = route.get('luggage_enabled', False) if route else False
    luggage_ppkg = route.get('luggage_price_per_kg', 0) if route else 0
    seat_n = int(seat_str) if seat_str.isdigit() else None
    luggage_w = float(luggage_weight) if has_luggage and luggage_weight.replace('.', '', 1).isdigit() else 0
    luggage_fee = int(luggage_w * luggage_ppkg) if luggage_enabled else 0
    ref = gen_ref()
    bid, err = add_booking_atomic(sid, name, phone, id_number, seat_n, ref, luggage_w, luggage_fee)
    if err:
        return {'ok': False, 'error': _(err)}
    return {'ok': True, 'bid': bid}

@app.route('/api/booking/payment-form/<int:bid>')
def booking_payment_form(bid):
    try:
        bk = get_booking(bid)
        if not bk: return {'ok': False, 'error': _('Booking not found.')}
        if bk['paid']: return {'ok': False, 'redirect': url_for('ticket', ref=bk['booking_ref'])}
        s = get_schedule(bk['schedule_id'])
        route = get_route(s['route_id']) if s else None
        bus = get_bus(s['bus_id']) if s else None
        agency = get_agency(route['agency_id']) if route else None
        vs = get_vip_surcharge(bus)
        price = (route['price'] + vs) if bus and bus['bus_type'] == 'vip' else route['price'] if route else 0
        luggage_fee = bk.get('luggage_fee', 0)
        total_price = price + luggage_fee
        providers = get_country_providers()
        html = render_template_string('''
    {% if bk.seat_number %}
    <div style="background:#e3f2fd; border-radius:6px; padding:6px 10px; margin-bottom:8px; font-size:12px; color:#1565c0; display:flex; align-items:center; gap:6px;">
        <i class="fas fa-couch"></i> {{ _('Seat') }} <strong>{{ bk.seat_number }}</strong>
    </div>
    {% endif %}
    <div style="background:linear-gradient(135deg,#f0fdf4,#e8f5e9); border-radius:8px; padding:12px; margin-bottom:12px; text-align:center;">
        <div style="font-size:11px; color:#555;">{{ _('Total to pay') }}</div>
        <div style="font-size:20px; font-weight:900; color:var(--flag-1);">{{ total_price|currency }}</div>
        <div style="font-size:11px; color:#555; margin-top:3px;">
            {{ _('Transport:') }} {{ price|currency }}
            {% if bus and bus.bus_type == 'vip' %}({{ _('VIP') }} {{ vs|currency }}){% endif %}
        </div>
        {% if luggage_fee %}
        <div style="font-size:11px; color:#e65100;">{{ _('Luggage:') }} {{ luggage_fee|currency }} ({{ bk.get('luggage_weight', 0) }} kg)</div>
        {% endif %}
        <hr style="margin:8px 0; border-color:#c8e6c9;">
    </div>
    <form id="paymentForm" onsubmit="return doPayment(event, {{ bid }})">
        <div style="margin-bottom:12px;">
            <label style="font-weight:600; font-size:12px; display:block; margin-bottom:6px;">{{ _('Select payment method') }}</label>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
                {% for p in providers %}
                <label class="pay-option" style="flex:1; min-width:80px; cursor:pointer;">
                    <input type="radio" name="provider" value="{{ p.code }}" required style="display:none;" onchange="this.parentElement.classList.toggle('selected')">
                    <div style="border:2px solid #e0e0e0; border-radius:8px; padding:10px; text-align:center; transition:all 0.2s;">
                        <div style="font-size:18px; margin-bottom:2px;"><i class="fas {{ p.icon }}" style="color:{{ p.color }};"></i></div>
                        <div style="font-weight:700; font-size:11px; color:#1a1a2e;">{{ p.name }}</div>
                    </div>
                </label>
                {% endfor %}
            </div>
        </div>
        <div class="form-group">
            <label style="font-size:12px;">{{ _('Mobile Money Phone Number') }}</label>
            <input type="tel" name="phone" class="form-control" required placeholder="{{ _('e.g. 677123456') }}" style="font-size:13px;">
            <div style="font-size:11px; color:#999; margin-top:3px;">
                <i class="fas fa-info-circle"></i> {{ _('Enter your mobile money phone number') }}
            </div>
        </div>
        <button type="submit" class="btn btn-success" style="width:100%; font-size:13px; padding:8px 14px;" id="payBtn">
            <i class="fas fa-check-circle"></i> {{ _('Confirm and Pay') }}
        </button>
    </form>
    ''', bk=bk, route=route, bus=bus, agency=agency, price=price, luggage_fee=luggage_fee, total_price=total_price, providers=providers, bid=bid, vs=vs)
    except Exception as ex:
        return {'ok': False, 'error': f'Error: {type(ex).__name__}: {str(ex)[:200] if str(ex) else "(empty)"}'}
    return {'ok': True, 'html': html}

@app.route('/api/booking/pay', methods=['POST'])
def booking_pay():
    bid = request.form.get('bid', '').strip()
    provider = request.form.get('provider', '')
    phone = request.form.get('phone', '').strip()
    if not bid or not bid.isdigit():
        return {'ok': False, 'error': _('Invalid booking.')}
    bid = int(bid)
    bk = get_booking(bid)
    if not bk: return {'ok': False, 'error': _('Booking not found.')}
    if bk['paid']: return {'ok': True, 'redirect': url_for('ticket', ref=bk['booking_ref'])}
    s = get_schedule(bk['schedule_id'])
    route = get_route(s['route_id']) if s else None
    bus = get_bus(s['bus_id']) if s else None
    agency = get_agency(route['agency_id']) if route else None
    vs = get_vip_surcharge(bus)
    price = (route['price'] + vs) if bus and bus['bus_type'] == 'vip' else route['price'] if route else 0
    luggage_fee = bk.get('luggage_fee', 0)
    total_price = price + luggage_fee
    valid_providers = [p['code'] for p in get_country_providers()]
    if not provider or provider not in valid_providers or not phone:
        return {'ok': False, 'error': _('Please select a payment method and enter your phone number.')}
    tx_id = f"TXN-{bk['booking_ref']}-{random.randint(1000,9999)}"
    ok, err = confirm_booking_atomic(bid, provider, tx_id)
    if err == 'seat_taken':
        return {'ok': False, 'error': _('Sorry, seat was taken by another passenger. Please rebook from the homepage.')}
    if not ok:
        return {'ok': False, 'error': _('Payment failed: {}').format(err)}
    if ok and agency and not has_active_subscription(agency['id']):
        commission = max(1, round(total_price * 0.01))
        country_code = session.get('country', 'cm')
        curr = COUNTRIES.get(country_code, COUNTRIES['cm'])['currency_code']
        add_commission(bid, agency['id'], commission, curr)
    return {'ok': True, 'redirect': url_for('ticket', ref=bk['booking_ref'])}

@app.route('/api/seats/<int:sid>/status')
def seat_status(sid):
    taken = get_booking_seat_numbers(sid)
    return {'taken': sorted(taken)}

@app.route('/api/agencies')
def api_agencies():
    country = session.get('country')
    agencies = get_approved_agencies_contact(country)
    return {'agencies': agencies}

# ============================================================
# AGENCY ROUTES
# ============================================================

@app.route('/agency/register', methods=['GET', 'POST'])
def agency_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        locations = request.form.getlist('locations')
        pw = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip().lower()
        if not name or not locations or not pw or not email:
            flash(_('All fields are required.'), 'error')
            return render_template('agency_register.html')
        code = session.get('country', 'cm')
        if '@' not in email:
            flash(_('Please enter a valid email address.'), 'error')
            return render_template('agency_register.html')
        whatsapp = request.form.get('whatsapp', '').strip()
        phone_code = COUNTRIES.get(code, COUNTRIES['cm']).get('phone_code', '')
        if whatsapp:
            if not whatsapp.isdigit():
                flash(_('WhatsApp number should contain only digits.'), 'error')
                return render_template('agency_register.html')
            if whatsapp.startswith(phone_code):
                flash(_('Please enter your number without the country code') + f' +{phone_code}.', 'error')
                return render_template('agency_register.html')
            whatsapp = phone_code + whatsapp
        agency_id, err = add_agency(name, generate_password_hash(pw), code, locations, date.today().isoformat(), approved=False, whatsapp=whatsapp, email=email)
        if err:
            if err == 'name_exists':
                flash(_('An agency with this name already exists in this country.'), 'error')
            elif err == 'email_exists':
                flash(_('An agency with this email already exists.'), 'error')
            else:
                flash(_('Registration failed. Please try again.'), 'error')
            return render_template('agency_register.html')
        # Parse dynamic bus rows
        plate_n = 1
        total_buses = 0
        i = 0
        while request.form.get(f'bus_type_{i}') is not None:
            btype = request.form.get(f'bus_type_{i}', 'standard')
            bcount = request.form.get(f'bus_count_{i}', '0').strip()
            bcap = request.form.get(f'bus_cap_{i}', '70').strip()
            try:
                bcount = max(0, int(bcount))
                bcap = max(14, min(80, int(bcap)))
            except ValueError:
                bcount = 0
                bcap = 70
            for x in range(bcount):
                add_bus(agency_id, f"{name[:3].upper()}-{plate_n:03d}", bcap, btype, 'available')
                plate_n += 1
                total_buses += 1
            i += 1
        if total_buses < 1:
            flash(_('You need at least one bus.'), 'error')
            return redirect(url_for('agency_register'))
        flash(_('Agency "{}" registered with {} bus(es). Pending Ministry of Transport approval.').format(name, total_buses), 'warning')
        return redirect(url_for('agency_login'))
    return render_template('agency_register.html')

@app.route('/agency/login', methods=['GET', 'POST'])
def agency_login():
    if request.method == 'POST':
        ip = request.remote_addr or 'unknown'
        blocked, wait = is_rate_limited(ip)
        if blocked:
            flash(_('Too many login attempts. Try again in {} minutes.').format(int(wait) + 1), 'warning')
            return render_template('agency_login.html')
        name = request.form.get('name', '').strip()
        pw = request.form.get('password', '').strip()
        sess_country = session.get('country', 'cm')
        agencies = get_agencies_by_country(sess_country)
        a = next((x for x in agencies if x['name'].lower() == name.lower()), None)
        if not a: flash(_('Incorrect agency name or password.'), 'error'); return render_template('agency_login.html')
        if not a['password'].startswith('scrypt:') and not a['password'].startswith('pbkdf2:'):
            if a['password'] != pw: flash(_('Incorrect agency name or password.'), 'error'); return render_template('agency_login.html')
            update_agency(a['id'], password=generate_password_hash(pw))
        elif not check_password_hash(a['password'], pw):
            flash(_('Incorrect agency name or password.'), 'error'); return render_template('agency_login.html')
        session['agency_id'] = a['id']
        session.permanent = True
        login_attempts.pop(ip, None)  # clear on success
        return redirect(url_for('agency_dashboard'))
    return render_template('agency_login.html')

@app.route('/agency/forgot-password', methods=['GET', 'POST'])
def agency_forgot_password():
    mc = session.get('country', 'cm')
    c = COUNTRIES.get(mc, COUNTRIES['cm'])
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        agency = get_agency_by_email(email, mc)
        if agency:
            code = ''.join(random.choices(string.digits, k=8))
            expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M')
            update_agency(agency['id'], reset_token=code, reset_token_expiry=expiry)
            session['reset_agency_id'] = agency['id']
            body = _("Your AFRI Trans agency password reset code is: <b>{code}</b><br>This code expires in 15 minutes.").format(code=code)
            sent = send_email(email, _('AFRI Trans - Password Reset Code'), body)
            if sent:
                flash(_('An 8-digit verification code has been sent to your email.'), 'success')
            else:
                flash(_('(Demo: your code is {code})').format(code=code), 'success')
        else:
            flash(_('No agency found with that email in this country.'), 'error')
            return redirect(url_for('agency_forgot_password'))
        return redirect(url_for('agency_verify_code'))
    return render_template('agency_forgot_password.html', country=c)

@app.route('/agency/verify-code', methods=['GET', 'POST'])
def agency_verify_code():
    aid = session.get('reset_agency_id')
    if not aid:
        return redirect(url_for('agency_forgot_password'))
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        agency = get_agency(aid)
        if not agency or agency.get('reset_token') != code:
            flash(_('Invalid verification code.'), 'error')
            return redirect(url_for('agency_verify_code'))
        expiry = datetime.strptime(agency.get('reset_token_expiry', '2000-01-01 00:00'), '%Y-%m-%d %H:%M')
        if datetime.now() > expiry:
            flash(_('Verification code has expired. Please request a new one.'), 'error')
            session.pop('reset_agency_id', None)
            return redirect(url_for('agency_forgot_password'))
        session['reset_verified'] = True
        return redirect(url_for('agency_reset_password'))
    return render_template('agency_verify_code.html')

@app.route('/agency/reset-password', methods=['GET', 'POST'])
def agency_reset_password():
    if not session.get('reset_verified') or not session.get('reset_agency_id'):
        return redirect(url_for('agency_forgot_password'))
    if request.method == 'POST':
        pw = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(pw) < 6:
            flash(_('Password must be at least 6 characters.'), 'error')
            return redirect(url_for('agency_reset_password'))
        if pw != confirm:
            flash(_('Passwords do not match.'), 'error')
            return redirect(url_for('agency_reset_password'))
        update_agency(session['reset_agency_id'], password=generate_password_hash(pw), reset_token=None, reset_token_expiry=None)
        session.pop('reset_agency_id', None)
        session.pop('reset_verified', None)
        flash(_('Password reset successful. Please log in.'), 'success')
        return redirect(url_for('agency_login'))
    return render_template('agency_reset_password.html')

@app.route('/agency/logout')
def agency_logout():
    session.pop('agency_id', None)
    session.pop('read_notification_ids', None)
    return redirect(url_for('index'))

def get_agency_session():
    if 'agency_id' not in session: return None
    a = get_agency(session['agency_id'])
    if not a:
        session.pop('agency_id', None)
        return None
    return a

def auto_revert_bus_status(agency_id):
    today_str = date.today().isoformat()
    buses = get_buses_by_agency(agency_id)
    routes = get_routes_by_agency(agency_id)
    all_schedules = get_schedules_by_route_ids([r['id'] for r in routes])
    active_bus_ids = set(s['bus_id'] for s in all_schedules if s['date'] >= today_str and s.get('status') not in ('cancelled',))
    db = get_db()
    for b in buses:
        if b['status'] == 'busy' and b['id'] not in active_bus_ids:
            db.execute("UPDATE buses SET status = 'available' WHERE id = ?", (b['id'],))
    db.commit()
    db.close()

@app.route('/agency/dashboard')
def agency_dashboard():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    auto_revert_bus_status(a['id'])
    expire_unpaid_bookings(30)
    buses = get_buses_by_agency(a['id'])
    routes = get_routes_by_agency(a['id'])
    route_ids = [r['id'] for r in routes]
    today_str = date.today().isoformat()
    all_schedules = get_schedules_by_route_ids(route_ids)
    all_bookings = get_bookings_by_schedule_ids([s['id'] for s in all_schedules])
    schedules = []
    total_revenue = 0
    for s in all_schedules:
        if s['date'] < today_str: continue
        route = next((r for r in routes if r['id'] == s['route_id']), None)
        bus = next((b for b in buses if b['id'] == s['bus_id']), None)
        taken = len([bk for bk in all_bookings if bk['schedule_id'] == s['id'] and bk['paid'] and bk['status'] == 'confirmed'])
        schedules.append({'id': s['id'], 'route': route, 'bus': bus, 'date': s['date'], 'time': s['time'], 'period': s['period'], 'status': s['status'], 'booked': taken, 'capacity': bus['capacity'] if bus else 0})
    paid_bookings = [bk for bk in all_bookings if bk.get('paid')]
    revenue_by_route = {}
    for bk in paid_bookings:
        s = next((x for x in all_schedules if x['id'] == bk['schedule_id']), None)
        route = next((r for r in routes if r['id'] == (s['route_id'] if s else None)), None) if s else None
        if route:
            bus = next((b for b in buses if b['id'] == (s['bus_id'] if s else None)), None)
            vs = bus.get('vip_price') if bus and bus.get('vip_price') is not None else COUNTRIES.get(session.get('country', 'cm'), COUNTRIES['cm']).get('vip_surcharge', 0)
            vip_extra = vs if (bus and bus['bus_type'] == 'vip') else 0
            amt = route['price'] + vip_extra + bk.get('luggage_fee', 0)
            total_revenue += amt
            key = f"{route['from']} → {route['to']}"
            revenue_by_route[key] = revenue_by_route.get(key, 0) + amt
    revenue_by_route = dict(sorted(revenue_by_route.items(), key=lambda x: -x[1]))
    agency_commission = get_total_commission(agency_ids=[a['id']])
    total_bookings = len([b for b in all_bookings if b.get('paid')])
    confirmed = len([b for b in all_bookings if b.get('paid') and b.get('status') == 'confirmed'])
    pending_bk = len([b for b in all_bookings if b.get('paid') and b.get('status') == 'pending'])
    cancelled_bk = len([b for b in all_bookings if b.get('status') == 'cancelled'])
    recent_bookings = sorted([b for b in all_bookings if b.get('paid')], key=lambda x: x.get('created_at', ''), reverse=True)[:8]
    for rb in recent_bookings:
        s = next((x for x in all_schedules if x['id'] == rb['schedule_id']), None)
        rb['_route'] = next((r for r in routes if r['id'] == (s['route_id'] if s else None)), None) if s else None
        rb['_date'] = s['date'] if s else ''
        rb['_time'] = s['time'] if s else ''
    today_trips = [s for s in schedules if s['date'] == today_str]
    sub = get_active_subscription(a['id'])
    curr = COUNTRIES.get(session.get('country', 'cm'), COUNTRIES['cm'])['currency_code']

    past_schedules = [s for s in all_schedules if s['date'] <= today_str]
    past_schedules.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    past_trip_reports = []
    for s in past_schedules:
        route = next((r for r in routes if r['id'] == s['route_id']), None)
        bus = next((b for b in buses if b['id'] == s['bus_id']), None)
        bkgs = [bk for bk in all_bookings if bk['schedule_id'] == s['id']]
        paid_bkgs = [bk for bk in bkgs if bk.get('paid')]
        taken = len(paid_bkgs)
        capacity = bus['capacity'] if bus else 0
        ticket_revenue = 0
        luggage_revenue = 0
        for bk in paid_bkgs:
            if route:
                vs = bus.get('vip_price') if bus and bus.get('vip_price') is not None else COUNTRIES.get(session.get('country', 'cm'), COUNTRIES['cm']).get('vip_surcharge', 0)
                vip_extra = vs if (bus and bus['bus_type'] == 'vip') else 0
                ticket_revenue += route['price'] + vip_extra
                luggage_revenue += bk.get('luggage_fee', 0)
        total_rev = ticket_revenue + luggage_revenue
        tr = get_trip_report(s['id'])
        expenses = 0
        if tr:
            expenses = tr['expenses']
        profit = total_rev - expenses
        past_trip_reports.append({
            'schedule': s, 'route': route, 'bus': bus,
            'booked': taken, 'capacity': capacity,
            'ticket_revenue': ticket_revenue, 'luggage_revenue': luggage_revenue,
            'total_revenue': total_rev, 'expenses': expenses, 'report': tr, 'profit': profit
        })
    cleanup_old_trip_reports(365)

    total_expenses = sum(tr['expenses'] for tr in past_trip_reports)
    total_commission_taken = agency_commission if not sub else 0
    agency_net = total_revenue - total_commission_taken
    total_profit = agency_net - total_expenses

    return render_template('agency_dashboard.html', agency=a, buses=buses, routes=routes, schedules=schedules, bookings_count=total_bookings, periods=PERIODS, total_revenue=total_revenue, agency_net=agency_net, total_expenses=total_expenses, total_profit=total_profit, total_commission_taken=total_commission_taken, revenue_by_route=revenue_by_route, confirmed_count=confirmed, pending_count=pending_bk, cancelled_count=cancelled_bk, recent_bookings=recent_bookings, today_trips=today_trips, sub=sub, sub_prices=SUBSCRIPTION_PRICES.get(curr, {}), country=COUNTRIES.get(session.get('country','cm'), COUNTRIES['cm']), past_trip_reports=past_trip_reports)

@app.route('/api/agency/trip-report', methods=['POST'])
def agency_trip_report_save():
    try:
        a = get_agency_session()
        if not a: return {'ok': False, 'error': 'Not logged in'}
        sid = request.form.get('schedule_id', '').strip()
        if not sid or not sid.isdigit(): return {'ok': False, 'error': 'Invalid schedule'}
        sid = int(sid)
        expenses = int(request.form.get('expenses', '0') or '0')
        add_trip_report(sid, a['id'], expenses)
        return {'ok': True}
    except Exception as ex:
        return {'ok': False, 'error': f'{type(ex).__name__}: {str(ex)[:200]}'}

@app.route('/agency/subscribe')
def agency_subscribe():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    country_code = session.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    curr = c['currency_code']
    prices = SUBSCRIPTION_PRICES.get(curr, SUBSCRIPTION_PRICES['XAF'])
    sub = get_active_subscription(a['id'])
    return render_template('agency_subscribe.html', agency=a, prices=prices, curr=curr, country=c, sub=sub)

@app.route('/agency/subscribe/pay')
def agency_subscribe_pay():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    plan = request.args.get('plan', '')
    custom_months = request.args.get('months', '')
    if plan == 'custom' and custom_months and custom_months.isdigit() and int(custom_months) >= 1:
        months = int(custom_months)
        country_code = session.get('country', 'cm')
        c = COUNTRIES.get(country_code, COUNTRIES['cm'])
        curr = c['currency_code']
        prices_db = get_subscription_prices()
        price_map = {p['currency']: p['monthly_price'] for p in prices_db}
        if curr not in price_map:
            price_map[curr] = SUBSCRIPTION_PRICES.get(curr, {}).get('monthly', 58000)
        amount = price_map[curr] * months
        providers = get_country_providers()
        return render_template('agency_subscribe_pay.html', agency=a, plan='custom', months=months, amount=amount, curr=curr, country=c, providers=providers)
    if plan not in ('monthly', 'semiannual', 'annual'):
        flash(_('Invalid plan.'), 'error')
        return redirect(url_for('agency_subscribe'))
    country_code = session.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    curr = c['currency_code']
    prices = SUBSCRIPTION_PRICES.get(curr, SUBSCRIPTION_PRICES['XAF'])
    amount = prices[plan]
    providers = get_country_providers()
    return render_template('agency_subscribe_pay.html', agency=a, plan=plan, amount=amount, curr=curr, country=c, providers=providers)

@app.route('/agency/subscribe/confirm', methods=['POST'])
def agency_subscribe_confirm():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    plan = request.form.get('plan', '')
    provider = request.form.get('provider', '').strip()
    phone = request.form.get('phone', '').strip()
    custom_months = request.form.get('custom_months', '')
    if plan == 'custom' and custom_months and custom_months.isdigit() and int(custom_months) >= 1:
        months = int(custom_months)
        valid_providers = [p['code'] for p in get_country_providers()]
        if provider not in valid_providers or not phone:
            flash(_('Please select a payment method and enter your phone number.'), 'error')
            return redirect(url_for('agency_subscribe_pay', plan='custom', months=months))
        country_code = session.get('country', 'cm')
        c = COUNTRIES.get(country_code, COUNTRIES['cm'])
        curr = c['currency_code']
        prices_db = get_subscription_prices()
        price_map = {p['currency']: p['monthly_price'] for p in prices_db}
        if curr not in price_map:
            price_map[curr] = SUBSCRIPTION_PRICES.get(curr, {}).get('monthly', 58000)
        amount = price_map[curr] * months
        extra_days = months * 30
        extend_subscription(a['id'], f'custom_{months}mo', amount, curr, extra_days)
        sub = get_active_subscription(a['id'])
        flash(_('Payment successful! Subscription active until {}.').format(sub['end_date']), 'success')
        return redirect(url_for('agency_dashboard'))
    if plan not in ('monthly', 'semiannual', 'annual'):
        flash(_('Invalid plan.'), 'error')
        return redirect(url_for('agency_subscribe'))
    valid_providers = [p['code'] for p in get_country_providers()]
    if provider not in valid_providers or not phone:
        flash(_('Please select a payment method and enter your phone number.'), 'error')
        return redirect(url_for('agency_subscribe_pay', plan=plan))
    country_code = session.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    curr = c['currency_code']
    prices = SUBSCRIPTION_PRICES.get(curr, SUBSCRIPTION_PRICES['XAF'])
    amount = prices[plan]
    extra_days = 30 if plan == 'monthly' else 180 if plan == 'semiannual' else 365
    extend_subscription(a['id'], plan, amount, curr, extra_days)
    sub = get_active_subscription(a['id'])
    flash(_('Payment successful! Subscription active until {}.').format(sub['end_date']), 'success')
    return redirect(url_for('agency_dashboard'))

@app.route('/agency/subscription')
def agency_subscription():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    sub = get_active_subscription(a['id'])
    country_code = session.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    curr = c['currency_code']
    prices = SUBSCRIPTION_PRICES.get(curr, SUBSCRIPTION_PRICES['XAF'])
    return render_template('agency_subscription.html', agency=a, sub=sub, prices=prices, curr=curr, country=c)

@app.route('/agency/buses')
def agency_buses():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    auto_revert_bus_status(a['id'])
    return render_template('agency_buses.html', agency=a, buses=get_buses_by_agency(a['id']))

@app.route('/agency/buses/add', methods=['GET', 'POST'])
def agency_bus_add():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    if request.method == 'POST':
        plate = request.form.get('plate', '').strip().upper()
        if not plate:
            flash(_('Plate number is required.'), 'error'); return render_template('agency_bus_form.html', agency=a, bus=None)
        capacity = request.form.get('capacity', '70').strip()
        try:
            capacity = max(14, min(80, int(capacity)))
        except ValueError:
            capacity = 71
        bus_type = request.form.get('bus_type', 'standard')
        vip_price = request.form.get('vip_price', '').strip()
        vip_price = int(vip_price) if vip_price and vip_price.isdigit() else None
        add_bus(a['id'], plate, capacity, bus_type, 'available', vip_price)
        flash(_('Bus added successfully ({} seats, {}).').format(capacity, bus_type.upper()), 'success'); return redirect(url_for('agency_buses'))
    return render_template('agency_bus_form.html', agency=a, bus=None)

@app.route('/agency/announcements', methods=['GET', 'POST'])
def agency_announcements():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    if request.method == 'POST':
        msg = request.form.get('message', '').strip()
        badge = request.form.get('badge', 'NEW').strip()
        if not msg:
            flash(_('Announcement message cannot be empty.'), 'error'); return redirect(url_for('agency_announcements'))
        add_announcement(a['id'], msg, badge)
        flash(_('Announcement posted!'), 'success')
        return redirect(url_for('agency_announcements'))
    anns = get_announcements(a['id'])
    return render_template('agency_announcements.html', agency=a, announcements=anns)

@app.route('/agency/announcement/<int:aid>/delete')
def agency_announcement_delete(aid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    deactivate_announcement(aid, a['id'])
    flash(_('Announcement removed.'), 'success')
    return redirect(url_for('agency_announcements'))

@app.route('/agency/bus/<int:bid>/toggle-status')
def agency_bus_toggle(bid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    bus = get_bus(bid)
    if bus and bus['agency_id'] == a['id']:
        new_status = 'busy' if bus['status'] == 'available' else 'available'
        update_bus(bid, status=new_status)
        flash(_('Bus {} is now {}.').format(bus['plate'], new_status), 'success')
    return redirect(url_for('agency_buses'))

@app.route('/agency/routes')
def agency_routes():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    return render_template('agency_routes.html', agency=a, routes=get_routes_by_agency(a['id']))

@app.route('/agency/routes/add', methods=['GET', 'POST'])
def agency_route_add():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    if request.method == 'POST':
        fr = request.form.get('from_city', '').strip()
        to = request.form.get('to_city', '').strip()
        dur = request.form.get('duration', '').strip()
        price = request.form.get('price', '').strip()
        luggage_enabled = request.form.get('luggage_enabled') == 'on'
        luggage_price_per_kg = request.form.get('luggage_price_per_kg', '0').strip()
        if not fr or not to or not dur or not price:
            flash(_('All fields are required.'), 'error'); return render_template('agency_route_form.html', agency=a, route=None)
        if fr == to: flash(_('Departure and arrival must be different.'), 'error'); return render_template('agency_route_form.html', agency=a, route=None)
        add_route(a['id'], fr, to, dur, int(price), luggage_enabled, int(luggage_price_per_kg) if luggage_enabled and luggage_price_per_kg.isdigit() else 0)
        flash(_('Route added successfully.'), 'success'); return redirect(url_for('agency_routes'))
    return render_template('agency_route_form.html', agency=a, route=None)

@app.route('/agency/schedules')
def agency_schedules():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    routes = get_routes_by_agency(a['id'])
    route_ids = [r['id'] for r in routes]
    buses = get_buses_by_agency(a['id'])
    all_schedules = get_schedules_by_route_ids(route_ids)
    all_bookings = get_bookings_by_schedule_ids([s['id'] for s in all_schedules])
    schedules = []
    for s in all_schedules:
        route = next((r for r in routes if r['id'] == s['route_id']), None)
        bus = next((b for b in buses if b['id'] == s['bus_id']), None)
        taken = len([bk for bk in all_bookings if bk['schedule_id'] == s['id'] and bk['paid'] and bk['status'] == 'confirmed'])
        schedules.append({'id': s['id'], 'route': route, 'bus': bus, 'date': s['date'], 'time': s['time'], 'period': s['period'], 'status': s['status'], 'booked': taken, 'capacity': bus['capacity'] if bus else 0})
    return render_template('agency_schedules.html', agency=a, schedules=schedules, periods=PERIODS)

@app.route('/agency/schedules/add', methods=['GET', 'POST'])
def agency_schedule_add():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    routes = get_routes_by_agency(a['id'])
    buses = [b for b in get_buses_by_agency(a['id']) if b.get('status', 'available') == 'available']
    if request.method == 'POST':
        rid = request.form.get('route_id', '').strip()
        bid = request.form.get('bus_id', '').strip()
        d = request.form.get('date', '').strip()
        t = request.form.get('time', '').strip()
        if not rid or not bid or not d or not t:
            flash(_('All fields are required.'), 'error'); return render_template('agency_schedule_form.html', agency=a, routes=routes, buses=buses, periods=PERIODS)
        period = period_key(t)
        add_schedule(int(rid), int(bid), d, t, period)
        flash(_('Trip scheduled successfully.'), 'success'); return redirect(url_for('agency_schedules'))
    return render_template('agency_schedule_form.html', agency=a, routes=routes, buses=buses, periods=PERIODS)

@app.route('/agency/schedule/<int:sid>/cancel')
def agency_schedule_cancel(sid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    s = get_schedule(sid)
    if s:
        route = get_route(s['route_id'])
        if route and route['agency_id'] == a['id']:
            update_schedule(sid, status='cancelled')
            flash(_('Trip cancelled.'), 'success')
    return redirect(url_for('agency_schedules'))

@app.route('/agency/schedule/<int:sid>/edit', methods=['GET', 'POST'])
def agency_schedule_edit(sid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    s = get_schedule(sid)
    if not s: flash(_('Schedule not found.'), 'error'); return redirect(url_for('agency_schedules'))
    route = get_route(s['route_id'])
    if not route or route['agency_id'] != a['id']: flash(_('Access denied.'), 'error'); return redirect(url_for('agency_dashboard'))
    routes = get_routes_by_agency(a['id'])
    buses = get_buses_by_agency(a['id'])
    if request.method == 'POST':
        rid = request.form.get('route_id', '').strip()
        bid = request.form.get('bus_id', '').strip()
        d = request.form.get('date', '').strip()
        t = request.form.get('time', '').strip()
        if not rid or not bid or not d or not t:
            flash(_('All fields are required.'), 'error'); return render_template('agency_schedule_form.html', agency=a, routes=routes, buses=buses, periods=PERIODS, schedule=s, edit_mode=True)
        update_schedule(sid, route_id=int(rid), bus_id=int(bid), date=d, time=t, period=period_key(t))
        flash(_('Trip updated successfully.'), 'success'); return redirect(url_for('agency_schedules'))
    return render_template('agency_schedule_form.html', agency=a, routes=routes, buses=buses, periods=PERIODS, schedule=s, edit_mode=True)

# ── Agency booking management ──
@app.route('/agency/bookings')
def agency_bookings():
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    routes = get_routes_by_agency(a['id'])
    route_ids = [r['id'] for r in routes]
    all_schedules = get_schedules_by_route_ids(route_ids)
    schedule_ids = [s['id'] for s in all_schedules]
    all_bookings = get_bookings_by_schedule_ids(schedule_ids)
    bookings = []
    for bk in all_bookings:
        s = next((x for x in all_schedules if x['id'] == bk['schedule_id']), None)
        route = next((r for r in routes if r['id'] == s['route_id']), None) if s else None
        bus = get_bus(s['bus_id']) if s else None
        is_expired = bk.get('status') == 'expired' or (s and booking_has_departed(s))
        bookings.append({**bk, 'schedule': s, 'route': route, 'bus': bus, '_is_expired': is_expired})
    return render_template('agency_bookings.html', agency=a, bookings=bookings, now=datetime.now())

@app.route('/agency/booking/<int:bid>/cancel')
def agency_booking_cancel(bid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    bk = get_booking(bid)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('agency_bookings'))
    s = get_schedule(bk['schedule_id'])
    route = get_route(s['route_id']) if s else None
    if not route or route['agency_id'] != a['id']: flash(_('Access denied.'), 'error'); return redirect(url_for('agency_dashboard'))
    update_booking(bid, status='cancelled')
    flash(_('Booking {} cancelled.').format(bk['booking_ref']), 'success')
    return redirect(url_for('agency_bookings'))

@app.route('/agency/booking/<int:bid>/reassign', methods=['GET', 'POST'])
def agency_booking_reassign(bid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    bk = get_booking(bid)
    if not bk: flash(_('Booking not found.'), 'error'); return redirect(url_for('agency_bookings'))
    old_s = get_schedule(bk['schedule_id'])
    old_route = get_route(old_s['route_id']) if old_s else None
    if not old_route or old_route['agency_id'] != a['id']: flash(_('Access denied.'), 'error'); return redirect(url_for('agency_dashboard'))
    routes = get_routes_by_agency(a['id'])
    route_ids = [r['id'] for r in routes]
    now = datetime.now()
    all_schedules = get_schedules_by_route_ids(route_ids)
    future = []
    for s in all_schedules:
        if s.get('status') != 'active': continue
        try:
            sdt = datetime.strptime(f"{s['date']} {s['time']}", "%Y-%m-%d %H:%M")
        except (ValueError, KeyError):
            continue
        if sdt <= now: continue
        route = next((r for r in routes if r['id'] == s['route_id']), None)
        bus = get_bus(s['bus_id'])
        taken = len(get_booking_seat_numbers(s['id']))
        available = (bus['capacity'] if bus else 0) - taken
        future.append({'schedule': s, 'route': route, 'bus': bus, 'available': available})
    if request.method == 'POST':
        new_sid = request.form.get('schedule_id', '').strip()
        if not new_sid or not new_sid.isdigit():
            flash(_('Please select a new trip.'), 'error'); return render_template('agency_booking_reassign.html', agency=a, bk=bk, old_s=old_s, old_route=old_route, future=future)
        new_s = get_schedule(int(new_sid))
        if not new_s or new_s['route_id'] not in route_ids:
            flash(_('Invalid trip.'), 'error'); return render_template('agency_booking_reassign.html', agency=a, bk=bk, old_s=old_s, old_route=old_route, future=future)
        new_status = 'confirmed' if bk.get('paid') else 'pending'
        update_booking(bid, schedule_id=int(new_sid), seat_number=None, status=new_status)
        flash(_('Passenger {} reassigned to new trip.').format(bk['passenger_name']), 'success')
        return redirect(url_for('agency_bookings'))
    return render_template('agency_booking_reassign.html', agency=a, bk=bk, old_s=old_s, old_route=old_route, future=future)

@app.route('/agency/schedule/<int:sid>/manifest')
def agency_manifest(sid):
    a = get_agency_session()
    if not a: return redirect(url_for('agency_login'))
    s = get_schedule(sid)
    if not s: flash(_('Schedule not found.'), 'error'); return redirect(url_for('agency_dashboard'))
    route = get_route(s['route_id'])
    if not route or route['agency_id'] != a['id']: flash(_('Access denied.'), 'error'); return redirect(url_for('agency_dashboard'))
    bus = get_bus(s['bus_id'])
    bookings = [bk for bk in get_bookings_by_schedule_ids([sid]) if bk['paid'] and bk['status'] == 'confirmed']
    return render_template('agency_manifest.html', agency=a, s=s, route=route, bus=bus, bookings=bookings, periods=PERIODS)

# ============================================================
# MINISTRY OF TRANSPORT PORTAL (per-country, two-factor)
# ============================================================
MINISTRY_PASSWORD_HASH = generate_password_hash('admin123')

def _ministry_country():
    return session.get('ministry_country', session.get('country', 'cm'))

def _ministry_agencies():
    mc = _ministry_country()
    return get_agencies_by_country(mc)

# ── First factor: shared country password ──

@app.route('/ministry/login', methods=['GET', 'POST'])
def ministry_login():
    mc = session.get('country', 'cm')
    c = COUNTRIES.get(mc, COUNTRIES['cm'])
    if is_shared_pw_used(mc):
        session['ministry_1fa'] = True
        session['ministry_country'] = mc
        return redirect(url_for('ministry_relogin'))
    if request.method == 'POST':
        ip = request.remote_addr or 'unknown'
        blocked, wait = is_rate_limited(ip)
        if blocked:
            flash(_('Too many login attempts. Try again in {} minutes.').format(int(wait) + 1), 'warning')
            return render_template('ministry_login.html', ministry_country=c)
        pw = request.form.get('password', '').strip()
        if is_shared_pw_used(mc):
            session['ministry_1fa'] = True
            session['ministry_country'] = mc
            flash(_('The shared password has already been used. Please sign in with your super admin credentials.'), 'error')
            return redirect(url_for('ministry_relogin'))
        if check_password_hash(MINISTRY_PASSWORD_HASH, pw):
            session['ministry_1fa'] = True
            session['ministry_country'] = mc
            login_attempts.pop(ip, None)
            return redirect(url_for('ministry_relogin'))
        flash(_('Incorrect ministry password.'), 'error')
    return render_template('ministry_login.html', ministry_country=c)

# ── Second factor: super admin email + password ──

@app.route('/ministry/relogin', methods=['GET', 'POST'])
def ministry_relogin():
    if not session.get('ministry_1fa'):
        return redirect(url_for('ministry_login'))
    mc = _ministry_country()
    c = COUNTRIES.get(mc, COUNTRIES['cm'])
    existing = get_super_admin_by_country(mc)

    if request.method == 'POST':
        action = request.form.get('action', 'login')

        if action == 'register':
            # First-time super admin registration
            email = request.form.get('email', '').strip().lower()
            pw = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            if not email or '@' not in email:
                flash(_('Please enter a valid email address.'), 'error')
                return redirect(url_for('ministry_relogin'))
            if len(pw) < 6:
                flash(_('Password must be at least 6 characters.'), 'error')
                return redirect(url_for('ministry_relogin'))
            if pw != confirm:
                flash(_('Passwords do not match.'), 'error')
                return redirect(url_for('ministry_relogin'))
            if get_super_admin_by_email(email, mc):
                flash(_('An admin with this email already exists.'), 'error')
                return redirect(url_for('ministry_relogin'))
            add_super_admin(email, generate_password_hash(pw), mc)
            flash(_('Super admin account created. Please log in.'), 'success')
            return redirect(url_for('ministry_relogin'))

        else:
            # Login existing super admin
            ip = request.remote_addr or 'unknown'
            blocked, wait = is_rate_limited(ip)
            if blocked:
                flash(_('Too many login attempts. Try again in {} minutes.').format(int(wait) + 1), 'warning')
                return redirect(url_for('ministry_relogin'))
            email = request.form.get('email', '').strip().lower()
            pw = request.form.get('password', '')
            admin = get_super_admin_by_email(email, mc)
            if not admin or not check_password_hash(admin['password_hash'], pw):
                flash(_('Invalid email or password.'), 'error')
                return redirect(url_for('ministry_relogin'))
            session['ministry'] = True
            session.permanent = True
            session['super_admin_id'] = admin['id']
            session['super_admin_email'] = admin['email']
            login_attempts.pop(ip, None)
            session.pop('ministry_1fa', None)
            mark_shared_pw_used(mc)
            flash(_('Welcome, {}.'.format(admin['email'])), 'success')
            return redirect(url_for('ministry_dashboard'))

    return render_template('ministry_relogin.html', ministry_country=c, has_admin=existing is not None)

# ── Forgot / Reset password ──

@app.route('/ministry/forgot-password', methods=['GET', 'POST'])
def ministry_forgot_password():
    if not session.get('ministry_1fa'):
        return redirect(url_for('ministry_login'))
    mc = _ministry_country()
    c = COUNTRIES.get(mc, COUNTRIES['cm'])
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        admin = get_super_admin_by_email(email, mc)
        if admin:
            code = ''.join(random.choices(string.digits, k=8))
            expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M')
            update_super_admin(admin['id'], reset_token=code, reset_token_expiry=expiry)
            session['reset_admin_id'] = admin['id']
            body = _("Your AFRI Trans ministry password reset code is: <b>{code}</b><br>This code expires in 15 minutes.").format(code=code)
            sent = send_email(email, _('AFRI Trans - Password Reset Code'), body)
            if sent:
                flash(_('An 8-digit verification code has been sent to your email.'), 'success')
            else:
                flash(_('(Demo: your code is {code})').format(code=code), 'success')
        else:
            flash(_('No admin found with that email.'), 'error')
            return redirect(url_for('ministry_forgot_password'))
        return redirect(url_for('ministry_verify_code'))
    return render_template('ministry_forgot_password.html', ministry_country=c)

@app.route('/ministry/verify-code', methods=['GET', 'POST'])
def ministry_verify_code():
    if not session.get('ministry_1fa'):
        return redirect(url_for('ministry_login'))
    aid = session.get('reset_admin_id')
    if not aid:
        return redirect(url_for('ministry_forgot_password'))
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        db = get_db()
        r = db.execute("SELECT * FROM super_admins WHERE id = ?", (aid,)).fetchone()
        db.close()
        admin = dict(r) if r else None
        if not admin or admin.get('reset_token') != code:
            flash(_('Invalid verification code.'), 'error')
            return redirect(url_for('ministry_verify_code'))
        expiry = datetime.strptime(admin.get('reset_token_expiry', '2000-01-01 00:00'), '%Y-%m-%d %H:%M')
        if datetime.now() > expiry:
            flash(_('Verification code has expired. Please request a new one.'), 'error')
            session.pop('reset_admin_id', None)
            return redirect(url_for('ministry_forgot_password'))
        session['reset_verified_sa'] = True
        return redirect(url_for('ministry_reset_password'))
    return render_template('ministry_verify_code.html', title=_('Super Admin'))

@app.route('/ministry/reset-password', methods=['GET', 'POST'])
def ministry_reset_password():
    if not session.get('ministry_1fa'):
        return redirect(url_for('ministry_login'))
    if not session.get('reset_verified_sa') or not session.get('reset_admin_id'):
        return redirect(url_for('ministry_forgot_password'))
    if request.method == 'POST':
        pw = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(pw) < 6:
            flash(_('Password must be at least 6 characters.'), 'error')
            return redirect(url_for('ministry_reset_password'))
        if pw != confirm:
            flash(_('Passwords do not match.'), 'error')
            return redirect(url_for('ministry_reset_password'))
        update_super_admin(session['reset_admin_id'], password_hash=generate_password_hash(pw), reset_token=None, reset_token_expiry=None)
        session.pop('reset_admin_id', None)
        session.pop('reset_verified_sa', None)
        flash(_('Password reset successful. Please log in.'), 'success')
        return redirect(url_for('ministry_relogin'))
    return render_template('ministry_reset_password.html')

# ── Logout ──

@app.route('/ministry/logout')
def ministry_logout():
    session.pop('ministry', None)
    session.pop('ministry_1fa', None)
    session.pop('ministry_country', None)
    session.pop('super_admin_id', None)
    session.pop('super_admin_email', None)
    return redirect(url_for('index'))

@app.route('/ministry')
def ministry_dashboard():
    if not session.get('ministry'): return redirect(url_for('ministry_login'))
    mc = _ministry_country()
    c = COUNTRIES.get(mc, COUNTRIES['cm'])
    agencies = _ministry_agencies()
    agency_ids = [a['id'] for a in agencies]
    bus_list = []
    all_routes = []
    schedule_ids = []
    all_bookings_list = []
    all_schedules_list = []
    agency_stats = {}
    for a in agencies:
        aid = a['id']
        ag_buses = get_buses_by_agency(aid)
        ag_routes = get_routes_by_agency(aid)
        ag_scheds = get_schedules_by_route_ids([r['id'] for r in ag_routes])
        ag_sched_ids = [s['id'] for s in ag_scheds]
        ag_bookings = get_bookings_by_schedule_ids(ag_sched_ids)
        ag_paid = [bk for bk in ag_bookings if bk.get('paid')]
        ag_revenue = 0
        for bk in ag_paid:
            s = next((x for x in ag_scheds if x['id'] == bk['schedule_id']), None)
            rt = next((r for r in ag_routes if r['id'] == (s['route_id'] if s else None)), None) if s else None
            if rt:
                bus = next((b for b in ag_buses if b['id'] == (s['bus_id'] if s else None)), None) if s else None
                vs = bus.get('vip_price') if bus and bus.get('vip_price') is not None else c.get('vip_surcharge', 0)
                vip_extra = vs if (bus and bus.get('bus_type') == 'vip') else 0
                ag_revenue += rt['price'] + vip_extra + bk.get('luggage_fee', 0)
        agency_stats[aid] = {'buses': ag_buses, 'routes': ag_routes, 'revenue': ag_revenue, 'bookings': len(ag_paid)}
        bus_list.extend(ag_buses)
        all_routes.extend(ag_routes)
        all_schedules_list.extend(ag_scheds)
        schedule_ids.extend(ag_sched_ids)
    all_bookings_list = get_bookings_by_schedule_ids(schedule_ids)
    total_agencies = len(agencies)
    pending_agencies = sum(1 for a in agencies if not a.get('approved', False))
    total_buses = len(bus_list)
    total_routes = len(all_routes)
    total_schedules = len(all_schedules_list)
    active_schedules = sum(1 for s in all_schedules_list if s.get('status') == 'active')
    total_bookings = len(all_bookings_list)
    total_revenue = sum(
        bk.get('luggage_fee', 0) + next((r['price'] for r in all_routes if r['id'] == next((s['route_id'] for s in all_schedules_list if s['id'] == bk['schedule_id']), None)), 0)
        for bk in all_bookings_list if bk.get('paid')
    )
    total_commission = get_total_commission(agency_ids=agency_ids if agency_ids else None)
    return render_template('ministry_dashboard.html', mc=mc, c=c, agencies=agencies, agency_stats=agency_stats, total_agencies=total_agencies, pending_agencies=pending_agencies, total_bookings=total_bookings, total_revenue=total_revenue, total_buses=total_buses, total_routes=total_routes, total_schedules=total_schedules, active_schedules=active_schedules, total_commission=total_commission)

@app.route('/ministry/agencies')
def ministry_agencies():
    if not session.get('ministry'): return redirect(url_for('ministry_login'))
    mc = _ministry_country()
    agencies_info = []
    for a in _ministry_agencies():
        cname = COUNTRIES.get(a.get('country', 'cm'), {}).get('name', '')
        bus_count = get_agency_bus_count(a['id'])
        routes = get_routes_by_agency(a['id'])
        route_ids = [r['id'] for r in routes]
        booking_count = len(get_bookings_by_schedule_ids([s['id'] for s in get_schedules_by_route_ids(route_ids)]))
        agencies_info.append({'agency': a, 'country_name': cname, 'buses': bus_count, 'routes': len(routes), 'bookings': booking_count, 'approved': a.get('approved', False)})
    return render_template('ministry_agencies.html', agencies=agencies_info, mc=mc)

@app.route('/ministry/agency/<int:aid>/approve', methods=['POST'])
def ministry_approve_agency(aid):
    if not session.get('ministry'): return redirect(url_for('ministry_login'))
    agencies = _ministry_agencies()
    agency = next((a for a in agencies if a['id'] == aid), None)
    if not agency: flash('Agency not found in your country.', 'error'); return redirect(url_for('ministry_agencies'))
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide an approval reason.', 'error')
        return redirect(url_for('ministry_agencies'))
    update_agency(aid, approved=True, rejection_reason=None, approval_reason=reason)
    flash(f'Agency "{agency["name"]}" approved: {reason}', 'success')
    return redirect(url_for('ministry_agencies'))

@app.route('/ministry/agency/<int:aid>/reject', methods=['POST'])
def ministry_reject_agency(aid):
    if not session.get('ministry'): return redirect(url_for('ministry_login'))
    agencies = _ministry_agencies()
    agency = next((a for a in agencies if a['id'] == aid), None)
    if not agency: flash('Agency not found in your country.', 'error'); return redirect(url_for('ministry_agencies'))
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a rejection reason.', 'error')
        return redirect(url_for('ministry_agencies'))
    update_agency(aid, approved=False, rejection_reason=reason)
    flash(f'Agency "{agency["name"]}" rejected: {reason}', 'error')
    return redirect(url_for('ministry_agencies'))

@app.route('/ministry/bookings')
def ministry_bookings():
    if not session.get('ministry'): return redirect(url_for('ministry_login'))
    mc = _ministry_country()
    agencies = _ministry_agencies()
    agency_ids = [a['id'] for a in agencies]
    all_routes = []
    for aid in agency_ids:
        all_routes.extend(get_routes_by_agency(aid))
    route_ids = [r['id'] for r in all_routes]
    all_schedules = get_schedules_by_route_ids(route_ids)
    schedule_ids = [s['id'] for s in all_schedules]
    all_bookings = get_bookings_by_schedule_ids(schedule_ids)
    bookings_info = []
    for bk in all_bookings:
        s = next((x for x in all_schedules if x['id'] == bk['schedule_id']), None)
        route = next((r for r in all_routes if r['id'] == (s['route_id'] if s else None)), None) if s else None
        agency = next((a for a in agencies if a['id'] == (route['agency_id'] if route else None)), None) if route else None
        bookings_info.append({
            'ref': bk.get('booking_ref', ''),
            'passenger': bk.get('passenger_name', ''),
            'phone': bk.get('phone', ''),
            'route': f"{route['from']}\u2192{route['to']}" if route else '?',
            'agency': agency['name'] if agency else '?',
            'date': s.get('date', '?') if s else '?',
            'status': bk.get('status', '?'),
            'paid': bk.get('paid', False),
            'amount': bk.get('luggage_fee', 0) + (route['price'] if route else 0)
        })
    return render_template('ministry_bookings.html', bookings=bookings_info, mc=mc)

# ── Super Admin Portal ──

ADMIN_PASSWORD = 'adolfai12'

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        pw = request.form.get('password', '').strip()
        if pw == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect(url_for('admin_dashboard'))
        flash(_('Incorrect password.'), 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    all_agencies = get_all_agencies()
    total_agencies = len(all_agencies)
    subscribed = 0
    for a in all_agencies:
        if has_active_subscription(a['id']):
            subscribed += 1
    total_commission = get_total_commission_global()
    subs = get_all_subscriptions()
    prices_db = get_subscription_prices()
    prices = {p['currency']: p['monthly_price'] for p in prices_db}
    for curr in ['XAF', 'XOF', 'NGN']:
        if curr not in prices:
            prices[curr] = SUBSCRIPTION_PRICES.get(curr, {}).get('monthly', 58000)
    return render_template('admin_dashboard.html',
        total_agencies=total_agencies,
        subscribed=subscribed,
        total_commission=total_commission,
        subscriptions=subs,
        prices=prices,
        all_agencies=all_agencies)

@app.route('/admin/prices', methods=['POST'])
def admin_update_prices():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    for currency in ['XAF', 'XOF', 'NGN']:
        val = request.form.get(f'price_{currency}', '').strip()
        if val and val.isdigit():
            set_subscription_price(currency, int(val))
    flash(_('Subscription prices updated.'), 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/subscribe/<int:aid>', methods=['POST'])
def admin_subscribe_agency(aid):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    months = request.form.get('months', '').strip()
    if not months or not months.isdigit() or int(months) < 1:
        flash(_('Please enter a valid number of months.'), 'error')
        return redirect(url_for('admin_dashboard'))
    months = int(months)
    agency = get_agency(aid)
    if not agency:
        flash(_('Agency not found.'), 'error')
        return redirect(url_for('admin_dashboard'))
    country_code = agency.get('country', 'cm')
    c = COUNTRIES.get(country_code, COUNTRIES['cm'])
    curr = c['currency_code']
    prices_db = get_subscription_prices()
    price_map = {p['currency']: p['monthly_price'] for p in prices_db}
    if curr not in price_map:
        price_map[curr] = SUBSCRIPTION_PRICES.get(curr, {}).get('monthly', 58000)
    amount = price_map[curr] * months
    extra_days = months * 30
    extend_subscription(aid, f'custom_{months}mo', amount, curr, extra_days)
    sub = get_active_subscription(aid)
    flash(_('Subscription added: {} months for {} {} (until {}).').format(months, amount, curr, sub['end_date']), 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
