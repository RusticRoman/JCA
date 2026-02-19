"""Tests for rabbi and teacher portal endpoints."""

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import _override_deps


async def test_rabbi_list_students(db: AsyncSession, rabbi_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/rabbi/students")
        assert resp.status_code == 200
    app.dependency_overrides.clear()


async def test_student_cannot_access_rabbi_portal(db: AsyncSession, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/rabbi/students")
        assert resp.status_code == 403
    app.dependency_overrides.clear()


async def test_teacher_list_students(db: AsyncSession, teacher_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, teacher_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/teacher/students")
        assert resp.status_code == 200
    app.dependency_overrides.clear()


async def test_student_cannot_access_teacher_portal(db: AsyncSession, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/teacher/students")
        assert resp.status_code == 403
    app.dependency_overrides.clear()


async def test_teacher_activity(db: AsyncSession, teacher_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, teacher_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/teacher/activity")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
    app.dependency_overrides.clear()
