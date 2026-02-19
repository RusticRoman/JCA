import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventRegistrationResponse, EventResponse
from app.services.event_service import register_for_event, unregister_from_event

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Event).order_by(Event.start_time))
    events = result.scalars().all()
    return [
        EventResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            event_type=e.event_type,
            start_time=e.start_time,
            end_time=e.end_time,
            location=e.location,
            capacity=e.capacity,
            registered_count=len(e.registrations),
        )
        for e in events
    ]


@router.post("/{event_id}/register", response_model=EventRegistrationResponse, status_code=201)
async def register(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        registration = await register_for_event(db=db, event_id=event_id, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return registration


@router.delete("/{event_id}/register", status_code=204)
async def unregister(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await unregister_from_event(db=db, event_id=event_id, user_id=current_user.id)
    if not removed:
        raise HTTPException(status_code=404, detail="Registration not found")
