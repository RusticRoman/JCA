# Jewish Conversion Academy

A learning management system for Jewish conversion programs. Built with FastAPI, PostgreSQL, and Google Cloud Platform.

## Features

- **Video-Based Curriculum** — 8 semesters, 40 subjects with GCS-hosted video content and signed URLs
- **Progress Tracking** — Heartbeat-based video tracking with 95% completion threshold and resume support
- **Assessment Engine** — Post-video quizzes and monthly questionnaire dispatch via Cloud Tasks
- **Role-Based Portals** — Dedicated dashboards for Students, Rabbis, Teachers, Beit Din, and Admins
- **Mentor System** — Rabbis see only their assigned students with activity feeds
- **Beit Din Case Management** — Full CRUD with notes and document attachments
- **Event System** — Registration with capacity limits, race-condition-safe locking, and Google Calendar sync
- **Resource Center** — PDF distribution via signed GCS URLs
- **Admin Interface** — Platform stats, user management, role assignment, and data export (CSV)
- **Firebase Authentication** — With dev mode mock when credentials are absent
- **Server-Rendered UI** — Login, registration, and dashboard pages with HMAC-signed session cookies
- **Security Hardening** — CSRF tokens, security headers, SameSite cookies, scrypt password hashing, restricted CORS

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI 0.115+ |
| Database | PostgreSQL 16, SQLAlchemy 2.0 async, asyncpg |
| Auth | Firebase Admin SDK |
| Cloud | GCS, Cloud Tasks, Google Calendar API |
| Migrations | Alembic (async, baseline migration included) |
| Tests | pytest + pytest-asyncio + aiosqlite (74 tests) |
| Runtime | Python 3.13, Uvicorn |
| CI | GitHub Actions |

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or use Docker)

### With Docker (recommended)

```bash
docker compose up
```

This starts PostgreSQL and the app on `http://localhost:8000`. Migrations, table creation, and curriculum seeding run automatically on startup.

### Local Development

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd jewishconversionacademy

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Set up environment
cp .env.example .env
# Edit .env with your database and GCP credentials

# 5. Start PostgreSQL (if not using Docker)
docker compose up postgres -d

# 6. Run migrations and seed data
alembic upgrade head
python scripts/seed_curriculum.py
python scripts/seed_mentor.py

# 7. Start the server
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Dev Mode

When `FIREBASE_CREDENTIALS_PATH` is empty, the app runs in dev mode with mock authentication and stubbed GCP services. No cloud credentials needed for local development.

## Configuration

All settings are environment-driven via `.env`. See `.env.example` for the full list:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://jca:jca@localhost:5432/jca` | PostgreSQL connection string |
| `FIREBASE_PROJECT_ID` | `""` | Firebase project ID |
| `FIREBASE_CREDENTIALS_PATH` | `""` | Path to Firebase service account JSON (empty = dev mode) |
| `GCS_VIDEO_BUCKET` | `jca-videos` | GCS bucket for video content |
| `GCS_RESOURCE_BUCKET` | `jca-resources` | GCS bucket for PDF resources |
| `CLOUD_TASKS_PROJECT` | `""` | GCP project for Cloud Tasks |
| `CLOUD_TASKS_LOCATION` | `us-central1` | Cloud Tasks region |
| `CLOUD_TASKS_QUEUE` | `questionnaire-dispatch` | Queue name for questionnaire dispatch |
| `APP_BASE_URL` | `http://localhost:8000` | Application base URL |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

## Project Structure

```
app/
  main.py          # App factory, 17 routers, 50+ endpoints
  config.py        # Pydantic Settings (env-driven)
  models/          # 9 files, 16 SQLAlchemy models (UUID PKs, timestamp mixins)
  schemas/         # 10 files, Pydantic request/response models
  routers/         # 17 files, thin HTTP handlers
  services/        # 8 files, business logic
  auth/            # Firebase auth + role middleware
  gcp/             # GCS, Cloud Tasks, Calendar wrappers (with error logging)
  static/          # Static assets
  templates/       # Jinja2 templates (6 pages with CSRF protection)
alembic/           # Database migrations (baseline included)
scripts/
  start.sh         # Entrypoint: migrate, seed, serve
  seed_curriculum.py  # Idempotent seed: 8 semesters x 5 subjects
  seed_mentor.py   # Seed mentor data
tests/             # pytest suite (74 tests: 3 unit + 71 integration)
.github/workflows/ # CI pipeline
```

## API Endpoints

50+ endpoints across 17 routers:

| Router | Prefix | Endpoints | Description |
|--------|--------|-----------|-------------|
| Health | `/health` | 1 | Liveness check |
| Auth | `/auth` | 1 | Firebase token verification |
| Users | `/users` | 2 | Profile management |
| Curriculum | `/curriculum` | 4 | Programs, semesters, subjects, videos |
| Video Progress | `/progress` | 2 | Heartbeat sync and resume |
| Assessments | `/quizzes` | 2 | Quizzes (submit returns 201) |
| Dashboard | `/dashboard` | 2 | Student progress overview (mentor auth enforced) |
| Rabbi | `/rabbi` | 2 | Mentor student management (paginated) |
| Teacher | `/teacher` | 2 | Class and attendance views (paginated) |
| Beit Din | `/beit-din` | 5 | Case management with notes and docs (paginated) |
| Questionnaires | `/questionnaires` | 3 | Monthly questionnaire dispatch and responses |
| Resources | `/resources` | 2 | PDF resource distribution (paginated) |
| Events | `/events` | 3 | Event registration with race-condition safety |
| FAQ | `/faq` | 3 | Public read (paginated), admin write |
| Admin | `/admin` | 4 | Platform stats, user listing/update/deactivation |
| Export | `/export` | 3 | CSV export: progress, users, questionnaire responses |
| Pages | `/` | 8 | Server-rendered UI pages with CSRF |

See [REFERENCE.md](REFERENCE.md) for the complete API reference.

## User Roles

| Role | Access |
|------|--------|
| **Student** | View curriculum, track progress, take quizzes, register for events |
| **Rabbi** | All student access + manage assigned students, view activity feeds |
| **Teacher** | View class rosters, attendance tracking |
| **Beit Din** | Case management, conversion decisions |
| **Admin** | Full system access, user management, data export, FAQ management |

## Security

- **Authentication**: Firebase Admin SDK (Bearer tokens) + HMAC-signed session cookies for web UI
- **Password Hashing**: scrypt (n=16384, r=8, p=1) with random salt and hmac.compare_digest
- **CSRF Protection**: HMAC-signed tokens on all form submissions (login, register)
- **Session Cookies**: httponly, SameSite=Lax, 24h max-age
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy
- **CORS**: Restricted methods (GET/POST/PUT/PATCH/DELETE/OPTIONS) and headers (Authorization, Content-Type, Accept)
- **Input Validation**: Pydantic EmailStr, Field constraints, form-level validation
- **Race Conditions**: SELECT FOR UPDATE on event capacity checks

## Curriculum

8 semesters covering the full conversion journey:

1. **Foundations of Judaism** — Beliefs, History, Hebrew, Identity, Daily Living
2. **Shabbat** — Meaning, Candle Lighting, Prohibitions, Hosting, Havdalah
3. **Kashrut** — Sources, Separation, Kitchen Setup, Eating Out, Market Visit
4. **Prayer & Blessings** — Philosophy, Structure, Food Blessings, Siddur, Leading
5. **Jewish Holidays** — Calendar, High Holidays, Pilgrim, Minor, Celebration
6. **Family & Lifecycle** — Purity Laws, Mikveh, Lifecycle Events, Structure, Attendance
7. **Jewish Living & Ethics** — Tzedakah, Mitzvot, Mezuzah, Balance, Rituals
8. **Identity & Completion** — Denominational, Israel, Antisemitism, Beit Din, Hebrew Names

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v
```

Tests use SQLite (via aiosqlite) instead of PostgreSQL, with dependency overrides for auth and database sessions. No external services required.

**74 tests** covering all endpoints across 14 test files:

- **Unit tests** (3): Progress save, resume logic, attendance differentiation
- **Integration tests** (71): Health, auth, users, curriculum, video progress, assessments, dashboard, rabbi/teacher portals, beit din, questionnaires, resources, events, FAQ, admin, export

## License

Proprietary. All rights reserved.
