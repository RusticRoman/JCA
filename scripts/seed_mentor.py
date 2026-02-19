"""Seed mentors, synthetic students, and assign students to mentors."""
import asyncio
import hashlib
import random
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models.curriculum import Program
from app.models.progress import AttendanceType, VideoProgress
from app.models.user import User, UserRole


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64
    ).hex()
    return f"{salt}:{hashed}"


MENTORS = [
    {
        "email": "mentor@jca.org",
        "password": "mentor123",
        "display_name": "Rabbi David Cohen",
        "hebrew_name": "David ben Avraham",
    },
    {
        "email": "mentor2@jca.org",
        "password": "mentor456",
        "display_name": "Rabbi Sarah Levy",
        "hebrew_name": "Sarah bat Miriam",
    },
]

STUDENTS = [
    {"display_name": "Anna Petrova", "email": "anna.p@example.com", "semester": 2},
    {"display_name": "Michael Torres", "email": "michael.t@example.com", "semester": 1},
    {"display_name": "Jessica Wang", "email": "jessica.w@example.com", "semester": 3},
    {"display_name": "Daniel Goldstein", "email": "daniel.g@example.com", "semester": 4},
    {"display_name": "Emily Robinson", "email": "emily.r@example.com", "semester": 1},
    {"display_name": "James Murphy", "email": "james.m@example.com", "semester": 2},
    {"display_name": "Sophia Martinez", "email": "sophia.m@example.com", "semester": 5},
    {"display_name": "Ethan Brooks", "email": "ethan.b@example.com", "semester": 3},
    {"display_name": "Olivia Novak", "email": "olivia.n@example.com", "semester": 6},
    {"display_name": "Benjamin Katz", "email": "benjamin.k@example.com", "semester": 1},
]

# Students assigned to mentor@jca.org (first 6), rest to mentor2@jca.org
MENTOR1_COUNT = 6


async def seed():
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # ── Create mentors ────────────────────────────────────────────
        mentor_objs = []
        for m in MENTORS:
            result = await session.execute(
                select(User).where(User.email == m["email"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"Mentor already exists: {existing.email}")
                mentor_objs.append(existing)
            else:
                mentor = User(
                    firebase_uid=f"local:{_hash_password(m['password'])}",
                    email=m["email"],
                    display_name=m["display_name"],
                    role=UserRole.RABBI,
                    hebrew_name=m["hebrew_name"],
                )
                session.add(mentor)
                await session.flush()
                mentor_objs.append(mentor)
                print(f"Created mentor: {mentor.display_name} ({mentor.email})")
                print(f"  Login: {m['email']} / {m['password']}")

        mentor1, mentor2 = mentor_objs[0], mentor_objs[1]

        # ── Create synthetic students ─────────────────────────────────
        student_objs = []
        for s in STUDENTS:
            result = await session.execute(
                select(User).where(User.email == s["email"])
            )
            if result.scalar_one_or_none():
                print(f"Student already exists: {s['email']}")
                continue

            student = User(
                firebase_uid=f"local:{_hash_password('student123')}",
                email=s["email"],
                display_name=s["display_name"],
                enrollment_semester=s["semester"],
            )
            session.add(student)
            await session.flush()
            student_objs.append(student)
            print(f"Created student: {student.display_name} (semester {s['semester']})")

        # ── Assign students to mentors ────────────────────────────────
        # Assign ALL unassigned students (including any registered via UI)
        result = await session.execute(
            select(User).where(
                User.role == UserRole.STUDENT,
                User.mentor_id.is_(None),
            )
        )
        unassigned = result.scalars().all()

        for i, student in enumerate(unassigned):
            if i < MENTOR1_COUNT:
                student.mentor_id = mentor1.id
                print(f"  {student.display_name} -> {mentor1.display_name}")
            else:
                student.mentor_id = mentor2.id
                print(f"  {student.display_name} -> {mentor2.display_name}")

        await session.flush()

        # ── Generate synthetic video progress ─────────────────────────
        programs_result = await session.execute(select(Program))
        programs = programs_result.scalars().all()
        all_videos = []
        for program in programs:
            for semester in program.semesters:
                for subject in semester.subjects:
                    for video in subject.videos:
                        all_videos.append((semester.number, video))

        # For each student, simulate progress based on their enrollment semester
        all_students_result = await session.execute(
            select(User).where(User.role == UserRole.STUDENT)
        )
        all_students = all_students_result.scalars().all()

        for student in all_students:
            # Check if student already has progress
            existing_progress = await session.execute(
                select(VideoProgress).where(VideoProgress.user_id == student.id).limit(1)
            )
            if existing_progress.scalar_one_or_none():
                continue

            for sem_num, video in all_videos:
                # Complete all videos in semesters before current enrollment
                if sem_num < student.enrollment_semester:
                    vp = VideoProgress(
                        user_id=student.id,
                        video_id=video.id,
                        last_position_seconds=video.duration_seconds,
                        total_duration_seconds=video.duration_seconds,
                        is_completed=True,
                        attendance_type=random.choice(
                            [AttendanceType.LIVE, AttendanceType.RECORDED, AttendanceType.RECORDED]
                        ),
                    )
                    session.add(vp)
                # Partially complete videos in current semester
                elif sem_num == student.enrollment_semester:
                    if random.random() < 0.6:  # 60% chance of some progress
                        position = random.randint(
                            int(video.duration_seconds * 0.2),
                            video.duration_seconds,
                        )
                        completed = position >= video.duration_seconds * 0.95
                        vp = VideoProgress(
                            user_id=student.id,
                            video_id=video.id,
                            last_position_seconds=position,
                            total_duration_seconds=video.duration_seconds,
                            is_completed=completed,
                            attendance_type=random.choice(
                                [AttendanceType.LIVE, AttendanceType.RECORDED]
                            ),
                        )
                        session.add(vp)
                # Future semesters: no progress

            print(f"  Generated progress for {student.display_name} (sem {student.enrollment_semester})")

        await session.commit()

    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
