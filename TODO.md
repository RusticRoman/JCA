# JCA Platform - Outstanding TODO Items

All unaddressed improvements identified across 3 audit rounds. Organized by priority.

---

## CRITICAL

- [ ] **Session secret from env var** — `app/routers/pages.py:28` — `_SESSION_SECRET = secrets.token_bytes(32)` regenerates on every restart, invalidating all sessions. Load from `SESSION_SECRET` env var with fallback to generated value.
- [ ] **Remove firebase_uid from UserResponse** — `app/schemas/user.py:17` — Sensitive auth identifier exposed in API responses. Remove `firebase_uid` field from response schema.
- [ ] **Server-side video duration for completion check** — `app/schemas/progress.py:10-11`, `app/services/progress_service.py:48` — Client-reported `total_duration_seconds` lets students cheat completion by sending fake short durations. Fetch true duration from Video model in DB.
- [ ] **Missing /notify endpoint for questionnaire dispatch** — `app/services/cloud_tasks_service.py:25` — Cloud Tasks dispatches to `/questionnaires/{id}/notify` which does not exist. Implement the endpoint or fix the URL.
- [ ] **Unbounded CSV export — OOM risk** — `app/routers/export.py:24-27,51-54,77-78` — All three export endpoints load ALL records via `.scalars().all()`. Add streaming pagination or hard row limit.
- [ ] **N+1 curriculum query** — `app/routers/dashboard.py:47-56`, `app/routers/pages.py:264-268` — Loads ALL programs/semesters/subjects/videos via selectin regardless of user's enrollment. Filter by `program_year`/`enrollment_semester`.
- [ ] **Event registration race condition (duplicate check)** — `app/services/event_service.py:39-47` — Duplicate check via SELECT happens before commit; two concurrent requests can both pass. Use `INSERT ... ON CONFLICT DO NOTHING` or catch `IntegrityError`.
- [ ] **Cascade delete without DB-level enforcement** — `app/models/curriculum.py:16,28,40`, `app/models/assessment.py:16,43` — `cascade="all, delete-orphan"` set on ORM relationships but ForeignKeys lack `ondelete="CASCADE"`. App crash leaves orphaned rows.
- [ ] **Zero tests for pages.py** — Largest router (467 lines, 8 endpoints: login, register, dashboard, mentor views, logout). No test file exists. Create `tests/routers/test_pages.py`.
- [ ] **Health check doesn't verify DB** — `app/routers/health.py:6-8` — Returns `{"status": "healthy"}` without querying database. Add `SELECT 1` probe.
- [ ] **No tests for /auth/register** — Firebase-based registration endpoint with 409 conflict detection is entirely untested.

---

## HIGH

- [ ] **Session cookie missing secure flag** — `app/routers/pages.py:150,237` — Add `secure=True` to `set_cookie()` calls (conditionally based on env).
- [ ] **Rabbi endpoint returns ALL students** — `app/routers/rabbi.py:14-26` — `list_students()` has no `mentor_id` filter. Add `.where(User.mentor_id == current_user.id)`.
- [ ] **Teacher endpoint returns ALL students** — `app/routers/teacher.py:14-26` — Same issue as rabbi endpoint. Add mentor filter.
- [ ] **Missing Content-Security-Policy header** — `app/main.py:41-48` — Security headers middleware lacks CSP. Add `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'`.
- [ ] **No rate limiting on login/register** — `app/routers/pages.py` — No throttling on auth endpoints. Add `slowapi` or similar rate limiter.
- [ ] **Weak password policy** — `app/routers/pages.py:203` — Only requires `len >= 8`. Add complexity requirements (uppercase, lowercase, digit, special char).
- [ ] **Weak email validation regex** — `app/routers/pages.py:191` — Basic `^[^@]+@[^@]+\.[^@]+$` allows invalid emails. Use Pydantic `EmailStr` or stricter regex.
- [ ] **Missing FK indexes** — Alembic migration — No indexes on: `quizzes.video_id`, `videos.subject_id`, `semesters.program_id`, `subjects.semester_id`, `quiz_attempts.quiz_id`, `event_registrations.event_id/user_id`, `questionnaire_fields.questionnaire_id`, `case_notes.case_id`, `case_documents.case_id`, `answers.attempt_id/question_id`.
- [ ] **Missing CHECK constraints** — Alembic migration — No DB-level constraints on: `enrollment_semester` (1-8), `passing_score` (0-100), `capacity` (>= 0), `last_position_seconds` (>= 0), `score` (0-100).
- [ ] **Blocking scrypt in async handlers** — `app/routers/pages.py:78-87` — `hashlib.scrypt()` is CPU-intensive and blocks the event loop. Wrap in `asyncio.to_thread()`.
- [ ] **No connection pool config** — `app/dependencies.py:10` — `create_async_engine()` uses default `pool_size=5`. Set explicit `pool_size=20, max_overflow=10, pool_recycle=3600`.
- [ ] **GCP clients recreated per request** — `app/gcp/storage.py:17-18`, `app/gcp/cloud_tasks.py:19-20`, `app/gcp/calendar_sync.py:21-29` — Each call creates new client. Create singleton clients at startup.
- [ ] **Calendar failure creates registration without calendar event** — `app/services/event_service.py:54-66` — Exception caught and logged but registration still commits. Queue calendar creation as retryable async task.
- [ ] **Inline import re** — `app/routers/pages.py:174` — Move `import re` to top-level imports.
- [ ] **No negative pagination validation** — Multiple routers — `skip` and `limit` accept negative integers. Add `Field(ge=0)` or manual validation.
- [ ] **Unused make_client fixture** — `tests/conftest.py:135-147` — Defined but never used. Remove or use in tests.
- [ ] **Inconsistent HTTP status codes** — Multiple routers — Mix of raw integers (`404`) and constants (`status.HTTP_409_CONFLICT`). Standardize to `fastapi.status` constants.
- [ ] **Silent quiz question skip** — `app/services/assessment_service.py:39-41` — Invalid `question_id` in submission silently `continue`s instead of raising error. Can inflate scores.

---

## MEDIUM

- [ ] **No HSTS header** — `app/main.py` — Add `Strict-Transport-Security: max-age=31536000; includeSubDomains` in security headers middleware.
- [ ] **No security event logging** — App-wide — Add logging for login attempts, failed auth, admin actions, role changes.
- [ ] **GCP credentials path not validated** — `app/auth/firebase.py:13-16` — Invalid path silently falls back to dev mode. Validate file exists on startup.
- [ ] **CSV export missing charset** — `app/routers/export.py` — Content-Type should be `text/csv; charset=utf-8`.
- [ ] **Pagination limit allows 0** — `app/routers/admin.py:62` — Enforce minimum: `limit = min(max(limit, 1), 100)`.
- [ ] **User.students selectin loading** — `app/models/user.py:37` — Change `lazy="selectin"` to `lazy="select"` on students relationship. Load explicitly when needed.
- [ ] **Mentor dashboard loads User.mentor unnecessarily** — `app/routers/dashboard.py:25-30` — Eager load mentor only when needed.
- [ ] **Questionnaire dispatch unbounded** — `app/services/cloud_tasks_service.py:18-21` — Process students in batches with offset/limit loop.
- [ ] **Mentor dashboard no pagination** — `app/routers/pages.py:297-300` — Loads all assigned students without limit.
- [ ] **Quiz grading partial failure** — `app/services/assessment_service.py:30-60` — Attempt flushed before all answers added. Add explicit rollback on error.
- [ ] **Missing ondelete CASCADE on beit_din FKs** — `app/models/beit_din.py:26-27` — CaseNote/CaseDocument ForeignKeys need `ondelete="CASCADE"`.
- [ ] **CI missing linting/type checking** — `.github/workflows/test.yml` — Add `ruff check .` and `mypy app` steps.
- [ ] **Missing 95% boundary tests** — `tests/unit/test_tracking.py` — Add tests for 94% (not complete), 95.0% (exact threshold), 0-duration edge case.
- [ ] **FAQ schemas inline in router** — `app/routers/faq.py:16-35` — Move `FAQResponse`, `FAQCreateRequest`, `FAQUpdateRequest` to `app/schemas/resource.py`.
- [ ] **Test DB path hardcoded** — `tests/conftest.py:14` — Load from `TEST_DATABASE_URL` env var with fallback.
- [ ] **setup_database drops tables on failure** — `tests/conftest.py:20-26` — Consider transaction rollback per test instead of full drop/recreate.
- [ ] **Session secret not configurable** — `app/routers/pages.py:28-30` — Duplicate of critical item #1; env var override needed.
- [ ] **Mentor dashboard N+1 and no caching** — `app/routers/pages.py:284-458` — Completion stats computed per student per request.

---

## LOW

- [ ] **Default DB credentials in config** — `app/config.py:5` — Hardcoded `jca:jca@localhost:5432/jca`. Remove default or use empty placeholder.
- [ ] **Admin stats: 4 separate COUNT queries** — `app/routers/admin.py:35-44` — Combine into single aggregated query.
- [ ] **Questionnaire index optimization** — Migration — Add `created_at` to `(questionnaire_id, user_id)` composite index for covering index.
- [ ] **Partial index on video_progress.is_completed** — Migration — Create partial index `WHERE is_completed = TRUE` for completion queries.
- [ ] **FAQ list potentially unbounded** — `app/routers/faq.py` — Add hard limit on public FAQ list.
- [ ] **No rate limiting on quiz submissions** — `app/routers/assessments.py:26-42` — Unlimited retakes could fill DB. Add throttle.
- [ ] **EventType not validated in request schemas** — `app/models/event.py:24` — Only validated at ORM level, not Pydantic.
- [ ] **SSRF risk in cloud_tasks URL** — `app/services/cloud_tasks_service.py:25` — `app_base_url` not validated as URL.
- [ ] **QuizAttemptResponse missing fields** — `app/schemas/assessment.py:38-45` — Add `user_id` and `created_at` to response.
- [ ] **Missing .env.example entries** — `.env.example` — Add `SESSION_SECRET`, `LOG_LEVEL`, `APP_ENVIRONMENT`.
- [ ] **No cascade delete tests** — Missing — Unknown behavior when Semester/Subject deleted with associated progress/attempts.
- [ ] **Incomplete rabbi/teacher tests** — `tests/routers/test_rabbi_teacher.py` — Missing pagination tests and `/rabbi/students/{id}/progress` endpoint test.
- [ ] **No CSRF/session expiration tests** — Missing — CSRF token expiry (1h), session expiry (24h), and failed login tracking untested.

---

## DEPLOYMENT (Completed 2026-03-18)

- [x] **GCE deployment** — `e2-small` in `us-central1-a` (97% Carbon Free Energy), project `rich-gift-487522-m6`
- [x] **Container registry** — Artifact Registry at `us-central1-docker.pkg.dev/rich-gift-487522-m6/jca/jca-app`
- [x] **Startup script** — `deploy/gce-startup.sh` installs Docker, pulls images, starts services
- [x] **Firewall rule** — `allow-http-jca` (TCP 80)
- [ ] **HTTPS/TLS** — Currently HTTP only. Add Let's Encrypt or GCP load balancer with managed cert.
- [ ] **Static IP** — Current IP is ephemeral. Reserve a static external IP.
- [ ] **Domain name** — No custom domain configured yet.
- [ ] **Production database credentials** — Using default `jca:jca` password. Set strong password via env vars.
- [ ] **Firebase production credentials** — Running in dev mode. Configure real Firebase for production auth.
- [ ] **Restrict CORS** — Currently `["*"]`. Set to actual domain once configured.

---

## Stats

| Severity | Count |
|----------|-------|
| Critical | 11 |
| High | 18 |
| Medium | 18 |
| Low | 13 |
| **Total** | **60** |

*Deduplicated from 68 raw audit findings (8 cross-category overlaps removed).*
