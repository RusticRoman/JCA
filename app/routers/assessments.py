import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.assessment import QuizAttemptResponse, QuizResponse, QuizSubmitRequest
from app.services.assessment_service import get_quiz, grade_quiz

router = APIRouter(prefix="/quizzes", tags=["assessments"])


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz_endpoint(
    quiz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizAttemptResponse)
async def submit_quiz(
    quiz_id: uuid.UUID,
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        attempt = await grade_quiz(
            db=db,
            quiz_id=quiz_id,
            user_id=current_user.id,
            submissions=[a.model_dump() for a in req.answers],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return attempt
