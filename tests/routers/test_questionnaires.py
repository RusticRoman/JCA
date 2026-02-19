"""Tests for questionnaire endpoints."""

import uuid
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import _override_deps
from tests.factories import make_questionnaire


async def test_get_current_questionnaire(client: AsyncClient, db: AsyncSession):
    q = make_questionnaire(title="March Check-in", month=3, year=2026)
    db.add(q)
    await db.commit()

    resp = await client.get("/questionnaires/current")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "March Check-in"


async def test_get_current_questionnaire_none(client: AsyncClient, db: AsyncSession):
    # No active questionnaires
    resp = await client.get("/questionnaires/current")
    assert resp.status_code == 200
    assert resp.json() is None


async def test_submit_questionnaire(client: AsyncClient, db: AsyncSession):
    q = make_questionnaire()
    db.add(q)
    await db.commit()
    await db.refresh(q)

    resp = await client.post(f"/questionnaires/{q.id}/submit", json={
        "answers": {"field1": "Good", "field2": "Excellent"},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["questionnaire_id"] == str(q.id)


async def test_submit_questionnaire_not_found(client: AsyncClient):
    resp = await client.post(f"/questionnaires/{uuid.uuid4()}/submit", json={
        "answers": {"field1": "Good"},
    })
    assert resp.status_code == 404


async def test_dispatch_admin_only(db: AsyncSession, student_user: User):
    from app.main import create_app

    q = make_questionnaire()
    db.add(q)
    await db.commit()
    await db.refresh(q)

    app = create_app()
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/questionnaires/dispatch", params={"questionnaire_id": str(q.id)})
        assert resp.status_code == 403
    app.dependency_overrides.clear()
