# INTERNSHIP REPORT

## AFRI Trans — Multi-Country Bus Ticketing Platform

---

**Presented by:** TEH ADOLF BUOH (ADOLF.AI)

**Internship Period:** 16/06/2026 – [End Date]

**Supervisor:** [Supervisor Name]

**Organisation:** Ferdsilink Buea, Cameroon

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Tools and Technologies Used](#4-tools-and-technologies-used)
5. [System Architecture](#5-system-architecture)
6. [Database Design](#6-database-design)
7. [Features Implemented](#7-features-implemented)
8. [Implementation Details](#8-implementation-details)
9. [Challenges and Solutions](#9-challenges-and-solutions)
10. [Testing and Results](#10-testing-and-results)
11. [Conclusion and Future Work](#11-conclusion-and-future-work)
12. [References](#12-references)

---

## 1. Introduction

AFRI Trans is a web-based bus ticketing platform designed to serve all 54 African countries. The platform connects passengers with bus agencies through a unified booking system, while also providing administrative portals for agencies and government transport ministries. The system supports multiple languages, local currencies, country-specific payment providers, and per-country ministry oversight workflows.

This report documents the development of the AFRI Trans platform during my internship at **Ferdsilink Buea, Cameroon**. The project was built using Python Flask for the backend, SQLite for data persistence, and vanilla HTML/CSS/JavaScript for the frontend.

### 1.1 Background

Inter-city bus travel is the primary mode of transportation for millions of Africans. However, most bus booking systems are paper-based, fragmented by country, or operated by individual agencies with no centralised platform. This creates several problems:

- Passengers must visit physical terminals to book tickets
- No way to compare prices across multiple agencies
- Limited payment options, often cash-only
- No standardised ticketing or booking records

AFRI Trans aims to solve these problems by providing a single, multi-country platform where passengers can search, compare, book, and pay for bus tickets across any African country.

---

## 2. Problem Statement

The African bus transportation industry faces several challenges:

1. **Lack of Centralization:** No single platform exists for booking bus tickets across multiple African countries. Passengers must interact with each agency separately.

2. **Language Barriers:** Africa has over 2,000 languages. A platform serving the continent must support multiple languages to be accessible.

3. **Currency and Payment Fragmentation:** Each country uses a different currency and has different mobile money providers. A unified system must handle this complexity.

4. **Regulatory Requirements:** Each country has its own Ministry of Transport that must approve and oversee agencies operating within its jurisdiction.

5. **Data Redundancy:** Initial implementation used flat JSON file storage, leading to duplicate data, ID collisions, and referential integrity issues.

6. **Agency Privacy:** Competing agencies should not have access to each other's operational data (pricing, routes, passenger manifests).

7. **Security:** A single shared password for all ministry users across all countries is insecure. Each country needs an individual super admin with email-based authentication and password recovery.

---

## 3. Objectives

### 3.1 Primary Objectives

- Develop a multi-country bus ticketing platform covering all 54 African nations
- Implement a language system supporting 11 African and international languages
- Create per-country payment provider integration
- Build a Ministry of Transport approval workflow for agency registration
- Design a fully responsive interface accessible on all device sizes

### 3.2 Secondary Objectives

- Normalise data storage and eliminate redundancy through SQLite migration
- Enforce privacy between competing agencies
- Generate e-tickets in both PNG image and PDF formats
- Support agency management of buses, routes, schedules, and bookings

---

## 4. Tools and Technologies Used

### 4.1 Backend

| Technology | Purpose |
|---|---|
| **Python 3** | Primary programming language |
| **Flask 2.x** | Web framework (routing, sessions, templating) |
| **SQLite 3** | Database engine (lightweight, no server required) |
| **Werkzeug** | Password hashing and security utilities |
| **Pillow (PIL)** | E-ticket image generation |
| **xhtml2pdf** | PDF ticket generation |
| **JSON** | Translation file format |

### 4.2 Frontend

| Technology | Purpose |
|---|---|
| **HTML5** | Page structure |
| **CSS3** | Styling and responsive design |
| **JavaScript (Vanilla)** | Client-side interactivity (modals, navigation) |
| **Jinja2** | Server-side templating (Flask integrated) |
| **Font Awesome** | Icon library |

### 4.3 Development Tools

| Tool | Purpose |
|---|---|
| **VS Code** | Code editor |
| **Git** | Version control |
| **PowerShell** | Command-line interface |

---

## 5. System Architecture

### 5.1 High-Level Architecture

AFRI Trans follows a monolithic Flask application pattern with three distinct user portals:

```
┌─────────────────────────────────────────────────────────────┐
│                        AFRI Trans                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │   Passenger App  │  │ Agency Portal│  │Ministry Portal│  │
│   │                  │  │              │  │              │  │
│   │ • Search trips   │  │ • Dashboard  │  │ • Dashboard  │  │
│   │ • Book tickets   │  │ • Buses      │  │ • Agencies   │  │
│   │ • Make payments  │  │ • Routes     │  │ • Approvals  │  │
│   │ • View tickets   │  │ • Schedules  │  │ • Bookings   │  │
│   │ • Browse agencies│  │ • Bookings   │  │ • Stats      │  │
│   └─────────────────┘  └──────────────┘  └──────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    Shared Services Layer                     │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌───────────────┐    │
│  │Translation│ │Country   │ │Payment  │ │Session/Auth   │    │
│  │Engine     │ │Manager   │ │Gateway  │ │Manager        │    │
│  └─────────┘ └──────────┘ └────────┘ └───────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                              │
│                    ┌──────────────┐                          │
│                    │   SQLite DB  │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Request Flow

A typical booking request flows through the system as follows:

```
Passenger → Search (country-cities) → Pick Schedule → Select Seat
    → Enter Details → Choose Payment → Confirm → Generate Ticket
```

### 5.3 User Roles

1. **Passenger:** Browses trips, books tickets, makes payments, views/downloads tickets
2. **Agency:** Registers on the platform, manages buses/routes/schedules, views bookings and manifests, reassigns bookings
3. **Ministry of Transport:** Logs in per country, reviews agency registrations, approves or rejects with reasons, views booking statistics

---

## 6. Database Design

### 6.1 Schema Overview

The database was initially implemented using flat JSON storage (`data.json`). During the internship, this was migrated to a normalised SQLite database (`data.db`) with the following schema:

```sql
-- Agencies (bus companies)
CREATE TABLE agencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    password    TEXT NOT NULL,          -- hashed with scrypt
    country     TEXT NOT NULL DEFAULT 'cm',
    locations   TEXT NOT NULL DEFAULT '[]',  -- JSON array
    approved    INTEGER NOT NULL DEFAULT 0,  -- 0=pending, 1=approved
    rejection_reason TEXT,
    approval_reason  TEXT,
    created_at  TEXT NOT NULL
);

-- Buses (vehicles owned by agencies)
CREATE TABLE buses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agency_id   INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    plate       TEXT NOT NULL,
    capacity    INTEGER NOT NULL DEFAULT 71,
    bus_type    TEXT NOT NULL DEFAULT 'standard', -- 'standard' or 'vip'
    status      TEXT NOT NULL DEFAULT 'available' -- 'available' or 'busy'
);

-- Routes (city pairs with pricing)
CREATE TABLE routes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    agency_id       INTEGER NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    from_city       TEXT NOT NULL,
    to_city         TEXT NOT NULL,
    duration        TEXT NOT NULL,
    price           INTEGER NOT NULL,
    luggage_enabled INTEGER NOT NULL DEFAULT 0,
    luggage_price_per_kg INTEGER NOT NULL DEFAULT 0
);

-- Schedules (specific trips on a route)
CREATE TABLE schedules (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id  INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    bus_id    INTEGER NOT NULL REFERENCES buses(id) ON DELETE CASCADE,
    date      TEXT NOT NULL,
    time      TEXT NOT NULL,
    period    TEXT NOT NULL,  -- 'morning', 'afternoon', 'night'
    status    TEXT NOT NULL DEFAULT 'active'
);

-- Passengers (normalised to avoid duplication)
CREATE TABLE passengers (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    phone     TEXT NOT NULL,
    id_number TEXT DEFAULT '',
    UNIQUE(phone, id_number)
);

-- Bookings (ticket purchases)
CREATE TABLE bookings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id     INTEGER NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    passenger_id    INTEGER NOT NULL REFERENCES passengers(id),
    seat_number     INTEGER,
    booking_ref     TEXT NOT NULL UNIQUE,
    paid            INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'pending',
    payment_method  TEXT,
    transaction_id  TEXT,
    created_at      TEXT NOT NULL,
    luggage_weight  REAL NOT NULL DEFAULT 0,
    luggage_fee     INTEGER NOT NULL DEFAULT 0
);

-- Meta (counters and migration tracking)
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### 6.2 Entity Relationship Diagram

```
Agencies 1───* Buses
Agencies 1───* Routes
Routes   1───* Schedules
Buses    1───* Schedules
Schedules 1───* Bookings
Passengers 1───* Bookings
```

### 6.3 Migration from JSON to SQLite

The original implementation stored all data in a single JSON file (`data.json`). This caused several problems:

| Issue | JSON Storage | SQLite Solution |
|---|---|---|
| **ID Collisions** | `len(data['x']) + 1` produced duplicate IDs when items were deleted | `AUTOINCREMENT` guarantees unique IDs |
| **Passenger Data Duplication** | Passenger details repeated across multiple bookings | Normalised `passengers` table with `UNIQUE(phone, id_number)` |
| **Route Price Duplication** | Route prices duplicated for every schedule | Route prices stored once in `routes` table |
| **Orphan Records** | Deleting an agency left orphan buses/routes/schedules | `ON DELETE CASCADE` automatically cleans up children |
| **Concurrent Writes** | Last writer wins, no transaction safety | WAL journal mode + per-connection transactions |

A migration function (`migrate_from_json()`) reads the existing JSON file once and imports all data into the normalised SQLite structure. It tracks completion via a `migrated` key in the `meta` table to ensure idempotent execution.

---

## 7. Features Implemented

### 7.1 Multi-Country Support

All 54 African countries are configured with:

- Country name and flag colors (up to 6 colors for complex flags)
- Local currency and currency code
- Major cities (8–18 per country)
- Default language and supported languages
- Local payment providers
- VIP surcharge (varies by country)

Example configuration:
```python
'ke': {
    'name': 'Kenya',
    'flag_colors': ['#000000','#ce1126','#006600'],
    'currency': 'KSh',
    'currency_code': 'KES',
    'ref_prefix': 'KE',
    'cities': ["Nairobi","Mombasa","Kisumu", ...],
    'lang': 'en',
    'languages': ['en', 'sw'],
    'providers': ['mpesa', 'airtel_money'],
    'vip_surcharge': 500
}
```

### 7.2 Internationalisation (11 Languages)

The platform supports 11 languages with full UI translation:

| Code | Language | Script | Countries Using |
|---|---|---|---|
| `en` | English | Latin | Nigeria, Ghana, Kenya, etc. |
| `fr` | French | Latin | Senegal, Côte d'Ivoire, DRC, etc. |
| `ar` | Arabic | Arabic | Egypt, Morocco, Algeria, etc. |
| `pt` | Portuguese | Latin | Angola, Mozambique, Cape Verde |
| `es` | Spanish | Latin | Equatorial Guinea |
| `sw` | Swahili | Latin | Tanzania, Kenya, Uganda |
| `am` | Amharic | Ge'ez | Ethiopia |
| `so` | Somali | Latin | Somalia |
| `ti` | Tigrinya | Ge'ez | Eritrea |
| `af` | Afrikaans | Latin | South Africa |
| `zu` | Zulu | Latin | South Africa |

**Translation Architecture:**
- All UI text is wrapped in `_("text")` function calls
- Each language has a JSON file with key-value pairs
- Missing keys fall back gracefully to English
- Language toggle is only shown when a country has 2+ supported languages
- Country-switching auto-selects the country's default language

### 7.3 Passenger Booking Flow

The booking process follows a clear step-by-step flow:

1. **Search:** Passenger selects origin city, destination city, and travel date
2. **Browse Results:** Available trips are displayed, grouped by period (morning/afternoon/night), showing agency name, bus type, price, and available seats
3. **Pick Seat:** Interactive seat map shows the 71-seat bus layout (13 rows of 5 + rear bench of 6). Occupied seats are greyed out, available seats are selectable
4. **Enter Details:** Passenger provides name, phone number, and ID number. Optional luggage can be added if the route supports it
5. **Payment:** Country-specific payment providers are displayed. Payment is simulated with transaction ID generation
6. **Ticket:** E-ticket is displayed with full details, downloadable as PDF or PNG image

**Business Rules:**
- Booking closes 15 minutes before departure
- Trips are auto-expired 2 hours after departure
- Bookings expire 24 hours after departure
- VIP surcharge is applied per-country (e.g., FCFA 3,000 in Cameroon, KSh 500 in Kenya)
- Database-level UNIQUE index on (schedule_id, seat_number) prevents double-booking atomically
- Rate limiting (10 attempts per 15 minutes per IP) on all login endpoints prevents brute-force attacks

### 7.4 Agency Portal

Agencies have a dedicated dashboard for managing their operations:

- **Dashboard:** Overview of buses, routes, upcoming schedules, and booking counts. Shows approval/rejection status banner
- **Buses:** Add new buses, toggle availability status, view all vehicles with plate numbers and types
- **Routes:** Define city pairs with duration, pricing, and optional luggage configuration
- **Schedules:** Schedule trips by assigning routes to buses with specific dates and times
- **Bookings:** View all bookings, cancel bookings, reassign passengers to alternative trips
- **Manifest:** Generate passenger manifest for any scheduled trip

**Registration Flow:**
1. Agency fills registration form with name, locations, admin email (for password reset), password, and desired bus count (standard/VIP)
2. System creates agency account with `approved: False` status
3. Agency remains invisible to passengers until Ministry approves
4. On approval, agency receives notification and becomes searchable

### 7.5 Ministry of Transport Portal

Each country has its own scoped Ministry portal:

- **Login:** Country-scoped authentication (minister selects country via globe menu, then logs in)
- **Dashboard:** Statistics showing total agencies, pending approvals, buses, routes, schedules, bookings, and revenue
- **Agency Registry:** Full list of agencies with:
  - Name, country, locations, bus/route/booking counts
  - Status badges (Approved green, PENDING orange, Rejected red)
  - **Approve action with reason modal** — minister writes why the agency is being approved
  - **Reject action with reason modal** — minister writes why the agency is being rejected (stored permanently)
- **Booking Records:** Cross-agency view of all bookings within the minister's country

### 7.6 E-Ticket Generation

Tickets are generated in three formats:

1. **HTML Ticket** (`/ticket/<ref>`): Web page with all booking details, styled with flag colors
2. **PNG Image** (`/ticket/<ref>/image`): Rendered with Pillow, featuring:
   - Country flag colors in header and footer
   - QR-style reference number display
   - Route (from→to), passenger details, seat number
   - VIP/Standard badge with colour coding
   - Price breakdown with VIP surcharge and luggage fees
   - Validity period
   - Agency and bus information
3. **PDF Document** (`/ticket/<ref>/pdf`): Generated via xhtml2pdf from the HTML template, suitable for printing or email

### 7.7 Responsive Design

The interface is fully responsive with four breakpoints:

| Breakpoint | Target | Changes |
|---|---|---|
| 1024px | Tablet | Grids collapse to 2-column, nav adjusts |
| 768px | Mobile | Single column, hamburger menu, scrollable tables |
| 480px | Small phone | Reduced typography, compact cards, smaller seats |
| 360px | Very small | Minimal padding, smallest font sizes |

**Key responsive features:**
- Hamburger navigation toggle with smooth open/close animation
- Click-outside-to-close for navigation menu
- All tables wrapped in scrollable containers with `overflow-x: auto`
- Seat layout scales down on mobile (30px max-width seats)
- Fluid typography using `clamp()` for headings
- Grid systems collapse progressively

### 7.8 Agency Privacy

Competing agencies cannot see each other's operational data:

- When an agency employee is logged in, all public-facing pages (homepage, search, agency listings) filter to show ONLY that agency's data
- Direct URL access to competitor agency pages is blocked with an "Access denied" message
- Regular passengers (not logged in as an agency) continue to see all approved agencies
- Ministry users see everything within their country scope

### 7.9 Payment Providers

20 African mobile money and digital payment providers are configured:

| Code | Name | Used In |
|---|---|---|
| `mtn_momo` | MTN MoMo | Cameroon, Nigeria, Ghana, etc. |
| `orange_money` | Orange Money | Francophone Africa |
| `mpesa` | M-Pesa | Kenya, Tanzania, DRC, etc. |
| `airtel_money` | Airtel Money | Kenya, Uganda, Rwanda, etc. |
| `emola` | EMOLA | Mozambique, Angola |
| `ecocash` | EcoCash | Zimbabwe |
| `wave` | Wave | Senegal, Côte d'Ivoire |
| `telebirr` | Telebirr | Ethiopia |
| `zaad` | Zaad | Somalia |
| `opay` | Opay | Nigeria |
| And 10 more... | | |

Payment is simulated with transaction ID generation. In production, these would connect to real mobile money APIs.

---

## 8. Implementation Details

### 8.1 Project Structure

```
transport/
│
├── app.py                     # Main Flask application (routes, config)
├── database.py                # SQLite database module (schema, CRUD, migration)
├── data.json                  # Original JSON storage (migrated to SQLite)
├── data.db                    # SQLite database (created by migration)
├── generate_translations.py   # Script to generate translation files
│
├── static/
│   └── style.css              # All site CSS (responsive, layout, components)
│
├── templates/
│   ├── base.html              # Base template (nav, footer, country modal)
│   ├── index.html             # Homepage
│   ├── search.html            # Trip search results
│   ├── book.html              # Booking form
│   ├── payment.html           # Payment page
│   ├── pick_seat.html         # Seat selection before payment
│   ├── seats.html             # Seat selection after payment
│   ├── ticket.html            # E-ticket display
│   ├── ticket_pdf.html        # PDF ticket template
│   ├── lookup.html            # Booking reference lookup
│   ├── agencies.html          # Browse all agencies
│   ├── agency_browse.html     # Single agency public page
│   ├── agency_register.html   # Agency registration
│   ├── agency_login.html      # Agency login
│   ├── agency_dashboard.html  # Agency dashboard
│   ├── agency_buses.html      # Agency bus management
│   ├── agency_routes.html     # Agency route management
│   ├── agency_schedules.html  # Agency schedule management
│   ├── agency_bookings.html   # Agency booking view
│   ├── agency_manifest.html   # Passenger manifest
│   ├── ministry_login.html    # Ministry login
│   ├── ministry_dashboard.html# Ministry dashboard
│   ├── ministry_agencies.html # Ministry agency registry
│   └── ministry_bookings.html # Ministry booking records
│
└── translations/
    ├── en.json                # English (source of truth, ~434 keys)
    ├── fr.json                # French
    ├── ar.json                # Arabic
    ├── pt.json                # Portuguese
    ├── es.json                # Spanish
    ├── sw.json                # Swahili
    ├── am.json                # Amharic
    ├── so.json                # Somali
    ├── ti.json                # Tigrinya
    ├── af.json                # Afrikaans
    └── zu.json                # Zulu
```

### 8.2 Key Code Patterns

**Translation Wrapper:**
```python
def _(text):
    lang = get_current_lang()
    t = load_translations(lang)
    return t.get(text, text)  # Falls back to original English
```

**Country-Scoped Query:**
```python
def _country_agencies():
    code = session.get('country', 'cm')
    agencies = get_approved_agencies_by_country(code)
    if 'agency_id' in session:
        agencies = [a for a in agencies if a['id'] == session['agency_id']]
    return agencies
```

**Auto-Expire System:**
```python
# Runs on every request via @app.before_request
def auto_expire_trips():
    # Mark schedules as 'completed' 2 hours after departure
    # Mark bookings as 'expired' 24 hours after departure
```

### 8.3 Bus Layout Algorithm

The 71-seat bus layout uses a 13×5 configuration with a walkway and rear bench:

```
Row 1:  [1] [2] [3]  |  [4] [5]   |  (aisle)
Row 2:  [6] [7] [8]  |  [9] [10]  |
...
Row 13: [61][62][63] | [64][65]   |
Rear:   [66][67][68] [69]  [70][71]  [exit]
```

The layout is generated programmatically by the `bus_layout()` function, supporting both standard and VIP styling.

---

## 9. Challenges and Solutions

### 9.1 Data Redundancy in JSON Storage

**Challenge:** The original `data.json` file stored all data in a flat, denormalised structure. Passenger details were repeated across every booking, route prices were duplicated for every schedule referencing them, and ID generation using `len(data['x']) + 1` produced collisions when items were deleted. There was no referential integrity — deleting an agency left orphan buses, routes, schedules, and bookings.

**Solution:** Migrated to SQLite with a fully normalised schema. Seven tables with proper foreign keys (`ON DELETE CASCADE`), `AUTOINCREMENT` for collision-free IDs, WAL journal mode for concurrent write safety, and a `UNIQUE` constraint on passenger phone+ID to eliminate duplication. A migration function imports existing JSON data into the new structure.

### 9.2 Multi-Language Translation Management

**Challenge:** Maintaining consistent translations across 11 languages with approximately 434 UI strings each. Adding new UI text required updating all 11 files. Non-Latin scripts (Arabic, Amharic, Tigrinya) required special handling.

**Solution:** A `generate_translations.py` script reads `en.json` (the source of truth) and regenerates all language files, adding missing keys. The `_()` function gracefully falls back to English when a key is missing in any language file.

### 9.3 Agency Privacy

**Challenge:** Competing agencies should not know each other's pricing, routes, or operational data. Since the booking platform is public, any agency employee could browse the site as a passenger to view competitor information.

**Solution:** Session-aware filtering in the `_country_agencies()` helper. When an `agency_id` is present in the session, all public pages filter to show only the logged-in agency's data. Direct URL access to competitor agency pages is explicitly blocked with authorisation checks.

### 9.4 Concurrent Booking Race Conditions

**Challenge:** Two passengers could select the same seat simultaneously. Without proper locking, both bookings would succeed for the same seat.

**Solution:** At payment time, the system re-checks seat availability before confirming. If the seat was taken between seat selection and payment, the passenger is redirected to choose another seat. This optimistic locking approach works well for the system's expected traffic volume.

### 9.5 Unclosed HTML Elements

**Challenge:** A missing `</div>` in the country modal caused the entire page footer to render inside the modal overlay (which had `display: none`), making the footer invisible.

**Solution:** Systematic div-counting review of all templates. The issue was fixed by properly closing the modal container before the footer.

### 9.6 Concurrent Login and Rate Limiting

**Challenge:** The teacher reviewing this project asked: *"Can 10 people use this site at the same time? How can Facebook handle 500 people submitting a login form simultaneously without crashing?"* The original login endpoints had no protection — an attacker (or 500 real users) could hammer `/agency/login`, `/ministry/login`, and `/ministry/relogin` with unlimited rapid attempts, potentially overwhelming the server or brute-forcing passwords.

**Solution:** An in-memory rate limiter was added to all three login endpoints:

```python
login_attempts = defaultdict(list)
RATE_LIMIT_WINDOW = 15  # minutes
RATE_LIMIT_MAX = 10     # max attempts per window

def is_rate_limited(ip):
    now = datetime.now()
    attempts = login_attempts[ip]
    attempts[:] = [t for t in attempts if now - t < timedelta(minutes=RATE_LIMIT_WINDOW)]
    if len(attempts) >= RATE_LIMIT_MAX:
        return True, remaining_minutes
    attempts.append(now)
    return False, 0
```

Each IP address is tracked independently. After 10 failed login attempts within 15 minutes, further attempts are blocked with a user-friendly message. On successful login, the attempt counter for that IP is cleared. This prevents brute-force attacks while allowing legitimate users to retry a reasonable number of times.

**Limitation:** This is a per-process in-memory solution. In a multi-server deployment (e.g., multiple Gunicorn workers), each process would have its own counter, so an attacker could distribute attempts across workers. A production deployment would use Redis or a database-backed rate limiter (e.g., Flask-Limiter) for cross-process coordination.

### 9.7 Concurrent Seat Booking (Race Condition)

**Challenge:** Two passengers could select the same seat at the exact same time. The original code checked seat availability (`get_booking_seat_numbers()`) and then inserted the booking in separate database operations — a classic **race condition** where both passengers could pass the availability check before either booking was committed.

This is the same concurrency problem Facebook, Ticketmaster, and airline booking systems face: when thousands of users try to book the same resource simultaneously, the system must prevent double-allocation.

**Solution:** Two layers of protection were implemented:

1. **Database-level unique constraint:** A partial unique index was added to the `bookings` table:
   ```sql
   CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_seat 
   ON bookings(schedule_id, seat_number) WHERE seat_number IS NOT NULL;
   ```
   This guarantees that even if two INSERT statements execute at the exact same microsecond, only one will succeed — the database itself enforces the rule.

2. **Atomic booking function (`add_booking_atomic`)**: The entire seat selection + booking creation is wrapped in a `BEGIN IMMEDIATE` transaction, which acquires a write lock immediately. If the unique constraint is violated, SQLite raises an `IntegrityError`, which is caught and shown to the user as "That seat was just taken."

3. **Atomic payment confirmation (`confirm_booking_atomic`)**: The seat is re-checked inside a transaction at payment time too. If another booking claimed the seat between booking creation and payment, the seat is released and the passenger is redirected to pick again.

These protections are similar to how production booking systems work: database-level constraints are the last line of defence, while application-level checks provide a better user experience (catching conflicts early rather than at insert time).

**Scaling further:** For Facebook-scale traffic (500+ writes/second), SQLite's single-writer model would become a bottleneck. A production deployment would migrate to PostgreSQL (which supports row-level locking and `SELECT ... FOR UPDATE`) and add Redis for real-time seat availability caching.

---

## 10. Testing and Results

### 10.1 Testing Approach

The application was tested using:

1. **Manual browser testing** across all routes and user flows
2. **Automated HTTP tests** using Python `http.client` to verify route responses
3. **Database verification** to confirm migration accuracy and data integrity
4. **Responsive testing** at all four breakpoints (1024, 768, 480, 360px)

### 10.2 Route Verification

All 25+ routes were verified to return HTTP 200 with valid HTML content:

| Route | Status | Content Verified |
|---|---|---|
| `/` (index) | 200 | Agency listing, hero section |
| `/search` | 200 | Trip results with pricing |
| `/book/<id>` | 200 | Booking form with seat selection |
| `/payment/<id>` | 200 | Payment provider options |
| `/ticket/<ref>` | 200 | E-ticket with all details |
| `/ticket/<ref>/pdf` | 200 | PDF download |
| `/ticket/<ref>/image` | 200 | PNG image |
| `/agencies` | 200 | Agency directory |
| `/agency/login` | 200 | Login form |
| `/agency/dashboard` | 200 | Agency stats and data |
| `/ministry/login` | 200 | Ministry login form |
| `/ministry/agencies` | 200 | Agency registry with statuses |

### 10.3 Migration Results

| Entity | JSON Records | SQLite Records | Match |
|---|---|---|---|
| Agencies | 7 | 7 | ✓ |
| Buses | 111 | 111 | ✓ |
| Routes | 9 | 9 | ✓ |
| Schedules | 11 | 11 | ✓ |
| Bookings | 18 | 18 | ✓ |
| Passengers (normalised) | N/A | 7 | ✓ (deduplicated) |

### 10.4 Screenshots

*(Insert screenshots here — 4–6 key screens showing homepage, search results, seat selection, booking form, e-ticket, ministry dashboard)*

---

## 11. Conclusion and Future Work

### 11.1 Summary of Achievements

The AFRI Trans platform successfully delivers a multi-country bus ticketing system with:

- **Complete coverage** of all 54 African countries with localised configuration
- **Multilingual interface** supporting 11 languages across different scripts
- **Full booking lifecycle** from search through payment to e-ticket delivery
- **Agency management** with registration, scheduling, and operations
- **Government oversight** with per-country ministry approval workflows
- **Responsive design** accessible on desktop, tablet, and mobile devices
- **Data integrity** through SQLite migration with normalised schema
- **Competitor privacy** preventing unauthorised data access between agencies

### 11.2 Future Improvements

1. **Security Enhancements**
   - Add CSRF protection to all forms *(still pending)*
   - Switch to HTTPS in production
   - ~~Implement rate limiting on login endpoints~~ ✅ Completed (10 attempts/15min per IP)

2. **Code Quality**
   - Refactor monolithic `app.py` into modular route blueprints
   - Separate business logic from route handlers
   - Add unit tests with pytest

3. **Real-Time Features**
   - WebSocket-based real-time seat availability
   - Live booking notifications for agencies
   - SMS/email booking confirmations

4. **Payment Integration**
   - Connect to real mobile money APIs (M-Pesa, MTN MoMo, Orange Money)
   - Implement webhook-based payment confirmation
   - Add payment receipt generation

5. **Performance Optimisation**
   - Add Redis caching for frequently accessed data
   - Implement database query optimisation
   - Add CDN for static assets

6. **Additional Features**
   - RTL support for Arabic-language countries
   - Mobile app (React Native or Flutter)
   - Driver/operator mobile interface for manifest management
   - Multi-trip and round-trip booking
   - Loyalty/rewards program

---

## 12. References

1. Flask Documentation — *The Flask Web Framework*. Pallets Project. https://flask.palletsprojects.com/
2. Python 3 Documentation — *Python Software Foundation*. https://docs.python.org/3/
3. SQLite Documentation — *SQLite Consortium*. https://www.sqlite.org/docs.html
4. Jinja2 Documentation — *Pallets Project*. https://jinja.palletsprojects.com/
5. Pillow (PIL Fork) Documentation — *Python Pillow*. https://pillow.readthedocs.io/
6. xhtml2pdf Documentation — *xhtml2pdf Project*. https://xhtml2pdf.readthedocs.io/
7. Werkzeug Documentation — *Pallets Project*. https://werkzeug.palletsprojects.com/
8. Font Awesome Icons — *Fonticons, Inc*. https://fontawesome.com/
9. ISO 3166-1 Country Codes — *International Organization for Standardization*. https://www.iso.org/iso-3166-country-codes.html
10. African Languages Reference — *Ethnologue: Languages of Africa*. SIL International. https://www.ethnologue.com/region/Africa
11. Mobile Money in Africa — *GSMA Mobile Money Report*. https://www.gsma.com/mobilemone
12. Bus Seat Layout Standards — *Industry standard 71-seater bus configuration for inter-city transport in West Africa*.

---

*Report prepared by **ADOLF BUOH** (ADOLF.AI)*

*Ferdsilink Buea — 2026*
