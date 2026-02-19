"""Tests for video progress router endpoints."""

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import make_program, make_semester, make_subject, make_video


async def _create_video(db: AsyncSession):
    program = make_program()
    db.add(program)
    await db.flush()
    semester = make_semester(program.id)
    db.add(semester)
    await db.flush()
    subject = make_subject(semester.id)
    db.add(subject)
    await db.flush()
    video = make_video(subject.id, duration_seconds=1000)
    db.add(video)
    await db.commit()
    await db.refresh(video)
    return video


async def test_sync_progress_endpoint(client: AsyncClient, db: AsyncSession):
    video = await _create_video(db)
    resp = await client.post("/progress/sync-progress", json={
        "video_id": str(video.id),
        "last_position_seconds": 100,
        "total_duration_seconds": 1000,
        "attendance_type": "RECORDED",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["last_position_seconds"] == 100
    assert data["is_completed"] is False


async def test_sync_progress_completion(client: AsyncClient, db: AsyncSession):
    video = await _create_video(db)
    resp = await client.post("/progress/sync-progress", json={
        "video_id": str(video.id),
        "last_position_seconds": 960,
        "total_duration_seconds": 1000,
        "attendance_type": "RECORDED",
    })
    assert resp.status_code == 200
    assert resp.json()["is_completed"] is True


async def test_video_state_endpoint(client: AsyncClient, db: AsyncSession):
    video = await _create_video(db)
    # Save progress first
    await client.post("/progress/sync-progress", json={
        "video_id": str(video.id),
        "last_position_seconds": 500,
        "total_duration_seconds": 1000,
    })
    # Retrieve state
    resp = await client.get(f"/progress/video-state/{video.id}")
    assert resp.status_code == 200
    assert resp.json()["last_position_seconds"] == 500


async def test_video_state_not_found(client: AsyncClient):
    resp = await client.get(f"/progress/video-state/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_sync_progress_rejects_negative_position(client: AsyncClient, db: AsyncSession):
    video = await _create_video(db)
    resp = await client.post("/progress/sync-progress", json={
        "video_id": str(video.id),
        "last_position_seconds": -1,
        "total_duration_seconds": 1000,
    })
    assert resp.status_code == 422


async def test_sync_progress_rejects_zero_duration(client: AsyncClient, db: AsyncSession):
    video = await _create_video(db)
    resp = await client.post("/progress/sync-progress", json={
        "video_id": str(video.id),
        "last_position_seconds": 0,
        "total_duration_seconds": 0,
    })
    assert resp.status_code == 422
