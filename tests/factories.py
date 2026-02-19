import uuid

from app.models.curriculum import Program, Semester, Subject, Video
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
