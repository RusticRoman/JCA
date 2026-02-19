import uuid
from datetime import datetime

from pydantic import BaseModel


class VideoResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    description: str
    duration_seconds: int
    order: int

    model_config = {"from_attributes": True}


class SubjectResponse(BaseModel):
    id: uuid.UUID
    semester_id: uuid.UUID
    name: str
    description: str
    order: int
    videos: list[VideoResponse] = []

    model_config = {"from_attributes": True}


class SemesterResponse(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    number: int
    name: str
    description: str
    subjects: list[SubjectResponse] = []

    model_config = {"from_attributes": True}


class ProgramResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    year: int
    semesters: list[SemesterResponse] = []

    model_config = {"from_attributes": True}
