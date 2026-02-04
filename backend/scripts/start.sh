#!/bin/bash
set -e

echo "Starting Course Companion FTE..."
echo "Starting Uvicorn server (skip alembic for now)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

