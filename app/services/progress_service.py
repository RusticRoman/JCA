import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import AttendanceType, VideoProgress

COMPLETION_THRESHOLD = 0.95


async def sync_progress(
    db: AsyncSession,
    user_id: uuid.UUID,
    video_id: uuid.UUID,
    last_position_seconds: int,
    total_duration_seconds: int,
    attendance_type: AttendanceType,
) -> VideoProgress:
    """Sync heartbeat progress. Implements 95% completion and no-downgrade logic."""
    result = await db.execute(
        select(VideoProgress).where(
            VideoProgress.user_id == user_id,
            VideoProgress.video_id == video_id,
        )
    )
    progress = result.scalar_one_or_none()

    if progress is None:
        progress = VideoProgress(
            user_id=user_id,
            video_id=video_id,
            last_position_seconds=last_position_seconds,
            total_duration_seconds=total_duration_seconds,
            attendance_type=attendance_type,
        )
        db.add(progress)
    else:
        progress.last_position_seconds = last_position_seconds
        progress.total_duration_seconds = total_duration_seconds

        # No-downgrade: LIVE status is never overwritten by RECORDED
        if progress.attendance_type != AttendanceType.LIVE:
            progress.attendance_type = attendance_type

    # 95% completion trigger
    if (
        total_duration_seconds > 0
        and last_position_seconds >= total_duration_seconds * COMPLETION_THRESHOLD
    ):
        progress.is_completed = True

    await db.commit()
    await db.refresh(progress)
    return progress


async def get_video_state(
    db: AsyncSession,
    user_id: uuid.UUID,
    video_id: uuid.UUID,
) -> VideoProgress | None:
    """Get the resume state for a video."""
    result = await db.execute(
        select(VideoProgress).where(
            VideoProgress.user_id == user_id,
            VideoProgress.video_id == video_id,
        )
    )
    return result.scalar_one_or_none()
