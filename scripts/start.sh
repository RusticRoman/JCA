#!/bin/sh
set -e

echo "Running migrations..."
if ! alembic upgrade head; then
    echo "Migrations failed — falling back to create_all..."
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
fi

echo "Seeding curriculum..."
python scripts/seed_curriculum.py || echo "WARNING: Curriculum seeding failed"

echo "Seeding mentor..."
python scripts/seed_mentor.py || echo "WARNING: Mentor seeding failed"

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
