"""Integration tests for role-based portals.

Required by CLAUDE_SPEC.md:
- test_biet_din_access: Only RABBI/BEIT_DIN roles can access case files
- test_monthly_questionnaire_dispatch: Cloud Tasks dispatches questionnaires
- test_retreat_signup_calendar: Signup triggers calendar event creation
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventType
from app.models.questionnaire import MonthlyQuestionnaire
from app.models.user import User, UserRole
from tests.conftest import _override_deps


async def test_biet_din_access(db: AsyncSession, student_user: User, rabbi_user: User):
    """Assert that only users with RABBI/BEIT_DIN role can access Biet Din case files.
    Students should be denied access."""
    from app.main import create_app

    app = create_app()

    # Student tries to access beit din cases → 403
    _override_deps(app, db, student_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/beit-din/cases")
        assert resp.status_code == 403

    app.dependency_overrides.clear()

    # Rabbi accesses beit din cases → 200
    _override_deps(app, db, rabbi_user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/beit-din/cases")
        assert resp.status_code == 200

    app.dependency_overrides.clear()


async def test_monthly_questionnaire_dispatch(db: AsyncSession, admin_user: User, student_user: User):
    """Mock Cloud Tasks to verify a monthly questionnaire is sent to all users."""
    from app.main import create_app

    # Create a questionnaire
    questionnaire = MonthlyQuestionnaire(
        title="Monthly Check-in February",
        month=2,
        year=2026,
        is_active=True,
    )
    db.add(questionnaire)
    await db.commit()
    await db.refresh(questionnaire)

    app = create_app()
    _override_deps(app, db, admin_user)

    with patch("app.services.cloud_tasks_service.create_task") as mock_task:
        mock_task.return_value = "dev-task-mock"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/questionnaires/dispatch",
                params={"questionnaire_id": str(questionnaire.id)},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["dispatched_to"] >= 1
            assert data["questionnaire_id"] == str(questionnaire.id)

        # Verify Cloud Tasks was called for each student
        assert mock_task.call_count >= 1

    app.dependency_overrides.clear()


async def test_retreat_signup_calendar(db: AsyncSession, student_user: User):
    """Verify that signing up for an annual retreat triggers a calendar event creation."""
    from app.main import create_app

    # Create a retreat event
    event = Event(
        title="Annual Conversion Retreat 2026",
        description="A weekend retreat for conversion students",
        event_type=EventType.RETREAT,
        start_time=datetime(2026, 6, 15, 9, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 17, 17, 0, tzinfo=timezone.utc),
        location="Camp David",
        capacity=50,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    app = create_app()
    _override_deps(app, db, student_user)

    with patch("app.services.event_service.create_calendar_event") as mock_calendar:
        mock_calendar.return_value = "cal-event-123"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(f"/events/{event.id}/register")
            assert resp.status_code == 201
            data = resp.json()
            assert data["event_id"] == str(event.id)
            assert data["user_id"] == str(student_user.id)

        # Verify calendar event creation was called
        mock_calendar.assert_called_once()
        call_kwargs = mock_calendar.call_args
        assert "Annual Conversion Retreat" in call_kwargs.kwargs.get("title", "") or \
               "Annual Conversion Retreat" in (call_kwargs.args[0] if call_kwargs.args else "")

    app.dependency_overrides.clear()
