"""Tests for dashboard endpoints."""

import uuid

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import _override_deps
from tests.factories import make_program, make_semester, make_subject, make_video


async def _seed_curriculum(db: AsyncSession):
    program = make_program()
    db.add(program)
    await db.flush()
    semester = make_semester(program.id)
    db.add(semester)
    await db.flush()
    subject = make_subject(semester.id)
    db.add(subject)
    await db.flush()
    video = make_video(subject.id)
    db.add(video)
    await db.commit()
    return video


async def test_get_own_dashboard(client: AsyncClient, db: AsyncSession):
    await _seed_curriculum(db)
    resp = await client.get("/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_completion_pct" in data
    assert data["overall_completion_pct"] == 0.0


async def test_get_student_dashboard_as_rabbi(
    db: AsyncSession, rabbi_user: User, student_user: User,
):
    from app.main import create_app

    # Assign student to this rabbi
    student_user.mentor_id = rabbi_user.id
    await db.commit()

    await _seed_curriculum(db)
    app = create_app()
    _override_deps(app, db, rabbi_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/dashboard/student/{student_user.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == str(student_user.id)

    app.dependency_overrides.clear()


async def test_student_cannot_view_other_student(
    db: AsyncSession, student_user: User,
):
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/dashboard/student/{uuid.uuid4()}")
        assert resp.status_code == 403

    app.dependency_overrides.clear()
