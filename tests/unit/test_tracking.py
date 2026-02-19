"""Unit tests for video progress tracking.

Required by CLAUDE_SPEC.md:
- test_progress_save: Ensure last_position_seconds updates correctly
- test_resume_logic: Verify the API returns the correct timestamp for a returning user
- test_attendance_differentiation: Confirm LIVE vs RECORDED distinction with no-downgrade
"""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import AttendanceType, VideoProgress
from app.models.user import User
from app.services.progress_service import get_video_state, sync_progress
from tests.factories import make_program, make_semester, make_subject, make_video


async def _create_video(db: AsyncSession):
    """Helper to create a video for testing."""
    program = make_program()
    db.add(program)
    await db.flush()

    semester = make_semester(program_id=program.id)
    db.add(semester)
    await db.flush()

    subject = make_subject(semester_id=semester.id)
    db.add(subject)
    await db.flush()

    video = make_video(subject_id=subject.id, duration_seconds=1000)
    db.add(video)
    await db.commit()
    await db.refresh(video)
    return video


async def test_progress_save(db: AsyncSession, student_user: User):
    """Ensure last_position_seconds updates correctly in the database."""
    video = await _create_video(db)

    # First heartbeat at 100 seconds
    progress = await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=100,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )
    assert progress.last_position_seconds == 100
    assert progress.is_completed is False

    # Second heartbeat at 500 seconds
    progress = await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=500,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )
    assert progress.last_position_seconds == 500
    assert progress.is_completed is False

    # Third heartbeat at 960 seconds (>= 95% of 1000) → completed
    progress = await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=960,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )
    assert progress.last_position_seconds == 960
    assert progress.is_completed is True


async def test_resume_logic(db: AsyncSession, student_user: User):
    """Verify the API returns the correct timestamp for a returning user."""
    video = await _create_video(db)

    # Save progress at 300 seconds
    await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=300,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )

    # Retrieve state - should return the saved position
    state = await get_video_state(db=db, user_id=student_user.id, video_id=video.id)
    assert state is not None
    assert state.last_position_seconds == 300
    assert state.total_duration_seconds == 1000
    assert state.is_completed is False

    # Continue watching to 750 seconds
    await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=750,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )

    # Resume should now return 750
    state = await get_video_state(db=db, user_id=student_user.id, video_id=video.id)
    assert state is not None
    assert state.last_position_seconds == 750


async def test_attendance_differentiation(db: AsyncSession, student_user: User):
    """Confirm the system distinguishes between LIVE and RECORDED,
    and that LIVE status is never downgraded to RECORDED."""
    video = await _create_video(db)

    # First: watch as RECORDED
    progress = await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=100,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )
    assert progress.attendance_type == AttendanceType.RECORDED

    # Upgrade to LIVE
    progress = await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=200,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.LIVE,
    )
    assert progress.attendance_type == AttendanceType.LIVE

    # Try to "downgrade" back to RECORDED - should stay LIVE
    progress = await sync_progress(
        db=db,
        user_id=student_user.id,
        video_id=video.id,
        last_position_seconds=300,
        total_duration_seconds=1000,
        attendance_type=AttendanceType.RECORDED,
    )
    assert progress.attendance_type == AttendanceType.LIVE
    assert progress.last_position_seconds == 300
