import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.curriculum import Program, Semester, Subject, Video
from app.models.user import User
from app.schemas.curriculum import (
    ProgramResponse,
    SemesterResponse,
    SubjectResponse,
    VideoResponse,
)

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/programs", response_model=list[ProgramResponse])
async def list_programs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Program))
    return result.scalars().all()


@router.get("/semesters/{semester_id}", response_model=SemesterResponse)
async def get_semester(
    semester_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Semester).where(Semester.id == semester_id))
    semester = result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    return semester


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video
