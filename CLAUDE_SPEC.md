# Jewish Conversion Academy - Technical Specification

This technical specification defines the **Jewish Conversion Academy (JCA) platform**, a cloud-native application built with **FastAPI + PostgreSQL + GCP** services. It serves as the authoritative reference for Claude Code's Spec-Driven Development (SDD) workflow.

---

## 1. System Architecture

| Component          | Technology                                         |
|--------------------|----------------------------------------------------|
| API Framework      | FastAPI (Python 3.12+), async                       |
| Database           | PostgreSQL via SQLAlchemy 2.0 async + asyncpg       |
| Migrations         | Alembic (async)                                     |
| Object Storage     | Google Cloud Storage (GCS) — videos, PDFs           |
| Authentication     | Firebase Admin SDK (ID token verification)          |
| Task Scheduling    | Google Cloud Tasks — monthly questionnaire dispatch |
| Calendar           | Google Calendar API — event sync on registration    |
| Configuration      | Pydantic Settings, env-driven (`.env`)              |

### Layered Architecture

```
Routers (HTTP) → Services (Business Logic) → Models (Data)
                                            → GCP Wrappers
```

- **Routers** are thin — parse requests, call services, return responses.
- **Services** contain all business logic and are independently testable.
- **Models** are SQLAlchemy 2.0 declarative with UUID primary keys and timestamp mixins.
- **GCP wrappers** isolate cloud SDK calls and return dev-mode stubs when credentials are absent.

---

## 2. Data Model

### 2.1 User Domain

**User** (`users`)
- `id` UUID PK, `firebase_uid` (unique, indexed), `email` (unique, indexed)
- `display_name`, `hebrew_name` (nullable)
- `role` enum: **STUDENT | RABBI | TEACHER | BEIT_DIN | ADMIN**
- `enrollment_semester` (int), `program_year` (int, for 2nd-year/graduate gating)
- `is_active` (bool)
- `mentor_id` UUID FK → `users.id` (nullable, indexed) — self-referential; links a student to their assigned mentor (RABBI/TEACHER)
- Relationships: `mentor` (many-to-one), `students` (one-to-many) via `mentor_id`

### 2.2 Curriculum Domain

**Program** → **Semester** → **Subject** → **Video**

- Program has `year` field (1 = standard, 2 = advanced/graduate)
- Semester has `number` (1–8) and `name`
- Subject has `order` within its semester
- Video has `gcs_path`, `duration_seconds`, `order`
- Standard curriculum: 8 semesters × 5 subjects = 40 subjects, 40+ videos

### 2.3 Progress Domain

**VideoProgress** (`video_progress`)
- Unique constraint: `(user_id, video_id)`
- `last_position_seconds`, `total_duration_seconds`
- `is_completed` (bool), `attendance_type` enum: **LIVE | RECORDED**

### 2.4 Assessment Domain

**Quiz** → **Question** (multiple choice A/B/C/D)
**QuizAttempt** → **Answer**

- Quiz linked to Video, has `passing_score` (default 70%)
- QuizAttempt stores `score` (percentage), `passed` (bool)

### 2.5 Beit Din Domain

**Case** → **CaseNote**, **CaseDocument**

- Case status workflow: `OPEN → IN_REVIEW → SCHEDULED → COMPLETED`
- Case linked to student and optionally to rabbi
- Documents store `gcs_path` for uploaded files

### 2.6 Questionnaire Domain

**MonthlyQuestionnaire** → **QuestionnaireField**
**QuestionnaireResponse**

- Field types: TEXT, TEXTAREA, SELECT, RATING
- Responses stored as JSON string

### 2.7 Resource & Event Domain

**Resource** — downloadable PDFs via signed GCS URLs
**FAQ** — public Q&A with `is_published` flag and `order`
**Event** → **EventRegistration**

- Event types: RETREAT, SHABBATON, HOLIDAY, CLASS, OTHER
- Capacity enforcement, duplicate registration prevention
- Registration triggers Google Calendar event creation

---

## 3. Video Tracking Logic

The core feature uses a heartbeat mechanism for YouTube-style video progress tracking.

### 3.1 Client-Side Heartbeat

The frontend sends `POST /progress/sync-progress` every 10 seconds with:
```json
{
  "video_id": "uuid",
  "last_position_seconds": 120,
  "total_duration_seconds": 2700,
  "attendance_type": "RECORDED"
}
```

### 3.2 Resume Capability

When a student opens a video, the frontend calls `GET /progress/video-state/{video_id}` to retrieve `last_position_seconds` and seek to that position.

### 3.3 Completion Trigger

When `last_position_seconds >= total_duration_seconds * 0.95`, the video is marked `is_completed = True`. This unlocks post-video quizzes.

### 3.4 Attendance No-Downgrade Rule

Once `attendance_type` is set to `LIVE`, it **cannot** be overwritten by `RECORDED`. This ensures students who attend live sessions retain credit even if they later watch the recording.

---

## 4. Role-Based Access Control

| Role       | Access                                                              |
|------------|---------------------------------------------------------------------|
| STUDENT    | Own dashboard, curriculum, progress, quizzes, events, resources     |
| RABBI      | All student access + student list, progress views, Beit Din cases   |
| TEACHER    | All student access + student list, activity feed                    |
| BEIT_DIN   | Beit Din case management                                           |
| ADMIN      | Everything + user management, data export, FAQ management, questionnaire dispatch |

Enforced via `require_roles()` FastAPI dependency factory in `app/auth/middleware.py`.

---

## 5. API Endpoints

### Public
| Method | Path            | Description          |
|--------|-----------------|----------------------|
| GET    | `/health`       | Health check         |
| GET    | `/faq`          | Published FAQ list   |

### Auth (no role required)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | `/auth/register`                  | Create user account            |
| GET    | `/users/me`                       | Current user profile           |
| PATCH  | `/users/me`                       | Update profile                 |

### Curriculum (authenticated)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/curriculum/programs`            | All programs with semesters    |
| GET    | `/curriculum/semesters/{id}`      | Semester detail                |
| GET    | `/curriculum/subjects/{id}`       | Subject detail                 |
| GET    | `/curriculum/videos/{id}`         | Video detail                   |

### Progress (authenticated)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | `/progress/sync-progress`         | Heartbeat sync                 |
| GET    | `/progress/video-state/{id}`      | Resume state                   |

### Assessments (authenticated)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/quizzes/{id}`                   | Quiz with questions            |
| POST   | `/quizzes/{id}/submit`            | Submit and grade               |

### Dashboard (authenticated)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/dashboard`                      | Own progress dashboard         |
| GET    | `/dashboard/student/{id}`         | Student dashboard (staff only) |

### Rabbi Portal (RABBI/ADMIN)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/rabbi/students`                 | All active students            |
| GET    | `/rabbi/students/{id}/progress`   | Student progress dashboard     |

### Teacher Portal (TEACHER/ADMIN)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/teacher/students`               | All active students            |
| GET    | `/teacher/activity`               | Recent video activity          |

### Beit Din (RABBI/BEIT_DIN/ADMIN)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/beit-din/cases`                 | All cases                      |
| POST   | `/beit-din/cases`                 | Create case                    |
| GET    | `/beit-din/cases/{id}`            | Case detail                    |
| PATCH  | `/beit-din/cases/{id}`            | Update case                    |
| POST   | `/beit-din/cases/{id}/notes`      | Add case note                  |

### Questionnaires
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/questionnaires/current`         | Active questionnaire (auth)    |
| POST   | `/questionnaires/{id}/submit`     | Submit response (auth)         |
| POST   | `/questionnaires/dispatch`        | Dispatch via Cloud Tasks (ADMIN) |

### Resources (authenticated)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/resources`                      | All resources                  |
| GET    | `/resources/{id}/download`        | Signed download URL            |

### Events (authenticated)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/events`                         | All events                     |
| POST   | `/events/{id}/register`           | Register for event             |
| DELETE | `/events/{id}/register`           | Unregister                     |

### FAQ (ADMIN for write)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | `/faq`                            | Create FAQ (ADMIN)             |
| PATCH  | `/faq/{id}`                       | Update FAQ (ADMIN)             |

### Admin (ADMIN)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/admin/stats`                    | Platform statistics            |
| GET    | `/admin/users`                    | List users (filterable by role, paginated) |
| PATCH  | `/admin/users/{id}`               | Update user role/status        |
| POST   | `/admin/users/{id}/deactivate`    | Deactivate user                |

### Export (ADMIN)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/export/progress.csv`            | CSV export of all progress     |
| GET    | `/export/users.csv`               | CSV export of all users        |
| GET    | `/export/questionnaire-responses.csv` | CSV export of responses    |

### Web UI Pages (session-cookie auth)
| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET/POST | `/pages/login`                 | Login form; redirects by role  |
| GET/POST | `/pages/register`              | Registration; auto-assigns mentor |
| GET    | `/pages/dashboard`                | Student dashboard              |
| GET    | `/pages/mentor-dashboard`         | Mentor view of assigned students |
| GET    | `/pages/mentor/student/{id}`      | Deep student progress view     |
| GET    | `/pages/logout`                   | Clear session, redirect to login |

---

## 6. Test-Driven Development Spec

### Unit Tests (`tests/unit/test_tracking.py`)

| Test                             | Verifies                                                    |
|----------------------------------|-------------------------------------------------------------|
| `test_progress_save`             | `last_position_seconds` updates correctly; 95% triggers completion |
| `test_resume_logic`              | `get_video_state()` returns correct timestamp for returning user    |
| `test_attendance_differentiation`| LIVE vs RECORDED distinction; LIVE never downgraded to RECORDED     |

### Integration Tests (`tests/integration/test_portals.py`)

| Test                                  | Verifies                                                  |
|---------------------------------------|-----------------------------------------------------------|
| `test_biet_din_access`                | Students get 403; Rabbis get 200 on `/beit-din/cases`     |
| `test_monthly_questionnaire_dispatch` | Cloud Tasks called for each student on dispatch            |
| `test_retreat_signup_calendar`        | Event registration triggers `create_calendar_event()`      |

---

## 7. Feature Checklist

- [x] **Video Management:** GCS signed URLs for streaming
- [x] **Video Tracking:** Heartbeat sync, 95% completion, resume, attendance type
- [x] **Assessment Engine:** Post-video quizzes with grading, monthly questionnaires
- [x] **User Dashboards:** Progress tracking per semester/subject/video
- [x] **Role-Based Portals:** Rabbi, Teacher, Beit Din with access control
- [x] **Mentor Dashboard:** Self-referential mentor_id assignment, mentor sees only their students, per-video progress dots, activity feed
- [x] **Web UI:** Server-rendered login/register/dashboard pages with HMAC session cookies, CSRF protection, role-based redirect, auto mentor assignment
- [x] **Beit Din Case Management:** Full CRUD with notes and documents
- [x] **Resource Center:** PDF distribution via signed GCS URLs
- [x] **Event System:** Registration with SELECT FOR UPDATE locking, capacity checks, and calendar sync (non-blocking on failure)
- [x] **FAQ:** Public read (paginated), admin write
- [x] **Admin Interface:** Platform stats, user management, role assignment, deactivation
- [x] **Data Export:** CSV export for progress, users, questionnaire responses (ADMIN only)
- [x] **Email Service:** Interface for welcome, reminder, confirmation emails
- [x] **Cloud Tasks:** Monthly questionnaire dispatch scheduling
- [x] **Security Hardening:** CSRF tokens, security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy), SameSite cookies, restricted CORS, scrypt password hashing
- [x] **Pagination:** skip/limit on all list endpoints (max 100)
- [x] **Input Validation:** EmailStr, Field constraints, form validation on register
- [x] **GCP Error Handling:** try/except with logging on all GCP wrapper calls
- [x] **Alembic Migration:** Baseline migration for all 20 tables
- [x] **Idempotent Seed:** Seed scripts check for existing data before inserting
- [x] **CI Pipeline:** GitHub Actions for automated testing
