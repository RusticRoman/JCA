import uuid
from datetime import datetime, timezone

from app.models.assessment import Answer, Question, Quiz, QuizAttempt
from app.models.beit_din import Case, CaseNote
from app.models.curriculum import Program, Semester, Subject, Video
from app.models.event import Event, EventRegistration, EventType
from app.models.questionnaire import MonthlyQuestionnaire, QuestionnaireField
from app.models.resource import FAQ, Resource
from app.models.user import User, UserRole


def make_user(**kwargs) -> User:
    defaults = {
        "firebase_uid": f"uid-{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@test.com",
        "display_name": "Test User",
        "role": UserRole.STUDENT,
    }
    defaults.update(kwargs)
    return User(**defaults)


def make_program(**kwargs) -> Program:
    defaults = {"name": "Test Program", "description": "A test program", "year": 1}
    defaults.update(kwargs)
    return Program(**defaults)


def make_semester(program_id: uuid.UUID, **kwargs) -> Semester:
    defaults = {
        "program_id": program_id,
        "number": 1,
        "name": "Test Semester",
        "description": "A test semester",
    }
    defaults.update(kwargs)
    return Semester(**defaults)


def make_subject(semester_id: uuid.UUID, **kwargs) -> Subject:
    defaults = {
        "semester_id": semester_id,
        "name": "Test Subject",
        "description": "A test subject",
        "order": 1,
    }
    defaults.update(kwargs)
    return Subject(**defaults)


def make_video(subject_id: uuid.UUID, **kwargs) -> Video:
    defaults = {
        "subject_id": subject_id,
        "title": "Test Video",
        "description": "A test video",
        "gcs_path": "videos/test.mp4",
        "duration_seconds": 2700,
        "order": 1,
    }
    defaults.update(kwargs)
    return Video(**defaults)


def make_quiz(video_id: uuid.UUID, **kwargs) -> Quiz:
    defaults = {
        "video_id": video_id,
        "title": "Test Quiz",
        "passing_score": 70,
    }
    defaults.update(kwargs)
    return Quiz(**defaults)


def make_question(quiz_id: uuid.UUID, **kwargs) -> Question:
    defaults = {
        "quiz_id": quiz_id,
        "text": "What is the answer?",
        "option_a": "Option A",
        "option_b": "Option B",
        "option_c": "Option C",
        "option_d": "Option D",
        "correct_option": "A",
        "order": 0,
    }
    defaults.update(kwargs)
    return Question(**defaults)


def make_event(**kwargs) -> Event:
    defaults = {
        "title": "Test Event",
        "description": "A test event",
        "event_type": EventType.OTHER,
        "start_time": datetime(2026, 6, 15, 9, 0, tzinfo=timezone.utc),
        "end_time": datetime(2026, 6, 15, 17, 0, tzinfo=timezone.utc),
        "location": "Test Location",
        "capacity": 50,
    }
    defaults.update(kwargs)
    return Event(**defaults)


def make_case(student_id: uuid.UUID, **kwargs) -> Case:
    defaults = {
        "student_id": student_id,
        "title": "Test Case",
        "description": "A test beit din case",
    }
    defaults.update(kwargs)
    return Case(**defaults)


def make_questionnaire(**kwargs) -> MonthlyQuestionnaire:
    defaults = {
        "title": "Monthly Check-in",
        "month": 2,
        "year": 2026,
        "is_active": True,
    }
    defaults.update(kwargs)
    return MonthlyQuestionnaire(**defaults)


def make_resource(**kwargs) -> Resource:
    defaults = {
        "title": "Test Resource",
        "description": "A test resource",
        "category": "general",
        "gcs_path": "resources/test.pdf",
        "filename": "test.pdf",
    }
    defaults.update(kwargs)
    return Resource(**defaults)


def make_faq(**kwargs) -> FAQ:
    defaults = {
        "question": "What is this?",
        "answer": "This is a test FAQ.",
        "order": 0,
        "is_published": True,
    }
    defaults.update(kwargs)
    return FAQ(**defaults)
