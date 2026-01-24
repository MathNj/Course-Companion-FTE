# Quickstart Guide: Course Companion FTE

**Purpose**: Get the development environment running in under 15 minutes
**Date**: 2026-01-24
**Prerequisites**: Python 3.11+, Node.js 18+, Docker, Git

## Table of Contents
1. [Clone Repository](#1-clone-repository)
2. [Backend Setup](#2-backend-setup)
3. [Database Setup](#3-database-setup)
4. [Frontend Setup](#4-frontend-setup)
5. [ChatGPT App Setup](#5-chatgpt-app-setup)
6. [Run Services](#6-run-services)
7. [Verify Installation](#7-verify-installation)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Clone Repository

```bash
git clone https://github.com/your-org/course-companion-fte.git
cd course-companion-fte
git checkout 001-course-companion-fte
```

---

## 2. Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python3.11 -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

### 2.3 Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Copy from example
cp .env.example .env
```

Edit `.env` and fill in values:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/course_companion

# Redis
REDIS_URL=redis://localhost:6379/0

# Cloudflare R2
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_BUCKET_NAME=course-companion-content

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Anthropic (Phase 2 only)
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Leave empty for Phase 1

# App Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 3. Database Setup

### 3.1 Start PostgreSQL (Docker)

```bash
# From repository root
docker-compose up -d postgres redis
```

This starts:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

### 3.2 Run Database Migrations

```bash
cd backend

# Initialize Alembic (first time only)
alembic init alembic

# Run migrations
alembic upgrade head
```

### 3.3 Seed Initial Data

```bash
# Load course content into database
python scripts/seed_content.py

# Create test user
python scripts/create_test_user.py \
  --email test@example.com \
  --password password123 \
  --tier premium
```

---

## 4. Frontend Setup (Phase 3)

### 4.1 Install Dependencies

```bash
cd web-app
npm install
```

### 4.2 Environment Variables

Create `.env.local` file in `web-app/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

---

## 5. ChatGPT App Setup (Phase 1 & 2)

### 5.1 Install OpenAI CLI

```bash
npm install -g @openai/cli
```

### 5.2 Configure ChatGPT App

```bash
cd chatgpt-app

# Login to OpenAI
openai-cli login

# Create app (first time only)
openai-cli apps create \
  --name "Course Companion FTE" \
  --description "Digital tutor for Generative AI Fundamentals" \
  --manifest manifest.yaml
```

### 5.3 Update Manifest with Backend URL

Edit `chatgpt-app/manifest.yaml`:

```yaml
api:
  base_url: http://localhost:8000/api/v1  # For local development
  # base_url: https://api.course-companion.example.com/api/v1  # For production
```

---

## 6. Run Services

### 6.1 Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # Or venv\Scripts\activate on Windows

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend now running at: http://localhost:8000

- API docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 6.2 Start Frontend (Terminal 2)

```bash
cd web-app

# Development server with hot reload
npm run dev
```

Frontend now running at: http://localhost:3000

### 6.3 Start ChatGPT App (Terminal 3)

```bash
cd chatgpt-app

# Deploy to ChatGPT (updates live)
openai-cli apps deploy

# Get app link
openai-cli apps list
```

Open the provided link to test in ChatGPT.

---

## 7. Verify Installation

### 7.1 Backend Health Check

```bash
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### 7.2 Test Authentication

```bash
# Register test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Save the access_token from response
```

### 7.3 Test Content API

```bash
# Get chapters (requires JWT)
curl http://localhost:8000/api/v1/chapters \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected: List of 6 chapters
```

### 7.4 Run Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### 7.5 Test Frontend

```bash
cd web-app

# Run Jest tests
npm test

# Run E2E tests (requires backend running)
npm run test:e2e
```

---

## 8. Troubleshooting

### 8.1 Database Connection Errors

**Error**: `could not connect to server: Connection refused`

**Solutions**:
1. Check PostgreSQL is running: `docker ps`
2. Verify `DATABASE_URL` in `.env` is correct
3. Restart Docker: `docker-compose restart postgres`

### 8.2 Redis Connection Errors

**Error**: `Redis connection failed`

**Solutions**:
1. Check Redis is running: `docker ps`
2. Verify `REDIS_URL` in `.env` is correct
3. Test Redis: `redis-cli ping` (should return `PONG`)

### 8.3 Cloudflare R2 Access Errors

**Error**: `403 Forbidden` or `Access Denied`

**Solutions**:
1. Verify R2 credentials in `.env`
2. Check bucket permissions in Cloudflare dashboard
3. For local dev, can skip R2 and use local files: `CONTENT_SOURCE=local` in `.env`

### 8.4 Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solutions**:
1. Ensure virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Add to PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` (from backend/)

### 8.5 FastAPI Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solutions**:
1. Find process: `lsof -i :8000`
2. Kill process: `kill -9 <PID>`
3. Or use different port: `uvicorn app.main:app --reload --port 8001`

### 8.6 Alembic Migration Errors

**Error**: `alembic.util.exc.CommandError: Can't locate revision identified by '...'`

**Solutions**:
1. Reset database: `docker-compose down -v && docker-compose up -d`
2. Re-run migrations: `alembic upgrade head`
3. If needed, stamp current version: `alembic stamp head`

---

## Development Workflow

### Making Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** to code

3. **Run tests**:
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd web-app && npm test
   ```

4. **Check code quality**:
   ```bash
   # Backend (Black + isort + mypy)
   cd backend
   black app/
   isort app/
   mypy app/

   # Frontend (ESLint + Prettier)
   cd web-app
   npm run lint
   npm run format
   ```

5. **Create database migration** (if models changed):
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of change"
   alembic upgrade head
   ```

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

### Running in Production Mode

```bash
# Backend
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd web-app
npm run build
npm start
```

---

## Useful Commands

### Database Management

```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
python scripts/seed_content.py

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Docker Management

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Clean up (removes volumes)
docker-compose down -v
```

### Testing

```bash
# Backend unit tests only
pytest tests/unit/

# Backend integration tests only
pytest tests/api/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Frontend unit tests
cd web-app && npm test

# Frontend E2E tests
cd web-app && npm run test:e2e
```

---

## Next Steps

1. ✅ Backend running on `localhost:8000`
2. ✅ Frontend running on `localhost:3000`
3. ✅ ChatGPT App deployed
4. ✅ Database migrated and seeded
5. ✅ Tests passing

**Ready to start implementing features!**

See `/sp.tasks` output for detailed implementation task breakdown.

---

## Support

- **Documentation**: See `specs/001-course-companion-fte/`
- **Constitution**: See `.specify/memory/constitution.md`
- **API Contracts**: See `specs/001-course-companion-fte/contracts/`
- **Data Model**: See `specs/001-course-companion-fte/data-model.md`

**Questions?** Create an issue in the repository.
