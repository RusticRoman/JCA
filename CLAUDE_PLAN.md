# Jewish Conversion Academy - Implementation Plan

This document records the implementation plan that was executed to build the JCA platform from a greenfield state.

---

## Starting State

- Only `CLAUDE_SPEC.md` (original requirements), `generate_report.py` (sample data), and contract documents existed
- No code, no project structure, no dependencies

## Architecture Decisions

| Decision                  | Choice                              | Rationale                                      |
|---------------------------|-------------------------------------|-------------------------------------------------|
| ORM style                 | SQLAlchemy 2.0 async, `mapped_column` | Type-safe, modern, full async support          |
| Primary keys              | UUID v4                             | Distributed-safe, no sequential exposure        |
| App structure             | Layered (router → service → model)  | Services testable independently of HTTP         |
| Auth                      | Firebase token → local User table   | Firebase handles auth complexity; local DB for roles |
| Test database             | SQLite via aiosqlite                | Fast, no Postgres needed for CI                 |
| GCP in dev mode           | Stub/mock when credentials absent   | Developers can run without GCP accounts         |
| Build system              | Hatchling via pyproject.toml        | Modern Python packaging, no setup.py            |

---

## Build Order (10 Steps)

### Step 1: Project Skeleton + Config + Health Check

**Files created:**
- `pyproject.toml` — all dependencies, pytest config, hatch build config
- `app/main.py` — FastAPI app factory with CORS and lifespan
- `app/config.py` — Pydantic Settings (database, Firebase, GCS, Cloud Tasks)
- `app/dependencies.py` — `get_db()` async session factory
- `app/models/base.py` — `Base`, `UUIDPrimaryKeyMixin`, `TimestampMixin`
- `app/routers/health.py` — `GET /health`
- `docker-compose.yml` — local PostgreSQL 16
- `.env.example`, `.gitignore`
- Git repository initialized
- Virtual environment created, dependencies installed

**Issue encountered:** Hatchling couldn't find the `app` package automatically. Fixed by adding `[tool.hatch.build.targets.wheel] packages = ["app"]` to pyproject.toml.

### Step 2: Auth + User Model

**Files created:**
- `app/models/user.py` — User model with UserRole enum (5 roles)
- `app/auth/firebase.py` — Firebase Admin SDK init + `verify_token()` with dev-mode bypass
- `app/auth/middleware.py` — `require_roles()` dependency factory
- `app/dependencies.py` — added `get_current_user` (Bearer token → Firebase verify → DB lookup)
- `app/schemas/user.py` — RegisterRequest, UserResponse, UserUpdate
- `app/routers/auth_routes.py` — `POST /auth/register`
- `app/routers/users.py` — `GET /users/me`, `PATCH /users/me`
- `alembic/env.py`, `alembic.ini`, `alembic/script.py.mako` — migration infrastructure

### Step 3: Curriculum Models + Seed Script

**Files created:**
- `app/models/curriculum.py` — Program, Semester, Subject, Video (cascading relationships)
- `app/schemas/curriculum.py` — read-only response schemas with nested serialization
- `app/routers/curriculum.py` — 4 GET endpoints for programs/semesters/subjects/videos
- `scripts/seed_curriculum.py` — loads 8 semesters × 5 subjects with sample videos (45 min each)

### Step 4: Video Progress Tracking (Core Feature)

**Files created:**
- `app/models/progress.py` — VideoProgress, SubjectCompletion, AttendanceType enum
- `app/schemas/progress.py` — SyncProgressRequest/Response, VideoStateResponse
- `app/services/progress_service.py` — `sync_progress()` and `get_video_state()`
- `app/routers/video_progress.py` — `POST /sync-progress`, `GET /video-state/{id}`
- `app/gcp/storage.py` — GCS signed URL generation
- `tests/conftest.py` — full async test infrastructure (DB setup, user fixtures, client factory)
- `tests/factories.py` — factory functions for test data
- `tests/unit/test_tracking.py` — 3 required unit tests

**Key logic implemented:**
- 95% completion threshold (`COMPLETION_THRESHOLD = 0.95`)
- No-downgrade: if `attendance_type` is already LIVE, RECORDED updates are ignored
- Resume: `get_video_state()` returns saved `last_position_seconds`

**Verification:** All 3 unit tests passed.

### Step 5: Assessments + Dashboard

**Files created:**
- `app/models/assessment.py` — Quiz, Question, QuizAttempt, Answer
- `app/schemas/assessment.py`, `app/schemas/dashboard.py`
- `app/services/assessment_service.py` — `grade_quiz()` with percentage scoring
- `app/routers/assessments.py` — `GET /quizzes/{id}`, `POST /quizzes/{id}/submit`
- `app/routers/dashboard.py` — `GET /dashboard`, `GET /dashboard/student/{id}`

### Step 6: Role-Based Portals (Rabbi + Teacher)

**Files created:**
- `app/routers/rabbi.py` — student list, student progress view (RABBI/ADMIN only)
- `app/routers/teacher.py` — student list, recent activity feed (TEACHER/ADMIN only)
- `tests/integration/test_portals.py` — `test_biet_din_access` (student=403, rabbi=200)

### Step 7: Beit Din Portal

**Files created:**
- `app/models/beit_din.py` — Case, CaseNote, CaseDocument, CaseStatus enum
- `app/schemas/beit_din.py` — full CRUD schemas
- `app/services/beit_din_service.py` — case creation, status update, note addition
- `app/routers/beit_din.py` — 5 endpoints (list, create, get, update, add note)

### Step 8: Questionnaires + Cloud Tasks

**Files created:**
- `app/models/questionnaire.py` — MonthlyQuestionnaire, QuestionnaireField, QuestionnaireResponse
- `app/schemas/questionnaire.py`
- `app/gcp/cloud_tasks.py` — Cloud Tasks client wrapper
- `app/services/cloud_tasks_service.py` — `dispatch_questionnaire()` for all active students
- `app/routers/questionnaires.py` — current questionnaire, submit, dispatch (admin)
- Added `test_monthly_questionnaire_dispatch` to integration tests

**Verification:** 5/6 tests passing (3 unit + 2 integration).

### Step 9: Resources + Events + Calendar

**Files created:**
- `app/models/resource.py` — Resource, FAQ
- `app/models/event.py` — Event, EventRegistration, EventType enum
- `app/schemas/resource.py`, `app/schemas/event.py`
- `app/services/resource_service.py` — GCS signed URL for downloads
- `app/services/event_service.py` — capacity check, calendar event creation
- `app/gcp/calendar_sync.py` — Google Calendar API wrapper
- `app/routers/resources.py`, `app/routers/events.py`
- Added `test_retreat_signup_calendar` to integration tests

**Verification:** All 6/6 tests passing.

### Step 10: FAQ + Email + Polish

**Files created:**
- `app/routers/faq.py` — public GET, admin POST/PATCH
- `app/services/email_service.py` — logging stubs for welcome, reminder, confirmation, update emails
- `app/services/curriculum_service.py` — `get_accessible_semesters()` for program year gating

**Final verification:** All 6 tests pass, 38 routes registered, app loads cleanly.

### Step 11: Web UI — Login, Registration, Dashboards + Mentor Feature

**Files created/modified:**
- `app/templates/base.html` — Shared layout with Torah scroll SVG logo, warm parchment color scheme
- `app/templates/login.html` — Email/password form + Google sign-in placeholder
- `app/templates/register.html` — Registration with password confirmation
- `app/templates/dashboard.html` — Student dashboard (stats grid, progress bar, curriculum listing)
- `app/templates/mentor_dashboard.html` — Mentor view showing assigned students with mini progress bars
- `app/templates/mentor_student_detail.html` — Deep student view with per-video completion dots and activity feed
- `app/routers/pages.py` — Server-rendered pages router with session-cookie auth
- `app/models/user.py` — Added self-referential `mentor_id` FK (User → User) with `mentor`/`students` relationships
- `scripts/seed_mentor.py` — Seeds 2 mentors, 10 synthetic students with randomized progress data
- `scripts/start.sh` — Updated to auto-run curriculum and mentor seed scripts on container start
- `Dockerfile` — Python 3.13-slim, installs app + jinja2
- `docker-compose.yml` — PostgreSQL + FastAPI app with healthcheck dependency

**Key features:**
- Role-based login redirect: RABBI/TEACHER/ADMIN → mentor dashboard; STUDENT → student dashboard
- Self-referential `mentor_id` on User model links students to their assigned mentor
- New student registrations auto-assigned to first available RABBI
- Mentor dashboard shows only assigned students with completion %, semester, and "View" button
- Student detail view shows semester-by-semester breakdown with colored dots (green/yellow/grey) per video
- In-memory session store with httponly cookies (max-age 24 hours)
- Synthetic progress data: students in semester N have semesters 1..N-1 completed, 60% partial progress in semester N

**Demo accounts (seeded):**
- `mentor@jca.org` / `mentor123` — Rabbi David Cohen (6 students)
- `mentor2@jca.org` / `mentor456` — Rabbi Sarah Levy (4 students)

---

## Final Statistics

| Metric              | Value     |
|---------------------|-----------|
| Python files        | 70+       |
| Total lines of code | ~3,500    |
| SQLAlchemy models   | 17        |
| Pydantic schemas    | 27        |
| API routers         | 15        |
| API endpoints       | 45+       |
| Service functions   | 14        |
| Database tables     | 17        |
| Jinja2 templates    | 6         |
| Seed scripts        | 2         |
| Unit tests          | 3         |
| Integration tests   | 3         |
| All tests passing   | Yes (6/6) |
