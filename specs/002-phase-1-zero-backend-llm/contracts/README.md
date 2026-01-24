# API Contracts: Phase 1 - Zero-Backend-LLM Course Companion

**Date**: 2026-01-24
**Feature**: Phase 1 - Zero-Backend-LLM Course Companion
**Purpose**: Define REST API endpoints, request/response formats, and error handling

## API Overview

**Base URL**: `https://api.course-companion.example.com` (production)
**Base URL**: `http://localhost:8000` (local development)

**API Versioning**:
- Version 1 (v1): `/api/v1/*` - Phase 1 deterministic endpoints
- Version 2 (v2): `/api/v2/*` - Phase 2 hybrid endpoints (future)

**Authentication**: JWT Bearer tokens
**Content Type**: `application/json`
**Character Encoding**: UTF-8

## Endpoint Summary

### Phase 1 (v1) - Deterministic Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| **Authentication** | | | |
| POST | `/auth/register` | Create new student account | No |
| POST | `/auth/login` | Authenticate and get JWT token | No |
| POST | `/auth/refresh` | Refresh JWT token | Yes |
| GET | `/auth/me` | Get current user info | Yes |
| **Content** | | | |
| GET | `/v1/chapters` | List all 6 chapters | Yes |
| GET | `/v1/chapters/{id}` | Get chapter content | Yes |
| GET | `/v1/chapters/{id}/next` | Get next chapter | Yes |
| GET | `/v1/chapters/{id}/previous` | Get previous chapter | Yes |
| GET | `/v1/search` | Search course content | Yes |
| **Quizzes** | | | |
| GET | `/v1/quizzes/{id}` | Get quiz questions | Yes |
| POST | `/v1/quizzes/{id}/submit` | Submit quiz answers | Yes |
| GET | `/v1/quizzes/{id}/results` | Get quiz attempt history | Yes |
| **Progress** | | | |
| GET | `/v1/progress` | Get user progress summary | Yes |
| PUT | `/v1/progress/chapter/{id}` | Update chapter progress | Yes |
| GET | `/v1/progress/streaks` | Get learning streaks | Yes |
| **Access Control** | | | |
| GET | `/v1/access/check` | Check content access rights | Yes |

**Total**: 18 endpoints (4 auth + 14 v1)

---

## Authentication Endpoints

### POST /auth/register

Create a new student account.

**Request**:
```http
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "SecurePass123",
  "full_name": "Jane Doe",
  "timezone": "America/New_York"
}
```

**Response (201 Created)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "full_name": "Jane Doe",
  "subscription_tier": "free",
  "created_at": "2026-01-24T15:30:00Z"
}
```

**Errors**:
- 400 Bad Request: Invalid email format or password too weak
- 409 Conflict: Email already registered

---

### POST /auth/login

Authenticate and receive JWT token.

**Request**:
```http
POST /auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 2592000,
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "subscription_tier": "free"
  }
}
```

**Errors**:
- 401 Unauthorized: Invalid email or password

---

### GET /auth/me

Get current authenticated user information.

**Request**:
```http
GET /auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "full_name": "Jane Doe",
  "subscription_tier": "free",
  "timezone": "America/New_York",
  "created_at": "2026-01-24T15:30:00Z",
  "last_active_at": "2026-01-25T10:15:00Z"
}
```

**Errors**:
- 401 Unauthorized: Invalid or expired token

---

## Content Endpoints

### GET /v1/chapters

List all course chapters with metadata.

**Request**:
```http
GET /v1/chapters HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "chapters": [
    {
      "chapter_id": "01-intro-genai",
      "chapter_number": 1,
      "title": "Introduction to Generative AI",
      "subtitle": "Understanding the GenAI landscape",
      "access_tier": "free",
      "estimated_time_minutes": 45,
      "difficulty_level": "beginner",
      "user_has_access": true,
      "user_progress": {
        "completion_status": "completed",
        "quiz_score": 85.0
      }
    },
    {
      "chapter_id": "04-rag",
      "chapter_number": 4,
      "title": "Retrieval-Augmented Generation",
      "subtitle": "RAG architecture and implementation",
      "access_tier": "premium",
      "estimated_time_minutes": 60,
      "difficulty_level": "intermediate",
      "user_has_access": false,
      "user_progress": null
    }
  ],
  "total_chapters": 6,
  "user_subscription": "free"
}
```

---

### GET /v1/chapters/{id}

Get full chapter content including all sections.

**Request**:
```http
GET /v1/chapters/01-intro-genai HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "chapter_id": "01-intro-genai",
  "chapter_number": 1,
  "title": "Introduction to Generative AI",
  "subtitle": "Understanding the GenAI landscape",
  "access_tier": "free",
  "estimated_time_minutes": 45,
  "difficulty_level": "beginner",
  "learning_objectives": [
    "Define Generative AI and distinguish from other AI types",
    "Identify key GenAI model categories (LLMs, image, multimodal)",
    "Understand the historical context and current landscape"
  ],
  "sections": [
    {
      "section_id": "01-what-is-genai",
      "title": "What is Generative AI?",
      "order": 1,
      "estimated_time_minutes": 10,
      "content_markdown": "# What is Generative AI?\n\nGenerative AI is a type of artificial intelligence that can create new content..."
    },
    {
      "section_id": "02-genai-types",
      "title": "Types of Generative Models",
      "order": 2,
      "estimated_time_minutes": 15,
      "content_markdown": "# Types of Generative Models\n\n## Large Language Models (LLMs)\n\nLLMs like GPT-4..."
    }
  ],
  "next_chapter": {
    "chapter_id": "02-llms",
    "title": "Large Language Models"
  },
  "previous_chapter": null
}
```

**Errors**:
- 403 Forbidden: User doesn't have access (free tier requesting premium chapter)
- 404 Not Found: Chapter doesn't exist

**Freemium Blocking (403)**:
```json
{
  "error": {
    "code": "ACCESS_DENIED",
    "message": "Chapter 4 (RAG) is part of our Premium content. Upgrade to unlock advanced topics like RAG, Fine-tuning, and AI Applications.",
    "details": {
      "chapter_id": "04-rag",
      "required_tier": "premium",
      "user_tier": "free",
      "upgrade_url": "/v1/access/upgrade"
    }
  }
}
```

---

### GET /v1/search

Search course content using keyword matching.

**Request**:
```http
GET /v1/search?q=transformer+architecture&limit=10 HTTP/1.1
Authorization: Bearer {token}
```

**Query Parameters**:
- `q`: Search query (required)
- `limit`: Max results (default: 20, max: 100)
- `chapter_id`: Filter by specific chapter (optional)

**Response (200 OK)**:
```json
{
  "query": "transformer architecture",
  "results": [
    {
      "chapter_id": "02-llms",
      "chapter_title": "Large Language Models",
      "section_id": "03-transformer-arch",
      "section_title": "Transformer Architecture Explained",
      "snippet": "...The **transformer architecture** is the foundation of modern LLMs. It uses self-attention mechanisms...",
      "relevance_score": 0.95
    }
  ],
  "total_results": 3,
  "query_time_ms": 45
}
```

---

## Quiz Endpoints

### GET /v1/quizzes/{id}

Get quiz questions for a chapter.

**Request**:
```http
GET /v1/quizzes/01-quiz HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "quiz_id": "01-quiz",
  "chapter_id": "01-intro-genai",
  "passing_score": 70,
  "total_questions": 10,
  "questions": [
    {
      "question_id": "q1",
      "question_text": "Which of the following is a generative model?",
      "type": "multiple-choice",
      "options": ["GPT-4", "Logistic Regression", "Decision Tree", "K-Means"]
    },
    {
      "question_id": "q2",
      "question_text": "Most LLMs are multimodal (text + image).",
      "type": "true-false"
    },
    {
      "question_id": "q3",
      "question_text": "Explain the difference between RAG and fine-tuning.",
      "type": "short-answer",
      "min_words": 20,
      "max_words": 100
    }
  ]
}
```

**Note**: Answer keys and explanations NOT included in GET response. Only provided after submission.

---

### POST /v1/quizzes/{id}/submit

Submit quiz answers and receive graded results.

**Request**:
```http
POST /v1/quizzes/01-quiz/submit HTTP/1.1
Authorization: Bearer {token}
Content-Type: application/json

{
  "answers": {
    "q1": "GPT-4",
    "q2": false,
    "q3": "RAG retrieves relevant documents at inference time, while fine-tuning updates model parameters during training. RAG is better for frequently changing information, while fine-tuning is better for domain adaptation."
  }
}
```

**Response (200 OK)**:
```json
{
  "attempt_id": "660f9511-f3ac-52e5-b827-557766551111",
  "quiz_id": "01-quiz",
  "score": 90.0,
  "passed": true,
  "total_questions": 10,
  "correct_answers": 9,
  "submitted_at": "2026-01-25T14:22:00Z",
  "grading_details": {
    "q1": {
      "correct": true,
      "explanation": "Correct! GPT-4 is a large language model that generates text."
    },
    "q2": {
      "correct": true,
      "explanation": "Correct! Most LLMs are text-only (GPT-3, Claude, etc.). Multimodal models are less common."
    },
    "q3": {
      "correct": true,
      "score": 9.0,
      "feedback": "Excellent explanation! You covered the key differences: retrieval vs training, and appropriate use cases."
    }
  },
  "progress_updated": {
    "chapter_progress": {
      "chapter_id": "01-intro-genai",
      "completion_status": "completed",
      "highest_quiz_score": 90.0
    },
    "overall_progress": {
      "chapters_completed": 1,
      "total_chapters": 6,
      "percentage": 16.67
    }
  }
}
```

**Errors**:
- 400 Bad Request: Missing answers or invalid answer format
- 422 Validation Error: Answer doesn't match expected type (e.g., string for boolean)

---

## Progress Endpoints

### GET /v1/progress

Get comprehensive progress summary for authenticated user.

**Request**:
```http
GET /v1/progress HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "overall_progress": {
    "chapters_completed": 2,
    "total_chapters": 6,
    "completion_percentage": 33.33,
    "total_study_time_minutes": 120,
    "started_at": "2026-01-20T10:00:00Z",
    "last_activity_at": "2026-01-25T14:22:00Z"
  },
  "chapters": [
    {
      "chapter_id": "01-intro-genai",
      "chapter_title": "Introduction to Generative AI",
      "completion_status": "completed",
      "quiz_score": 90.0,
      "time_spent_minutes": 50,
      "last_accessed_at": "2026-01-25T14:22:00Z",
      "completed_at": "2026-01-25T14:22:00Z"
    },
    {
      "chapter_id": "02-llms",
      "chapter_title": "Large Language Models",
      "completion_status": "in_progress",
      "quiz_score": null,
      "time_spent_minutes": 30,
      "last_accessed_at": "2026-01-25T16:00:00Z",
      "completed_at": null
    }
  ],
  "streak": {
    "current_streak": 5,
    "longest_streak": 7,
    "last_activity_date": "2026-01-25"
  },
  "milestones": {
    "achieved": ["first_chapter", "3_day_streak"],
    "next_milestone": {
      "name": "7_day_streak",
      "description": "Study for 7 consecutive days",
      "progress": "5/7 days"
    }
  }
}
```

---

### GET /v1/progress/streaks

Get detailed streak information.

**Request**:
```http
GET /v1/progress/streaks HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "current_streak": 5,
  "longest_streak": 7,
  "last_activity_date": "2026-01-25",
  "timezone": "America/New_York",
  "activity_calendar": {
    "2026-01-21": true,
    "2026-01-22": true,
    "2026-01-23": true,
    "2026-01-24": true,
    "2026-01-25": true
  },
  "milestones": {
    "3_day_streak": {
      "achieved": true,
      "achieved_at": "2026-01-23"
    },
    "7_day_streak": {
      "achieved": false,
      "days_remaining": 2
    }
  },
  "encouragement": "5-day streak! Keep it going. Study tomorrow to reach a 6-day streak!"
}
```

---

## Access Control Endpoints

### GET /v1/access/check

Check which content user has access to based on subscription.

**Request**:
```http
GET /v1/access/check HTTP/1.1
Authorization: Bearer {token}
```

**Response (200 OK)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "subscription_tier": "free",
  "subscription_expires_at": null,
  "access": {
    "free_chapters": ["01-intro-genai", "02-llms", "03-prompting"],
    "premium_chapters": ["04-rag", "05-fine-tuning", "06-ai-applications"],
    "accessible_chapters": ["01-intro-genai", "02-llms", "03-prompting"],
    "locked_chapters": ["04-rag", "05-fine-tuning", "06-ai-applications"]
  },
  "upgrade_benefits": [
    "Access to Chapters 4-6 (RAG, Fine-tuning, AI Applications)",
    "Advanced topics and hands-on exercises",
    "Certificate of completion"
  ],
  "upgrade_url": "/v1/access/upgrade"
}
```

---

## Error Responses

All errors follow consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Resource retrieved successfully |
| 201 | Created | User registered successfully |
| 400 | Bad Request | Invalid input data (missing required field) |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Free tier accessing premium content |
| 404 | Not Found | Chapter ID doesn't exist |
| 409 | Conflict | Email already registered |
| 422 | Validation Error | Pydantic validation failed |
| 429 | Rate Limit Exceeded | Too many requests from this user |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Maintenance mode or dependency failure |

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400/422 | Invalid request data |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `ACCESS_DENIED` | 403 | Insufficient permissions (freemium gate) |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `DUPLICATE_RESOURCE` | 409 | Resource already exists (e.g., email) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error (logged for investigation) |
| `SERVICE_UNAVAILABLE` | 503 | Temporary service disruption |

---

## Rate Limiting

**Rate Limits** (per user):
- Free tier: 1,000 requests per hour
- Premium tier: 10,000 requests per hour

**Headers**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1706112000
X-RateLimit-Tier: free
```

**Rate Limit Exceeded (429)**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 15 minutes.",
    "details": {
      "limit": 1000,
      "reset_at": "2026-01-25T17:00:00Z",
      "tier": "free"
    }
  }
}
```

---

## Pagination

List endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response Format**:
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 147,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## OpenAPI Specification

FastAPI auto-generates OpenAPI 3.0 specification:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

The auto-generated spec can be downloaded and used for:
- Client SDK generation (openapi-generator)
- API testing (Postman, Insomnia)
- Contract validation

---

**API Contracts Complete. Ready for quickstart guide.**
