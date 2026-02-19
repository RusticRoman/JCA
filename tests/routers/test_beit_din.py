"""Tests for beit din case management endpoints."""

import uuid

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from tests.conftest import _override_deps
from tests.factories import make_case


async def test_student_cannot_access_cases(db: AsyncSession, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/beit-din/cases")
        assert resp.status_code == 403
    app.dependency_overrides.clear()


async def test_rabbi_can_list_cases(db: AsyncSession, rabbi_user: User, student_user: User):
    from app.main import create_app

    case = make_case(student_id=student_user.id, rabbi_id=rabbi_user.id)
    db.add(case)
    await db.commit()

    app = create_app()
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/beit-din/cases")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
    app.dependency_overrides.clear()


async def test_create_case(db: AsyncSession, rabbi_user: User, student_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/beit-din/cases", json={
            "student_id": str(student_user.id),
            "title": "Conversion Review",
            "description": "Ready for review",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Conversion Review"
        assert data["student_id"] == str(student_user.id)
        assert data["rabbi_id"] == str(rabbi_user.id)
    app.dependency_overrides.clear()


async def test_get_case_not_found(db: AsyncSession, rabbi_user: User):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/beit-din/cases/{uuid.uuid4()}")
        assert resp.status_code == 404
    app.dependency_overrides.clear()


async def test_update_case_status(db: AsyncSession, rabbi_user: User, student_user: User):
    from app.main import create_app

    case = make_case(student_id=student_user.id, rabbi_id=rabbi_user.id)
    db.add(case)
    await db.commit()
    await db.refresh(case)

    app = create_app()
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.patch(f"/beit-din/cases/{case.id}", json={
            "status": "IN_REVIEW",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "IN_REVIEW"
    app.dependency_overrides.clear()


async def test_add_note_to_case(db: AsyncSession, rabbi_user: User, student_user: User):
    from app.main import create_app

    case = make_case(student_id=student_user.id, rabbi_id=rabbi_user.id)
    db.add(case)
    await db.commit()
    await db.refresh(case)

    app = create_app()
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(f"/beit-din/cases/{case.id}/notes", json={
            "content": "Student is making good progress.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "Student is making good progress."
        assert data["author_id"] == str(rabbi_user.id)
    app.dependency_overrides.clear()
