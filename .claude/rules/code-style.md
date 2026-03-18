---
paths:
  - "app/**/*.py"
---

# Python / FastAPI Code Style

- Python 3.13, async everywhere (asyncpg, SQLAlchemy async sessions)
- SQLAlchemy 2.0 declarative with `mapped_column`, UUID v4 primary keys, `TimestampMixin`
- Pydantic v2 schemas in `app/schemas/`, models in `app/models/`
- Routers are thin — parse request, call service, return response
- Services in `app/services/` hold all business logic
- GCP wrappers in `app/gcp/` isolate SDK calls, return stubs in dev mode
- Auth via `get_current_user` dependency (Firebase token → DB lookup)
- Role enforcement via `require_roles()` dependency factory in `app/auth/middleware.py`
- Use `status.HTTP_*` constants, not raw integers, for HTTP status codes
- Imports at module top (not inline)
- Password hashing: `hashlib.scrypt` with random salt + `hmac.compare_digest`
