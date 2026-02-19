import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_db
from app.models.beit_din import Case
from app.models.user import User, UserRole
from app.schemas.beit_din import (
    CaseCreateRequest,
    CaseNoteCreate,
    CaseNoteResponse,
    CaseResponse,
    CaseUpdateRequest,
)
from app.services.beit_din_service import add_note, create_case, update_case_status

router = APIRouter(prefix="/beit-din", tags=["beit-din"])


@router.get("/cases", response_model=list[CaseResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.BEIT_DIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Case).order_by(Case.created_at.desc()).offset(skip).limit(min(limit, 100))
    )
    return result.scalars().all()


@router.post("/cases", response_model=CaseResponse, status_code=201)
async def create_case_endpoint(
    req: CaseCreateRequest,
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.BEIT_DIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    case = await create_case(
        db=db,
        student_id=req.student_id,
        title=req.title,
        description=req.description,
        rabbi_id=current_user.id if current_user.role == UserRole.RABBI else None,
    )
    return case


@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.BEIT_DIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    req: CaseUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.BEIT_DIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    case = await update_case_status(
        db=db, case_id=case_id, status=req.status, title=req.title, description=req.description
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/cases/{case_id}/notes", response_model=CaseNoteResponse, status_code=201)
async def create_note(
    case_id: uuid.UUID,
    req: CaseNoteCreate,
    current_user: User = Depends(require_roles(UserRole.RABBI, UserRole.BEIT_DIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    note = await add_note(db=db, case_id=case_id, author_id=current_user.id, content=req.content)
    return note
