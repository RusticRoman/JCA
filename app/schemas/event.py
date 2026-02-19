import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.event import EventType


class EventResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    event_type: EventType
    start_time: datetime
    end_time: datetime
    location: str
    capacity: int
    registered_count: int = 0

    model_config = {"from_attributes": True}


class EventRegistrationResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
