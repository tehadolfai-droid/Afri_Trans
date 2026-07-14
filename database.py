import sqlite3
import json
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')

def get_db():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def rows_to_list(rows):
    return [dict(r) for r in rows]

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS agencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT DEFAULT '',
            password TEXT NOT NULL,
            country TEXT NOT NULL DEFAULT 'cm',
            locations TEXT NOT NULL DEFAULT '[]',
            approved INTEGER NOT NULL DEFAULT 0,
            rejection_reason TEXT,
            approval_reason TEXT,
            reset_token TEXT,
            reset_token_expiry TEXT,
            created_at TEXT NOT NULL,
            whatsapp TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_id INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            plate TEXT NOT NULL,
            capacity INTEGER NOT NULL DEFAULT 71,
            bus_type TEXT NOT NULL DEFAULT 'standard',
            status TEXT NOT NULL DEFAULT 'available',
            vip_price REAL DEFAULT NULL
        );
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_id INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            from_city TEXT NOT NULL,
            to_city TEXT NOT NULL,
            duration TEXT NOT NULL,
            price INTEGER NOT NULL,
            luggage_enabled INTEGER NOT NULL DEFAULT 0,
            luggage_price_per_kg INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
            bus_id INTEGER NOT NULL REFERENCES buses(id) ON DELETE CASCADE,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            period TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            id_number TEXT DEFAULT '',
            UNIQUE(phone, id_number)
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
            passenger_id INTEGER NOT NULL REFERENCES passengers(id),
            seat_number INTEGER,
            booking_ref TEXT NOT NULL UNIQUE,
            paid INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            payment_method TEXT,
            transaction_id TEXT,
            created_at TEXT NOT NULL,
            luggage_weight REAL NOT NULL DEFAULT 0,
            luggage_fee INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS super_admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            country_code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            reset_token TEXT,
            reset_token_expiry TEXT,
            UNIQUE(email, country_code)
        );
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_buses_agency ON buses(agency_id);
        CREATE INDEX IF NOT EXISTS idx_routes_agency ON routes(agency_id);
        CREATE INDEX IF NOT EXISTS idx_schedules_route ON schedules(route_id);
        CREATE INDEX IF NOT EXISTS idx_schedules_bus ON schedules(bus_id);
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
            agency_id INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL,
            currency_code TEXT NOT NULL DEFAULT 'XAF',
            created_at TEXT NOT NULL,
            settled INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS agency_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_id INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            plan TEXT NOT NULL,
            amount_paid INTEGER NOT NULL,
            currency TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_id INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            badge TEXT NOT NULL DEFAULT 'NEW',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT '',
            role TEXT DEFAULT 'user',
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS subscription_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT UNIQUE NOT NULL,
            monthly_price INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_bookings_schedule ON bookings(schedule_id);
        CREATE INDEX IF NOT EXISTS idx_bookings_passenger ON bookings(passenger_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_seat ON bookings(schedule_id, seat_number) WHERE seat_number IS NOT NULL;
    ''')
    # Migrate existing databases: add missing columns
    for col in ('approval_reason', 'email', 'reset_token', 'reset_token_expiry'):
        try:
            db.execute(f"ALTER TABLE agencies ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    # Add global unique index on agency email
    try:
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_agencies_email ON agencies(email) WHERE email != ''")
    except sqlite3.OperationalError:
        pass
    # Create notification_log table
    try:
        db.execute("SELECT 1 FROM notification_log LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("""CREATE TABLE IF NOT EXISTS notification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
            notification_type TEXT NOT NULL,
            sent_at TEXT NOT NULL
        )""")
    # Add unique index on agency name + country to prevent duplicates
    try:
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_agencies_name_country ON agencies(LOWER(name), country)")
    except sqlite3.OperationalError:
        pass
    # Add announcements table for existing databases
    try:
        db.execute("SELECT 1 FROM announcements LIMIT 1")
    except sqlite3.OperationalError:
        db.execute("""CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_id INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            badge TEXT NOT NULL DEFAULT 'NEW',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )""")
    # Add message_fr column for bilingual announcements
    try:
        db.execute("ALTER TABLE announcements ADD COLUMN message_fr TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    # Add message columns for all 11 languages
    for lang_col in ('message_ar', 'message_pt', 'message_sw', 'message_am',
                     'message_so', 'message_ti', 'message_es', 'message_af', 'message_zu'):
        try:
            db.execute(f"ALTER TABLE announcements ADD COLUMN {lang_col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    # Add whatsapp column for agency contact
    try:
        db.execute("ALTER TABLE agencies ADD COLUMN whatsapp TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    # Add vip_price column for per-bus VIP pricing
    try:
        db.execute("ALTER TABLE buses ADD COLUMN vip_price REAL DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
    db.commit()
    db.close()

def migrate_from_json():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
    if not os.path.exists(json_path):
        return
    # Check if migration already done
    db = get_db()
    existing = db.execute("SELECT value FROM meta WHERE key = 'migrated'").fetchone()
    if existing:
        db.close()
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Migrate agencies
    for a in data.get('agencies', []):
        locations_json = json.dumps(a.get('locations', []), ensure_ascii=False)
        approved = 1 if a.get('approved', False) else 0
        created_at = a.get('created_at', datetime.now().strftime('%Y-%m-%d'))
        rejection_reason = a.get('rejection_reason')
        db.execute(
            "INSERT INTO agencies (id, name, password, country, locations, approved, rejection_reason, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (a['id'], a['name'], a['password'], a.get('country', 'cm'), locations_json, approved, rejection_reason, created_at)
        )

    # Migrate buses
    for b in data.get('buses', []):
        db.execute(
            "INSERT INTO buses (id, agency_id, plate, capacity, bus_type, status) VALUES (?, ?, ?, ?, ?, ?)",
            (b['id'], b['agency_id'], b['plate'], b.get('capacity', 71), b.get('bus_type', 'standard'), b.get('status', 'available'))
        )

    # Migrate routes
    for r in data.get('routes', []):
        luggage_enabled = 1 if r.get('luggage_enabled', False) else 0
        db.execute(
            "INSERT INTO routes (id, agency_id, from_city, to_city, duration, price, luggage_enabled, luggage_price_per_kg) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (r['id'], r['agency_id'], r['from'], r['to'], r['duration'], r['price'], luggage_enabled, r.get('luggage_price_per_kg', 0))
        )

    # Migrate schedules
    for s in data.get('schedules', []):
        db.execute(
            "INSERT INTO schedules (id, route_id, bus_id, date, time, period, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (s['id'], s['route_id'], s['bus_id'], s['date'], s['time'], s['period'], s.get('status', 'active'))
        )

    # Migrate bookings + passengers
    passenger_cache = {}
    for bk in data.get('bookings', []):
        name = bk.get('passenger_name', '')
        phone = bk.get('phone', '')
        id_number = bk.get('id_number', '')
        # Find or create passenger
        pkey = (phone, id_number)
        if pkey not in passenger_cache:
            existing_p = db.execute("SELECT id FROM passengers WHERE phone = ? AND id_number = ?", (phone, id_number)).fetchone()
            if existing_p:
                passenger_cache[pkey] = existing_p['id']
            else:
                db.execute("INSERT INTO passengers (name, phone, id_number) VALUES (?, ?, ?)", (name, phone, id_number))
                passenger_cache[pkey] = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        paid = 1 if bk.get('paid', False) else 0
        db.execute(
            "INSERT INTO bookings (id, schedule_id, passenger_id, seat_number, booking_ref, paid, status, payment_method, transaction_id, created_at, luggage_weight, luggage_fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (bk['id'], bk['schedule_id'], passenger_cache[pkey], bk.get('seat_number'), bk['booking_ref'], paid, bk.get('status', 'pending'), bk.get('payment_method'), bk.get('transaction_id'), bk.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M')), bk.get('luggage_weight', 0), bk.get('luggage_fee', 0))
        )

    # Migrate next_ref
    db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", ('next_ref', str(data.get('next_ref', 1))))

    # Mark migration complete
    db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", ('migrated', '1'))
    db.commit()
    db.close()

# ── Helper functions to convert DB rows to app dicts ──

def agency_from_row(r):
    d = dict(r)
    d['locations'] = json.loads(d.get('locations', '[]'))
    d['approved'] = bool(d['approved'])
    return d

def route_from_row(r):
    d = dict(r)
    d['from'] = d.pop('from_city')
    d['to'] = d.pop('to_city')
    d['luggage_enabled'] = bool(d['luggage_enabled'])
    return d

def booking_from_row(r, passenger=None):
    d = dict(r)
    d['paid'] = bool(d['paid'])
    if passenger:
        d['passenger_name'] = passenger['name']
        d['phone'] = passenger['phone']
        d['id_number'] = passenger.get('id_number', '')
    return d

def schedule_from_row(r):
    return dict(r)

def bus_from_row(r):
    return dict(r)

# ── CRUD: Agencies ──

def get_agencies():
    db = get_db()
    rows = db.execute("SELECT * FROM agencies ORDER BY id").fetchall()
    db.close()
    return [agency_from_row(r) for r in rows]

def get_agency(aid):
    db = get_db()
    r = db.execute("SELECT * FROM agencies WHERE id = ?", (aid,)).fetchone()
    db.close()
    return agency_from_row(r) if r else None

def get_agencies_by_country(code):
    db = get_db()
    rows = db.execute("SELECT * FROM agencies WHERE country = ? ORDER BY id", (code,)).fetchall()
    db.close()
    return [agency_from_row(r) for r in rows]

def get_approved_agencies_by_country(code):
    db = get_db()
    rows = db.execute("SELECT * FROM agencies WHERE country = ? AND approved = 1 ORDER BY id", (code,)).fetchall()
    db.close()
    return [agency_from_row(r) for r in rows]

def get_approved_agencies_contact():
    db = get_db()
    rows = db.execute("SELECT id, name, whatsapp FROM agencies WHERE approved = 1 AND whatsapp != '' ORDER BY name").fetchall()
    db.close()
    return [dict(r) for r in rows]

def add_agency(name, password, country, locations, created_at, approved=False, whatsapp='', email=''):
    db = get_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        # Check name+country duplicate inside transaction
        if db.execute("SELECT id FROM agencies WHERE LOWER(name) = LOWER(?) AND country = ?", (name, country)).fetchone():
            db.rollback()
            db.close()
            return (None, 'name_exists')
        # Check email duplicate inside transaction
        if email and db.execute("SELECT id FROM agencies WHERE LOWER(email) = LOWER(?)", (email,)).fetchone():
            db.rollback()
            db.close()
            return (None, 'email_exists')
        loc_json = json.dumps(locations, ensure_ascii=False)
        c = db.execute(
            "INSERT INTO agencies (name, password, country, locations, approved, created_at, whatsapp, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, password, country, loc_json, 1 if approved else 0, created_at, whatsapp, email)
        )
        aid = c.lastrowid
        db.commit()
        db.close()
        return (aid, None)
    except sqlite3.IntegrityError:
        db.rollback()
        db.close()
        return (None, 'name_exists')

def update_agency(aid, **kwargs):
    db = get_db()
    fields = []
    vals = []
    for k, v in kwargs.items():
        if k == 'locations':
            v = json.dumps(v, ensure_ascii=False)
        elif k == 'approved':
            v = 1 if v else 0
        fields.append(f"{k} = ?")
        vals.append(v)
    vals.append(aid)
    db.execute(f"UPDATE agencies SET {', '.join(fields)} WHERE id = ?", vals)
    db.commit()
    db.close()

def agency_name_exists(name, country):
    db = get_db()
    r = db.execute("SELECT id FROM agencies WHERE LOWER(name) = LOWER(?) AND country = ?", (name, country)).fetchone()
    db.close()
    return r is not None

def get_agency_by_email(email, country):
    db = get_db()
    r = db.execute("SELECT * FROM agencies WHERE LOWER(email) = LOWER(?) AND country = ?", (email, country)).fetchone()
    db.close()
    return agency_from_row(r) if r else None

def get_agency_by_email_global(email):
    db = get_db()
    r = db.execute("SELECT * FROM agencies WHERE LOWER(email) = LOWER(?)", (email,)).fetchone()
    db.close()
    return agency_from_row(r) if r else None

def get_agency_by_reset_token(token):
    db = get_db()
    r = db.execute("SELECT * FROM agencies WHERE reset_token = ?", (token,)).fetchone()
    db.close()
    return agency_from_row(r) if r else None

# ── CRUD: Buses ──

def get_buses_by_agency(aid):
    db = get_db()
    rows = db.execute("SELECT * FROM buses WHERE agency_id = ? ORDER BY id", (aid,)).fetchall()
    db.close()
    return rows_to_list(rows)

def get_bus(bid):
    db = get_db()
    r = db.execute("SELECT * FROM buses WHERE id = ?", (bid,)).fetchone()
    db.close()
    return dict(r) if r else None

def add_bus(agency_id, plate, capacity=71, bus_type='standard', status='available', vip_price=None):
    db = get_db()
    c = db.execute(
        "INSERT INTO buses (agency_id, plate, capacity, bus_type, status, vip_price) VALUES (?, ?, ?, ?, ?, ?)",
        (agency_id, plate, capacity, bus_type, status, vip_price)
    )
    bid = c.lastrowid
    db.commit()
    db.close()
    return bid

def update_bus(bid, **kwargs):
    db = get_db()
    fields = []
    vals = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        vals.append(v)
    vals.append(bid)
    db.execute(f"UPDATE buses SET {', '.join(fields)} WHERE id = ?", vals)
    db.commit()
    db.close()

def get_agency_bus_count(aid):
    db = get_db()
    r = db.execute("SELECT COUNT(*) FROM buses WHERE agency_id = ?", (aid,)).fetchone()
    db.close()
    return r[0]

# ── CRUD: Routes ──

def get_routes_by_agency(aid):
    db = get_db()
    rows = db.execute("SELECT * FROM routes WHERE agency_id = ? ORDER BY id", (aid,)).fetchall()
    db.close()
    return [route_from_row(r) for r in rows]

def get_route(rid):
    db = get_db()
    r = db.execute("SELECT * FROM routes WHERE id = ?", (rid,)).fetchone()
    db.close()
    return route_from_row(r) if r else None

def add_route(agency_id, from_city, to_city, duration, price, luggage_enabled=False, luggage_price_per_kg=0):
    db = get_db()
    c = db.execute(
        "INSERT INTO routes (agency_id, from_city, to_city, duration, price, luggage_enabled, luggage_price_per_kg) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (agency_id, from_city, to_city, duration, price, 1 if luggage_enabled else 0, luggage_price_per_kg)
    )
    rid = c.lastrowid
    db.commit()
    db.close()
    return rid

def get_all_routes():
    db = get_db()
    rows = db.execute("SELECT * FROM routes ORDER BY id").fetchall()
    db.close()
    return [route_from_row(r) for r in rows]

# ── CRUD: Schedules ──

def get_schedules():
    db = get_db()
    rows = db.execute("SELECT * FROM schedules ORDER BY id").fetchall()
    db.close()
    return rows_to_list(rows)

def get_schedule(sid):
    db = get_db()
    r = db.execute("SELECT * FROM schedules WHERE id = ?", (sid,)).fetchone()
    db.close()
    return dict(r) if r else None

def add_schedule(route_id, bus_id, date, time, period, status='active'):
    db = get_db()
    c = db.execute(
        "INSERT INTO schedules (route_id, bus_id, date, time, period, status) VALUES (?, ?, ?, ?, ?, ?)",
        (route_id, bus_id, date, time, period, status)
    )
    sid = c.lastrowid
    db.execute("UPDATE buses SET status = 'busy' WHERE id = ?", (bus_id,))
    db.commit()
    db.close()
    return sid

def update_schedule(sid, **kwargs):
    db = get_db()
    fields = []
    vals = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        vals.append(v)
    vals.append(sid)
    db.execute(f"UPDATE schedules SET {', '.join(fields)} WHERE id = ?", vals)
    if kwargs.get('status') == 'cancelled':
        s = db.execute("SELECT bus_id FROM schedules WHERE id = ?", (sid,)).fetchone()
        if s:
            db.execute("UPDATE buses SET status = 'available' WHERE id = ?", (s['bus_id'],))
    db.commit()
    db.close()

def get_schedules_by_route_ids(route_ids):
    if not route_ids:
        return []
    placeholders = ','.join('?' * len(route_ids))
    db = get_db()
    rows = db.execute(f"SELECT * FROM schedules WHERE route_id IN ({placeholders}) ORDER BY id", route_ids).fetchall()
    db.close()
    return rows_to_list(rows)

# ── CRUD: Bookings ──

def get_bookings():
    db = get_db()
    rows = db.execute("SELECT b.*, p.name AS passenger_name, p.phone, p.id_number FROM bookings b JOIN passengers p ON b.passenger_id = p.id ORDER BY b.id").fetchall()
    db.close()
    return [booking_from_row(r) for r in rows]

def get_booking(bid):
    db = get_db()
    r = db.execute("SELECT b.*, p.name AS passenger_name, p.phone, p.id_number FROM bookings b JOIN passengers p ON b.passenger_id = p.id WHERE b.id = ?", (bid,)).fetchone()
    db.close()
    return booking_from_row(r) if r else None

def get_booking_by_ref(ref):
    db = get_db()
    r = db.execute("SELECT b.*, p.name AS passenger_name, p.phone, p.id_number FROM bookings b JOIN passengers p ON b.passenger_id = p.id WHERE b.booking_ref = ?", (ref,)).fetchone()
    db.close()
    return booking_from_row(r) if r else None

def add_booking(schedule_id, passenger_name, phone, id_number, seat_number, booking_ref, luggage_weight=0, luggage_fee=0):
    db = get_db()
    # Find or create passenger
    p = db.execute("SELECT id FROM passengers WHERE phone = ? AND id_number = ?", (phone, id_number or '')).fetchone()
    if p:
        passenger_id = p['id']
    else:
        c = db.execute("INSERT INTO passengers (name, phone, id_number) VALUES (?, ?, ?)", (passenger_name, phone, id_number or ''))
        passenger_id = c.lastrowid
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    c = db.execute(
        "INSERT INTO bookings (schedule_id, passenger_id, seat_number, booking_ref, paid, status, created_at, luggage_weight, luggage_fee) VALUES (?, ?, ?, ?, 0, 'pending', ?, ?, ?)",
        (schedule_id, passenger_id, seat_number, booking_ref, now, luggage_weight, luggage_fee)
    )
    bid = c.lastrowid
    db.commit()
    db.close()
    return bid

def add_booking_atomic(schedule_id, passenger_name, phone, id_number, seat_number, booking_ref, luggage_weight=0, luggage_fee=0):
    """Atomically book a seat — uses DB-level unique index to prevent race conditions.
    Returns (bid, None) on success, or (None, error_message) if seat was taken."""
    db = get_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        p = db.execute("SELECT id FROM passengers WHERE phone = ? AND id_number = ?", (phone, id_number or '')).fetchone()
        if p:
            passenger_id = p['id']
        else:
            c = db.execute("INSERT INTO passengers (name, phone, id_number) VALUES (?, ?, ?)", (passenger_name, phone, id_number or ''))
            passenger_id = c.lastrowid
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        c = db.execute(
            "INSERT INTO bookings (schedule_id, passenger_id, seat_number, booking_ref, paid, status, created_at, luggage_weight, luggage_fee) VALUES (?, ?, ?, ?, 0, 'pending', ?, ?, ?)",
            (schedule_id, passenger_id, seat_number, booking_ref, now, luggage_weight, luggage_fee)
        )
        bid = c.lastrowid
        db.commit()
        return (bid, None)
    except sqlite3.IntegrityError:
        db.rollback()
        return (None, 'That seat was just taken by another passenger. Please pick a different seat.')
    finally:
        db.close()

def confirm_booking_atomic(bid, payment_method, transaction_id):
    """Atomically confirm a booking payment — double-checks seat availability inside a transaction."""
    db = get_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        bk = db.execute("SELECT b.*, s.date, s.time FROM bookings b JOIN schedules s ON b.schedule_id = s.id WHERE b.id = ?", (bid,)).fetchone()
        if not bk:
            db.rollback()
            return (False, 'Booking not found.')
        if bk['paid']:
            db.commit()
            return (True, None)
        if bk['seat_number']:
            taken = db.execute(
                "SELECT 1 FROM bookings WHERE schedule_id = ? AND seat_number = ? AND id != ? AND paid = 1 AND status IN ('confirmed')",
                (bk['schedule_id'], bk['seat_number'], bid)
            ).fetchone()
            if taken:
                db.execute("UPDATE bookings SET seat_number = NULL WHERE id = ?", (bid,))
                db.commit()
                return (False, 'seat_taken')
        db.execute(
            "UPDATE bookings SET paid = 1, status = 'confirmed', payment_method = ?, transaction_id = ? WHERE id = ?",
            (payment_method, transaction_id, bid)
        )
        db.commit()
        return (True, None)
    except Exception as e:
        db.rollback()
        return (False, str(e))
    finally:
        db.close()

def update_booking(bid, **kwargs):
    db = get_db()
    fields = []
    vals = []
    for k, v in kwargs.items():
        if k in ('paid',):
            v = 1 if v else 0
        fields.append(f"{k} = ?")
        vals.append(v)
    vals.append(bid)
    db.execute(f"UPDATE bookings SET {', '.join(fields)} WHERE id = ?", vals)
    db.commit()
    db.close()

def get_booking_seat_numbers(schedule_id, exclude_bid=None, statuses=('confirmed',)):
    db = get_db()
    if exclude_bid:
        rows = db.execute(
            "SELECT seat_number FROM bookings WHERE schedule_id = ? AND id != ? AND paid = 1 AND status IN ({}) AND seat_number IS NOT NULL".format(','.join('?' * len(statuses))),
            (schedule_id, exclude_bid) + statuses
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT seat_number FROM bookings WHERE schedule_id = ? AND paid = 1 AND status IN ({}) AND seat_number IS NOT NULL".format(','.join('?' * len(statuses))),
            (schedule_id,) + statuses
        ).fetchall()
    db.close()
    return {r['seat_number'] for r in rows}

def get_bookings_by_schedule_ids(schedule_ids):
    if not schedule_ids:
        return []
    placeholders = ','.join('?' * len(schedule_ids))
    db = get_db()
    rows = db.execute(f"SELECT b.*, p.name AS passenger_name, p.phone, p.id_number FROM bookings b JOIN passengers p ON b.passenger_id = p.id WHERE b.schedule_id IN ({placeholders}) ORDER BY b.id", schedule_ids).fetchall()
    db.close()
    return [booking_from_row(r) for r in rows]

def get_booking_max_id():
    db = get_db()
    r = db.execute("SELECT COALESCE(MAX(id), 0) FROM bookings").fetchone()
    db.close()
    return r[0]

# ── Meta helpers ──

def get_next_ref():
    db = get_db()
    db.execute("BEGIN IMMEDIATE")
    r = db.execute("SELECT value FROM meta WHERE key = 'next_ref'").fetchone()
    if not r:
        n = 1
        db.execute("INSERT INTO meta (key, value) VALUES ('next_ref', '2')")
    else:
        n = int(r['value'])
        db.execute("UPDATE meta SET value = ? WHERE key = 'next_ref'", (str(n + 1),))
    db.commit()
    db.close()
    return n

def is_shared_pw_used(country_code):
    db = get_db()
    r = db.execute("SELECT value FROM meta WHERE key = ?", ('shared_pw_used_'+country_code,)).fetchone()
    db.close()
    return r is not None

def mark_shared_pw_used(country_code):
    db = get_db()
    db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, '1')", ('shared_pw_used_'+country_code,))
    db.commit()
    db.close()

# ── CRUD: Super Admins ──

def get_super_admin_by_email(email, country_code):
    db = get_db()
    r = db.execute("SELECT * FROM super_admins WHERE LOWER(email) = LOWER(?) AND country_code = ?", (email, country_code)).fetchone()
    db.close()
    return dict(r) if r else None

def get_super_admin_by_country(country_code):
    db = get_db()
    r = db.execute("SELECT * FROM super_admins WHERE country_code = ?", (country_code,)).fetchone()
    db.close()
    return dict(r) if r else None

def add_super_admin(email, password_hash, country_code):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    db = get_db()
    c = db.execute(
        "INSERT INTO super_admins (email, password_hash, country_code, created_at) VALUES (?, ?, ?, ?)",
        (email, password_hash, country_code, now)
    )
    aid = c.lastrowid
    db.commit()
    db.close()
    return aid

def update_super_admin(sid, **kwargs):
    db = get_db()
    fields = []
    vals = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        vals.append(v)
    vals.append(sid)
    db.execute(f"UPDATE super_admins SET {', '.join(fields)} WHERE id = ?", vals)
    db.commit()
    db.close()

def get_super_admin_by_reset_token(token):
    db = get_db()
    r = db.execute("SELECT * FROM super_admins WHERE reset_token = ?", (token,)).fetchone()
    db.close()
    return dict(r) if r else None

# ── Commission helpers ──

def add_commission(booking_id, agency_id, amount, currency_code):
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    db.execute(
        "INSERT INTO commissions (booking_id, agency_id, amount, currency_code, created_at) VALUES (?, ?, ?, ?, ?)",
        (booking_id, agency_id, amount, currency_code, now)
    )
    db.commit()
    db.close()

def get_total_commission(agency_ids=None):
    db = get_db()
    if agency_ids:
        placeholders = ','.join('?' * len(agency_ids))
        r = db.execute(f"SELECT COALESCE(SUM(amount), 0) FROM commissions WHERE agency_id IN ({placeholders})", agency_ids).fetchone()
    else:
        r = db.execute("SELECT COALESCE(SUM(amount), 0) FROM commissions").fetchone()
    db.close()
    return r[0]

def get_commission_summary_by_agency(agency_ids):
    if not agency_ids:
        return {}
    placeholders = ','.join('?' * len(agency_ids))
    db = get_db()
    rows = db.execute(f"SELECT agency_id, COALESCE(SUM(amount), 0) AS total FROM commissions WHERE agency_id IN ({placeholders}) GROUP BY agency_id", agency_ids).fetchall()
    db.close()
    return {r['agency_id']: r['total'] for r in rows}

def get_commissions_for_booking(booking_id):
    db = get_db()
    rows = db.execute("SELECT * FROM commissions WHERE booking_id = ?", (booking_id,)).fetchall()
    db.close()
    return rows_to_list(rows)

# ── Subscription helpers ──

def add_subscription(agency_id, plan, amount_paid, currency, start_date, end_date):
    db = get_db()
    db.execute(
        "INSERT INTO agency_subscriptions (agency_id, plan, amount_paid, currency, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?, 'active')",
        (agency_id, plan, amount_paid, currency, start_date, end_date)
    )
    db.commit()
    db.close()

def get_active_subscription(agency_id):
    db = get_db()
    r = db.execute(
        "SELECT * FROM agency_subscriptions WHERE agency_id = ? AND status = 'active' AND end_date >= date('now') ORDER BY end_date DESC LIMIT 1",
        (agency_id,)
    ).fetchone()
    db.close()
    return dict(r) if r else None

def has_active_subscription(agency_id):
    return get_active_subscription(agency_id) is not None

def extend_subscription(agency_id, plan, amount_paid, currency, extra_days):
    from datetime import date, timedelta
    existing = get_active_subscription(agency_id)
    if existing:
        new_end = (date.fromisoformat(existing['end_date']) + timedelta(days=extra_days)).isoformat()
        db = get_db()
        db.execute(
            "UPDATE agency_subscriptions SET end_date = ?, amount_paid = amount_paid + ?, plan = ? WHERE id = ?",
            (new_end, amount_paid, plan, existing['id'])
        )
        db.commit()
        db.close()
    else:
        start = date.today().isoformat()
        end = (date.today() + timedelta(days=extra_days)).isoformat()
        add_subscription(agency_id, plan, amount_paid, currency, start, end)

LANGUAGE_COLUMNS = {
    'fr': 'message_fr',
    'ar': 'message_ar', 'pt': 'message_pt', 'sw': 'message_sw',
    'am': 'message_am', 'so': 'message_so', 'ti': 'message_ti',
    'es': 'message_es', 'af': 'message_af', 'zu': 'message_zu',
}

def add_announcement(agency_id, message, badge='NEW', **kwargs):
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lang_cols = {}
    # Use provided translations or auto-translate
    from deep_translator import GoogleTranslator
    for lang_code, col_name in LANGUAGE_COLUMNS.items():
        existing = kwargs.get(col_name, '') or kwargs.get(lang_code, '')
        if existing:
            lang_cols[col_name] = existing
        else:
            try:
                lang_cols[col_name] = GoogleTranslator(source='en', target=lang_code).translate(message)
            except:
                lang_cols[col_name] = message
    col_names = ['agency_id', 'message', 'badge', 'created_at'] + list(lang_cols.keys())
    placeholders = ['?'] * len(col_names)
    values = [agency_id, message, badge, now] + list(lang_cols.values())
    db.execute(f"INSERT INTO announcements ({', '.join(col_names)}) VALUES ({', '.join(placeholders)})", values)
    db.commit()
    db.close()

def get_announcements(agency_id=None, active_only=True, country=None):
    db = get_db()
    q = "SELECT a.*, ag.name AS agency_name FROM announcements a JOIN agencies ag ON a.agency_id = ag.id"
    params = []
    clauses = []
    if agency_id is not None:
        clauses.append("a.agency_id = ?")
        params.append(agency_id)
    if active_only:
        clauses.append("a.is_active = 1")
    if country is not None:
        clauses.append("ag.country = ?")
        params.append(country)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY a.created_at DESC"
    rows = db.execute(q, params).fetchall()
    db.close()
    return rows_to_list(rows)

def deactivate_announcement(aid, agency_id):
    db = get_db()
    db.execute("UPDATE announcements SET is_active = 0 WHERE id = ? AND agency_id = ?", (aid, agency_id))
    db.commit()
    db.close()

def add_feedback(name, role, message):
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    db.execute("INSERT INTO feedback (name, role, message, created_at) VALUES (?, ?, ?, ?)",
               (name, role, message, now))
    db.commit()
    db.close()

def get_all_feedback():
    db = get_db()
    rows = db.execute("SELECT * FROM feedback ORDER BY created_at DESC").fetchall()
    db.close()
    return rows_to_list(rows)

def get_upcoming_bookings(minutes_from_now):
    """Return confirmed bookings where departure is exactly `minutes_from_now` minutes away."""
    from datetime import datetime, timedelta
    target = datetime.now() + timedelta(minutes=minutes_from_now)
    target_date = target.strftime('%Y-%m-%d')
    # Allow +/- 2 minute window for the time
    target_time = target.strftime('%H:%M')
    db = get_db()
    rows = db.execute("""
        SELECT b.id, b.booking_ref, b.schedule_id, b.seat_number,
               p.name AS pname, p.phone,
               s.date AS sdate, s.time AS stime,
               r.from_city, r.to_city, r.price,
               ag.name AS agency_name, ag.country AS agency_country
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.id
        JOIN schedules s ON b.schedule_id = s.id
        JOIN routes r ON s.route_id = r.id
        JOIN agencies ag ON r.agency_id = ag.id
        WHERE b.paid = 1 AND b.status = 'confirmed'
          AND s.date = ? AND s.status = 'active'
          AND substr(s.time, 1, 5) BETWEEN ? AND ?
    """, (target_date, target_time, target_time)).fetchall()
    db.close()
    return rows_to_list(rows)

def notification_sent(booking_id, notification_type):
    db = get_db()
    r = db.execute("SELECT id FROM notification_log WHERE booking_id = ? AND notification_type = ?",
                   (booking_id, notification_type)).fetchone()
    db.close()
    return r is not None

def log_notification(booking_id, notification_type):
    from datetime import datetime
    db = get_db()
    db.execute("INSERT INTO notification_log (booking_id, notification_type, sent_at) VALUES (?, ?, ?)",
               (booking_id, notification_type, datetime.now().strftime('%Y-%m-%d %H:%M')))
    db.commit()
    db.close()

# ── Admin functions ──

def get_all_agencies():
    db = get_db()
    rows = db.execute("SELECT * FROM agencies ORDER BY id DESC").fetchall()
    db.close()
    return rows_to_list(rows)

def get_all_subscriptions():
    db = get_db()
    rows = db.execute("""
        SELECT s.*, a.name as agency_name, a.country
        FROM agency_subscriptions s
        JOIN agencies a ON s.agency_id = a.id
        ORDER BY s.id DESC
    """).fetchall()
    db.close()
    return rows_to_list(rows)

def get_total_commission_global():
    db = get_db()
    r = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM commissions").fetchone()
    db.close()
    return r['total'] if r else 0

def get_subscription_prices():
    db = get_db()
    rows = db.execute("SELECT * FROM subscription_prices ORDER BY id").fetchall()
    db.close()
    return rows_to_list(rows)

def set_subscription_price(currency, monthly_price):
    db = get_db()
    existing = db.execute("SELECT id FROM subscription_prices WHERE currency = ?", (currency,)).fetchone()
    if existing:
        db.execute("UPDATE subscription_prices SET monthly_price = ? WHERE currency = ?", (monthly_price, currency))
    else:
        db.execute("INSERT INTO subscription_prices (currency, monthly_price) VALUES (?, ?)", (currency, monthly_price))
    db.commit()
    db.close()
