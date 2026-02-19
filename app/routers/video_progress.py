import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.progress import SyncProgressRequest, SyncProgressResponse, VideoStateResponse
from app.services.progress_service import get_video_state, sync_progress

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/sync-progress", response_model=SyncProgressResponse)
async def sync(
    req: SyncProgressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    progress = await sync_progress(
        db=db,
        user_id=current_user.id,
        video_id=req.video_id,
        last_position_seconds=req.last_position_seconds,
        total_duration_seconds=req.total_duration_seconds,
        attendance_type=req.attendance_type,
    )
    return SyncProgressResponse(
        video_id=progress.video_id,
        last_position_seconds=progress.last_position_seconds,
        total_duration_seconds=progress.total_duration_seconds,
        is_completed=progress.is_completed,
        attendance_type=progress.attendance_type,
    )


@router.get("/video-state/{video_id}", response_model=VideoStateResponse)
async def video_state(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    progress = await get_video_state(db=db, user_id=current_user.id, video_id=video_id)
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this video")
    return VideoStateResponse(
        video_id=progress.video_id,
        last_position_seconds=progress.last_position_seconds,
        total_duration_seconds=progress.total_duration_seconds,
        is_completed=progress.is_completed,
        attendance_type=progress.attendance_type,
    )
