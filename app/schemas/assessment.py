import uuid
from typing import Literal

from pydantic import BaseModel


class QuestionResponse(BaseModel):
    id: uuid.UUID
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    order: int

    model_config = {"from_attributes": True}


class QuizResponse(BaseModel):
    id: uuid.UUID
    video_id: uuid.UUID
    title: str
    passing_score: int
    questions: list[QuestionResponse] = []

    model_config = {"from_attributes": True}


class AnswerSubmission(BaseModel):
    question_id: uuid.UUID
    selected_option: Literal["A", "B", "C", "D"]


class QuizSubmitRequest(BaseModel):
    answers: list[AnswerSubmission]


class QuizAttemptResponse(BaseModel):
    id: uuid.UUID
    quiz_id: uuid.UUID
    score: int
    total_questions: int
    passed: bool

    model_config = {"from_attributes": True}
