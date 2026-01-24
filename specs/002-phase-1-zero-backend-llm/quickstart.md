# Quickstart Guide: Phase 1 - Zero-Backend-LLM Course Companion

**Date**: 2026-01-24
**Feature**: Phase 1 - Zero-Backend-LLM Course Companion
**Purpose**: Get development environment running in under 15 minutes

## Prerequisites

- Python 3.11 or higher
- Docker Desktop (for PostgreSQL + Redis)
- Git
- Code editor (VS Code, PyCharm, etc.)

## Quick Start (5 Steps)

### 1. Clone Repository

```bash
git checkout 002-phase-1-zero-backend-llm
cd Course-Companion-FTE
```

### 2. Start Database Services

```bash
# Start PostgreSQL and Redis via Docker Compose
docker-compose up -d

# Verify services are running
docker ps
# Should show: postgres:15 and redis:7 containers
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings (see Configuration section below)

# Run database migrations
alembic upgrade head

# Seed initial data
python scripts/seed_content.py
```

### 4. Run Backend Server

```bash
# From backend/ directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend now running at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 5. Test API

```bash
# In a new terminal, test authentication
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'

# Copy the access_token from response
export TOKEN="<your_access_token>"

# Get chapters
curl http://localhost:8000/api/v1/chapters \
  -H "Authorization: Bearer $TOKEN"
```

---

## Detailed Setup

### Configuration (.env File)

Create `backend/.env` with the following variables:

```env
# Database (PostgreSQL via Docker Compose)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/course_companion

# Redis Cache (via Docker Compose)
REDIS_URL=redis://localhost:6379/0

# Cloudflare R2 (S3-Compatible Storage)
# For local development, can use MinIO or local files
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_r2_access_key
R2_SECRET_KEY=your_r2_secret_key
R2_BUCKET_NAME=course-companion-content

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=43200  # 30 days

# Application Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Email Service (Optional - for password reset)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
FROM_EMAIL=noreply@course-companion.example.com

# Content Storage Mode (local or r2)
CONTENT_SOURCE=local  # Use local files for development
# CONTENT_SOURCE=r2   # Use Cloudflare R2 for production
```

### Docker Compose Services

`docker-compose.yml` (in repository root):

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: course_companion_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: course_companion
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: course_companion_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

### Database Initialization

```bash
cd backend

# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Verify database
psql postgresql://postgres:postgres@localhost:5432/course_companion -c "\dt"
# Should show: students, chapter_progress, quiz_attempts, streaks tables
```

### Seed Content

```bash
cd backend

# Seed course content (chapters + quizzes)
python scripts/seed_content.py

# This uploads content from content/ directory to:
# - Cloudflare R2 (if CONTENT_SOURCE=r2)
# - Local file system (if CONTENT_SOURCE=local)

# Create test users
python scripts/create_test_user.py \
  --email free@example.com \
  --password Test123456 \
  --tier free

python scripts/create_test_user.py \
  --email premium@example.com \
  --password Test123456 \
  --tier premium
```

---

## ChatGPT App Setup

### 1. Install OpenAI CLI

```bash
npm install -g @openai/cli
```

### 2. Login to OpenAI

```bash
openai-cli login
```

### 3. Create ChatGPT App

```bash
cd chatgpt-app

# Create app
openai-cli apps create \
  --name "Course Companion FTE" \
  --description "Digital tutor for Generative AI Fundamentals" \
  --manifest manifest.yaml
```

### 4. Update Manifest

Edit `chatgpt-app/manifest.yaml` to point to your backend:

```yaml
name: "Course Companion FTE"
description: "Your 24/7 companion for mastering LLMs, RAG, and fine-tuning"
version: "1.0.0"
author: "Your Name"

api:
  base_url: "http://localhost:8000"  # Local development
  # base_url: "https://api.course-companion.example.com"  # Production

actions:
  - name: "get_chapters"
    endpoint: "/api/v1/chapters"
    method: "GET"
    description: "List all course chapters"

  - name: "get_chapter"
    endpoint: "/api/v1/chapters/{id}"
    method: "GET"
    description: "Get full chapter content"

  - name: "get_quiz"
    endpoint: "/api/v1/quizzes/{id}"
    method: "GET"
    description: "Get quiz questions"

  - name: "submit_quiz"
    endpoint: "/api/v1/quizzes/{id}/submit"
    method: "POST"
    description: "Submit quiz answers for grading"

  - name: "get_progress"
    endpoint: "/api/v1/progress"
    method: "GET"
    description: "Get student progress summary"

authentication:
  type: "bearer"
  token_endpoint: "/auth/login"
```

### 5. Deploy ChatGPT App

```bash
cd chatgpt-app

# Deploy (updates live)
openai-cli apps deploy

# Get app URL
openai-cli apps list
```

---

## Running Tests

### Unit Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_v1_deterministic.py

# Run with verbose output
pytest -v

# Open HTML coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Zero-LLM Verification Test

**Critical**: This test must pass to maintain constitutional compliance.

```bash
cd backend

# Run zero-LLM verification
pytest tests/test_v1_deterministic.py::test_zero_llm_calls -v

# This test:
# 1. Mocks OpenAI and Anthropic API endpoints
# 2. Calls all v1 endpoints
# 3. Fails if any LLM API calls are detected
```

### Integration Tests

```bash
cd backend

# Run API integration tests
pytest tests/api/ -v

# Test specific endpoints
pytest tests/api/test_auth.py -v
pytest tests/api/test_chapters.py -v
pytest tests/api/test_quizzes.py -v
pytest tests/api/test_progress.py -v
```

---

## Development Workflow

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/add-new-endpoint

# 2. Make changes to code

# 3. Run tests
pytest

# 4. Check code quality
black app/
isort app/
mypy app/

# 5. Commit changes
git add .
git commit -m "feat(api): add new endpoint for X

- Added endpoint GET /v1/x
- Updated data model
- Added tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 6. Push to remote
git push origin feature/add-new-endpoint
```

### Database Migrations

```bash
# When you change models in app/models/

# 1. Create migration
alembic revision --autogenerate -m "Add column to students table"

# 2. Review migration file in alembic/versions/
# Make sure it looks correct!

# 3. Apply migration
alembic upgrade head

# 4. Test with rollback
alembic downgrade -1
alembic upgrade head
```

### Code Quality Tools

```bash
# Install dev dependencies (if not already installed)
pip install -r requirements-dev.txt

# Format code with Black
black app/

# Sort imports with isort
isort app/

# Type check with mypy
mypy app/

# Lint with flake8
flake8 app/

# Run all checks
black app/ && isort app/ && mypy app/ && flake8 app/ && pytest
```

---

## Troubleshooting

### Database Connection Errors

**Error**: `could not connect to server: Connection refused`

**Solutions**:
1. Check Docker containers are running: `docker ps`
2. Restart Docker Compose: `docker-compose restart`
3. Verify DATABASE_URL in `.env` matches Docker configuration
4. Check PostgreSQL logs: `docker logs course_companion_db`

### Redis Connection Errors

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solutions**:
1. Check Redis container is running: `docker ps | grep redis`
2. Test Redis connection: `redis-cli ping` (should return `PONG`)
3. Verify REDIS_URL in `.env`: `redis://localhost:6379/0`

### Cloudflare R2 Access Errors

**Error**: `botocore.exceptions.ClientError: An error occurred (403)`

**Solutions**:
1. Verify R2 credentials in `.env` are correct
2. Check R2 bucket permissions in Cloudflare dashboard
3. For local development, use `CONTENT_SOURCE=local` to skip R2
4. Test R2 connection with AWS CLI:
   ```bash
   aws s3 ls s3://your-bucket --endpoint-url https://your-account.r2.cloudflarestorage.com
   ```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solutions**:
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Add to PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` (from backend/)
4. Run from correct directory (backend/)

### Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solutions**:
1. Find process using port: `lsof -i :8000` (Unix) or `netstat -ano | findstr :8000` (Windows)
2. Kill process: `kill -9 <PID>`
3. Or use different port: `uvicorn app.main:app --reload --port 8001`

### Alembic Migration Errors

**Error**: `alembic.util.exc.CommandError: Can't locate revision`

**Solutions**:
1. Reset database: `docker-compose down -v && docker-compose up -d`
2. Re-run migrations: `alembic upgrade head`
3. If needed, stamp current version: `alembic stamp head`

---

## Useful Commands

### Docker Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart single service
docker-compose restart postgres

# Remove all data (WARNING: destructive)
docker-compose down -v
```

### Database Management

```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres@localhost:5432/course_companion

# Common queries
\dt               # List tables
\d students       # Describe students table
\du               # List users
\l                # List databases

# Backup database
pg_dump -U postgres course_companion > backup.sql

# Restore database
psql -U postgres course_companion < backup.sql
```

### Redis Management

```bash
# Connect to Redis
redis-cli

# Common commands
PING              # Test connection
KEYS *            # List all keys (dev only!)
GET chapter:01    # Get cached chapter
FLUSHDB           # Clear database (dev only!)
INFO              # Server info
```

---

## Next Steps

✅ Backend running on `localhost:8000`
✅ Database migrated and seeded
✅ Tests passing
✅ ChatGPT App deployed

**Ready for implementation!**

See `specs/002-phase-1-zero-backend-llm/tasks.md` (generated via `/sp.tasks`) for detailed implementation breakdown.

---

## Production Deployment

### Fly.io Deployment

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Initialize app
fly launch

# Set secrets
fly secrets set JWT_SECRET_KEY=your-production-secret
fly secrets set DATABASE_URL=your-neon-postgres-url
fly secrets set REDIS_URL=your-upstash-redis-url
fly secrets set R2_ACCESS_KEY=your-r2-key
fly secrets set R2_SECRET_KEY=your-r2-secret

# Deploy
fly deploy

# View logs
fly logs
```

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to project
railway link

# Set environment variables (via dashboard or CLI)
railway variables set JWT_SECRET_KEY=your-production-secret

# Deploy
railway up
```

---

## Support & Resources

- **Specification**: `specs/002-phase-1-zero-backend-llm/spec.md`
- **Implementation Plan**: `specs/002-phase-1-zero-backend-llm/plan.md`
- **Data Model**: `specs/002-phase-1-zero-backend-llm/data-model.md`
- **API Contracts**: `specs/002-phase-1-zero-backend-llm/contracts/README.md`
- **Constitution**: `.specify/memory/constitution.md`

**Questions?** Create an issue in the repository or consult the team.

---

**Quickstart Guide Complete. Development environment ready for implementation.**
