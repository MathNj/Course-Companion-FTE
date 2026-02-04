#!/bin/bash
set -e

echo "Starting Course Companion FTE..."

# Check if using SQLite
if [[ "$DATABASE_URL" == sqlite* ]]; then
    echo "SQLite detected - using SQLAlchemy create_all()"
    python -c "
import asyncio
from app.config import settings
from app.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine

async def create_tables():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print('Database tables created successfully')

asyncio.run(create_tables())
"
else
    echo "PostgreSQL detected - running Alembic migrations"
    alembic upgrade head
fi

echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
