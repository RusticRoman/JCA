import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse

router = APIRouter(prefix="/rabbi", tags=["rabbi"])


@router.get("/students", response_model=list[UserResponse])
async def list_students(
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.role == UserRole.STUDENT, User.is_active == True)
    )
    return result.scalars().all()


@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    from app.routers.dashboard import _build_dashboard

    result = await db.execute(select(User).where(User.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return await _build_dashboard(db, student)
