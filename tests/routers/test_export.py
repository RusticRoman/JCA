"""Tests for data export endpoints."""

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import _override_deps


async def test_export_progress_csv(db: AsyncSession, admin_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/export/progress.csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert "user_id" in resp.text  # CSV header
    app.dependency_overrides.clear()


async def test_export_users_csv(db: AsyncSession, admin_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/export/users.csv")
        assert resp.status_code == 200
        assert "email" in resp.text
    app.dependency_overrides.clear()


async def test_export_questionnaire_responses_csv(db: AsyncSession, admin_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/export/questionnaire-responses.csv")
        assert resp.status_code == 200
        assert "questionnaire_id" in resp.text
    app.dependency_overrides.clear()


async def test_export_student_forbidden(db: AsyncSession, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/export/progress.csv")
        assert resp.status_code == 403
    app.dependency_overrides.clear()
