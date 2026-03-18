---
paths:
  - "app/auth/**"
  - "app/routers/pages.py"
  - "app/routers/export.py"
  - "app/services/**"
  - "app/gcp/**"
---

# Security Rules (from AUDIT_ROUND3.md)

## CRITICAL — do not re-introduce these patterns

- Session secret MUST come from env var, not `secrets.token_bytes()` at import time (invalidates sessions on restart)
- Never expose `firebase_uid` in API responses — remove from response schemas
- Never trust client-reported `total_duration_seconds` for completion — use DB video duration
- Verify Cloud Tasks target endpoints actually exist before dispatching

## HIGH — enforce in new code

- Set `secure=True` on session cookies in production
- Rabbi/Teacher endpoints must filter by `mentor_id`, not return ALL students
- Add `Content-Security-Policy` header
- Validate and rate-limit login/register endpoints
- Use `EmailStr` (not regex) for email validation
- Run `hashlib.scrypt` in `asyncio.to_thread()` to avoid blocking the event loop

## Patterns to follow

- CSRF: HMAC-signed tokens on all form submissions
- Sessions: httponly, SameSite=Lax, 24h max-age cookies
- CORS: restrict to specific origins (not `["*"]` in production)
- CSV exports: stream results, don't load all into memory
- GCP clients: create singletons at startup, not per-request
