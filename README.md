# AFRI Trans

Multi-country inter-city bus ticketing platform serving 11 languages across 54 African nations with dynamic seat maps, agency management, ministry oversight, super admin control panel, and commission-based monetisation.

---

## 1. Overview

AFRI Trans is a full-stack web application that digitises inter-city bus ticketing across Africa. It connects **passengers** (who search, book, and pay for trips), **transport agencies** (who manage buses, routes, schedules, and bookings), a **Ministry of Transport** (per-country super admin who approves agencies and oversees operations), and a **Super Admin** (global owner who manages subscriptions and revenue).

### Core Problem Solved
- Manual bus ticketing is paper-based, error-prone, and lacks oversight
- No centralised system for tracking agency revenue, bookings, and compliance
- Passengers have no way to compare trips, pick seats, or get e-tickets
- Ministries have no visibility into transport sector performance

### Solution
A self-contained Flask web app with:
- **Passenger app**: search, seat selection, mobile money payment, e-ticket (image + PDF)
- **Agency dashboard**: bus/route/schedule CRUD, booking management, trip reports, revenue analytics
- **Ministry portal**: per-country oversight, agency approval/rejection, national statistics
- **Super Admin panel**: global subscription management, commission tracking, pricing control

---

## 2. Features

### Passenger
- **Trip search** — search by origin, destination, and date across all approved agencies in the selected country
- **Interactive seat picker** — visual bus layout with VIP/standard classes, taken/available indicators, and real-time pricing (4 layout classes: 14-20, 22-35, 36-52, 53-80 seats)
- **Multi-class seating** — Standard and VIP buses (14–80 seats), per-bus VIP surcharge configurable by agency
- **Mobile money payment** — country-specific providers (MTN MoMo, Orange Money, M-Pesa, etc.)
- **E-ticket generation** — downloadable image ticket (Pillow) and PDF ticket (xhtml2pdf) with booking reference, route, seat, amount breakdown
- **Ticket lookup** — retrieve e-ticket by reference number (format: `CM-ABC-0001`)
- **Luggage booking** — optional per-kg luggage fee on routes that support it
- **Feedback form** — auto-detects role (passenger/agency/ministry), emailed to admin
- **Multi-language** — 11 languages (en, fr, ar, pt, sw, am, so, ti, es, af, zu), 538+ translation keys with `_()` function and English fallback
- **Multi-currency** — per-country currency display with `|currency` Jinja filter

### Agency
- **Dashboard** — 4 summary cards (Total Revenue, Expenditures, Profit, Platform Commission), revenue breakdown by route, recent bookings, today's trips, trip reports with filters + export to Excel/PDF
- **Bus management** — add/edit buses (plate, capacity 14-80, type: standard/VIP, per-bus VIP price), auto status revert (busy ↔ available)
- **Route management** — origin → destination with pricing, duration, luggage options (enabled/disabled, price per kg)
- **Schedule management** — create trips with morning/afternoon/night periods, auto-detection from time
- **Booking management** — view all bookings, cancel bookings, reassign passengers to different trips, generate passenger manifests
- **Announcements** — post announcements auto-translated to all 11 languages via Google Translate API
- **Trip reports** — log expenses per trip, calculate profit (revenue − expenses), filter by route/date/bus, export to Excel (CSV) and PDF (print), Load More/Show Less pagination
- **Subscription** — monthly/semiannual/annual plans; subscribers skip 1% platform commission

### Ministry of Transport (Per-Country Super Admin)
- **Two-factor login** — shared country password (`Admin123`, invalidated after first use) → personal email + password registration/login
- **Dashboard** — national overview with agency summary table (Agency, Buses, Routes, Revenue), totals for agencies, bookings, revenue, buses, routes, active trips, commission
- **Agency management** — approve/reject agency registrations with mandatory reason
- **Booking oversight** — view all bookings across all agencies in the country
- **Password recovery** — forgot password with 8-digit email verification code

### Super Admin (Global)
- **Single-password login** — password: `adolfai12`
- **Dashboard** — total agencies, subscribed agencies count, global commission, all subscriptions
- **Subscription management** — set subscription prices per currency (XAF, XOF, NGN), manually add subscription months to any agency
- **Agency overview** — list all agencies globally

### General
- **Notifications** — per-notification read tracking via localStorage (`afri_read_anns`), unread = faint green background, bell badge computed client-side
- **Country switching** — 54 African country flag themes with dynamic CSS variables, auto-detect country by IP on first visit
- **Password visibility toggle** — show/hide checkbox on all login/register forms
- **Mobile-responsive** — hamburger nav, stacked grids, touch-friendly seat picker
- **Rate limiting** — in-memory per-IP login attempt tracking (max 10 attempts per 15 minutes)

---

## 3. Booking Flow (End-to-End)

```
1. Passenger visits homepage (/)
   → Country auto-detected by IP geolocation (ip-api.com)
   → Session set with country code, cities, currency

2. Search trips (POST /api/booking/search)
   → Origin, destination, date
   → Returns matching active schedules grouped by period (morning/afternoon/night)
   → Shows bus type, agency name, available seats, price

3. Pick seat (GET /api/booking/seats/<sid>)
   → Interactive seat map rendered from bus_layout()
   → 4 layout classes based on capacity
   → Real-time taken/available status
   → Price updates based on VIP/standard

4. Passenger details (GET /api/booking/form/<sid>)
   → Name, phone, ID number
   → Optional luggage weight (if route supports it)
   → Price breakdown shown

5. Create booking (POST /api/booking/confirm)
   → Atomic seat reservation (DB-level unique index prevents double-booking)
   → Booking reference generated: {COUNTRY}-{3 letters}-{4 digits}
   → 15-minute minimum before departure enforced
   → Seat locked for this passenger

6. Payment (POST /api/booking/pay)
   → Select mobile money provider (country-specific)
   → Enter phone number
   → Atomic confirmation (re-checks seat availability)
   → Transaction ID generated

7. Commission recorded (if no active subscription)
   → 1% of total price (ticket + VIP surcharge + luggage)
   → Stored in commissions table

8. E-ticket displayed (/ticket/<ref>)
   → Ticket image (Pillow-generated PNG)
   → PDF download (xhtml2pdf)
   → Reference for lookup
```

---

## 4. Database Schema

**Database**: SQLite (single file: `data.db`), raw SQL, WAL mode, foreign keys enabled.

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `agencies` | Transport companies | id, name, email (globally unique), password (bcrypt), country, locations (JSON), approved, whatsapp |
| `buses` | Fleet vehicles | id, agency_id (FK), plate, capacity (14-80), bus_type (standard/vip), status (available/busy), vip_price (nullable, per-bus surcharge) |
| `routes` | City-to-city paths | id, agency_id (FK), from_city, to_city, duration, price, luggage_enabled, luggage_price_per_kg |
| `schedules` | Scheduled trips | id, route_id (FK), bus_id (FK), date, time, period (morning/afternoon/night), status (active/cancelled/completed) |
| `passengers` | Unique travellers | id, name, phone, id_number, UNIQUE(phone, id_number) |
| `bookings` | Ticket reservations | id, schedule_id (FK), passenger_id (FK), seat_number, booking_ref (unique), paid, status (pending/confirmed/cancelled/expired), payment_method, luggage_weight, luggage_fee |
| `super_admins` | Ministry admin accounts | id, email, password_hash (bcrypt), country_code, reset_token |
| `commissions` | Platform fees | id, booking_id (FK), agency_id (FK), amount, currency_code, created_at |
| `agency_subscriptions` | Subscription records | id, agency_id (FK), plan, amount_paid, currency, start_date, end_date, status |
| `announcements` | Agency notifications | id, agency_id (FK), message, message_fr, message_ar...message_zu, badge, is_active |
| `feedback` | User feedback | id, name, role, message, created_at |
| `subscription_prices` | Admin-set pricing | currency (unique), monthly_price |
| `trip_reports` | Expense tracking | id, schedule_id (FK), agency_id (FK), expenses, created_at |
| `notification_log` | SMS/WhatsApp log | id, booking_id (FK), notification_type, sent_at |
| `meta` | Key-value store | key (PK), value (used for: next_ref counter, migration flag, shared_pw_used flags) |

### Indexes
- `idx_buses_agency`, `idx_routes_agency` — fast agency lookups
- `idx_schedules_route`, `idx_schedules_bus` — fast schedule queries
- `idx_bookings_schedule`, `idx_bookings_passenger` — fast booking queries
- `idx_bookings_seat` — UNIQUE partial index preventing double-booking
- `idx_trip_reports_schedule`, `idx_trip_reports_agency` — fast trip report queries
- `idx_agencies_email` — UNIQUE partial index (global email uniqueness)
- `idx_agencies_name_country` — UNIQUE index (prevent duplicate agency names per country)

---

## 5. Architecture

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | Python 3.10+ / Flask | Lightweight, fast development, suitable for single-developer project |
| Database | SQLite (raw SQL) | Zero-config, single-file, sufficient for agency-scale traffic |
| Templates | Jinja2 (custom CSS) | No framework overhead, full control over layout |
| Ticket Image | Pillow (PIL) | Programmatic image generation with fonts, colours, layout |
| PDF | xhtml2pdf | HTML-to-PDF conversion for downloadable tickets |
| Translation | deep-translator (Google Translate) | Auto-translate announcements to 11 languages |
| Email | smtplib (Gmail SMTP) | Feedback notifications, password reset codes |
| Notifications | WhatsApp Cloud API + Twilio SMS + USB GSM Modem | Multi-channel: WhatsApp (free) → GSM Modem (free) → SMS (paid) |
| Env vars | python-dotenv | Keeps SMTP/API credentials out of source control |
| Security | werkzeug.security | Password hashing (scrypt/pbkdf2) |

### Project Structure

```
transport/
├── app.py                        # Flask application (2200+ lines: routes, logic, context processors)
├── database.py                   # SQLite schema, CRUD functions, migrations
├── data.db                       # Live SQLite database
├── .env                          # Environment variables (SMTP, WhatsApp, Twilio, GSM)
├── static/
│   ├── style.css                 # All styles (responsive, animations, components)
│   └── img/                      # Logos, SVGs
├── templates/
│   ├── base.html                 # Layout (nav, footer, country modal, flash, password toggle)
│   ├── index.html                # Homepage: hero, search, agencies, announcements
│   ├── notifications.html        # Announcements list (localStorage read/unread)
│   ├── notification_detail.html  # Single announcement (marks read in localStorage)
│   ├── agencies.html             # Browse all agencies in country
│   ├── agency_browse.html        # Single agency detail (routes, schedules, announcements)
│   ├── lookup.html               # Ticket lookup by reference
│   ├── feedback.html             # Feedback submission
│   ├── feedback_all.html         # Ministry: view all feedback
│   ├── agency_*.html             # Agency: register, login, dashboard, buses, routes, schedules, bookings, announcements, subscriptions, manifest, reassign
│   ├── ministry_*.html           # Ministry: login, relogin (2FA), dashboard, agencies, bookings, forgot/reset password
│   ├── admin_*.html              # Super Admin: login, dashboard
│   └── partials/                 # AJAX-loaded components (search_results, seat_layout, passenger_form, flags_macro)
├── translations/                 # 11 language JSON files (538+ keys each)
│   ├── en.json                   # English (source)
│   ├── fr.json                   # French
│   ├── ar.json                   # Arabic
│   ├── pt.json                   # Portuguese
│   ├── sw.json                   # Swahili
│   ├── am.json                   # Amharic
│   ├── so.json                   # Somali
│   ├── ti.json                   # Tigrinya
│   ├── es.json                   # Spanish
│   ├── af.json                   # Afrikaans
│   └── zu.json                   # Zulu
└── REVIVAL_INNOVATION_HUB_FINAL.docx
```

---

## 6. Key Architecture Decisions

| Decision | Rationale |
|---|---|
| **SQLite** | Single-file, zero-config, sufficient for agency-scale traffic. WAL mode for concurrent reads. |
| **AJAX booking flow** | Search → seat pick → form → confirm all via fetch() API returning HTML fragments. No page reloads. |
| **Atomic seat booking** | `add_booking_atomic()` uses `BEGIN IMMEDIATE` + unique partial index to prevent race conditions / double-booking. |
| **localStorage for notifications** | Read/unread state persists across sessions without requiring user login. Session-based approach was abandoned. |
| **Per-bus VIP pricing** | Each bus can have its own VIP surcharge (`vip_price` column). Falls back to country default if NULL. |
| **1% commission per booking** | Deducted at payment time per individual booking. Amount hidden from agencies; only rate shown as badge. |
| **Subscription skips commission** | Agencies with active subscription pay no per-booking commission. incentivises subscription adoption. |
| **Auto bus status revert** | `auto_revert_bus_status()` runs on dashboard/buses page load. Fixes stuck "busy" buses with no active future schedules. |
| **Unpaid booking expiry** | `expire_unpaid_bookings(30)` frees seats for unpaid pending bookings older than 30 minutes. Runs on dashboard load. |
| **Auto trip expiry** | `auto_expire_trips()` runs on every request. Marks past schedules as completed, frees buses after 48h, expires old bookings after 24h. |
| **Two-factor ministry login** | Shared country password (one-time) → personal email + password. Prevents unauthorised access after first admin sets up. |
| **Country-scoped sessions** | Switching country clears all auth sessions. Agency/ministry sessions are country-bound. |
| **`message_fr` + 9 language columns** | Translations stored at announcement creation time (not on-the-fly) to avoid repeated API calls and ensure offline availability. |
| **Rate limiting** | In-memory per-IP tracking. Max 10 login attempts per 15-minute window. Prevents brute-force attacks. |
| **IP geolocation auto-detect** | First visit auto-selects country via ip-api.com. User can manually switch via flag modal. |
| **Password hashing** | werkzeug.security (scrypt/pbkdf2). Legacy plain-text passwords auto-hashed on next login. |
| **`load_dotenv()` with `.env`** | Keeps SMTP credentials, WhatsApp tokens, Twilio keys, GSM port out of source control. |
| **Inline CSS** | Deliberate choice — no build step, single developer, rapid iteration. |

---

## 7. Security Features

| Feature | Implementation |
|---------|---------------|
| **Password hashing** | werkzeug.security (scrypt with salt) |
| **Rate limiting** | In-memory per-IP, 10 attempts per 15 minutes on all login routes |
| **Session persistence** | 15-day lifetime for agency, ministry, and admin sessions |
| **Atomic seat booking** | DB-level unique index prevents double-booking race conditions |
| **Payment re-verification** | `confirm_booking_atomic()` re-checks seat availability before confirming |
| **Country-scoped auth** | Switching country clears all auth sessions |
| **One-time shared password** | Ministry `Admin123` invalidated after first super admin login via `meta` table flag |
| **Email uniqueness** | Global unique constraint on agency email; global unique on super admin email |
| **Role-based access** | `get_agency_session()` guards all `/agency/*` routes; `session['ministry']` guards `/ministry/*` routes; `session['admin_logged_in']` guards `/admin/*` routes |
| **Auto trip expiry** | Past bookings automatically expired after 24h |
| **Unpaid booking release** | Seats freed after 30 minutes of non-payment |
| **GSM modem AT commands** | Input sanitised for SMS sending |

---

## 8. Monetisation Model

### Per-Booking Commission (1%)
- Calculated on: `ticket_price + VIP_surcharge + luggage_fee` per individual booking
- Recorded in `commissions` table via `add_commission()` at payment time
- **Skipped** if agency has an active subscription
- Amount **hidden** from agencies/ministry — only the 1% rate is shown as a badge

### Agency Subscriptions
- Plans: Monthly, Semi-annual, Annual (prices per currency)
- **XAF/XOF**: 58,000 / 250,000 / 500,000
- **NGN**: 15,000 / 75,000 / 150,000
- Custom month packages supported
- Admin can manually add subscription months to any agency
- Admin can set custom subscription prices per currency
- Subscribers pay no per-booking commission

### Revenue Calculation (Agency Dashboard)
```
Total Revenue    = sum of (ticket_price + VIP_surcharge + luggage_fee) for all paid bookings
Commission       = sum of 1% commissions (0 if subscribed)
Net Revenue      = Total Revenue − Commission
Expenses         = sum of trip report expenses (logged manually by agency)
Profit           = Net Revenue − Expenses
```

---

## 9. Multi-Country System

### 54 Countries Configured
Each country has:
- **Name**, **flag colours** (3 hex values for dynamic CSS theming)
- **Currency** symbol and code
- **Cities** (10-18 per country for route origins/destinations)
- **Languages** (1-3 per country for translation selection)
- **Payment providers** (2-3 per country, e.g., MTN MoMo, Orange Money, M-Pesa)
- **Phone code** (for WhatsApp/SMS formatting)
- **VIP surcharge** (default per-bus price, overridable by agency)

### Country Features
- **Auto-detection**: IP geolocation on first visit via ip-api.com
- **Manual switching**: Flag modal in navbar, clears all auth sessions
- **Dynamic theming**: CSS variables `--flag-1`, `--flag-2`, `--flag-3` set from country flag colours
- **Currency filter**: `{{ price|currency }}` Jinja filter displays amount with country symbol

---

## 10. Notification System

### Channels (Priority Order)
1. **WhatsApp Cloud API** (Meta) — free 1000 conversations/month
2. **USB GSM Modem** — free if SIM has SMS bundle (AT commands via pyserial)
3. **Twilio SMS** — paid fallback
4. **Console log** — always logs if no channel available

### Departure Reminders
- Background thread runs every 60 seconds
- Checks for bookings departing in 90 and 45 minutes
- Sends WhatsApp/SMS reminder with trip details
- Logged in `notification_log` to prevent duplicates

### In-App Notifications (Announcements)
- Agency posts announcement → auto-translated to 11 languages via Google Translate
- Stored in `announcements` table with per-language columns
- Displayed on homepage and `/notifications` page
- Read/unread tracked via `localStorage` key `afri_read_anns`
- Unread notifications: faint green background (`#f0fdf4`)
- Bell badge computed client-side from localStorage

---

## 11. Bus Layout System

4 layout classes based on capacity:

| Class | Capacity | Layout | Seats/Row |
|-------|----------|--------|-----------|
| Minibus | 14-20 | 1+2 Asymmetric | 3 |
| Midi-Bus | 22-35 | 2+2 Narrow Centre | 4 |
| Standard Coach | 36-52 | 2+2 Symmetric | 4 |
| High-Capacity | 53-80 | 3+2 Standard Centre | 5 |

- Rear exit door indicated in layout
- Seats rendered as interactive grid with CSS
- Taken seats greyed out, available seats selectable
- Price updates dynamically based on seat selection and bus type

---

## 12. Setup & Installation

```bash
# 1. Install dependencies
pip install flask pillow xhtml2pdf python-dotenv deep-translator werkzeug

# 2. Configure environment (create .env file)
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_FROM=your@gmail.com
FEEDBACK_EMAIL=your@gmail.com
# Optional: WhatsApp, Twilio, GSM modem
WHATSAPP_TOKEN=your-token
WHATSAPP_PHONE_ID=your-phone-id
TWILIO_SID=your-sid
TWILIO_TOKEN=your-token
TWILIO_FROM=+1234567890
GSM_MODEM_PORT=COM3

# 3. Run (database auto-initialises on first run)
python app.py
```

### Default Credentials
| Role | URL | Credentials |
|------|-----|-------------|
| Ministry | `/ministry/login` | Password: `Admin123` (one-time, then create super admin account) |
| Super Admin | `/admin/login` | Password: `adolfai12` |
| Agency | `/agency/register` | Register new account, pending ministry approval |

---

## 13. API Endpoints

### Public (Passenger)
| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/` | Homepage with search, agencies, announcements |
| POST | `/api/booking/search` | Search trips by origin/destination/date |
| GET | `/api/booking/seats/<sid>` | Get seat layout for a schedule |
| GET | `/api/booking/form/<sid>` | Get passenger form for a schedule |
| POST | `/api/booking/confirm` | Create booking (atomic seat reservation) |
| GET | `/api/booking/payment-form/<bid>` | Get payment form for a booking |
| POST | `/api/booking/pay` | Process payment (atomic confirmation) |
| GET | `/api/seats/<sid>/status` | Real-time seat status (for polling) |
| GET | `/ticket/<ref>` | E-ticket display |
| GET | `/ticket/<ref>/pdf` | PDF download |
| GET | `/ticket/<ref>/image` | Ticket image (PNG) |
| GET | `/lookup` | Ticket lookup by reference |
| GET | `/notifications` | Announcements list |
| GET | `/notification/<nid>` | Single announcement detail |
| GET | `/agencies` | Browse agencies |
| GET | `/agency/<aid>/browse` | Single agency detail |
| POST | `/feedback` | Submit feedback |

### Agency (requires session)
| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/agency/register` | Register new agency |
| GET/POST | `/agency/login` | Agency login |
| GET | `/agency/dashboard` | Dashboard with stats, trip reports |
| GET/POST | `/agency/buses`, `/agency/buses/add` | Bus management |
| GET/POST | `/agency/routes`, `/agency/routes/add` | Route management |
| GET/POST | `/agency/schedules`, `/agency/schedules/add` | Schedule management |
| GET | `/agency/bookings` | Booking list |
| GET | `/agency/booking/<bid>/reassign` | Reassign passenger to new trip |
| GET | `/agency/schedule/<sid>/manifest` | Passenger manifest |
| POST | `/api/agency/trip-report` | Save trip expenses |
| GET/POST | `/agency/announcements` | Post/manage announcements |
| GET | `/agency/subscribe` | View subscription plans |
| GET/POST | `/agency/subscription` | Subscription status |

### Ministry (requires 2FA session)
| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/ministry/login` | First-factor login (shared password) |
| GET/POST | `/ministry/relogin` | Second-factor login (email + password) |
| GET | `/ministry/dashboard` | National overview with agency summary table |
| GET | `/ministry/agencies` | Manage agencies |
| POST | `/ministry/agency/<aid>/approve` | Approve agency |
| POST | `/ministry/agency/<aid>/reject` | Reject agency |
| GET | `/ministry/bookings` | View all bookings |

### Super Admin (requires password)
| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/admin/login` | Admin login |
| GET | `/admin/dashboard` | Global stats, subscription management |
| POST | `/admin/prices` | Update subscription prices |
| POST | `/admin/subscribe/<aid>` | Manually add subscription to agency |

---

## 14. Key Functions Reference

### Database Layer (`database.py`)
- `init_db()` — Create all tables and indexes, run migrations
- `add_booking_atomic()` — Atomically reserve a seat with race-condition protection
- `confirm_booking_atomic()` — Atomically confirm payment with seat re-verification
- `expire_unpaid_bookings(30)` — Free seats for unpaid bookings older than 30 minutes
- `cleanup_old_trip_reports(365)` — Delete trip reports older than 1 year

### Application Layer (`app.py`)
- `auto_expire_trips()` — Runs on every request: mark past schedules completed, free buses, expire old bookings
- `auto_revert_bus_status(agency_id)` — Fix stuck "busy" buses on dashboard/buses page load
- `bus_layout(bus_type, capacity)` — Generate seat grid for 4 layout classes
- `ticket_image(bk, s, route, bus, agency, ...)` — Generate e-ticket as Pillow PNG
- `send_notification(phone, message, country)` — Multi-channel notification (WhatsApp → GSM → SMS → console)
- `send_departure_reminders()` — Background thread: 90min and 45min reminders
- `gen_ref()` — Generate booking reference: `{PREFIX}-{3 letters}-{4 digits}`
- `_(text)` — Translation function, returns translated text or English fallback

---

## 15. Notes

- UK English spelling throughout (colour, organisation, normalised, centre, etc.)
- All `/agency/*` routes require `get_agency_session()` — passengers cannot access agency features
- Translation auto-generation may time out for large batches; manual edits or English fallback serve as backup
- Bus capacity range: 14–80 seats
- One email = one agency globally (unique constraint on `agencies.email`)
- Cameroon is bilingual (English/French) — announcements auto-translate to French
- `_()` function falls back to English text if key is missing in the target language
- `for _ in range(...)` shadows `_()` — use a different loop variable in templates
- `countries.json` removed — all country data now embedded in `app.py` COUNTRIES dict
- Trip reports auto-deleted after 365 days via `cleanup_old_trip_reports()`
