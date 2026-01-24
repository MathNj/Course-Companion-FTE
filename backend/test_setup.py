#!/usr/bin/env python3
"""
Infrastructure Test Script

Tests the backend setup without requiring external services.
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import os
    os.system("chcp 65001 > nul 2>&1")

print("=" * 60)
print("Course Companion FTE - Infrastructure Test")
print("=" * 60)
print()

# Test 1: Python Version
print("[*] Testing Python version...")
version_info = sys.version_info
if version_info >= (3, 11):
    print(f"  [OK] Python {version_info.major}.{version_info.minor}.{version_info.micro} (>= 3.11 required)")
else:
    print(f"  [FAIL] Python {version_info.major}.{version_info.minor}.{version_info.micro} (3.11+ required)")
    sys.exit(1)

# Test 2: Import Dependencies
print("\n[*] Testing package imports...")
try:
    import fastapi
    print(f"  [OK] FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"  [FAIL] FastAPI not installed: {e}")
    print("     Run: pip install -e \".[dev]\"")
    sys.exit(1)

try:
    import sqlalchemy
    print(f"  [OK] SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"  [FAIL] SQLAlchemy not installed: {e}")
    sys.exit(1)

try:
    import pydantic
    print(f"  [OK] Pydantic {pydantic.__version__}")
except ImportError as e:
    print(f"  [FAIL] Pydantic not installed: {e}")
    sys.exit(1)

try:
    import redis
    print(f"  [OK] redis-py {redis.__version__}")
except ImportError as e:
    print(f"  [FAIL] redis-py not installed: {e}")
    sys.exit(1)

try:
    import alembic
    print(f"  [OK] Alembic {alembic.__version__}")
except ImportError as e:
    print(f"  [FAIL] Alembic not installed: {e}")
    sys.exit(1)

# Test 3: Application Imports
print("\n[*] Testing application imports...")
try:
    from app.config import settings
    print(f"  [OK] app.config imported")
    print(f"     App Name: {settings.app_name}")
    print(f"     Environment: {settings.app_env}")
except ImportError as e:
    print(f"  [FAIL] Failed to import app.config: {e}")
    sys.exit(1)

try:
    from app.models.base import Base, TimestampMixin
    print(f"  [OK] app.models.base imported")
except ImportError as e:
    print(f"  [FAIL] Failed to import app.models.base: {e}")
    sys.exit(1)

# Test 4: Configuration
print("\n[*] Testing configuration...")
print(f"  API Prefix: {settings.api_v1_prefix}")
print(f"  Database URL: {settings.database_url[:50]}... (truncated)")
print(f"  Redis URL: {settings.redis_url}")
print(f"  JWT Algorithm: {settings.jwt_algorithm}")
print(f"  Chapter Count: {settings.chapter_count}")

# Test 5: File Structure
print("\n[*] Testing file structure...")
required_dirs = [
    "app/api/v1",
    "app/models",
    "app/services",
    "app/schemas",
    "app/utils",
    "app/skills",
    "alembic/versions",
]

for dir_path in required_dirs:
    full_path = Path(__file__).parent / dir_path
    if full_path.exists():
        print(f"  [OK] {dir_path}/")
    else:
        print(f"  [FAIL] {dir_path}/ (missing)")

# Test 6: Alembic Configuration
print("\n[*] Testing Alembic configuration...")
alembic_ini = Path(__file__).parent / "alembic.ini"
if alembic_ini.exists():
    print(f"  [OK] alembic.ini exists")
else:
    print(f"  [FAIL] alembic.ini missing")

alembic_env = Path(__file__).parent / "alembic" / "env.py"
if alembic_env.exists():
    print(f"  [OK] alembic/env.py exists")
else:
    print(f"  [FAIL] alembic/env.py missing")

# Test 7: Environment File
print("\n[*] Testing environment configuration...")
env_example = Path(__file__).parent / ".env.example"
if env_example.exists():
    print(f"  [OK] .env.example exists")
else:
    print(f"  [FAIL] .env.example missing")

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print(f"  [OK] .env exists (configured)")
else:
    print(f"  [WARN]  .env not found (using defaults)")
    print(f"     Run: cp .env.example .env")

print("\n" + "=" * 60)
print("Infrastructure Test Complete!")
print("=" * 60)
print()
print("Next Steps:")
print("1. Start Docker Desktop (if using Docker)")
print("2. Run: docker-compose up -d postgres redis")
print("3. Configure .env file with database credentials")
print("4. Run: alembic upgrade head (when models are created)")
print("5. Begin Phase 2 implementation")
print()
