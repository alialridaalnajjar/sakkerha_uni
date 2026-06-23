# Sakkerha

**Fix the flow of your city.**

Sakkerha is a civic infrastructure reporting platform built for Lebanon. Citizens file geolocated street issues on an interactive map; Google Gemini AI rates severity and flags invalid reports; municipal admins triage submissions from a dashboard and publish resolved work to the public map.

---

## Features

**Citizens** — sign up, reset password via email, drop pins on a Leaflet map, upload up to 3 photos, get AI severity ratings, manage profile, view/delete own reports.

**Admins** — filterable dashboard, status workflow (`pending` → `ongoing` → `completed` / `rejected`), report detail with AI notes, read-only admin map, profile management.

**Platform** — session auth with role-based access, Firebase image storage, flash messages, landing page with Wissam 3D mascot (Three.js).

---

## Tech Stack

Flask 3 · Flask-SQLAlchemy · PostgreSQL · Firebase Storage · Google Gemini · Leaflet / OpenStreetMap · Jinja2 · vanilla JS · Flask-Mail · Gunicorn · python-dotenv

---

## Architecture (MVC+)

Sakkerha uses **MVC+** — standard Model–View–Controller, plus a routing layer, Builder pattern, and a controller-orchestrated AI integration.

```
Request → Routes (+) → Controllers (C) → Builders (+) → Models (M) → PostgreSQL
                              ↓
                         Views (V)  ←  templates/ + static/
```

| Layer | Folder | Responsibility |
|-------|--------|----------------|
| **Routes (+)** | `routes/` | URL dispatch, auth decorators (`login_required`, `user_required`, `admin_required`) |
| **Controllers (C)** | `controllers/` | Validation, orchestration, Firebase/Gemini/Mail calls |
| **Builders (+)** | `models/builders/` | Fluent construction of `User` and `Report` objects |
| **Models (M)** | `models/` | SQLAlchemy schema, queries, password hashing |
| **Views (V)** | `templates/`, `static/` | Presentation only — no direct DB access |

**Blueprints:** `auth_bp` (`/`), `report_bp` (`/`), `admin_bp` (`/admin`), `profile_bp` (`/profile`).

**Example — report submission:**
```
POST /report/submit → user_required → submit_report()
  → Firebase upload → Gemini assessment → ReportBuilder → save → JSON response
```

Models never render HTML. Routes never hold business logic. Controllers are the only layer that coordinates everything in one flow.

---

## AI Layer

Runs inside `report_controller._assess_with_gemini()` at submit time — not a separate service, but an integration boundary kept out of models and views.

```
Upload images → build prompt + fetch/base64 images → Gemini 2.5 Flash → parse JSON → save severity + ai_note
```

**Two-step prompt:**
1. **Validity** — flag `invalid` for unrelated images, spam/gibberish, water coordinates, or contradictions between photo and description.
2. **Severity** (if valid) — `low` (minor debris/cracks), `medium` (10–30 cm potholes, partial damage), `high` (sinkholes, collapsed road, immediate hazard). Images are primary evidence.

**Output** → stored in `reports.severity` and `reports.ai_note`. Admins see it as a triage hint but always make the final status call.

| AI result | Initial status | Public map |
|-----------|----------------|------------|
| `invalid` | `invalid` | Hidden (admin: `?show_invalid=1`) |
| `low` / `medium` / `high` | `pending` | Shown only after admin sets `ongoing` or `completed` |

On API failure, defaults to `medium` with a fallback note — the report still saves. Requires `GEMINI_API_KEY` in `.env`.

---

## Project Structure

```
├── app.py                  # App entry, blueprints, error handlers
├── config.py               # Env-based Config
├── database.py             # SQLAlchemy init
├── controllers/            # Business logic
├── routes/                 # Blueprints + auth decorators
├── models/                 # User, Report + builders/
├── templates/              # Jinja2 views
└── static/                 # CSS, JS (map, admin, profile, wissam)
```

---

## Setup

**Requirements:** Python 3.10+, PostgreSQL, Firebase Storage, Gemini API key. Gmail App Password optional (password reset emails).

```bash
git clone <repository-url>
cd SakkerhaCharlie
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
FLASK_DEBUG=1
DATABASE_URL=postgresql://user:password@host:5432/dbname
GEMINI_API_KEY=your-gemini-api-key
FIREBASE_API_KEY=...
FIREBASE_PROJECT_ID=...
FIREBASE_STORAGE_BUCKET=...
FIREBASE_DATABASE_URL=...
FIREBASE_AUTH_DOMAIN=...
MAIL_USERNAME=your@gmail.com        # optional
MAIL_PASSWORD=app-password          # optional
MAIL_DEFAULT_SENDER=your@gmail.com  # optional
```

Tables auto-create on first run. To create an admin, sign up then run:

```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

**Run locally:** `python app.py` → [http://127.0.0.1:5000](http://127.0.0.1:5000)

**Production:** `gunicorn -w 4 -b 0.0.0.0:8000 app:app`

---

## User Roles

| Role | Access |
|------|--------|
| Guest | Home, public map (view only) |
| `user` | Submit reports, `/profile` |
| `admin` | `/admin` dashboard, status management, `/admin/profile` |

---

## Report Lifecycle

```
Submit → Firebase upload → Gemini AI
  → invalid?  status: invalid (hidden from queue)
  → valid?    status: pending
Admin triage → ongoing → completed  (or rejected)
Only ongoing + completed appear on the public map
```

---

## Key Routes

| Path | Who | What |
|------|-----|------|
| `/`, `/login`, `/signup` | Public | Auth |
| `/map` | Public | Live map |
| `/report/submit` | User | File report (JSON) |
| `/profile` | User | Profile & account |
| `/admin` | Admin | Dashboard & triage |
| `/admin/report/<id>/status` | Admin | Update status (JSON) |

---

## Contact

**Ali Al Rida Al Najjar** — [alialridaalnajjar@gmail.com](mailto:alialridaalnajjar@gmail.com)

Map default: **33.828091112441875, 35.51138497471992** (Beirut, Lebanon)
