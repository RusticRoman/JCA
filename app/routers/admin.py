"""Admin endpoints for user and content management."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminUserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None
    enrollment_semester: int | None = None


class PlatformStats(BaseModel):
    total_users: int
    active_students: int
    total_rabbis: int
    total_teachers: int


@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    total = (await db.execute(select(func.count(User.id)))).scalar() or 0
    students = (await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.STUDENT, User.is_active.is_(True))
    )).scalar() or 0
    rabbis = (await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.RABBI)
    )).scalar() or 0
    teachers = (await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.TEACHER)
    )).scalar() or 0
    return PlatformStats(
        total_users=total, active_students=students,
        total_rabbis=rabbis, total_teachers=teachers,
    )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    role: UserRole | None = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).order_by(User.created_at.desc())
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query.offset(skip).limit(min(limit, 100)))
    return result.scalars().all()


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    req: AdminUserUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
    if req.enrollment_semester is not None:
        user.enrollment_semester = req.enrollment_semester

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user
