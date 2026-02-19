import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.beit_din import CaseStatus


class CaseCreateRequest(BaseModel):
    student_id: uuid.UUID
    title: str
    description: str = ""


class CaseUpdateRequest(BaseModel):
    status: CaseStatus | None = None
    title: str | None = None
    description: str | None = None


class CaseNoteCreate(BaseModel):
    content: str


class CaseNoteResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseDocumentResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    uploaded_by: uuid.UUID
    filename: str
    gcs_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    rabbi_id: uuid.UUID | None
    status: CaseStatus
    title: str
    description: str
    notes: list[CaseNoteResponse] = []
    documents: list[CaseDocumentResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
