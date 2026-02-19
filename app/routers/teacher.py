from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_db
from app.models.progress import VideoProgress
from app.models.user import User, UserRole
from app.schemas.user import UserResponse

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/students", response_model=list[UserResponse])
async def list_students(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.role == UserRole.STUDENT, User.is_active.is_(True))
        .offset(skip).limit(min(limit, 100))
    )
    return result.scalars().all()


@router.get("/activity")
async def get_recent_activity(
    current_user: User = Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoProgress)
        .order_by(VideoProgress.updated_at.desc())
        .limit(50)
    )
    progress_list = result.scalars().all()
    return [
        {
            "user_id": str(p.user_id),
            "video_id": str(p.video_id),
            "last_position_seconds": p.last_position_seconds,
            "is_completed": p.is_completed,
            "attendance_type": p.attendance_type.value,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in progress_list
    ]
