"""Tests for event endpoints."""

import uuid
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import _override_deps
from tests.factories import make_event


async def test_list_events(client: AsyncClient, db: AsyncSession):
    event = make_event(title="Shabbaton 2026")
    db.add(event)
    await db.commit()

    resp = await client.get("/events")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Shabbaton 2026"


async def test_register_event(db: AsyncSession, student_user: User):
    from app.main import create_app

    event = make_event()
    db.add(event)
    await db.commit()
    await db.refresh(event)

    app = create_app()
    _override_deps(app, db, student_user)

    with patch("app.services.event_service.create_calendar_event") as mock_cal:
        mock_cal.return_value = "cal-123"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(f"/events/{event.id}/register")
            assert resp.status_code == 201
            data = resp.json()
            assert data["event_id"] == str(event.id)
            assert data["user_id"] == str(student_user.id)

    app.dependency_overrides.clear()


async def test_register_duplicate(db: AsyncSession, student_user: User):
    from app.main import create_app

    event = make_event()
    db.add(event)
    await db.commit()
    await db.refresh(event)

    app = create_app()
    _override_deps(app, db, student_user)

    with patch("app.services.event_service.create_calendar_event") as mock_cal:
        mock_cal.return_value = "cal-123"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            await ac.post(f"/events/{event.id}/register")
            resp = await ac.post(f"/events/{event.id}/register")
            assert resp.status_code == 400
            assert "Already registered" in resp.json()["detail"]

    app.dependency_overrides.clear()


async def test_register_full_capacity(db: AsyncSession, student_user: User):
    from app.main import create_app

    event = make_event(capacity=0)  # 0 = unlimited
    db.add(event)
    await db.commit()
    await db.refresh(event)

    # Create event with capacity of 1
    limited_event = make_event(title="Limited", capacity=1)
    db.add(limited_event)
    await db.commit()
    await db.refresh(limited_event)

    # Register first user
    other_user = User(
        firebase_uid="other-uid", email="other@test.com",
        display_name="Other", role=student_user.role,
    )
    db.add(other_user)
    await db.commit()
    await db.refresh(other_user)

    app = create_app()

    with patch("app.services.event_service.create_calendar_event") as mock_cal:
        mock_cal.return_value = "cal-123"

        # Register other_user first
        _override_deps(app, db, other_user)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(f"/events/{limited_event.id}/register")
            assert resp.status_code == 201

        # student_user tries to register → full
        _override_deps(app, db, student_user)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(f"/events/{limited_event.id}/register")
            assert resp.status_code == 400
            assert "full" in resp.json()["detail"].lower()

    app.dependency_overrides.clear()


async def test_unregister(db: AsyncSession, student_user: User):
    from app.main import create_app

    event = make_event()
    db.add(event)
    await db.commit()
    await db.refresh(event)

    app = create_app()
    _override_deps(app, db, student_user)

    with patch("app.services.event_service.create_calendar_event") as mock_cal:
        mock_cal.return_value = "cal-123"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            await ac.post(f"/events/{event.id}/register")
            resp = await ac.delete(f"/events/{event.id}/register")
            assert resp.status_code == 204

    app.dependency_overrides.clear()


async def test_unregister_not_found(client: AsyncClient):
    resp = await client.delete(f"/events/{uuid.uuid4()}/register")
    assert resp.status_code == 404
