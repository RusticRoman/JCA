import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.gcp.calendar_sync import create_calendar_event
from app.models.event import Event, EventRegistration
from app.models.user import User


async def register_for_event(
    db: AsyncSession,
    event_id: uuid.UUID,
    user: User,
) -> EventRegistration:
    """Register a user for an event. Creates a calendar event if applicable."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise ValueError("Event not found")

    # Check capacity
    if event.capacity > 0:
        count_result = await db.execute(
            select(func.count(EventRegistration.id)).where(
                EventRegistration.event_id == event_id
            )
        )
        current_count = count_result.scalar() or 0
        if current_count >= event.capacity:
            raise ValueError("Event is full")

    # Check for existing registration
    existing = await db.execute(
        select(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Already registered")

    registration = EventRegistration(event_id=event_id, user_id=user.id)
    db.add(registration)

    # Create calendar event
    calendar_event_id = create_calendar_event(
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        attendee_email=user.email,
    )

    if not event.google_calendar_event_id:
        event.google_calendar_event_id = calendar_event_id

    await db.commit()
    await db.refresh(registration)
    return registration


async def unregister_from_event(
    db: AsyncSession,
    event_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        select(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user_id,
        )
    )
    registration = result.scalar_one_or_none()
    if not registration:
        return False

    await db.delete(registration)
    await db.commit()
    return True
