# AFRI Trans

Multi-country inter-city bus ticketing platform serving 11 African nations with bilingual support, dynamic seat maps, agency management, ministry oversight, and commission-based monetisation.

## Features

### Passenger
- **Trip search** — search by origin, destination, and date across all agencies
- **Visual seat picker** — interactive bus layout with VIP/standard classes, taken/available indicators, and real-time pricing
- **Multi-class seating** — Standard, VIP, and mixed-configuration buses (14–80 seats), 4 seat layout classes
- **Ticket lookup** — retrieve e-ticket by reference number
- **Feedback form** — submit feedback (auto-detects role: passenger/agency/ministry), emailed directly to admin
- **Multi-language** — 11 languages (en, fr, ar, pt, sw, am, so, ti, es, af, zu), 538+ translation keys
- **Multi-currency** — per-country currency display

### Agency
- **Dashboard** — revenue breakdown by route, recent bookings, today's trips overview, stats cards
- **Bus management** — add/edit buses, auto status (busy when scheduled, available when cancelled)
- **Route management** — origin → destination with pricing, duration, luggage options
- **Schedule management** — create trips with morning/afternoon/night periods
- **Booking management** — view bookings, reassign passengers, generate passenger manifests
- **Announcements** — auto-translated to French for Cameroonian passengers
- **Commission** — 1% platform fee deducted automatically (amount hidden, rate shown as badge)

### Ministry (Super Admin)
- **Dashboard** — national overview: agencies, bookings, revenue, active trips
- **Agency management** — approve/reject agency registrations with reason
- **Booking oversight** — view all bookings across all agencies
- **One-time shared password** — Admin123 invalidated after first login

### General
- **Notifications** — per-notification read tracking via session cookie (blue dot = unread, green check = read), red bell badge
- **Country switching** — 54 African country flag themes with dynamic CSS variables
- **PDF ticket generation** — downloadable e-tickets
- **Mobile-responsive** — hamburger nav, stacked grids, touch-friendly seat picker

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask |
| Database | SQLite (via raw SQL) |
| Templates | Jinja2 (custom CSS, no framework) |
| Icons | Font Awesome 6.5.1 |
| Fonts | Inter (Google Fonts) |
| PDF | xhtml2pdf |
| Images | Pillow |
| Email | smtplib (Gmail SMTP) |
| Translation | deep-translator (Google Translate) |
| Env vars | python-dotenv |

## Setup

```bash
# 1. Install dependencies
pip install flask pillow xhtml2pdf python-dotenv deep-translator

# 2. Configure email (required for feedback notifications)
# Create .env file:
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_FROM=your@gmail.com
FEEDBACK_EMAIL=your@gmail.com

# 3. Initialise the database
python -c "from database import init_db, migrate_from_json; init_db(); migrate_from_json('countries.json')"

# 4. Run
python app.py

# Default super admin shared password: Admin123 (one-time use)
```

## Project Structure

```
transport/
├── app.py                      # Flask application (routes, context processors)
├── database.py                 # SQLite schema, CRUD functions
├── generate_translations.py    # Auto-translate all language JSON files
├── translate_announcements.py  # Back-fill French translations for announcements
├── countries.json              # Country data (cities, flag colours, languages, currencies)
├── .env                        # Environment variables (SMTP, etc.)
├── static/
│   ├── style.css               # All styles (responsive, animations, components)
│   └── img/                    # Logos, SVGs
├── templates/
│   ├── base.html               # Layout (nav, footer, country modal, flash)
│   ├── index.html              # Homepage: hero, search, agencies, stats
│   ├── search.html             # Trip results grouped by period
│   ├── pick_seat.html          # Interactive seat selection
│   ├── book.html               # Passenger details form
│   ├── payment.html            # Payment method selection
│   ├── ticket.html             # E-ticket display
│   ├── ticket_pdf.html         # PDF ticket template
│   ├── lookup.html             # Ticket lookup by reference
│   ├── notifications.html      # Announcements list
│   ├── notification_detail.html# Single announcement
│   ├── feedback.html           # Feedback submission form
│   ├── feedback_all.html       # Ministry: view all feedback
│   ├── agencies.html           # Browse all agencies
│   ├── agency_browse.html      # Single agency detail
│   ├── agency_dashboard.html   # Agency control panel
│   ├── agency_login.html       # Agency sign in
│   ├── agency_register.html    # Agency registration
│   ├── agency_buses.html       # Bus list
│   ├── agency_bus_form.html    # Add/edit bus
│   ├── agency_routes.html      # Route list
│   ├── agency_route_form.html  # Add/edit route
│   ├── agency_schedules.html   # Schedule list
│   ├── agency_schedule_form.html# Add/edit schedule
│   ├── agency_bookings.html    # Booking list
│   ├── agency_booking_reassign.html # Reassign booking
│   ├── agency_manifest.html    # Passenger manifest
│   ├── agency_announcements.html# Announcement management
│   ├── agency_forgot_password.html
│   ├── agency_reset_password.html
│   ├── agency_verify_code.html
│   ├── ministry_dashboard.html # Ministry overview
│   ├── ministry_login.html     # Ministry sign in (2-step)
│   ├── ministry_relogin.html   # Password change after first login
│   ├── ministry_agencies.html  # Manage all agencies
│   ├── ministry_bookings.html  # View all bookings
│   ├── ministry_forgot_password.html
│   ├── ministry_reset_password.html
│   └── ministry_verify_code.html
└── translations/
    ├── en.json                 # English (source, 538+ keys)
    ├── fr.json                 # French
    ├── ar.json                 # Arabic
    ├── pt.json                 # Portuguese
    ├── sw.json                 # Swahili
    ├── am.json                 # Amharic
    ├── so.json                 # Somali
    ├── ti.json                 # Tigrinya
    ├── es.json                 # Spanish
    ├── af.json                 # Afrikaans
    └── zu.json                 # Zulu
```

## Key Architecture Decisions

| Decision | Rationale |
|---|---|
| **SQLite** | Single-file, zero-config, sufficient for agency-scale traffic |
| **Session-based notification tracking** | Works without user login; read IDs stored in `session['read_notification_ids']` |
| **`message_fr` column** | French translation stored at creation time (not on-the-fly) to avoid repeated API calls |
| **1% commission hidden** | Amount deducted at source; only rate shown as badge — prevents agency/ministry friction |
| **Bus auto-status** | Schedule assignment sets bus to "busy"; cancellation reverts to "available" |
| **One-time shared password** | `Admin123` invalidated after first super admin login via `meta` table flag |
| **Inline CSS** | Deliberate choice — no build step, single developer, rapid iteration |
| **`load_dotenv()` with `.env`** | Keeps SMTP credentials out of source control |

## Notes

- UK English spelling throughout (colour, organisation, normalised, centre, etc.)
- All `/agency/*` routes require `get_agency_session()` — passengers cannot access agency features
- Translation auto-generation (`generate_translations.py`) may time out for large batches; manual French edits or English fallback serve as backup
- Bus capacity range: 14–80 seats
- One email = one agency globally (unique constraint on `agencies.email`)
- Cameroon is bilingual (English/French) — announcements auto-translate to French
- `_()` function falls back to English text if key is missing in the target language
- `for _ in range(...)` shadows `_()` — use a different loop variable in templates
