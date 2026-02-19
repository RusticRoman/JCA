"""Curriculum service for semester/subject progression and program year gating."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum import Program, Semester
from app.models.user import User


async def get_accessible_semesters(db: AsyncSession, user: User) -> list[Semester]:
    """Get semesters accessible to a user based on their program year."""
    result = await db.execute(
        select(Semester)
        .join(Program)
        .where(Program.year <= user.program_year)
        .order_by(Semester.number)
    )
    return list(result.scalars().all())
