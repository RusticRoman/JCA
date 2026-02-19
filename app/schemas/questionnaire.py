import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.questionnaire import FieldType


class QuestionnaireFieldResponse(BaseModel):
    id: uuid.UUID
    label: str
    field_type: FieldType
    options: str
    order: int
    required: bool

    model_config = {"from_attributes": True}


class QuestionnaireResponse(BaseModel):
    id: uuid.UUID
    title: str
    month: int
    year: int
    is_active: bool
    fields: list[QuestionnaireFieldResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionnaireSubmitRequest(BaseModel):
    answers: dict[str, str]  # field_id -> answer


class QuestionnaireSubmitResponse(BaseModel):
    id: uuid.UUID
    questionnaire_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DispatchResponse(BaseModel):
    dispatched_to: int
    questionnaire_id: uuid.UUID
