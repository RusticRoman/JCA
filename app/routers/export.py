"""Data export endpoints for admin reporting."""
import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_db
from app.models.progress import VideoProgress
from app.models.questionnaire import QuestionnaireResponse
from app.models.user import User, UserRole

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/progress.csv")
async def export_progress(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoProgress).order_by(VideoProgress.created_at.desc())
    )
    rows = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "video_id", "last_position_seconds", "total_duration_seconds", "is_completed", "attendance_type", "created_at"])
    for r in rows:
        writer.writerow([
            str(r.user_id), str(r.video_id), r.last_position_seconds,
            r.total_duration_seconds, r.is_completed, r.attendance_type.value,
            r.created_at.isoformat() if r.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=progress.csv"},
    )


@router.get("/questionnaire-responses.csv")
async def export_questionnaire_responses(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(QuestionnaireResponse).order_by(QuestionnaireResponse.created_at.desc())
    )
    rows = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "questionnaire_id", "user_id", "answers", "created_at"])
    for r in rows:
        writer.writerow([
            str(r.id), str(r.questionnaire_id), str(r.user_id),
            r.answers, r.created_at.isoformat() if r.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=questionnaire-responses.csv"},
    )


@router.get("/users.csv")
async def export_users(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    rows = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "display_name", "role", "is_active", "enrollment_semester", "created_at"])
    for r in rows:
        writer.writerow([
            str(r.id), r.email, r.display_name, r.role.value,
            r.is_active, r.enrollment_semester,
            r.created_at.isoformat() if r.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )
