#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head 2>/dev/null || echo "No migrations to run, creating tables directly..."

echo "Ensuring tables exist..."
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.config import settings

async def init():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print('Tables created successfully.')

asyncio.run(init())
"

echo "Seeding curriculum..."
python scripts/seed_curriculum.py 2>/dev/null || echo "Curriculum already seeded."

echo "Seeding mentor..."
python scripts/seed_mentor.py 2>/dev/null || echo "Mentor already seeded."

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
