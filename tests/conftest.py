import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.user import User, UserRole

# Import all models so Base.metadata is complete
from app.models import *  # noqa: F401, F403

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        yield session


@pytest.fixture
async def student_user(db: AsyncSession) -> User:
    user = User(
        firebase_uid="test-student-uid",
        email="student@test.com",
        display_name="Test Student",
        role=UserRole.STUDENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def rabbi_user(db: AsyncSession) -> User:
    user = User(
        firebase_uid="test-rabbi-uid",
        email="rabbi@test.com",
        display_name="Test Rabbi",
        role=UserRole.RABBI,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def teacher_user(db: AsyncSession) -> User:
    user = User(
        firebase_uid="test-teacher-uid",
        email="teacher@test.com",
        display_name="Test Teacher",
        role=UserRole.TEACHER,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def beit_din_user(db: AsyncSession) -> User:
    user = User(
        firebase_uid="test-beitdin-uid",
        email="beitdin@test.com",
        display_name="Test Beit Din",
        role=UserRole.BEIT_DIN,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        firebase_uid="test-admin-uid",
        email="admin@test.com",
        display_name="Test Admin",
        role=UserRole.ADMIN,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _override_deps(app, db_session: AsyncSession, user: User):
    """Override app dependencies for testing."""
    from app.dependencies import get_current_user, get_db

    async def _get_db():
        yield db_session

    async def _get_user():
        return user

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _get_user


@pytest.fixture
async def client(db: AsyncSession, student_user: User) -> AsyncGenerator[AsyncClient, None]:
    from app.main import create_app

    app = create_app()
    _override_deps(app, db, student_user)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def make_client(db: AsyncSession):
    """Factory to create a test client with a specific user."""

    async def _make(user: User) -> AsyncClient:
        from app.main import create_app

        app = create_app()
        _override_deps(app, db, user)
        return AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )

    return _make
