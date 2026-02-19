import uuid

from pydantic import BaseModel


class VideoProgressSummary(BaseModel):
    video_id: uuid.UUID
    title: str
    is_completed: bool
    last_position_seconds: int
    total_duration_seconds: int


class SubjectProgressSummary(BaseModel):
    subject_id: uuid.UUID
    subject_name: str
    videos_completed: int
    videos_total: int


class SemesterProgressSummary(BaseModel):
    semester_id: uuid.UUID
    semester_name: str
    semester_number: int
    subjects: list[SubjectProgressSummary]


class DashboardResponse(BaseModel):
    user_id: uuid.UUID
    display_name: str
    enrollment_semester: int
    overall_completion_pct: float
    semesters: list[SemesterProgressSummary]
    recent_quiz_scores: list["QuizScoreSummary"]


class QuizScoreSummary(BaseModel):
    quiz_id: uuid.UUID
    quiz_title: str
    score: int
    total_questions: int
    passed: bool
