# Quickstart Guide: Phase 2 - Hybrid Intelligence

**Feature Branch**: `003-phase-2-hybrid-intelligence`
**Created**: 2026-01-24
**Related Artifacts**: [spec.md](./spec.md) | [plan.md](./plan.md) | [data-model.md](./data-model.md) | [contracts/README.md](./contracts/README.md)

---

## Overview

This guide walks you through setting up the Phase 2 development environment, running migrations, testing LLM integrations, and verifying Phase 1/2 isolation. Follow these steps sequentially to ensure proper configuration.

**Prerequisites**:
- Phase 1 fully implemented and operational
- Python 3.11+ installed
- PostgreSQL database running (Neon/Supabase)
- Redis server running
- Git repository cloned locally

---

## 1. Environment Setup

### 1.1 Install Phase 2 Dependencies

Phase 2 adds Anthropic Claude SDK and token counting libraries to the existing Phase 1 stack.

**Install new dependencies**:
```bash
cd backend
pip install anthropic==0.40.0
pip install tiktoken==0.5.2
pip install pydantic-settings==2.1.0  # If not already installed
```

**Verify installation**:
```bash
python -c "import anthropic; print(f'Anthropic SDK version: {anthropic.__version__}')"
python -c "import tiktoken; print(f'Tiktoken version: {tiktoken.__version__}')"
```

**Expected output**:
```
Anthropic SDK version: 0.40.0
Tiktoken version: 0.5.2
```

---

### 1.2 Configure Environment Variables

Phase 2 requires Anthropic API credentials and LLM configuration settings.

**Edit `.env` file** (create if it doesn't exist):
```bash
# Phase 1 settings (UNCHANGED)
DATABASE_URL=postgresql://user:password@localhost:5432/course_companion
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
CLOUDFLARE_R2_BUCKET=course-content
CLOUDFLARE_R2_ACCESS_KEY=your-r2-access-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret-key

# Phase 2 LLM Settings (NEW)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-API-KEY-HERE
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_TIMEOUT=30  # Seconds
ANTHROPIC_MAX_RETRIES=3

# Cost Monitoring (NEW)
LLM_COST_ALERT_THRESHOLD=0.50  # Alert if per-user monthly cost exceeds this
LLM_COST_ALERT_EMAIL=admin@example.com

# Rate Limiting (NEW)
PREMIUM_ADAPTIVE_PATHS_LIMIT=10  # Per month
PREMIUM_ASSESSMENTS_LIMIT=20  # Per month

# Feature Flags (NEW)
ENABLE_ADAPTIVE_PATHS=true
ENABLE_LLM_ASSESSMENTS=true
ENABLE_PHASE2_CACHING=true
```

**Get Anthropic API Key**:
1. Sign up at https://console.anthropic.com
2. Navigate to API Keys section
3. Create new API key (starts with `sk-ant-api03-`)
4. Copy key to `.env` file (NEVER commit to git)

**Verify environment variables**:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('ANTHROPIC_API_KEY:', os.getenv('ANTHROPIC_API_KEY')[:20] + '...')"
```

---

### 1.3 Update `.gitignore`

Ensure sensitive credentials are never committed.

**Add to `.gitignore`** (if not already present):
```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Anthropic credentials
anthropic_api_key.txt
*.anthropic

# Cost logs (local development)
cost_logs/
llm_usage_dev.csv
```

---

## 2. Database Migrations

### 2.1 Run Phase 2 Migrations

Phase 2 adds 5 new tables to the existing schema without modifying Phase 1 tables.

**Check current migration status**:
```bash
cd backend
alembic current
```

**Expected output** (Phase 1 complete):
```
001_phase1_complete (head)
```

**Run Phase 2 migrations sequentially**:
```bash
# Migration 002: Add adaptive_paths table
alembic upgrade 002_phase2_adaptive_paths

# Migration 003: Add assessment_submissions and assessment_feedback tables
alembic upgrade 003_phase2_assessments

# Migration 004: Add llm_usage_logs and premium_usage_quotas tables
alembic upgrade 004_phase2_usage_tracking

# Or upgrade all at once
alembic upgrade head
```

**Verify migrations**:
```bash
alembic current
```

**Expected output**:
```
004_phase2_usage_tracking (head)
```

---

### 2.2 Verify Database Schema

Check that all Phase 2 tables were created successfully.

**Connect to database** (using psql, pgAdmin, or your preferred client):
```bash
psql $DATABASE_URL
```

**Verify tables exist**:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'adaptive_paths',
    'assessment_submissions',
    'assessment_feedback',
    'llm_usage_logs',
    'premium_usage_quotas'
  );
```

**Expected output** (5 rows):
```
      table_name
-------------------------
 adaptive_paths
 assessment_feedback
 assessment_submissions
 llm_usage_logs
 premium_usage_quotas
```

**Check foreign key relationships**:
```sql
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name IN (
    'adaptive_paths',
    'assessment_submissions',
    'assessment_feedback',
    'llm_usage_logs',
    'premium_usage_quotas'
  );
```

**Expected output**: All Phase 2 tables should reference `students.student_id`

---

## 3. Seed Phase 2 Content

### 3.1 Upload Assessment Questions to R2

Phase 2 includes 18 open-ended assessment questions (3 per chapter for Chapters 4-6).

**Run seed script**:
```bash
cd backend
python scripts/seed_phase2_content.py
```

**Expected output**:
```
Seeding Phase 2 content...
✓ Uploaded 04-rag-assessments.json (3 questions)
✓ Uploaded 05-fine-tuning-assessments.json (3 questions)
✓ Uploaded 06-ai-apps-assessments.json (3 questions)
Total: 18 assessment questions uploaded to Cloudflare R2
```

**Verify R2 upload**:
```bash
# Using AWS CLI (compatible with R2)
aws s3 ls s3://course-content/assessments/ --endpoint-url=https://your-r2-endpoint.r2.cloudflarestorage.com

# Expected output:
# 04-rag-assessments.json
# 05-fine-tuning-assessments.json
# 06-ai-apps-assessments.json
```

---

### 3.2 Create Test Premium User

Create a premium-tier test user for development testing.

**Run Python script**:
```python
# backend/scripts/create_test_premium_user.py
from app.models.user import Student
from app.database import SessionLocal
from app.services.auth import hash_password
from datetime import datetime, timedelta

db = SessionLocal()

# Create premium test user
premium_user = Student(
    email="premium@test.com",
    password_hash=hash_password("premium123"),
    full_name="Premium Test User",
    subscription_tier="premium",
    subscription_expires_at=datetime.utcnow() + timedelta(days=365)
)

db.add(premium_user)
db.commit()

print(f"✓ Created premium test user: {premium_user.email}")
print(f"  Student ID: {premium_user.student_id}")
print(f"  Subscription expires: {premium_user.subscription_expires_at}")

db.close()
```

**Run script**:
```bash
python scripts/create_test_premium_user.py
```

---

## 4. Testing Phase 2 Features

### 4.1 Test Anthropic API Connection

Verify Claude Sonnet API is accessible and credentials are valid.

**Create test script** (`backend/tests/test_anthropic_connection.py`):
```python
import os
from anthropic import Anthropic

def test_anthropic_connection():
    """Test connection to Anthropic API"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    assert api_key, "ANTHROPIC_API_KEY not set in environment"

    client = Anthropic(api_key=api_key)

    # Simple test prompt
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'API connection successful' if you can read this."}
        ]
    )

    assert response.content, "No response from Claude"
    assert "successful" in response.content[0].text.lower(), "Unexpected response"

    print(f"✓ Anthropic API connection successful")
    print(f"  Model: {response.model}")
    print(f"  Tokens used: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    print(f"  Response: {response.content[0].text}")

if __name__ == "__main__":
    test_anthropic_connection()
```

**Run test**:
```bash
python tests/test_anthropic_connection.py
```

**Expected output**:
```
✓ Anthropic API connection successful
  Model: claude-sonnet-4-5-20250929
  Tokens used: 15 input, 8 output
  Response: API connection successful.
```

---

### 4.2 Test Adaptive Path Generation (Mocked)

Test adaptive path service layer with mocked Anthropic client (no real API calls).

**Run unit tests**:
```bash
pytest backend/tests/services/test_llm/test_adaptive_path_generator.py -v
```

**Expected output**:
```
tests/services/test_llm/test_adaptive_path_generator.py::test_generate_path_with_weak_areas PASSED
tests/services/test_llm/test_adaptive_path_generator.py::test_generate_path_insufficient_data PASSED
tests/services/test_llm/test_adaptive_path_generator.py::test_parse_recommendations_json PASSED
tests/services/test_llm/test_adaptive_path_generator.py::test_cost_calculation PASSED
```

---

### 4.3 Test LLM Assessment Grading (Mocked)

Test assessment grading service with mocked responses.

**Run unit tests**:
```bash
pytest backend/tests/services/test_llm/test_assessment_grader.py -v
```

**Expected output**:
```
tests/services/test_llm/test_assessment_grader.py::test_grade_excellent_answer PASSED
tests/services/test_llm/test_assessment_grader.py::test_grade_poor_answer PASSED
tests/services/test_llm/test_assessment_grader.py::test_detect_off_topic_submission PASSED
tests/services/test_llm/test_assessment_grader.py::test_parse_feedback_json PASSED
```

---

### 4.4 CRITICAL TEST: Verify Phase 1/2 Isolation

This test MUST pass to ensure Phase 1 endpoints remain LLM-free after Phase 2 deployment.

**Run isolation test**:
```bash
pytest backend/tests/test_phase_isolation.py -v
```

**Test code** (`backend/tests/test_phase_isolation.py`):
```python
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@patch('anthropic.Anthropic')
def test_phase1_endpoints_remain_llm_free(mock_anthropic):
    """
    CRITICAL: Verify Phase 1 endpoints make ZERO LLM calls after Phase 2 deployment.
    This test ensures constitutional requirement (FR-032) is met.
    """
    # Arrange: Mock Anthropic client to track calls
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client

    # Get auth headers for test user
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Act: Call all Phase 1 endpoints
    phase1_endpoints = [
        ("GET", "/api/v1/chapters"),
        ("GET", "/api/v1/chapters/01-intro"),
        ("GET", "/api/v1/quizzes/01-intro-quiz"),
        ("POST", "/api/v1/quizzes/01-intro-quiz/submit", {
            "answers": {"q1": "a", "q2": "b"}
        }),
        ("GET", "/api/v1/progress"),
        ("GET", "/api/v1/progress/quiz-history")
    ]

    for method, endpoint, *body in phase1_endpoints:
        if method == "GET":
            response = client.get(endpoint, headers=auth_headers)
        elif method == "POST":
            response = client.post(endpoint, headers=auth_headers, json=body[0] if body else {})

        # Assert: All Phase 1 endpoints should succeed
        assert response.status_code in [200, 201], f"Phase 1 endpoint {endpoint} failed: {response.status_code}"

    # Assert: Anthropic API was NEVER called
    mock_anthropic.assert_not_called()
    mock_client.messages.create.assert_not_called()

    print("✓ Phase 1 isolation verified: Zero LLM calls from v1 endpoints")

if __name__ == "__main__":
    test_phase1_endpoints_remain_llm_free()
```

**Expected output**:
```
tests/test_phase_isolation.py::test_phase1_endpoints_remain_llm_free PASSED
✓ Phase 1 isolation verified: Zero LLM calls from v1 endpoints
```

**CRITICAL**: If this test fails, Phase 2 cannot be deployed. Investigate and fix contamination before proceeding.

---

### 4.5 Test Premium Gating

Verify free-tier users are blocked from Phase 2 features.

**Run premium gating tests**:
```bash
pytest backend/tests/test_v2_hybrid.py::test_adaptive_path_premium_gating -v
pytest backend/tests/test_v2_hybrid.py::test_assessment_premium_gating -v
```

**Expected output**:
```
tests/test_v2_hybrid.py::test_adaptive_path_premium_gating PASSED
tests/test_v2_hybrid.py::test_assessment_premium_gating PASSED
```

**Test code snippet**:
```python
def test_adaptive_path_premium_gating():
    """Free users should receive 403 Forbidden for adaptive paths"""
    # Arrange: Log in as free-tier user
    response = client.post("/api/v1/auth/login", json={
        "email": "free@test.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Act: Attempt to request adaptive path
    response = client.post("/api/v2/adaptive/path", headers=headers, json={
        "force_refresh": false
    })

    # Assert: Should be blocked with clear upgrade messaging
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PREMIUM_REQUIRED"
    assert "upgrade_url" in response.json()["error"]
    print("✓ Premium gating working: Free users blocked from adaptive paths")
```

---

### 4.6 Test Rate Limiting

Verify monthly quotas are enforced (10 paths, 20 assessments).

**Run rate limiting tests**:
```bash
pytest backend/tests/test_v2_hybrid.py::test_rate_limit_enforcement -v
```

**Test code snippet**:
```python
def test_rate_limit_enforcement():
    """Premium users should be limited to 10 adaptive paths per month"""
    # Arrange: Log in as premium user
    token = get_premium_user_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Act: Request 10 adaptive paths (should all succeed)
    for i in range(10):
        response = client.post("/api/v2/adaptive/path", headers=headers, json={})
        assert response.status_code == 200, f"Request {i+1} failed: {response.status_code}"

    # Act: 11th request should be rate-limited
    response = client.post("/api/v2/adaptive/path", headers=headers, json={})

    # Assert: Should receive 429 Rate Limit Exceeded
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert response.json()["error"]["quota"]["used"] == 10
    assert response.json()["error"]["quota"]["limit"] == 10
    print("✓ Rate limiting working: 11th request blocked")
```

---

### 4.7 Test Cost Tracking

Verify every LLM call is logged with token count and cost.

**Run cost tracking tests**:
```bash
pytest backend/tests/test_v2_hybrid.py::test_llm_cost_tracking -v
```

**Test code snippet**:
```python
def test_llm_cost_tracking():
    """Every LLM call should create a usage log entry"""
    # Arrange
    token = get_premium_user_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Act: Request adaptive path
    response = client.post("/api/v2/adaptive/path", headers=headers, json={})
    assert response.status_code == 200

    path_id = response.json()["path_id"]
    student_id = response.json()["student_id"]

    # Assert: Usage log entry created
    from app.models.usage import LLMUsageLog
    from app.database import SessionLocal

    db = SessionLocal()
    log = db.query(LLMUsageLog).filter_by(
        student_id=student_id,
        reference_id=path_id,
        feature="adaptive-path"
    ).first()

    assert log is not None, "No usage log entry found"
    assert log.tokens_input > 0, "Missing token count"
    assert log.tokens_output > 0, "Missing token count"
    assert log.cost_usd > 0, "Missing cost calculation"
    assert log.success == True, "Call marked as failed"

    print(f"✓ Cost tracking working: {log.tokens_total} tokens, ${log.cost_usd:.4f}")
    db.close()
```

---

## 5. Development Workflow

### 5.1 Start Development Server

Run FastAPI backend with hot reload for development.

**Start server**:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify server is running**:
```bash
curl http://localhost:8000/api/v1/health
```

**Expected output**:
```json
{
  "status": "healthy",
  "phase1_enabled": true,
  "phase2_enabled": true,
  "timestamp": "2026-01-24T18:30:00Z"
}
```

---

### 5.2 Test Phase 2 Endpoints (Manual)

Use `curl` or Postman to test API endpoints.

**1. Log in as premium user**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"premium@test.com","password":"premium123"}'

# Save token from response
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**2. Request adaptive path**:
```bash
curl -X POST http://localhost:8000/api/v2/adaptive/path \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh":false,"include_reasoning":true}'
```

**3. Check usage quota**:
```bash
curl -X GET http://localhost:8000/api/v2/usage/quota \
  -H "Authorization: Bearer $TOKEN"
```

**4. Submit assessment**:
```bash
curl -X POST http://localhost:8000/api/v2/assessments/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id":"04-rag-q1",
    "answer_text":"RAG is best for scenarios requiring up-to-date information..."
  }'

# Save submission_id from response
export SUBMISSION_ID="9a8b7c6d-5e4f-3210-9876-543210fedcba"
```

**5. Get assessment feedback**:
```bash
curl -X GET http://localhost:8000/api/v2/assessments/feedback/$SUBMISSION_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5.3 Monitor Cost Metrics

Track LLM usage and costs during development.

**Query database for cost summary**:
```sql
-- Monthly cost per student
SELECT
    student_id,
    COUNT(*) AS total_requests,
    SUM(tokens_input) AS total_input_tokens,
    SUM(tokens_output) AS total_output_tokens,
    SUM(cost_usd) AS total_cost_usd,
    AVG(latency_ms) AS avg_latency_ms
FROM llm_usage_logs
WHERE DATE_TRUNC('month', request_timestamp) = DATE_TRUNC('month', CURRENT_TIMESTAMP)
    AND deleted_at IS NULL
    AND success = TRUE
GROUP BY student_id
ORDER BY total_cost_usd DESC;
```

**Check for cost threshold violations**:
```sql
-- Students exceeding $0.50/month threshold
SELECT
    student_id,
    SUM(cost_usd) AS monthly_cost
FROM llm_usage_logs
WHERE DATE_TRUNC('month', request_timestamp) = DATE_TRUNC('month', CURRENT_TIMESTAMP)
    AND deleted_at IS NULL
    AND success = TRUE
GROUP BY student_id
HAVING SUM(cost_usd) > 0.50;
```

---

### 5.4 Redis Cache Inspection

Verify adaptive path caching and quota tracking in Redis.

**Connect to Redis**:
```bash
redis-cli
```

**Check cached adaptive path**:
```redis
# Get cached path (replace student_id)
GET adaptive_path:550e8400-e29b-41d4-a716-446655440000

# Check TTL (should be ~86400 seconds = 24 hours)
TTL adaptive_path:550e8400-e29b-41d4-a716-446655440000
```

**Check quota counters**:
```redis
# Get adaptive paths used this month
GET quota:550e8400-e29b-41d4-a716-446655440000:2026-01:adaptive_paths

# Get assessments used this month
GET quota:550e8400-e29b-41d4-a716-446655440000:2026-01:assessments
```

**Expected output**:
```
"7"   # 7 adaptive paths used
"14"  # 14 assessments used
```

---

## 6. Troubleshooting

### Issue 1: Anthropic API Key Invalid

**Error**:
```
anthropic.AuthenticationError: 401 Invalid API key
```

**Solution**:
1. Verify `ANTHROPIC_API_KEY` in `.env` file starts with `sk-ant-api03-`
2. Check API key is active in Anthropic Console: https://console.anthropic.com/settings/keys
3. Regenerate key if expired or revoked
4. Restart development server to reload environment variables

---

### Issue 2: Phase 1 Isolation Test Failing

**Error**:
```
AssertionError: Anthropic client was called during Phase 1 endpoint execution
```

**Root Cause**: Phase 2 LLM logic contaminated Phase 1 code paths

**Solution**:
1. Check Phase 1 router imports: `backend/app/api/v1/*.py` should NOT import from `services/llm/`
2. Verify middleware: Premium gating middleware should NOT trigger for v1 endpoints
3. Review dependency injection: v1 routes should not inject LLM services
4. Add linting rule to prevent cross-module imports:
   ```python
   # .flake8
   [flake8]
   exclude = .git,__pycache__,venv
   per-file-ignores =
       app/api/v1/*:F401  # Ignore unused imports in v1 (catch accidental LLM imports)
   ```

---

### Issue 3: Rate Limiting Not Working

**Error**: Premium users can request >10 adaptive paths per month

**Solution**:
1. Check Redis is running: `redis-cli ping` (should return `PONG`)
2. Verify quota counters exist:
   ```bash
   redis-cli GET quota:550e8400-e29b-41d4-a716-446655440000:2026-01:adaptive_paths
   ```
3. Check PostgreSQL quota table:
   ```sql
   SELECT * FROM premium_usage_quotas WHERE student_id = '550e8400-e29b-41d4-a716-446655440000';
   ```
4. Ensure `verify_quota` dependency is applied to v2 routes:
   ```python
   @router.post("/adaptive/path", dependencies=[Depends(verify_premium), Depends(verify_quota)])
   ```

---

### Issue 4: Database Migrations Failing

**Error**:
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**Solution**:
1. Check current migration version:
   ```bash
   alembic current
   ```
2. If stuck on old version, manually verify database state:
   ```sql
   SELECT version_num FROM alembic_version;
   ```
3. Rollback and retry:
   ```bash
   alembic downgrade 001_phase1_complete
   alembic upgrade head
   ```
4. If migrations are corrupted, drop Phase 2 tables and re-run:
   ```sql
   DROP TABLE IF EXISTS premium_usage_quotas CASCADE;
   DROP TABLE IF EXISTS llm_usage_logs CASCADE;
   DROP TABLE IF EXISTS assessment_feedback CASCADE;
   DROP TABLE IF EXISTS assessment_submissions CASCADE;
   DROP TABLE IF EXISTS adaptive_paths CASCADE;
   ```
   Then: `alembic upgrade head`

---

### Issue 5: LLM Responses Too Slow

**Error**: Adaptive path generation taking >10 seconds (exceeds 5s p95 target)

**Solution**:
1. Check Anthropic API latency:
   ```sql
   SELECT AVG(latency_ms), MAX(latency_ms) FROM llm_usage_logs WHERE feature = 'adaptive-path';
   ```
2. Reduce max_tokens in prompts (currently 500 for adaptive paths, 400 for assessments)
3. Enable request queuing to handle bursts:
   ```python
   # backend/app/services/llm/client.py
   async def generate_with_queue(prompt, max_tokens):
       if queue.size() > 50:
           raise HTTPException(503, "Service temporarily busy. Try again in a moment.")
       return await anthropic_client.messages.create(...)
   ```
4. Check database query performance (slow student data retrieval):
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM quiz_results WHERE student_id = '...' ORDER BY completed_at DESC LIMIT 10;
   ```

---

### Issue 6: Cost Tracking Missing Entries

**Error**: `llm_usage_logs` table has no entries after API calls

**Solution**:
1. Check database connection in LLM service:
   ```python
   # backend/app/services/llm/cost_tracker.py
   def log_usage(student_id, feature, tokens_input, tokens_output, cost_usd):
       log = LLMUsageLog(...)
       db.add(log)
       db.commit()  # Ensure commit is called
   ```
2. Verify cost calculation is correct:
   ```python
   cost = (tokens_input * 0.000003) + (tokens_output * 0.000015)
   assert cost > 0, "Cost must be positive"
   ```
3. Check for exceptions during logging (should not fail silently):
   ```python
   try:
       log_usage(...)
   except Exception as e:
       logger.error(f"Failed to log LLM usage: {e}")
       # Still proceed with request, but alert admin
   ```

---

## 7. Cost Monitoring Dashboard

### 7.1 Admin Cost Metrics Endpoint

Admins can monitor LLM costs via `/api/v2/admin/costs`.

**Request**:
```bash
# Log in as admin user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

export ADMIN_TOKEN="..."

# Get cost breakdown for January 2026
curl -X GET "http://localhost:8000/api/v2/admin/costs?start_date=2026-01-01&end_date=2026-01-31&group_by=feature" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Response**:
```json
{
  "period": {"start_date": "2026-01-01", "end_date": "2026-01-31"},
  "total_cost_usd": 247.50,
  "total_requests": 11250,
  "average_cost_per_student": 0.248,
  "breakdown_by_feature": [
    {
      "feature": "adaptive-path",
      "total_requests": 3750,
      "total_cost_usd": 102.00,
      "average_cost_per_request": 0.0091
    },
    {
      "feature": "assessment",
      "total_requests": 7500,
      "total_cost_usd": 145.50,
      "average_cost_per_request": 0.0066
    }
  ],
  "alerts": [
    {
      "type": "COST_THRESHOLD_EXCEEDED",
      "student_id": "abc12345-6789-0abc-def1-234567890abc",
      "cost_usd": 0.67,
      "threshold_usd": 0.50
    }
  ]
}
```

---

### 7.2 Set Up Cost Alerts

Configure email alerts when per-student costs exceed $0.50/month.

**Add to `.env`**:
```bash
LLM_COST_ALERT_THRESHOLD=0.50
LLM_COST_ALERT_EMAIL=admin@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Create alert script** (`backend/scripts/check_cost_alerts.py`):
```python
import os
from sqlalchemy import func
from app.models.usage import LLMUsageLog
from app.database import SessionLocal
from app.services.email import send_alert_email

def check_cost_alerts():
    db = SessionLocal()
    threshold = float(os.getenv("LLM_COST_ALERT_THRESHOLD", 0.50))

    # Query students exceeding threshold
    results = db.query(
        LLMUsageLog.student_id,
        func.sum(LLMUsageLog.cost_usd).label("total_cost")
    ).filter(
        func.date_trunc('month', LLMUsageLog.request_timestamp) == func.date_trunc('month', func.current_timestamp()),
        LLMUsageLog.deleted_at.is_(None),
        LLMUsageLog.success == True
    ).group_by(LLMUsageLog.student_id).having(
        func.sum(LLMUsageLog.cost_usd) > threshold
    ).all()

    for student_id, total_cost in results:
        print(f"⚠️ Alert: Student {student_id} exceeded threshold (${total_cost:.2f} > ${threshold:.2f})")
        send_alert_email(student_id, total_cost, threshold)

    db.close()

if __name__ == "__main__":
    check_cost_alerts()
```

**Schedule with cron** (run daily at 9 AM):
```bash
crontab -e

# Add line:
0 9 * * * cd /path/to/backend && python scripts/check_cost_alerts.py
```

---

## 8. Next Steps

After completing this quickstart:

1. **Generate tasks.md**: Run `/sp.tasks` to create implementation task list
2. **Implement LLM service layer**: Start with `backend/app/services/llm/client.py`
3. **Create v2 API routers**: Implement `/api/v2/adaptive.py` and `/api/v2/assessments.py`
4. **Write comprehensive tests**: Target >80% coverage for Phase 2 code
5. **Update ChatGPT App**: Add Phase 2 actions to `chatgpt-app/manifest.yaml`
6. **Deploy to staging**: Test full workflow with real Claude Sonnet API
7. **Monitor costs**: Track actual vs projected costs for first 100 premium users

---

## Appendix: Quick Reference

### Environment Variables (Phase 2 Only)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Claude Sonnet API key (starts with `sk-ant-api03-`) |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-5-20250929` | Model version identifier |
| `ANTHROPIC_TIMEOUT` | No | `30` | API request timeout (seconds) |
| `ANTHROPIC_MAX_RETRIES` | No | `3` | Max retry attempts on failure |
| `LLM_COST_ALERT_THRESHOLD` | No | `0.50` | Alert threshold (USD per student per month) |
| `PREMIUM_ADAPTIVE_PATHS_LIMIT` | No | `10` | Monthly quota for adaptive paths |
| `PREMIUM_ASSESSMENTS_LIMIT` | No | `20` | Monthly quota for assessments |

### Common Commands
```bash
# Run all tests
pytest backend/tests/ -v

# Run only Phase 2 tests
pytest backend/tests/test_v2_hybrid.py backend/tests/services/test_llm/ -v

# Run CRITICAL isolation test
pytest backend/tests/test_phase_isolation.py -v

# Check database migrations
alembic current

# Upgrade to latest migration
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Start dev server
uvicorn app.main:app --reload

# Monitor Redis cache
redis-cli MONITOR

# Check cost summary (SQL)
psql $DATABASE_URL -c "SELECT SUM(cost_usd) FROM llm_usage_logs WHERE DATE_TRUNC('month', request_timestamp) = DATE_TRUNC('month', CURRENT_TIMESTAMP);"
```

---

**Quickstart Complete. You are now ready to implement Phase 2 features.**
