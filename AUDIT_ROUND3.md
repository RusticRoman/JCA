# JCA Platform - Audit Round 3 (2026-02-19)

Third round of comprehensive audit across security, data integrity/performance, and testing/code quality.

---

## Security (20 items)

| # | Severity | Issue | File | OWASP |
|---|----------|-------|------|-------|
| 1 | CRITICAL | Session secret regenerates on restart — all sessions invalidated; no env var override implemented despite comment saying to do so | `app/routers/pages.py:28` | A07 |
| 2 | CRITICAL | `UserResponse` schema exposes `firebase_uid` — sensitive auth identifier leaked in API responses | `app/schemas/user.py:17` | A01 |
| 3 | CRITICAL | Client-reported `total_duration_seconds` in sync-progress allows students to cheat completion by sending fake short durations | `app/schemas/progress.py:10-11` | A04 |
| 4 | CRITICAL | Cloud Tasks dispatches to `/questionnaires/{id}/notify` endpoint that does not exist | `app/services/cloud_tasks_service.py:25` | A01 |
| 5 | HIGH | Session cookie missing `secure=True` flag — vulnerable to interception over HTTP | `app/routers/pages.py:150,237` | A07 |
| 6 | HIGH | Rabbi `/rabbi/students` endpoint returns ALL active students, not just mentor-assigned ones | `app/routers/rabbi.py:14-26` | A01 |
| 7 | HIGH | Teacher `/teacher/students` endpoint returns ALL active students, not just mentor-assigned ones | `app/routers/teacher.py:14-26` | A01 |
| 8 | HIGH | Missing `Content-Security-Policy` header in security headers middleware | `app/main.py:41-48` | A03 |
| 9 | HIGH | No rate limiting on login/register — brute force / credential stuffing possible | `app/routers/pages.py` | A07 |
| 10 | HIGH | Weak password policy — only requires length >= 8, no complexity (uppercase, digit, special char) | `app/routers/pages.py:203` | A07 |
| 11 | HIGH | Weak email validation regex `^[^@]+@[^@]+\.[^@]+$` allows many invalid addresses | `app/routers/pages.py:191` | A07 |
| 12 | MEDIUM | No `Strict-Transport-Security` (HSTS) header — allows downgrade attacks in production | `app/main.py` | A02 |
| 13 | MEDIUM | Overly permissive CORS with `allow_credentials=True` — risky if origins misconfigured | `app/main.py:34-39` | A07 |
| 14 | MEDIUM | No logging of security events (login attempts, failed auth, admin actions, role changes) | app-wide | A09 |
| 15 | MEDIUM | GCP credentials path not validated on startup — silently falls back to dev mode if path wrong | `app/auth/firebase.py:13-16` | A06 |
| 16 | MEDIUM | CSV export missing proper charset in Content-Type (`text/csv; charset=utf-8`) | `app/routers/export.py` | A05 |
| 17 | MEDIUM | Pagination limit allows `limit=0` — should enforce minimum of 1 | `app/routers/admin.py:62` | A05 |
| 18 | LOW | Default database credentials hardcoded in config (`jca:jca@localhost:5432/jca`) | `app/config.py:5` | A02 |
| 19 | LOW | GCP credentials path not validated — no warning if file doesn't exist | `app/auth/firebase.py:13-16` | A06 |
| 20 | LOW | No audit logging for any security events | app-wide | A09 |

---

## Data Integrity & Performance (28 items)

| # | Severity | Issue | File |
|---|----------|-------|------|
| 21 | CRITICAL | N+1 query: curriculum hierarchy loads ALL programs/semesters/subjects/videos via selectin, ignoring user's program_year/enrollment_semester | `app/routers/dashboard.py:47-56`, `app/routers/pages.py:264-268` |
| 22 | CRITICAL | Unbounded CSV export loads ALL records into memory via `.scalars().all()` — OOM risk with large datasets | `app/routers/export.py:24-27,51-54,77-78` |
| 23 | CRITICAL | Event registration race condition: duplicate check via SELECT happens before commit, allowing two concurrent requests to both pass | `app/services/event_service.py:39-47` |
| 24 | CRITICAL | `cascade="all, delete-orphan"` on curriculum/assessment models without `ondelete="CASCADE"` on FK — app crash leaves orphaned rows | `app/models/curriculum.py:16,28,40` |
| 25 | CRITICAL | Client-reported `total_duration_seconds` bypasses 95% completion check — should use DB video duration | `app/services/progress_service.py:48` |
| 26 | HIGH | Missing FK indexes on 10+ foreign key columns: `quizzes.video_id`, `videos.subject_id`, `semesters.program_id`, `subjects.semester_id`, `quiz_attempts.quiz_id`, `event_registrations.event_id/user_id`, `questionnaire_fields.questionnaire_id`, `case_notes.case_id`, `case_documents.case_id`, `answers.attempt_id/question_id` | migration |
| 27 | HIGH | Missing CHECK constraints: `enrollment_semester` (1-8), `passing_score` (0-100), `capacity` (>= 0), `last_position_seconds` (>= 0), `score` (0-100) | migration |
| 28 | HIGH | Blocking `hashlib.scrypt()` calls in async handlers — CPU-intensive work blocks event loop | `app/routers/pages.py:78-87` |
| 29 | HIGH | No connection pool configuration — default `pool_size=5` too small for production | `app/dependencies.py:10` |
| 30 | HIGH | GCP clients (`storage.Client()`, `CloudTasksClient()`, `build("calendar",...)`) recreated on every request — no connection pooling | `app/gcp/storage.py:17-18`, `app/gcp/cloud_tasks.py:19-20`, `app/gcp/calendar_sync.py:21-29` |
| 31 | HIGH | Calendar event creation failure is logged but registration still commits — creates registrations without calendar events | `app/services/event_service.py:54-66` |
| 32 | MEDIUM | `User.students` relationship with `lazy="selectin"` causes excess queries when loading user lists | `app/models/user.py:37` |
| 33 | MEDIUM | Mentor dashboard eager loads User.mentor relationship even when not needed | `app/routers/dashboard.py:25-30` |
| 34 | MEDIUM | Quiz grading silently skips invalid question IDs with `continue` — can inflate scores | `app/services/assessment_service.py:39-41` |
| 35 | MEDIUM | Questionnaire dispatch loads ALL active students without pagination — memory spike risk | `app/services/cloud_tasks_service.py:18-21` |
| 36 | MEDIUM | Mentor dashboard queries all assigned students without pagination — performance degrades with 100+ students | `app/routers/pages.py:297-300` |
| 37 | MEDIUM | No unique constraint validation on QuizAttempt — unlimited retakes stored without ordering | `app/models/assessment.py:34-42` |
| 38 | MEDIUM | Quiz grading partial failure: attempt inserted and flushed before all answers added — crash leaves partial data | `app/services/assessment_service.py:30-60` |
| 39 | MEDIUM | CaseNote/CaseDocument ForeignKeys missing `ondelete="CASCADE"` — app crash orphans child rows | `app/models/beit_din.py:26-27` |
| 40 | LOW | Questionnaire composite index missing `created_at` for covering index optimization | migration |
| 41 | LOW | No partial index on `video_progress.is_completed` for completion queries | migration |
| 42 | LOW | Admin `/admin/stats` runs 4 separate COUNT queries instead of one aggregated query | `app/routers/admin.py:35-44` |
| 43 | LOW | FAQ list endpoint may return unbounded results | `app/routers/faq.py` |
| 44 | LOW | Resource download creates new GCS client per request (subset of #30) | `app/routers/resources.py:29-41` |
| 45 | LOW | No rate limiting on quiz submissions — DoS potential via unlimited retakes | `app/routers/assessments.py:26-42` |
| 46 | LOW | EventType enum not validated in request schemas (only at ORM level) | `app/models/event.py:24` |
| 47 | LOW | Session secret not rotatable without invalidating all sessions | `app/routers/pages.py:28-29` |
| 48 | LOW | SSRF risk in cloud_tasks URL construction — `app_base_url` not validated | `app/services/cloud_tasks_service.py:25` |

---

## Testing & Code Quality (20 items)

| # | Severity | Issue | File |
|---|----------|-------|------|
| 49 | CRITICAL | Zero tests for `pages.py` — largest file (467 lines, 8 endpoints covering login, registration, dashboards, mentor views) | missing `tests/routers/test_pages.py` |
| 50 | CRITICAL | Health check returns `{"status": "healthy"}` without verifying database connectivity | `app/routers/health.py:6-8` |
| 51 | CRITICAL | No tests for `/auth/register` endpoint (Firebase-based registration, 409 conflict detection) | missing |
| 52 | HIGH | Inline `import re` inside `register_submit()` function — violates PEP 8 | `app/routers/pages.py:174` |
| 53 | HIGH | No validation for negative pagination params (`skip=-1`, `limit=-10`) across all list endpoints | multiple routers |
| 54 | HIGH | `make_client` fixture defined in `conftest.py` but never used in any test | `tests/conftest.py:135-147` |
| 55 | HIGH | Inconsistent HTTP status codes — raw integers (`404`, `403`) mixed with constants (`status.HTTP_409_CONFLICT`) | multiple routers |
| 56 | HIGH | Silent failure on invalid quiz question IDs — `continue` instead of error | `app/services/assessment_service.py:39-41` |
| 57 | MEDIUM | CI pipeline missing linting (`ruff`/`black`) and type checking (`mypy`) | `.github/workflows/test.yml` |
| 58 | MEDIUM | Missing boundary tests for 95% completion threshold (94%, 95.0%, 0-duration edge case) | `tests/unit/test_tracking.py` |
| 59 | MEDIUM | FAQ schemas (`FAQResponse`, `FAQCreateRequest`, `FAQUpdateRequest`) defined inline in router instead of `schemas/` | `app/routers/faq.py:16-35` |
| 60 | MEDIUM | Test DB path hardcoded to `sqlite+aiosqlite:///./test.db` — not configurable for CI | `tests/conftest.py:14` |
| 61 | MEDIUM | `setup_database` fixture drops all tables after every test including on failures — hard to debug | `tests/conftest.py:20-26` |
| 62 | MEDIUM | Session secret hardcoded/regenerated — no env var override, no tests for session persistence | `app/routers/pages.py:28-30` |
| 63 | MEDIUM | Mentor dashboard + student detail compute completion without caching — N+1 and slow at scale | `app/routers/pages.py:284-458` |
| 64 | LOW | `QuizAttemptResponse` schema missing `user_id` and `created_at` fields | `app/schemas/assessment.py:38-45` |
| 65 | LOW | Missing `.env.example` entries: `SESSION_SECRET`, `LOG_LEVEL`, `APP_ENVIRONMENT` | `.env.example` |
| 66 | LOW | No cascade delete tests — unknown behavior when Semester/Subject deleted with associated progress | missing |
| 67 | LOW | Missing tests for rabbi/teacher pagination and `/rabbi/students/{id}/progress` endpoint | `tests/routers/test_rabbi_teacher.py` |
| 68 | LOW | No tests for CSRF token expiration, session expiration, or failed login tracking | missing |

---

## Summary

| Category | CRITICAL | HIGH | MEDIUM | LOW | Total |
|----------|----------|------|--------|-----|-------|
| Security | 4 | 7 | 5 | 4 | 20 |
| Data Integrity & Performance | 5 | 6 | 8 | 9 | 28 |
| Testing & Code Quality | 3 | 5 | 7 | 5 | 20 |
| **Total** | **12** | **18** | **20** | **18** | **68** |

**Note:** Some items overlap across categories (e.g., client-reported video duration appears in both Security #3 and Data Integrity #25; session secret in Security #1 and Testing #62). After deduplication, approximately **50 unique actionable items** remain.

---

## Top Priority Recommendations

1. **Session secret from env var** (#1, #62) — prevents session loss on restart
2. **Server-side video duration** (#3, #25) — prevents completion cheating
3. **Unbounded CSV export** (#22) — prevents OOM in production
4. **Rabbi/Teacher mentor filter** (#6, #7) — fixes authorization bypass
5. **Tests for pages.py** (#49) — largest file with zero coverage
6. **Health check with DB verify** (#50) — essential for production monitoring
7. **Missing FK indexes** (#26) — prevents query performance degradation
8. **Remove firebase_uid from response** (#2) — stops leaking sensitive data
