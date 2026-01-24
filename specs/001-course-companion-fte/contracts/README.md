# API Contracts: Course Companion FTE

**Date**: 2026-01-24
**Purpose**: Define HTTP API contracts for backend services

## Contract Files

| File | Description | Endpoints |
|------|-------------|-----------|
| `phase1-v1.yaml` | Phase 1 deterministic APIs (Zero-Backend-LLM) | 15 endpoints |
| `phase2-v2.yaml` | Phase 2 hybrid APIs (premium features) | 4 endpoints |
| `openapi.yaml` | Complete OpenAPI 3.0 specification (auto-generated from FastAPI) | All endpoints |

## API Versioning

### Version 1 (v1) - Deterministic APIs
- **Prefix**: `/api/v1/`
- **Phase**: 1 (Zero-Backend-LLM)
- **Characteristics**: No LLM inference, pure deterministic logic
- **Authentication**: JWT Bearer token
- **Rate Limiting**: 1000 requests/hour (free tier), 10000 requests/hour (premium)

### Version 2 (v2) - Hybrid APIs
- **Prefix**: `/api/v2/`
- **Phase**: 2 (Hybrid Intelligence)
- **Characteristics**: LLM-powered features (Claude Sonnet)
- **Authentication**: JWT Bearer token + premium subscription required
- **Rate Limiting**: 100 requests/hour (premium), 500 requests/hour (pro)

## Endpoint Summary

### Phase 1 (v1) - Deterministic

**Authentication** (`/auth`)
- `POST /auth/register` - Create user account
- `POST /auth/login` - Authenticate and get JWT token
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/me` - Get current user info

**Chapters** (`/v1/chapters`)
- `GET /v1/chapters` - List all chapters
- `GET /v1/chapters/{id}` - Get chapter content
- `GET /v1/chapters/{id}/sections` - Get chapter sections
- `GET /v1/chapters/{id}/next` - Get next chapter
- `GET /v1/chapters/{id}/previous` - Get previous chapter

**Quizzes** (`/v1/quizzes`)
- `GET /v1/quizzes/{id}` - Get quiz questions
- `POST /v1/quizzes/{id}/submit` - Submit quiz answers (deterministic grading)
- `GET /v1/quizzes/{id}/results` - Get quiz results history

**Progress** (`/v1/progress`)
- `GET /v1/progress` - Get user progress summary
- `PUT /v1/progress/chapter/{id}` - Update chapter progress
- `GET /v1/progress/streaks` - Get learning streaks

**Access Control** (`/v1/access`)
- `GET /v1/access/check` - Check access to content
- `POST /v1/access/upgrade` - Upgrade subscription

**Search** (`/v1/search`)
- `GET /v1/search?q={query}` - Search course content

### Phase 2 (v2) - Hybrid (Premium)

**Adaptive Learning** (`/v2/adaptive`)
- `POST /v2/adaptive/path` - Generate personalized learning path
- `GET /v2/adaptive/recommendations` - Get current recommendations

**LLM Assessments** (`/v2/assessments`)
- `POST /v2/assessments/{id}/submit` - Submit open-ended answer for LLM grading
- `GET /v2/assessments/{id}/feedback` - Get detailed LLM feedback

## Authentication Flow

```
┌──────┐                                    ┌─────────┐
│Client│                                    │ Backend │
└──┬───┘                                    └────┬────┘
   │                                             │
   │ POST /auth/register                         │
   │ {email, password}                           │
   │────────────────────────────────────────────>│
   │                                             │
   │                    201 Created              │
   │                    {user_id, email}         │
   │<────────────────────────────────────────────│
   │                                             │
   │ POST /auth/login                            │
   │ {email, password}                           │
   │────────────────────────────────────────────>│
   │                                             │
   │                    200 OK                   │
   │                    {access_token, expires_in}│
   │<────────────────────────────────────────────│
   │                                             │
   │ GET /v1/chapters/1                          │
   │ Authorization: Bearer {access_token}        │
   │────────────────────────────────────────────>│
   │                                             │
   │                    200 OK                   │
   │                    {chapter_data}           │
   │<────────────────────────────────────────────│
```

## Error Responses

All endpoints return consistent error format:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Chapter with ID '99-invalid' not found",
    "details": {
      "resource_type": "chapter",
      "resource_id": "99-invalid"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Resource retrieved successfully |
| 201 | Created | User registered successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Free tier accessing premium content |
| 404 | Not Found | Chapter ID doesn't exist |
| 409 | Conflict | Email already registered |
| 422 | Validation Error | Pydantic validation failed |
| 429 | Rate Limit Exceeded | Too many requests |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Maintenance mode |

## Request/Response Examples

### Get Chapter Content
```http
GET /api/v1/chapters/01-intro-genai HTTP/1.1
Host: api.course-companion.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (200 OK):
```json
{
  "chapter_id": "01-intro-genai",
  "chapter_number": 1,
  "title": "Introduction to Generative AI",
  "subtitle": "Understanding the GenAI landscape",
  "learning_objectives": [
    "Define Generative AI and distinguish from other AI types",
    "Identify key GenAI model categories (LLMs, image, multimodal)"
  ],
  "estimated_time_minutes": 45,
  "access_tier": "free",
  "sections": [
    {
      "section_id": "01-what-is-genai",
      "title": "What is Generative AI?",
      "content_markdown": "# What is Generative AI?\n\nGenerative AI...",
      "estimated_time_minutes": 10
    }
  ]
}
```

### Submit Quiz
```http
POST /api/v1/quizzes/01-quiz/submit HTTP/1.1
Host: api.course-companion.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "answers": {
    "q1": "a",
    "q2": false,
    "q3": "RAG retrieves relevant documents at inference time while fine-tuning updates model parameters..."
  }
}
```

**Response** (200 OK):
```json
{
  "quiz_id": "01-quiz",
  "attempt_id": "550e8400-e29b-41d4-a716-446655440000",
  "score": 87.5,
  "total_questions": 8,
  "correct_answers": 7,
  "passed": true,
  "grading_details": {
    "q1": {
      "correct": true,
      "explanation": "Correct! LLMs like GPT are generative models."
    },
    "q2": {
      "correct": true,
      "explanation": "Correct! Most LLMs are text-only."
    },
    "q3": {
      "correct": true,
      "score": 8.5,
      "comment": "Good explanation. Could elaborate on cost tradeoffs."
    }
  },
  "submitted_at": "2026-01-24T15:30:00Z"
}
```

### Generate Adaptive Path (Phase 2, Premium)
```http
POST /api/v2/adaptive/path HTTP/1.1
Host: api.course-companion.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "context": "I'm struggling with RAG concepts"
}
```

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "priority": 1,
      "chapter_id": "04-rag",
      "section_id": "02-embeddings",
      "reason": "Your quiz score (55%) indicates weak understanding of embeddings, which are fundamental to RAG.",
      "estimated_time_minutes": 20
    },
    {
      "priority": 2,
      "chapter_id": "04-rag",
      "section_id": "03-vector-db",
      "reason": "Understanding vector databases will clarify how RAG retrieves relevant documents.",
      "estimated_time_minutes": 25
    }
  ],
  "overall_guidance": "Focus on embeddings and vector databases before attempting RAG implementation exercises.",
  "estimated_total_time_minutes": 45,
  "generated_at": "2026-01-24T15:35:00Z",
  "cost_tokens": 1850
}
```

## Rate Limiting Headers

All responses include rate limit headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1706112000
X-RateLimit-Tier: free
```

## Pagination

List endpoints support pagination:

```http
GET /api/v1/quizzes/01-quiz/results?page=1&per_page=20
```

**Response**:
```json
{
  "items": [...],
  "page": 1,
  "per_page": 20,
  "total": 147,
  "total_pages": 8,
  "has_next": true,
  "has_prev": false
}
```

## WebSocket Support (Future)

Phase 3 may add WebSocket endpoints for real-time features:

- `/ws/progress` - Live progress updates
- `/ws/chat` - Real-time conversational tutoring

## OpenAPI Auto-Generation

The complete OpenAPI 3.0 specification is auto-generated from FastAPI:

```python
# Access at /docs (Swagger UI) or /redoc (ReDoc)
# Download JSON at /openapi.json

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Course Companion FTE API",
        version="1.0.0",
        description="Digital Full-Time Equivalent Educational Tutor API",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

**Next Steps**:
1. Implement FastAPI endpoints following these contracts
2. Generate full `openapi.yaml` from FastAPI `/openapi.json`
3. Create contract tests to validate API behavior
4. Document authentication setup in `quickstart.md`
