# JCA — Jewish Conversion Academy

FastAPI LMS for Jewish conversion programs. Python 3.13, SQLAlchemy 2.0 async, PostgreSQL 16, GCP.

## Live

- **URL**: http://35.188.107.106
- **GCP Project**: `rich-gift-487522-m6`
- **Instance**: `jca-server` in `us-central1-a`

## Commands

```bash
# Local dev
docker compose up                    # http://localhost:8000
pytest -v                            # 74 tests (SQLite, no PG needed)
pip install -e ".[dev]"              # dev install
uvicorn app.main:app --reload        # without Docker

# Deploy (MUST target linux/amd64 from Mac)
docker buildx build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/rich-gift-487522-m6/jca/jca-app:latest --push .
gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
  --command="cd /opt/jca && sudo docker compose pull && sudo docker compose up -d --force-recreate"
```

## Credentials

| Role | Email | Password |
|------|-------|----------|
| Rabbi | `mentor@jca.org` | `mentor123` |
| Rabbi | `mentor2@jca.org` | `mentor456` |
| Student (x10) | `anna.p@example.com` etc. | `student123` |
| Admin | (none seeded) | Register + update role in DB |

## Architecture

```
Routers (HTTP) → Services (Business Logic) → Models (SQLAlchemy) → PostgreSQL
                                            → GCP Wrappers (GCS, Cloud Tasks, Calendar)
```

- 17 routers, 50+ endpoints, 16 models, 6 Jinja2 templates
- Firebase Auth (dev mode when credentials absent)
- Layered: routers are thin, services hold logic, models hold data

## Key docs (read on demand, not auto-loaded)

- @CLAUDE_SPEC.md — Full technical spec, data model, all endpoints
- @REFERENCE.md — Complete API reference (large)
- @SKILL.md — Operations runbook (deploy, logs, DB access)
- @TODO.md — Outstanding issues by priority
- @AUDIT_ROUND3.md — Security/performance audit (68 findings)
