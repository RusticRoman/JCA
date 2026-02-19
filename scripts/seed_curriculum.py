"""Seed the database with 8 semesters x 5 subjects curriculum data."""
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base
from app.models.curriculum import Program, Semester, Subject, Video

CURRICULUM = {
    1: ("Foundations of Judaism", [
        "Jewish Beliefs/Values",
        "Jewish History Overview",
        "Hebrew Alphabet Basics",
        "Jewish Identity Concepts",
        "Daily Jewish Living Intro",
    ]),
    2: ("Shabbat", [
        "Shabbat Meaning",
        "Candle Lighting/Kiddush",
        "Shabbat Prohibitions",
        "Shabbat Meal Hosting",
        "Havdalah Ritual",
    ]),
    3: ("Kashrut", [
        "Kashrut Sources",
        "Meat/Dairy Separation",
        "Kosher Kitchen Setup",
        "Eating Out Kosher",
        "Kosher Market Visit",
    ]),
    4: ("Prayer & Blessings", [
        "Brachot Philosophy",
        "Prayer Structure",
        "Food Blessings",
        "Siddur Navigation",
        "Leading Prayers",
    ]),
    5: ("Jewish Holidays", [
        "Holiday Calendar",
        "High Holidays Deep Dive",
        "Pilgrim Festivals",
        "Minor Holidays",
        "Holiday Celebration Practice",
    ]),
    6: ("Family & Lifecycle", [
        "Family Purity Laws",
        "Mikveh Practice",
        "Lifecycle Events",
        "Jewish Family Structure",
        "Lifecycle Attendance",
    ]),
    7: ("Jewish Living & Ethics", [
        "Tzedakah Practice",
        "Mitzvot Daily Living",
        "Mezuzah Installation",
        "Jewish/Non-Jewish Balance",
        "Home Rituals",
    ]),
    8: ("Identity & Completion", [
        "Denominational Differences",
        "Israel History",
        "Antisemitism Education",
        "Beit Din Preparation",
        "Hebrew Name Selection",
    ]),
}


async def seed():
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Check if already seeded
        existing = await session.execute(select(Program).where(Program.name == "Conversion Program"))
        if existing.scalar_one_or_none():
            print("Curriculum already seeded — skipping.")
            await engine.dispose()
            return

        program = Program(name="Conversion Program", description="Standard conversion curriculum", year=1)
        session.add(program)
        await session.flush()

        for sem_num, (sem_name, subjects) in CURRICULUM.items():
            semester = Semester(
                program_id=program.id,
                number=sem_num,
                name=sem_name,
                description=f"Semester {sem_num}: {sem_name}",
            )
            session.add(semester)
            await session.flush()

            for idx, subj_name in enumerate(subjects):
                subject = Subject(
                    semester_id=semester.id,
                    name=subj_name,
                    description=f"Study of {subj_name}",
                    order=idx + 1,
                )
                session.add(subject)
                await session.flush()

                video = Video(
                    subject_id=subject.id,
                    title=f"{subj_name} - Lecture",
                    description=f"Video lecture on {subj_name}",
                    gcs_path=f"videos/semester-{sem_num}/{subj_name.lower().replace(' ', '-').replace('/', '-')}.mp4",
                    duration_seconds=2700,  # 45 minutes
                    order=1,
                )
                session.add(video)

        await session.commit()
        print(f"Seeded {len(CURRICULUM)} semesters with {sum(len(s) for _, s in CURRICULUM.values())} subjects")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
