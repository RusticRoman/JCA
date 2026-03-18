---
paths:
  - "tests/**/*.py"
---

# Testing Conventions

- Tests use SQLite via aiosqlite (not PostgreSQL) — no external services needed
- Test DB: `sqlite+aiosqlite:///./test.db` (configured in `tests/conftest.py`)
- Fixtures in `tests/conftest.py`: async DB session, user fixtures (student, rabbi, admin), HTTP client
- Factory functions in `tests/factories.py` for all model types
- Auth overridden via FastAPI dependency injection (no real Firebase in tests)
- 74 tests: 3 unit (`tests/unit/`) + 71 integration (`tests/integration/`)
- Run: `pytest -v` or `pytest tests/unit/ -v` for unit only
- Key unit tests in `test_tracking.py`: progress save, resume logic, attendance no-downgrade
