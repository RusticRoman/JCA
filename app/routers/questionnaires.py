import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_current_user, get_db
from app.models.questionnaire import MonthlyQuestionnaire
from app.models.questionnaire import QuestionnaireResponse as QResponseModel
from app.models.user import User, UserRole
from app.schemas.questionnaire import (
    DispatchResponse,
    QuestionnaireResponse,
    QuestionnaireSubmitRequest,
    QuestionnaireSubmitResponse,
)
from app.services.cloud_tasks_service import dispatch_questionnaire

router = APIRouter(prefix="/questionnaires", tags=["questionnaires"])


@router.get("/current", response_model=QuestionnaireResponse | None)
async def get_current_questionnaire(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MonthlyQuestionnaire)
        .where(MonthlyQuestionnaire.is_active == True)
        .order_by(MonthlyQuestionnaire.year.desc(), MonthlyQuestionnaire.month.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.post("/{questionnaire_id}/submit", response_model=QuestionnaireSubmitResponse)
async def submit_questionnaire(
    questionnaire_id: uuid.UUID,
    req: QuestionnaireSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify questionnaire exists
    result = await db.execute(
        select(MonthlyQuestionnaire).where(MonthlyQuestionnaire.id == questionnaire_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    response = QResponseModel(
        questionnaire_id=questionnaire_id,
        user_id=current_user.id,
        answers=json.dumps(req.answers),
    )
    db.add(response)
    await db.commit()
    await db.refresh(response)
    return response


@router.post("/dispatch", response_model=DispatchResponse)
async def dispatch(
    questionnaire_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    count = await dispatch_questionnaire(db, questionnaire_id)
    return DispatchResponse(dispatched_to=count, questionnaire_id=questionnaire_id)
