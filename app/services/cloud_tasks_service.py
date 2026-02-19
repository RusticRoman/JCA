import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.gcp.cloud_tasks import create_task
from app.models.questionnaire import MonthlyQuestionnaire
from app.models.user import User, UserRole


async def dispatch_questionnaire(
    db: AsyncSession,
    questionnaire_id: uuid.UUID,
) -> int:
    """Schedule questionnaire notification for all active students.
    Returns the number of tasks dispatched."""
    result = await db.execute(
        select(User).where(User.role == UserRole.STUDENT, User.is_active.is_(True))
    )
    students = result.scalars().all()

    dispatched = 0
    for student in students:
        url = f"{settings.app_base_url}/questionnaires/{questionnaire_id}/notify"
        payload = {
            "user_id": str(student.id),
            "questionnaire_id": str(questionnaire_id),
        }
        create_task(url=url, payload=payload)
        dispatched += 1

    return dispatched
