import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.beit_din import Case, CaseNote, CaseStatus


async def create_case(
    db: AsyncSession,
    student_id: uuid.UUID,
    title: str,
    description: str = "",
    rabbi_id: uuid.UUID | None = None,
) -> Case:
    case = Case(
        student_id=student_id,
        rabbi_id=rabbi_id,
        title=title,
        description=description,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


async def update_case_status(
    db: AsyncSession,
    case_id: uuid.UUID,
    status: CaseStatus | None = None,
    title: str | None = None,
    description: str | None = None,
) -> Case | None:
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        return None

    if status is not None:
        case.status = status
    if title is not None:
        case.title = title
    if description is not None:
        case.description = description

    await db.commit()
    await db.refresh(case)
    return case


async def add_note(
    db: AsyncSession,
    case_id: uuid.UUID,
    author_id: uuid.UUID,
    content: str,
) -> CaseNote:
    note = CaseNote(case_id=case_id, author_id=author_id, content=content)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note
