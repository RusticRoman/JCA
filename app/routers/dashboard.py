import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.assessment import QuizAttempt
from app.models.curriculum import Program, Semester, Subject, Video
from app.models.progress import VideoProgress
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
    QuizScoreSummary,
    SemesterProgressSummary,
    SubjectProgressSummary,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def _build_dashboard(db: AsyncSession, user: User) -> DashboardResponse:
    # Get all programs with semesters/subjects/videos
    programs_result = await db.execute(select(Program))
    programs = programs_result.scalars().all()

    # Get user's video progress
    progress_result = await db.execute(
        select(VideoProgress).where(VideoProgress.user_id == user.id)
    )
    progress_map = {p.video_id: p for p in progress_result.scalars().all()}

    # Get recent quiz attempts
    quiz_result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
        .limit(10)
    )
    quiz_attempts = quiz_result.scalars().all()

    semesters_summary = []
    total_videos = 0
    completed_videos = 0

    for program in programs:
        for semester in program.semesters:
            subjects_summary = []
            for subject in semester.subjects:
                vids_total = len(subject.videos)
                vids_completed = sum(
                    1 for v in subject.videos if progress_map.get(v.id) and progress_map[v.id].is_completed
                )
                total_videos += vids_total
                completed_videos += vids_completed

                subjects_summary.append(SubjectProgressSummary(
                    subject_id=subject.id,
                    subject_name=subject.name,
                    videos_completed=vids_completed,
                    videos_total=vids_total,
                ))

            semesters_summary.append(SemesterProgressSummary(
                semester_id=semester.id,
                semester_name=semester.name,
                semester_number=semester.number,
                subjects=subjects_summary,
            ))

    overall_pct = (completed_videos / total_videos * 100) if total_videos > 0 else 0.0

    quiz_scores = []
    for attempt in quiz_attempts:
        quiz_scores.append(QuizScoreSummary(
            quiz_id=attempt.quiz_id,
            quiz_title="",  # Would need join to get title
            score=attempt.score,
            total_questions=attempt.total_questions,
            passed=attempt.passed,
        ))

    return DashboardResponse(
        user_id=user.id,
        display_name=user.display_name,
        enrollment_semester=user.enrollment_semester,
        overall_completion_pct=round(overall_pct, 1),
        semesters=semesters_summary,
        recent_quiz_scores=quiz_scores,
    )


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _build_dashboard(db, current_user)


@router.get("/student/{student_id}", response_model=DashboardResponse)
async def get_student_dashboard(
    student_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import UserRole
    from fastapi import HTTPException

    if current_user.role not in (UserRole.RABBI, UserRole.TEACHER, UserRole.ADMIN, UserRole.BEIT_DIN):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(select(User).where(User.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return await _build_dashboard(db, student)
