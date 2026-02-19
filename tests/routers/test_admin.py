"""Tests for admin endpoints."""

import uuid

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from tests.conftest import _override_deps


async def test_admin_stats(db: AsyncSession, admin_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_users"] >= 2
        assert data["active_students"] >= 1
    app.dependency_overrides.clear()


async def test_admin_list_users(db: AsyncSession, admin_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/admin/users")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2
    app.dependency_overrides.clear()


async def test_admin_list_users_by_role(db: AsyncSession, admin_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/admin/users", params={"role": "STUDENT"})
        assert resp.status_code == 200
        for u in resp.json():
            assert u["role"] == "STUDENT"
    app.dependency_overrides.clear()


async def test_admin_update_user(db: AsyncSession, admin_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.patch(f"/admin/users/{student_user.id}", json={"role": "TEACHER"})
        assert resp.status_code == 200
        assert resp.json()["role"] == "TEACHER"
    app.dependency_overrides.clear()


async def test_admin_deactivate_user(db: AsyncSession, admin_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(f"/admin/users/{student_user.id}/deactivate")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False
    app.dependency_overrides.clear()


async def test_admin_student_forbidden(db: AsyncSession, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/admin/stats")
        assert resp.status_code == 403
    app.dependency_overrides.clear()


async def test_admin_update_user_not_found(db: AsyncSession, admin_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, admin_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.patch(f"/admin/users/{uuid.uuid4()}", json={"role": "TEACHER"})
        assert resp.status_code == 404
    app.dependency_overrides.clear()
