import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_roles
from app.dependencies import get_db
from app.models.resource import FAQ
from app.models.user import User, UserRole

router = APIRouter(prefix="/faq", tags=["faq"])


class FAQResponse(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    order: int

    model_config = {"from_attributes": True}


class FAQCreateRequest(BaseModel):
    question: str
    answer: str
    order: int = 0


class FAQUpdateRequest(BaseModel):
    question: str | None = None
    answer: str | None = None
    order: int | None = None
    is_published: bool | None = None


@router.get("", response_model=list[FAQResponse])
async def list_faqs(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Public endpoint - no auth required."""
    result = await db.execute(
        select(FAQ).where(FAQ.is_published.is_(True)).order_by(FAQ.order).offset(skip).limit(min(limit, 100))
    )
    return result.scalars().all()


@router.post("", response_model=FAQResponse, status_code=201)
async def create_faq(
    req: FAQCreateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    faq = FAQ(question=req.question, answer=req.answer, order=req.order)
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    return faq


@router.patch("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: uuid.UUID,
    req: FAQUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalar_one_or_none()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    if req.question is not None:
        faq.question = req.question
    if req.answer is not None:
        faq.answer = req.answer
    if req.order is not None:
        faq.order = req.order
    if req.is_published is not None:
        faq.is_published = req.is_published

    await db.commit()
    await db.refresh(faq)
    return faq
