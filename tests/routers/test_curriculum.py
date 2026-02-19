"""Tests for curriculum endpoints."""

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import make_program, make_semester, make_subject, make_video


async def _seed_curriculum(db: AsyncSession):
    program = make_program()
    db.add(program)
    await db.flush()
    semester = make_semester(program.id, name="Semester 1")
    db.add(semester)
    await db.flush()
    subject = make_subject(semester.id, name="Foundations")
    db.add(subject)
    await db.flush()
    video = make_video(subject.id, title="Intro Video")
    db.add(video)
    await db.commit()
    return program, semester, subject, video


async def test_list_programs(client: AsyncClient, db: AsyncSession):
    program, *_ = await _seed_curriculum(db)
    resp = await client.get("/curriculum/programs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_get_semester(client: AsyncClient, db: AsyncSession):
    _, semester, *_ = await _seed_curriculum(db)
    resp = await client.get(f"/curriculum/semesters/{semester.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Semester 1"


async def test_get_semester_not_found(client: AsyncClient):
    resp = await client.get(f"/curriculum/semesters/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_get_subject(client: AsyncClient, db: AsyncSession):
    *_, subject, _ = await _seed_curriculum(db)
    resp = await client.get(f"/curriculum/subjects/{subject.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Foundations"


async def test_get_video(client: AsyncClient, db: AsyncSession):
    *_, video = await _seed_curriculum(db)
    resp = await client.get(f"/curriculum/videos/{video.id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Intro Video"


async def test_get_video_not_found(client: AsyncClient):
    resp = await client.get(f"/curriculum/videos/{uuid.uuid4()}")
    assert resp.status_code == 404
