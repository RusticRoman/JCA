# JCA Platform - Reference Manual

Complete technical reference for developers working on the Jewish Conversion Academy platform.

---

## Table of Contents

1. [Architecture](#1-architecture)
2. [Database Schema](#2-database-schema)
3. [API Reference](#3-api-reference)
4. [Services](#4-services)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [GCP Integration](#6-gcp-integration)
7. [Testing](#7-testing)
8. [Development Guide](#8-development-guide)
9. [File Reference](#9-file-reference)

---

## 1. Architecture

### Layered Design

```
┌─────────────┐
│   Routers    │  HTTP request/response, validation, status codes
├─────────────┤
│   Services   │  Business logic, rules, orchestration
├─────────────┤
│   Models     │  SQLAlchemy ORM, database access
├─────────────┤
│ GCP Wrappers │  Cloud Storage, Cloud Tasks, Calendar API
└─────────────┘
```

### Key Patterns

- **App Factory**: `create_app()` in `app/main.py` constructs the FastAPI instance, adds middleware, and registers all routers
- **Dependency Injection**: `get_db()` provides async DB sessions; `get_current_user()` extracts the authenticated user from the Bearer token
- **Role Enforcement**: `require_roles(UserRole.RABBI, UserRole.ADMIN)` returns a FastAPI dependency that checks the user's role
- **Dev Mode**: When `FIREBASE_CREDENTIALS_PATH` is empty, all GCP services return stubs/mocks — no cloud credentials needed for local development

### Module Dependencies

```
app/config.py          ← read by all modules
app/dependencies.py    ← imports models, auth
app/auth/middleware.py  ← imports dependencies
app/routers/*          ← imports dependencies, schemas, services
app/services/*         ← imports models, GCP wrappers
app/gcp/*              ← imports config
```

---

## 2. Database Schema

### 2.1 Tables Overview

| Table                     | Model                 | Description                          |
|---------------------------|-----------------------|--------------------------------------|
| `users`                   | User                  | All platform users (self-referential `mentor_id` FK) |
| `programs`                | Program               | Curriculum programs (year 1, 2, etc) |
| `semesters`               | Semester              | 8 semesters per program              |
| `subjects`                | Subject               | 5 subjects per semester              |
| `videos`                  | Video                 | Video lectures per subject           |
| `video_progress`          | VideoProgress         | Per-user video watch state           |
| `quizzes`                 | Quiz                  | Post-video quizzes                   |
| `questions`               | Question              | Multiple-choice questions            |
| `quiz_attempts`           | QuizAttempt           | User quiz submissions                |
| `answers`                 | Answer                | Per-question answers                 |
| `beit_din_cases`          | Case                  | Conversion case files                |
| `case_notes`              | CaseNote              | Notes on cases                       |
| `case_documents`          | CaseDocument          | Uploaded documents                   |
| `monthly_questionnaires`  | MonthlyQuestionnaire  | Monthly check-in forms               |
| `questionnaire_fields`    | QuestionnaireField    | Form fields                          |
| `questionnaire_responses` | QuestionnaireResponse | Submitted answers                    |
| `resources`               | Resource              | Downloadable PDFs/materials          |
| `faqs`                    | FAQ                   | Frequently asked questions           |
| `events`                  | Event                 | Calendar events/retreats             |
| `event_registrations`     | EventRegistration     | User event signups                   |

### 2.2 Enums

```python
class UserRole(str, Enum):
    STUDENT = "STUDENT"
    RABBI = "RABBI"
    TEACHER = "TEACHER"
    BEIT_DIN = "BEIT_DIN"
    ADMIN = "ADMIN"

class AttendanceType(str, Enum):
    LIVE = "LIVE"
    RECORDED = "RECORDED"

class CaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"

class EventType(str, Enum):
    RETREAT = "RETREAT"
    SHABBATON = "SHABBATON"
    HOLIDAY = "HOLIDAY"
    CLASS = "CLASS"
    OTHER = "OTHER"

class FieldType(str, Enum):
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    SELECT = "SELECT"
    RATING = "RATING"
```

### 2.3 Unique Constraints

| Table                  | Columns              | Constraint Name    |
|------------------------|----------------------|--------------------|
| `video_progress`       | (user_id, video_id)  | `uq_user_video`   |
| `event_registrations`  | (event_id, user_id)  | `uq_event_user`   |

### 2.4 Indexes

- `users.firebase_uid` — unique index
- `users.email` — unique index
- `users.mentor_id` — index (self-referential FK to `users.id`)
- `video_progress.user_id` — index
- `video_progress.video_id` — index
- `beit_din_cases.student_id` — index
- `monthly_questionnaires.(is_active, year, month)` — compound index
- `questionnaire_responses.(questionnaire_id, user_id)` — compound index

### 2.5 Relationship Loading

All parent→child relationships use `lazy="selectin"` for eager loading within async sessions:
- Program → Semester → Subject → Video
- Quiz → Question
- QuizAttempt → Answer
- Case → CaseNote, CaseDocument
- MonthlyQuestionnaire → QuestionnaireField
- Event → EventRegistration
- User → User (self-referential: `mentor` ↔ `students` via `mentor_id`)

### 2.6 Mixins

```python
class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

class TimestampMixin:
    created_at: Mapped[datetime]  # server_default=func.now()
    updated_at: Mapped[datetime]  # server_default=func.now(), onupdate=func.now()
```

All models use both mixins.

---

## 3. API Reference

### 3.1 Health

#### `GET /health`
- **Auth**: None
- **Response**: `{"status": "healthy"}`

### 3.2 Auth

#### `POST /auth/register`
- **Auth**: None
- **Request Body**:
  ```json
  {
    "firebase_uid": "abc123",
    "email": "user@example.com",
    "display_name": "John Doe"
  }
  ```
- **Response** (201): UserResponse
- **Errors**: 409 if user already exists

### 3.3 Users

#### `GET /users/me`
- **Auth**: Bearer token
- **Response**: UserResponse

#### `PATCH /users/me`
- **Auth**: Bearer token
- **Request Body**:
  ```json
  {
    "display_name": "New Name",
    "hebrew_name": "Yochanan"
  }
  ```
- **Response**: UserResponse

### 3.4 Curriculum

#### `GET /curriculum/programs`
- **Response**: ProgramResponse[] (includes nested semesters, subjects, videos)

#### `GET /curriculum/semesters/{semester_id}`
- **Response**: SemesterResponse (includes subjects and videos)

#### `GET /curriculum/subjects/{subject_id}`
- **Response**: SubjectResponse (includes videos)

#### `GET /curriculum/videos/{video_id}`
- **Response**: VideoResponse

### 3.5 Video Progress

#### `POST /progress/sync-progress`
- **Auth**: Bearer token
- **Request Body**:
  ```json
  {
    "video_id": "uuid",
    "last_position_seconds": 120,
    "total_duration_seconds": 2700,
    "attendance_type": "RECORDED"
  }
  ```
- **Response**: SyncProgressResponse
- **Logic**: Updates position, checks 95% completion, enforces no-downgrade on attendance type

#### `GET /progress/video-state/{video_id}`
- **Auth**: Bearer token
- **Response**: VideoStateResponse
- **Errors**: 404 if no progress record exists

### 3.6 Assessments

#### `GET /quizzes/{quiz_id}`
- **Auth**: Bearer token
- **Response**: QuizResponse (includes questions with options, but not correct answers exposed in the response schema — the `correct_option` field is excluded from `QuestionResponse`)

#### `POST /quizzes/{quiz_id}/submit`
- **Auth**: Bearer token
- **Request Body**:
  ```json
  {
    "answers": [
      {"question_id": "uuid", "selected_option": "A"},
      {"question_id": "uuid", "selected_option": "C"}
    ]
  }
  ```
- **Response** (201): QuizAttemptResponse (`score`, `total_questions`, `passed`)

### 3.7 Dashboard

#### `GET /dashboard`
- **Auth**: Bearer token
- **Response**: DashboardResponse
  ```json
  {
    "user_id": "uuid",
    "display_name": "...",
    "enrollment_semester": 1,
    "overall_completion_pct": 45.5,
    "semesters": [
      {
        "semester_id": "uuid",
        "semester_name": "Foundations of Judaism",
        "semester_number": 1,
        "subjects": [
          {
            "subject_id": "uuid",
            "subject_name": "Jewish Beliefs/Values",
            "videos_completed": 1,
            "videos_total": 1
          }
        ]
      }
    ],
    "recent_quiz_scores": [
      {"quiz_id": "uuid", "quiz_title": "", "score": 80, "total_questions": 5, "passed": true}
    ]
  }
  ```

#### `GET /dashboard/student/{student_id}`
- **Auth**: Bearer token (RABBI, TEACHER, ADMIN, or BEIT_DIN)
- **Authorization**: Rabbis and Teachers can only view their own assigned students (`student.mentor_id == current_user.id`). Admins and Beit Din can view any student.
- **Response**: Same as above, for the specified student

### 3.8 Rabbi Portal

#### `GET /rabbi/students`
- **Auth**: RABBI or ADMIN
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100)
- **Response**: UserResponse[] (active students only)

#### `GET /rabbi/students/{student_id}/progress`
- **Auth**: RABBI or ADMIN
- **Response**: DashboardResponse

### 3.9 Teacher Portal

#### `GET /teacher/students`
- **Auth**: TEACHER or ADMIN
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100)
- **Response**: UserResponse[]

#### `GET /teacher/activity`
- **Auth**: TEACHER or ADMIN
- **Response**: JSON array of recent video progress entries (last 50)

### 3.10 Beit Din

#### `GET /beit-din/cases`
- **Auth**: RABBI, BEIT_DIN, or ADMIN
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100)
- **Response**: CaseResponse[]

#### `POST /beit-din/cases`
- **Auth**: RABBI, BEIT_DIN, or ADMIN
- **Request Body**:
  ```json
  {
    "student_id": "uuid",
    "title": "Conversion Case - John Doe",
    "description": "..."
  }
  ```
- **Response** (201): CaseResponse

#### `GET /beit-din/cases/{case_id}`
- **Auth**: RABBI, BEIT_DIN, or ADMIN
- **Response**: CaseResponse (includes notes and documents)

#### `PATCH /beit-din/cases/{case_id}`
- **Auth**: RABBI, BEIT_DIN, or ADMIN
- **Request Body**:
  ```json
  {
    "status": "IN_REVIEW",
    "title": "Updated title",
    "description": "Updated description"
  }
  ```
- **Response**: CaseResponse

#### `POST /beit-din/cases/{case_id}/notes`
- **Auth**: RABBI, BEIT_DIN, or ADMIN
- **Request Body**: `{"content": "Meeting notes..."}`
- **Response** (201): CaseNoteResponse

### 3.11 Questionnaires

#### `GET /questionnaires/current`
- **Auth**: Bearer token
- **Response**: QuestionnaireResponse | null

#### `POST /questionnaires/{questionnaire_id}/submit`
- **Auth**: Bearer token
- **Request Body**: `{"answers": {"field-uuid": "answer text"}}`
- **Response** (201): QuestionnaireSubmitResponse

#### `POST /questionnaires/dispatch?questionnaire_id={uuid}`
- **Auth**: ADMIN
- **Response**: `{"dispatched_to": 15, "questionnaire_id": "uuid"}`
- **Side Effect**: Creates a Cloud Tasks task for each active student

### 3.12 Resources

#### `GET /resources`
- **Auth**: Bearer token
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100)
- **Response**: ResourceResponse[]

#### `GET /resources/{resource_id}/download`
- **Auth**: Bearer token
- **Response**: `{"download_url": "https://storage.googleapis.com/..."}`

### 3.13 Events

#### `GET /events`
- **Auth**: Bearer token
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100)
- **Response**: EventResponse[] (includes `registered_count`)

#### `POST /events/{event_id}/register`
- **Auth**: Bearer token
- **Response** (201): EventRegistrationResponse
- **Side Effect**: Creates Google Calendar event (non-blocking — failure is logged, registration succeeds)
- **Concurrency**: Uses `SELECT FOR UPDATE` row lock on event to prevent race conditions on capacity check
- **Errors**: 400 if event is full or already registered

#### `DELETE /events/{event_id}/register`
- **Auth**: Bearer token
- **Response**: 204 No Content
- **Errors**: 404 if not registered

### 3.14 FAQ

#### `GET /faq`
- **Auth**: None (public)
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100)
- **Response**: FAQResponse[] (published only, ordered)

#### `POST /faq`
- **Auth**: ADMIN
- **Request Body**: `{"question": "...", "answer": "...", "order": 1}`
- **Response** (201): FAQResponse

#### `PATCH /faq/{faq_id}`
- **Auth**: ADMIN
- **Request Body**: `{"question": "...", "answer": "...", "order": 2, "is_published": false}`
- **Response**: FAQResponse

### 3.15 Admin (`/admin`)

#### `GET /admin/stats`
- **Auth**: ADMIN
- **Response**: `{"total_users": 50, "active_students": 35, "total_rabbis": 5, "total_teachers": 3}`

#### `GET /admin/users`
- **Auth**: ADMIN
- **Query Params**: `skip` (default 0), `limit` (default 50, max 100), `role` (optional filter)
- **Response**: UserResponse[]

#### `PATCH /admin/users/{user_id}`
- **Auth**: ADMIN
- **Request Body**: `{"role": "TEACHER", "is_active": true, "enrollment_semester": 3}`
- **Response**: UserResponse

#### `POST /admin/users/{user_id}/deactivate`
- **Auth**: ADMIN
- **Response**: UserResponse (with `is_active: false`)

### 3.16 Export (`/export`)

#### `GET /export/progress.csv`
- **Auth**: ADMIN
- **Response**: CSV file (Content-Disposition: attachment)
- **Columns**: user_id, video_id, last_position_seconds, total_duration_seconds, is_completed, attendance_type, created_at

#### `GET /export/users.csv`
- **Auth**: ADMIN
- **Response**: CSV file
- **Columns**: id, email, display_name, role, is_active, enrollment_semester, created_at

#### `GET /export/questionnaire-responses.csv`
- **Auth**: ADMIN
- **Response**: CSV file
- **Columns**: id, questionnaire_id, user_id, answers, created_at

### 3.17 Web UI Pages (`/pages`)

Server-rendered HTML pages using Jinja2 templates with HMAC-signed session cookies and CSRF protection.

#### `GET /pages/login`
- Renders login form (email/password + Google sign-in placeholder) with CSRF token

#### `POST /pages/login`
- Validates CSRF token, authenticates user (generic "Invalid email or password" error to prevent enumeration)
- Creates session cookie (httponly, SameSite=Lax)
- **Redirect**: RABBI/TEACHER/ADMIN → `/pages/mentor-dashboard`; STUDENT → `/pages/dashboard`

#### `GET /pages/register` / `POST /pages/register`
- Registration form with CSRF token; validates display name (1-100 chars), email format, password length (8+)
- Creates user with scrypt-hashed password (`local:salt:hash` in `firebase_uid`)
- Auto-assigns new students to first available RABBI mentor
- Auto-login after registration → redirect to dashboard

#### `GET /pages/dashboard`
- **Auth**: Session cookie (STUDENT view)
- Shows: completion stats, progress bar, curriculum listing by semester

#### `GET /pages/mentor-dashboard`
- **Auth**: Session cookie (RABBI, TEACHER, or ADMIN only)
- Shows: assigned student count, average progress, total videos completed
- Lists each assigned student with name, email, semester, mini progress bar, "View" link

#### `GET /pages/mentor/student/{student_id}`
- **Auth**: Session cookie (mentor must own this student)
- Shows: student header (name, email, semester, join date)
- 4 stat cards: completed, in progress, total videos, live sessions
- Per-semester breakdown with colored dots per video (green=done, yellow=in progress, grey=not started)
- Recent activity feed with LIVE/RECORDED badges and dates

#### `GET /pages/logout`
- Clears session cookie and redirects to login

---

## 4. Services

### 4.1 Progress Service (`app/services/progress_service.py`)

**`sync_progress(db, user_id, video_id, last_position_seconds, total_duration_seconds, attendance_type)`**
- Creates or updates a VideoProgress record
- Sets `is_completed = True` when position >= 95% of duration
- Enforces no-downgrade: if attendance is already LIVE, ignores RECORDED updates
- Returns: VideoProgress

**`get_video_state(db, user_id, video_id)`**
- Retrieves the saved progress for resume capability
- Returns: VideoProgress | None

### 4.2 Assessment Service (`app/services/assessment_service.py`)

**`get_quiz(db, quiz_id)`**
- Fetches quiz with eager-loaded questions
- Returns: Quiz | None

**`grade_quiz(db, quiz_id, user_id, submissions)`**
- Creates QuizAttempt and Answer records
- Calculates percentage score
- Sets `passed = True` if score >= quiz.passing_score
- Returns: QuizAttempt

### 4.3 Beit Din Service (`app/services/beit_din_service.py`)

**`create_case(db, student_id, title, description, rabbi_id)`**
- Creates a new case with OPEN status
- Returns: Case

**`update_case_status(db, case_id, status, title, description)`**
- Updates any combination of status/title/description
- Returns: Case | None

**`add_note(db, case_id, author_id, content)`**
- Adds a timestamped note to a case
- Returns: CaseNote

### 4.4 Event Service (`app/services/event_service.py`)

**`register_for_event(db, event_id, user)`**
- Uses `SELECT FOR UPDATE` to lock event row (prevents race conditions on capacity)
- Checks capacity (if > 0)
- Prevents duplicate registration
- Flushes registration, then attempts Google Calendar event creation (non-blocking — failure is logged but does not rollback)
- Returns: EventRegistration

**`unregister_from_event(db, event_id, user_id)`**
- Removes registration
- Returns: bool

### 4.5 Cloud Tasks Service (`app/services/cloud_tasks_service.py`)

**`dispatch_questionnaire(db, questionnaire_id)`**
- Queries all active students
- Creates a Cloud Tasks task for each student
- Returns: int (count dispatched)

### 4.6 Email Service (`app/services/email_service.py`)

Provides async function stubs for integration with an email provider:
- `send_welcome_email(email, display_name)`
- `send_questionnaire_reminder(email, questionnaire_title)`
- `send_event_confirmation(email, event_title, event_date)`
- `send_beit_din_update(email, case_title, new_status)`

Currently logs to the Python logger. Replace with SendGrid/Mailgun/Gmail API in production.

### 4.7 Resource Service (`app/services/resource_service.py`)

**`get_download_url(gcs_path)`**
- Generates a signed GCS URL for resource download

---

## 5. Authentication & Authorization

### 5.1 Token Flow

1. Client obtains a Firebase ID token (via Firebase Auth SDK)
2. Client sends `Authorization: Bearer <token>` header
3. `get_current_user()` dependency:
   - Extracts token from header
   - Calls `verify_token()` → Firebase Admin SDK verification
   - Looks up User by `firebase_uid` in local database
   - Returns User object or raises 401/403

### 5.2 Dev Mode Auth

When `FIREBASE_CREDENTIALS_PATH` is empty:
- `verify_token(token)` returns `{"uid": token, "email": f"{token}@dev.local"}`
- Any string can be used as the Bearer token — it becomes the `firebase_uid`

### 5.3 Role Enforcement

```python
from app.auth.middleware import require_roles
from app.models.user import UserRole

# In a router:
@router.get("/admin-only")
async def admin_endpoint(
    user: User = Depends(require_roles(UserRole.ADMIN))
):
    ...
```

`require_roles()` is a dependency factory that returns a FastAPI dependency. It internally depends on `get_current_user()`, then checks the user's role. Returns 403 if the role doesn't match.

---

## 6. GCP Integration

### 6.1 Cloud Storage (`app/gcp/storage.py`)

- `generate_signed_url(bucket, blob_path, expiration_minutes=60)` — V4 signed URL
- `get_video_url(gcs_path)` — shortcut for video bucket
- `get_resource_url(gcs_path)` — shortcut for resource bucket
- **Dev mode**: Returns placeholder URL `https://storage.googleapis.com/{bucket}/{path}?dev=true`
- **Error handling**: All GCP calls wrapped in try/except with `logger.exception()` — errors are logged and re-raised

### 6.2 Cloud Tasks (`app/gcp/cloud_tasks.py`)

- `create_task(url, payload, delay_seconds=0)` — creates an HTTP POST task
- **Dev mode**: Returns `f"dev-task-{url}"` without making any API call
- **Error handling**: Logs and re-raises on failure

### 6.3 Calendar Sync (`app/gcp/calendar_sync.py`)

- `create_calendar_event(title, description, start_time, end_time, location, attendee_email)` — creates a Google Calendar event via service account
- **Dev mode**: Returns `f"dev-calendar-event-{title}"`
- **Error handling**: Logs and re-raises on failure. Event registration catches this exception to avoid blocking the registration.

---

## 7. Testing

### 7.1 Test Infrastructure

- **Database**: SQLite via aiosqlite (`sqlite+aiosqlite:///./test.db`)
- **Fixtures** (`tests/conftest.py`):
  - `setup_database` — auto-creates/drops all tables per test (autouse)
  - `db` — async session
  - `student_user`, `rabbi_user`, `teacher_user`, `beit_din_user`, `admin_user` — pre-created users with specific roles
  - `client` — httpx AsyncClient with student user, dependencies overridden
  - `make_client` — factory to create client with any user
- **Factories** (`tests/factories.py`): `make_user`, `make_program`, `make_semester`, `make_subject`, `make_video`, `make_quiz`, `make_question`, `make_event`, `make_case`, `make_questionnaire`, `make_resource`, `make_faq`
- **Dependency overrides**: `_override_deps(app, db_session, user)` replaces `get_db` and `get_current_user` for test isolation

### 7.2 Test Inventory

#### Unit Tests (`tests/unit/test_tracking.py`)

| Test | What it verifies |
|------|-----------------|
| `test_progress_save` | Position updates correctly; 95% threshold triggers `is_completed = True` |
| `test_resume_logic` | `get_video_state()` returns saved position; updates reflect correctly |
| `test_attendance_differentiation` | RECORDED→LIVE upgrade works; LIVE→RECORDED downgrade is blocked |

#### Integration Tests (`tests/integration/test_portals.py`)

| Test | What it verifies |
|------|-----------------|
| `test_biet_din_access` | Student gets 403 on `/beit-din/cases`; Rabbi gets 200 |
| `test_monthly_questionnaire_dispatch` | Cloud Tasks `create_task` is called for each active student |
| `test_retreat_signup_calendar` | Event registration calls `create_calendar_event` with correct title |

#### Router Tests (`tests/routers/`)

| File | Tests | Coverage |
|------|-------|----------|
| `test_health.py` | 1 | Health endpoint |
| `test_users.py` | 2 | Profile read/update |
| `test_curriculum.py` | 4 | Programs, semesters, subjects, videos (including 404s) |
| `test_video_progress.py` | 5 | Sync, completion, resume, validation |
| `test_assessments.py` | 6 | Quiz get, submit (correct/partial/failing), 404, validation |
| `test_events.py` | 5 | List, register, unregister, capacity, duplicate |
| `test_beit_din.py` | 6 | Cases CRUD, notes, access control |
| `test_questionnaires.py` | 5 | Current, submit, dispatch, 404, access control |
| `test_resources.py` | 3 | List, download, 404 |
| `test_faq.py` | 5 | List (published filter), create, update, 404, access control |
| `test_dashboard.py` | 3 | Own dashboard, rabbi view (mentor auth), student forbidden |
| `test_rabbi_teacher.py` | 5 | Student list, access control, teacher activity |
| `test_admin.py` | 7 | Stats, list users, filter by role, update, deactivate, 403, 404 |
| `test_export.py` | 4 | CSV progress, users, questionnaires, 403 |

### 7.3 Running Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific test
pytest tests/unit/test_tracking.py::test_progress_save -v

# With print output
pytest -s
```

---

## 8. Development Guide

### 8.1 Adding a New Router

1. Create `app/routers/new_feature.py` with an `APIRouter`
2. Import and register in `app/main.py`:
   ```python
   from app.routers import new_feature
   app.include_router(new_feature.router)
   ```

### 8.2 Adding a New Model

1. Create `app/models/new_model.py` inheriting from `Base`, `UUIDPrimaryKeyMixin`, `TimestampMixin`
2. Import in `app/models/__init__.py` so Alembic detects it
3. Generate migration: `alembic revision --autogenerate -m "Add new_model table"`
4. Apply: `alembic upgrade head`

### 8.3 Adding a New Service

1. Create `app/services/new_service.py`
2. Accept `db: AsyncSession` as first parameter
3. Import and call from routers — do not import routers from services

### 8.4 Adding Tests

1. Add test functions to appropriate file in `tests/unit/` or `tests/integration/`
2. Use fixtures from `conftest.py` (e.g., `db`, `student_user`, `client`)
3. For integration tests that need HTTP, use `_override_deps()` pattern

### 8.5 Database Migrations

```bash
# Generate a migration after model changes
alembic revision --autogenerate -m "Description of change"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 9. File Reference

### Core Application

| File | Purpose |
|------|---------|
| `app/main.py` | App factory, CORS, security headers, logging middleware, 17 router registrations |
| `app/config.py` | Pydantic Settings |
| `app/dependencies.py` | `get_db`, `get_current_user` |

### Auth

| File | Purpose |
|------|---------|
| `app/auth/firebase.py` | Firebase init, `verify_token()` |
| `app/auth/middleware.py` | `require_roles()` dependency factory |

### Models (16 model classes)

| File | Models | Table(s) |
|------|--------|----------|
| `app/models/base.py` | Base, UUIDPrimaryKeyMixin, TimestampMixin | — |
| `app/models/user.py` | User, UserRole | `users` (self-ref `mentor_id` FK) |
| `app/models/curriculum.py` | Program, Semester, Subject, Video | `programs`, `semesters`, `subjects`, `videos` |
| `app/models/progress.py` | VideoProgress, AttendanceType | `video_progress` |
| `app/models/assessment.py` | Quiz, Question, QuizAttempt, Answer | `quizzes`, `questions`, `quiz_attempts`, `answers` |
| `app/models/beit_din.py` | Case, CaseNote, CaseDocument, CaseStatus | `beit_din_cases`, `case_notes`, `case_documents` |
| `app/models/questionnaire.py` | MonthlyQuestionnaire, QuestionnaireField, QuestionnaireResponse | `monthly_questionnaires`, `questionnaire_fields`, `questionnaire_responses` |
| `app/models/resource.py` | Resource, FAQ | `resources`, `faqs` |
| `app/models/event.py` | Event, EventRegistration, EventType | `events`, `event_registrations` |

### Schemas (27 Pydantic models)

| File | Schemas |
|------|---------|
| `app/schemas/user.py` | RegisterRequest, UserResponse, UserUpdate |
| `app/schemas/curriculum.py` | VideoResponse, SubjectResponse, SemesterResponse, ProgramResponse |
| `app/schemas/progress.py` | SyncProgressRequest, SyncProgressResponse, VideoStateResponse |
| `app/schemas/assessment.py` | QuestionResponse, QuizResponse, AnswerSubmission, QuizSubmitRequest, QuizAttemptResponse |
| `app/schemas/dashboard.py` | VideoProgressSummary, SubjectProgressSummary, SemesterProgressSummary, DashboardResponse, QuizScoreSummary |
| `app/schemas/beit_din.py` | CaseCreateRequest, CaseUpdateRequest, CaseNoteCreate, CaseNoteResponse, CaseDocumentResponse, CaseResponse |
| `app/schemas/questionnaire.py` | QuestionnaireFieldResponse, QuestionnaireResponse, QuestionnaireSubmitRequest, QuestionnaireSubmitResponse, DispatchResponse |
| `app/schemas/resource.py` | ResourceResponse, ResourceDownloadResponse |
| `app/schemas/event.py` | EventResponse, EventRegistrationResponse |

### Routers (17 routers, 50+ endpoints)

| File | Prefix | Endpoints |
|------|--------|-----------|
| `app/routers/health.py` | `/` | GET /health |
| `app/routers/auth_routes.py` | `/auth` | POST /register |
| `app/routers/users.py` | `/users` | GET /me, PATCH /me |
| `app/routers/curriculum.py` | `/curriculum` | GET /programs, /semesters/{id}, /subjects/{id}, /videos/{id} |
| `app/routers/video_progress.py` | `/progress` | POST /sync-progress, GET /video-state/{id} |
| `app/routers/assessments.py` | `/quizzes` | GET /{id}, POST /{id}/submit (201) |
| `app/routers/dashboard.py` | `/dashboard` | GET /, GET /student/{id} (mentor auth) |
| `app/routers/rabbi.py` | `/rabbi` | GET /students (paginated), GET /students/{id}/progress |
| `app/routers/teacher.py` | `/teacher` | GET /students (paginated), GET /activity |
| `app/routers/beit_din.py` | `/beit-din` | GET /cases (paginated), POST /cases, GET /cases/{id}, PATCH /cases/{id}, POST /cases/{id}/notes |
| `app/routers/questionnaires.py` | `/questionnaires` | GET /current, POST /{id}/submit (201), POST /dispatch |
| `app/routers/resources.py` | `/resources` | GET / (paginated), GET /{id}/download |
| `app/routers/events.py` | `/events` | GET / (paginated), POST /{id}/register (row lock), DELETE /{id}/register |
| `app/routers/faq.py` | `/faq` | GET / (paginated), POST /, PATCH /{id} |
| `app/routers/admin.py` | `/admin` | GET /stats, GET /users (paginated), PATCH /users/{id}, POST /users/{id}/deactivate |
| `app/routers/export.py` | `/export` | GET /progress.csv, GET /users.csv, GET /questionnaire-responses.csv |
| `app/routers/pages.py` | `/pages` | GET/POST /login (CSRF), GET/POST /register (CSRF), GET /dashboard, GET /mentor-dashboard, GET /mentor/student/{id}, GET /logout |

### Services (12 functions)

| File | Functions |
|------|-----------|
| `app/services/progress_service.py` | `sync_progress`, `get_video_state` |
| `app/services/assessment_service.py` | `get_quiz`, `grade_quiz` |
| `app/services/beit_din_service.py` | `create_case`, `update_case_status`, `add_note` |
| `app/services/event_service.py` | `register_for_event` (with row lock + non-blocking calendar), `unregister_from_event` |
| `app/services/cloud_tasks_service.py` | `dispatch_questionnaire` |
| `app/services/resource_service.py` | `get_download_url` |
| `app/services/email_service.py` | `send_welcome_email`, `send_questionnaire_reminder`, `send_event_confirmation`, `send_beit_din_update` |

### GCP Wrappers (all with error logging)

| File | Functions |
|------|-----------|
| `app/gcp/storage.py` | `generate_signed_url`, `get_video_url`, `get_resource_url` |
| `app/gcp/cloud_tasks.py` | `create_task` |
| `app/gcp/calendar_sync.py` | `create_calendar_event` |

### Templates (Jinja2)

| File | Description |
|------|-------------|
| `app/templates/base.html` | Shared layout with Torah scroll SVG logo, warm parchment styling |
| `app/templates/login.html` | Email/password form + Google sign-in button |
| `app/templates/register.html` | Registration form with password confirmation |
| `app/templates/dashboard.html` | Student dashboard: stats grid, progress bar, curriculum |
| `app/templates/mentor_dashboard.html` | Mentor view: assigned students list with progress bars |
| `app/templates/mentor_student_detail.html` | Deep student view: per-semester/subject/video dots, activity feed |

### Seed Scripts

| File | Description |
|------|-------------|
| `scripts/seed_curriculum.py` | Idempotent: loads 8 semesters x 5 subjects with sample 45-min videos (skips if already seeded) |
| `scripts/seed_mentor.py` | Creates 2 mentor accounts, 10 synthetic students, assigns to mentors, generates progress data |

### Tests (74 tests)

| File | Tests | Description |
|------|-------|-------------|
| `tests/conftest.py` | — | 9 fixtures + `_override_deps` helper |
| `tests/factories.py` | — | 12 factory functions |
| `tests/unit/test_tracking.py` | 3 | Progress save, resume, attendance differentiation |
| `tests/integration/test_portals.py` | 3 | Beit din access, questionnaire dispatch, calendar sync |
| `tests/routers/test_health.py` | 1 | Health endpoint |
| `tests/routers/test_users.py` | 2 | Profile read/update |
| `tests/routers/test_curriculum.py` | 4 | Curriculum CRUD + 404s |
| `tests/routers/test_video_progress.py` | 5 | Sync, completion, resume, validation |
| `tests/routers/test_assessments.py` | 6 | Quiz get/submit/validation |
| `tests/routers/test_events.py` | 5 | Event registration lifecycle |
| `tests/routers/test_beit_din.py` | 6 | Cases CRUD + notes + access |
| `tests/routers/test_questionnaires.py` | 5 | Questionnaire lifecycle + access |
| `tests/routers/test_resources.py` | 3 | List, download, 404 |
| `tests/routers/test_faq.py` | 5 | FAQ CRUD + published filter + access |
| `tests/routers/test_dashboard.py` | 3 | Dashboard views + mentor auth |
| `tests/routers/test_rabbi_teacher.py` | 5 | Portal access + activity |
| `tests/routers/test_admin.py` | 7 | Stats, CRUD, filters, access |
| `tests/routers/test_export.py` | 4 | CSV exports + access |

### Migrations

| File | Description |
|------|-------------|
| `alembic/env.py` | Async Alembic env with DATABASE_URL override |
| `alembic/versions/7860d8a96b01_baseline.py` | Baseline migration: all 20 tables with indexes and constraints |
