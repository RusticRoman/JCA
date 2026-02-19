import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    firebase_uid: str
    email: EmailStr
    display_name: str = ""


class UserResponse(BaseModel):
    id: uuid.UUID
    firebase_uid: str
    email: str
    display_name: str
    role: UserRole
    is_active: bool
    hebrew_name: str | None
    enrollment_semester: int
    program_year: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
    hebrew_name: str | None = None
