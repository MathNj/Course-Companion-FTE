# API Contracts: Phase 2 - Hybrid Intelligence

**Feature Branch**: `003-phase-2-hybrid-intelligence`
**Created**: 2026-01-24
**Related Artifacts**: [spec.md](../spec.md) | [plan.md](../plan.md) | [data-model.md](../data-model.md)

---

## Overview

Phase 2 introduces 11 new REST API endpoints under the `/api/v2/*` namespace, completely isolated from Phase 1's `/api/v1/*` endpoints. All Phase 2 endpoints require:
- **Authentication**: JWT bearer token (same as Phase 1)
- **Premium Gating**: `subscription_tier='premium'` verified via middleware
- **Rate Limiting**: 10 adaptive paths + 20 assessments per premium user per month

**Base URL**: `https://api.example.com`
**API Version**: v2 (Phase 2 - Hybrid Intelligence)

---

## Authentication & Premium Gating

All Phase 2 endpoints require a valid JWT token with premium subscription verification.

### Authentication Header
```http
Authorization: Bearer <jwt_token>
```

### Premium Verification
The JWT token must include:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "subscription_tier": "premium",
  "subscription_expires_at": "2026-12-31T23:59:59Z"
}
```

### Error Response: Unauthorized (401)
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required. Please log in.",
    "details": null
  }
}
```

### Error Response: Premium Required (403)
```json
{
  "error": {
    "code": "PREMIUM_REQUIRED",
    "message": "This feature requires a Premium subscription.",
    "benefits": [
      "Personalized adaptive learning paths based on your performance",
      "Detailed AI-powered feedback on open-ended assessments",
      "Priority support and advanced analytics"
    ],
    "upgrade_url": "/api/v1/access/upgrade",
    "pricing": {
      "monthly": 9.99,
      "annual": 99.99
    }
  }
}
```

### Error Response: Rate Limit Exceeded (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded your monthly quota for this feature.",
    "quota": {
      "feature": "adaptive-path",
      "used": 10,
      "limit": 10,
      "reset_date": "2026-02-01T00:00:00Z"
    },
    "upgrade_option": {
      "tier": "pro",
      "benefit": "Unlimited adaptive paths and assessments",
      "price_monthly": 19.99
    }
  }
}
```

---

## Adaptive Learning Path Endpoints

### 1. Generate Adaptive Learning Path

Generate personalized learning recommendations based on student performance patterns.

**Endpoint**: `POST /api/v2/adaptive/path`

**Request Headers**:
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "force_refresh": false,
  "include_reasoning": true
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `force_refresh` | boolean | No | Bypass 24h cache and regenerate path (default: false) |
| `include_reasoning` | boolean | No | Include detailed reasoning for recommendations (default: true) |

**Success Response (200 OK)**:
```json
{
  "path_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "generated_at": "2026-01-24T14:30:00Z",
  "expires_at": "2026-01-25T14:30:00Z",
  "status": "active",
  "recommendations": [
    {
      "chapter_id": "04-rag",
      "section_id": "embeddings-review",
      "priority": 1,
      "reason": "Your quiz scores show weak understanding of vector embeddings (45%), which are foundational for RAG systems. Reviewing this section will significantly improve your comprehension of retrieval mechanisms.",
      "estimated_impact": "high",
      "estimated_time_minutes": 30,
      "links": {
        "chapter": "/api/v1/chapters/04-rag",
        "section": "/api/v1/chapters/04-rag/sections/embeddings-review"
      }
    },
    {
      "chapter_id": "02-llm-training",
      "section_id": "tokenization",
      "priority": 2,
      "reason": "You spent 2.5x average time on Chapter 4, suggesting prerequisite gaps. Tokenization is critical for understanding embeddings and RAG pipelines.",
      "estimated_impact": "high",
      "estimated_time_minutes": 20,
      "links": {
        "chapter": "/api/v1/chapters/02-llm-training",
        "section": "/api/v1/chapters/02-llm-training/sections/tokenization"
      }
    },
    {
      "chapter_id": "04-rag",
      "section_id": "vector-databases",
      "priority": 3,
      "reason": "After mastering embeddings, understanding vector database tradeoffs (Pinecone vs FAISS) will complete your RAG knowledge.",
      "estimated_impact": "medium",
      "estimated_time_minutes": 25,
      "links": {
        "chapter": "/api/v1/chapters/04-rag",
        "section": "/api/v1/chapters/04-rag/sections/vector-databases"
      }
    }
  ],
  "reasoning": "Your learning pattern shows strong performance on Chapters 1-3 (avg 88%) but a significant drop on Chapter 4 (55%). The extended time spent (2.5x average) indicates struggle rather than thoroughness. The core issue appears to be vector embedding concepts, which are prerequisites for RAG understanding. I recommend starting with prerequisite review (tokenization) before re-attempting RAG concepts.",
  "metadata": {
    "total_recommendations": 3,
    "high_priority_count": 2,
    "estimated_total_time_minutes": 75,
    "cached": false
  }
}
```

**Error Response: Insufficient Data (400 Bad Request)**:
```json
{
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "Not enough learning data to generate meaningful recommendations. Complete at least 2 quizzes to receive personalized guidance.",
    "required_quizzes": 2,
    "completed_quizzes": 1,
    "next_steps": [
      "Complete Chapter 2 quiz",
      "Return to request adaptive path after completing more content"
    ]
  }
}
```

**Error Response: Service Unavailable (503)**:
```json
{
  "error": {
    "code": "LLM_SERVICE_UNAVAILABLE",
    "message": "The recommendation service is temporarily unavailable. Your progress is saved, and you can continue learning with standard content. Try again in a few minutes.",
    "fallback": {
      "suggestion": "Review chapters with quiz scores below 70%",
      "weak_chapters": ["04-rag", "05-fine-tuning"]
    },
    "retry_after_seconds": 300
  }
}
```

**Rate Limiting**: 10 requests per premium user per month

**Caching**: Results cached for 24 hours; cache invalidated on new quiz completion (score change >20%)

---

### 2. Get Adaptive Path by ID

Retrieve a previously generated adaptive learning path.

**Endpoint**: `GET /api/v2/adaptive/path/{path_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `path_id` | UUID | Unique identifier of the adaptive path |

**Success Response (200 OK)**:
```json
{
  "path_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "generated_at": "2026-01-24T14:30:00Z",
  "expires_at": "2026-01-25T14:30:00Z",
  "status": "active",
  "recommendations": [...],
  "reasoning": "...",
  "progress": {
    "followed_at": "2026-01-24T15:00:00Z",
    "completed_recommendations": 1,
    "total_recommendations": 3,
    "completion_percentage": 33
  }
}
```

**Error Response: Not Found (404)**:
```json
{
  "error": {
    "code": "PATH_NOT_FOUND",
    "message": "No adaptive path found with ID 7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "suggestion": "Request a new adaptive path via POST /api/v2/adaptive/path"
  }
}
```

---

### 3. List Student's Adaptive Paths

Retrieve all adaptive paths for the authenticated student.

**Endpoint**: `GET /api/v2/adaptive/paths`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status: `active`, `expired`, `superseded` (default: all) |
| `limit` | integer | No | Max results to return (default: 10, max: 50) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Success Response (200 OK)**:
```json
{
  "paths": [
    {
      "path_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "generated_at": "2026-01-24T14:30:00Z",
      "expires_at": "2026-01-25T14:30:00Z",
      "status": "active",
      "recommendations_count": 3,
      "completion_percentage": 33
    },
    {
      "path_id": "a1b2c3d4-e5f6-4747-8888-999999999999",
      "generated_at": "2026-01-20T10:15:00Z",
      "expires_at": "2026-01-21T10:15:00Z",
      "status": "expired",
      "recommendations_count": 4,
      "completion_percentage": 100
    }
  ],
  "pagination": {
    "total": 2,
    "limit": 10,
    "offset": 0,
    "has_more": false
  }
}
```

---

### 4. Mark Recommendation as Completed

Track when a student completes a specific recommendation from their adaptive path.

**Endpoint**: `POST /api/v2/adaptive/path/{path_id}/complete`

**Request Body**:
```json
{
  "chapter_id": "04-rag",
  "section_id": "embeddings-review"
}
```

**Success Response (200 OK)**:
```json
{
  "message": "Recommendation marked as completed",
  "path_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "completed_recommendations": 2,
  "total_recommendations": 3,
  "completion_percentage": 67,
  "next_recommendation": {
    "chapter_id": "04-rag",
    "section_id": "vector-databases",
    "priority": 3
  }
}
```

---

## LLM Assessment Endpoints

### 5. Submit Open-Ended Assessment

Submit a written answer for LLM-powered grading and detailed feedback.

**Endpoint**: `POST /api/v2/assessments/submit`

**Request Headers**:
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "question_id": "04-rag-q1",
  "answer_text": "RAG (Retrieval-Augmented Generation) is best for scenarios requiring up-to-date information or when dealing with large, frequently changing knowledge bases. For example, customer support systems benefit from RAG because product documentation updates regularly. Fine-tuning is better when you need specialized behavior or domain-specific language that won't change often, like medical terminology for a healthcare chatbot. Cost-wise, RAG has ongoing API costs for retrieval but no training costs, while fine-tuning has upfront training costs but cheaper inference. Data privacy is another consideration—RAG can keep sensitive data in your own vector database, whereas fine-tuning embeds data in the model weights."
}
```

**Request Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question_id` | string | Yes | Unique identifier of the assessment question (e.g., "04-rag-q1") |
| `answer_text` | string | Yes | Student's written answer (50-5000 characters) |

**Success Response (202 Accepted)**:
```json
{
  "submission_id": "9a8b7c6d-5e4f-3210-9876-543210fedcba",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_id": "04-rag-q1",
  "submitted_at": "2026-01-24T16:45:00Z",
  "grading_status": "processing",
  "estimated_completion_seconds": 8,
  "feedback_url": "/api/v2/assessments/feedback/9a8b7c6d-5e4f-3210-9876-543210fedcba"
}
```

**Error Response: Answer Too Short (400 Bad Request)**:
```json
{
  "error": {
    "code": "INVALID_ANSWER_LENGTH",
    "message": "Answer must be between 50 and 5000 characters.",
    "current_length": 35,
    "minimum_length": 50,
    "maximum_length": 5000
  }
}
```

**Error Response: Off-Topic/Abusive (400 Bad Request)**:
```json
{
  "error": {
    "code": "INVALID_SUBMISSION",
    "message": "Your answer does not address the question. Please provide a thoughtful response about when to use RAG vs fine-tuning.",
    "suggestion": "Review Chapter 4, Section 5 if you need a refresher on RAG and fine-tuning tradeoffs."
  }
}
```

**Rate Limiting**: 20 submissions per premium user per month

---

### 6. Get Assessment Feedback

Retrieve LLM-generated grading feedback for a submission.

**Endpoint**: `GET /api/v2/assessments/feedback/{submission_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `submission_id` | UUID | Unique identifier of the assessment submission |

**Success Response (200 OK)**:
```json
{
  "feedback_id": "f1e2d3c4-b5a6-9788-6543-210987654321",
  "submission_id": "9a8b7c6d-5e4f-3210-9876-543210fedcba",
  "question_id": "04-rag-q1",
  "grading_status": "completed",
  "quality_score": 8.5,
  "strengths": [
    "Excellent explanation of use case differences (knowledge freshness for RAG, specialized behavior for fine-tuning)",
    "Strong use of concrete examples (customer support, healthcare chatbot)",
    "Good coverage of cost tradeoffs (ongoing API costs vs upfront training costs)",
    "Addressed data privacy considerations with specific technical details"
  ],
  "improvements": [
    "Could expand on latency considerations—RAG typically has higher latency due to retrieval step",
    "Missing discussion of hybrid approaches (combining RAG with fine-tuned models)",
    "Consider mentioning computational requirements for vector database scaling"
  ],
  "detailed_feedback": "Your answer demonstrates strong understanding of the core tradeoffs between RAG and fine-tuning. You effectively used real-world examples to illustrate when each approach is appropriate, and your discussion of cost and data privacy shows practical thinking. To reach expert level, consider exploring latency implications (RAG's retrieval adds 50-200ms overhead) and hybrid architectures that combine both techniques. Overall, this is a high-quality response that goes beyond surface-level understanding.",
  "generated_at": "2026-01-24T16:45:08Z",
  "metadata": {
    "model_version": "claude-sonnet-4-5-20250929",
    "tokens_used": 1420,
    "cost_usd": 0.0066,
    "latency_ms": 3200
  }
}
```

**Response (Grading In Progress - 202 Accepted)**:
```json
{
  "submission_id": "9a8b7c6d-5e4f-3210-9876-543210fedcba",
  "grading_status": "processing",
  "estimated_completion_seconds": 5,
  "message": "Your submission is being graded. Refresh this endpoint in a few seconds for feedback."
}
```

**Error Response: Grading Failed (500 Internal Server Error)**:
```json
{
  "error": {
    "code": "GRADING_FAILED",
    "message": "Failed to grade your submission due to a temporary service issue. Your answer has been saved, and we'll retry grading automatically.",
    "submission_id": "9a8b7c6d-5e4f-3210-9876-543210fedcba",
    "retry_strategy": "Automatic retry in 5 minutes. You'll receive a notification when grading completes."
  }
}
```

---

### 7. List Student's Assessment Submissions

Retrieve all assessment submissions for the authenticated student.

**Endpoint**: `GET /api/v2/assessments/submissions`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question_id` | string | No | Filter by specific question (e.g., "04-rag-q1") |
| `grading_status` | string | No | Filter by status: `pending`, `processing`, `completed`, `failed` |
| `limit` | integer | No | Max results (default: 20, max: 100) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Success Response (200 OK)**:
```json
{
  "submissions": [
    {
      "submission_id": "9a8b7c6d-5e4f-3210-9876-543210fedcba",
      "question_id": "04-rag-q1",
      "submitted_at": "2026-01-24T16:45:00Z",
      "grading_status": "completed",
      "quality_score": 8.5,
      "attempt_number": 1
    },
    {
      "submission_id": "b1c2d3e4-5f6a-7890-1234-567890abcdef",
      "question_id": "05-fine-tuning-q2",
      "submitted_at": "2026-01-23T14:20:00Z",
      "grading_status": "completed",
      "quality_score": 6.0,
      "attempt_number": 2
    }
  ],
  "pagination": {
    "total": 2,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

---

### 8. Get Assessment Question

Retrieve details for a specific open-ended assessment question.

**Endpoint**: `GET /api/v2/assessments/questions/{question_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `question_id` | string | Unique identifier of the question (e.g., "04-rag-q1") |

**Success Response (200 OK)**:
```json
{
  "question_id": "04-rag-q1",
  "chapter_id": "04-rag",
  "question_text": "Explain when you would use RAG (Retrieval-Augmented Generation) versus fine-tuning for a production LLM application. Discuss at least three key factors in your decision (e.g., data freshness, cost, privacy, latency).",
  "evaluation_criteria": [
    "Identifies appropriate use cases for RAG (knowledge freshness, large/changing data)",
    "Identifies appropriate use cases for fine-tuning (specialized behavior, domain language)",
    "Discusses cost tradeoffs (ongoing API costs vs training costs)",
    "Addresses data privacy and security considerations",
    "Mentions latency or performance implications"
  ],
  "example_excellent_answer": "RAG is ideal when dealing with frequently updated knowledge bases, such as product documentation or news content, because it can retrieve current information without retraining. Fine-tuning excels for domain-specific language patterns that remain stable, like medical or legal terminology. Cost-wise, RAG has ongoing retrieval API costs but no training overhead, while fine-tuning requires upfront GPU hours but cheaper inference. For data privacy, RAG can keep sensitive data in your own vector database, whereas fine-tuning embeds data in model weights. Latency is typically higher for RAG (50-200ms retrieval overhead) compared to fine-tuned models. In practice, hybrid approaches combining both techniques often yield the best results.",
  "example_poor_answer": "RAG is better because it uses retrieval. Fine-tuning changes the model. You should use RAG for most things.",
  "expected_length": {
    "minimum_words": 50,
    "recommended_words": 150,
    "maximum_words": 500
  },
  "metadata": {
    "difficulty": "intermediate",
    "estimated_time_minutes": 10,
    "premium_only": true
  }
}
```

---

### 9. List Available Assessment Questions

Retrieve all open-ended assessment questions for premium students.

**Endpoint**: `GET /api/v2/assessments/questions`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chapter_id` | string | No | Filter by chapter (e.g., "04-rag") |

**Success Response (200 OK)**:
```json
{
  "questions": [
    {
      "question_id": "04-rag-q1",
      "chapter_id": "04-rag",
      "question_text": "Explain when you would use RAG versus fine-tuning...",
      "difficulty": "intermediate",
      "student_status": {
        "attempted": true,
        "latest_score": 8.5,
        "attempts_remaining": 2
      }
    },
    {
      "question_id": "04-rag-q2",
      "chapter_id": "04-rag",
      "question_text": "Design a vector database architecture for...",
      "difficulty": "advanced",
      "student_status": {
        "attempted": false,
        "latest_score": null,
        "attempts_remaining": 3
      }
    }
  ],
  "total": 18,
  "chapters_covered": ["04-rag", "05-fine-tuning", "06-ai-apps"]
}
```

---

## Usage Tracking & Admin Endpoints

### 10. Get Student's Usage Quota

Check remaining quota for adaptive paths and assessments in the current month.

**Endpoint**: `GET /api/v2/usage/quota`

**Success Response (200 OK)**:
```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "subscription_tier": "premium",
  "month": "2026-01",
  "adaptive_paths": {
    "used": 7,
    "limit": 10,
    "remaining": 3,
    "reset_date": "2026-02-01T00:00:00Z"
  },
  "assessments": {
    "used": 14,
    "limit": 20,
    "remaining": 6,
    "reset_date": "2026-02-01T00:00:00Z"
  },
  "upgrade_options": [
    {
      "tier": "pro",
      "benefit": "Unlimited adaptive paths and assessments",
      "price_monthly": 19.99
    }
  ]
}
```

---

### 11. Admin: Get Cost Breakdown (Admin Only)

Retrieve detailed LLM cost metrics for monitoring and optimization.

**Endpoint**: `GET /api/v2/admin/costs`

**Authorization**: Requires admin privileges (`role='admin'` in JWT)

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | date | Yes | Start of date range (YYYY-MM-DD) |
| `end_date` | date | Yes | End of date range (YYYY-MM-DD) |
| `group_by` | string | No | Group results by: `student`, `feature`, `day` (default: `feature`) |

**Success Response (200 OK)**:
```json
{
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "total_cost_usd": 247.50,
  "total_requests": 11250,
  "average_cost_per_student": 0.248,
  "breakdown_by_feature": [
    {
      "feature": "adaptive-path",
      "total_requests": 3750,
      "total_cost_usd": 102.00,
      "average_cost_per_request": 0.0091,
      "average_tokens_per_request": 1510
    },
    {
      "feature": "assessment",
      "total_requests": 7500,
      "total_cost_usd": 145.50,
      "average_cost_per_request": 0.0066,
      "average_tokens_per_request": 1195
    }
  ],
  "top_users_by_cost": [
    {
      "student_id": "550e8400-e29b-41d4-a716-446655440000",
      "total_cost_usd": 0.89,
      "requests": {
        "adaptive_paths": 10,
        "assessments": 20
      }
    }
  ],
  "alerts": [
    {
      "type": "COST_THRESHOLD_EXCEEDED",
      "student_id": "abc12345-6789-0abc-def1-234567890abc",
      "cost_usd": 0.67,
      "threshold_usd": 0.50,
      "message": "Student exceeded $0.50/month threshold. Review usage patterns."
    }
  ]
}
```

**Error Response: Forbidden (403)**:
```json
{
  "error": {
    "code": "ADMIN_REQUIRED",
    "message": "This endpoint requires administrator privileges.",
    "required_role": "admin"
  }
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE_CONSTANT",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context",
      "another_field": "More details"
    }
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_REQUEST` | Malformed request body or parameters |
| 400 | `INVALID_ANSWER_LENGTH` | Answer text outside 50-5000 character range |
| 400 | `INSUFFICIENT_DATA` | Not enough learning data for adaptive path |
| 401 | `UNAUTHORIZED` | Missing or invalid JWT token |
| 403 | `PREMIUM_REQUIRED` | Free-tier user attempting premium feature |
| 403 | `ADMIN_REQUIRED` | Non-admin user attempting admin endpoint |
| 404 | `PATH_NOT_FOUND` | Adaptive path ID not found |
| 404 | `SUBMISSION_NOT_FOUND` | Assessment submission ID not found |
| 404 | `QUESTION_NOT_FOUND` | Assessment question ID not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Monthly quota exhausted (10 paths or 20 assessments) |
| 500 | `INTERNAL_SERVER_ERROR` | Unexpected server error |
| 503 | `LLM_SERVICE_UNAVAILABLE` | Anthropic API temporarily unavailable |

---

## Rate Limiting Details

**Premium Tier Quotas** (Per Calendar Month):
- Adaptive paths: 10 requests/month
- LLM assessments: 20 submissions/month

**Reset Schedule**: Quotas reset on the 1st day of each month at 00:00:00 UTC

**Quota Headers** (Included in all Phase 2 responses):
```http
X-RateLimit-Limit-Paths: 10
X-RateLimit-Remaining-Paths: 3
X-RateLimit-Reset-Paths: 2026-02-01T00:00:00Z

X-RateLimit-Limit-Assessments: 20
X-RateLimit-Remaining-Assessments: 6
X-RateLimit-Reset-Assessments: 2026-02-01T00:00:00Z
```

**Rate Limit Exceeded Response** (429):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have used all 10 adaptive paths for this month.",
    "quota": {
      "feature": "adaptive-path",
      "used": 10,
      "limit": 10,
      "reset_date": "2026-02-01T00:00:00Z"
    },
    "upgrade_option": {
      "tier": "pro",
      "benefit": "Unlimited adaptive paths and assessments",
      "price_monthly": 19.99
    }
  }
}
```

---

## Performance Guarantees

**Latency Targets**:
- Adaptive path generation: <5 seconds (p95)
- LLM assessment grading: <10 seconds (p95)
- Quota checks: <50ms (cached in Redis)

**Availability**:
- Target: 99.5% uptime (allows 3.6 hours downtime per month)
- Graceful degradation during LLM service outages (cached results, fallback recommendations)

**Concurrency**:
- Supports 100 concurrent premium users using Phase 2 features
- Request queuing during bursts (max queue depth: 50)

---

## Example Workflows

### Workflow 1: Generate and Follow Adaptive Path

```
1. POST /api/v2/adaptive/path
   → Receive personalized recommendations

2. GET /api/v1/chapters/04-rag/sections/embeddings-review
   → Study recommended section (Phase 1 endpoint)

3. POST /api/v2/adaptive/path/{path_id}/complete
   → Mark recommendation as completed

4. GET /api/v2/adaptive/path/{path_id}
   → Check remaining recommendations and progress
```

### Workflow 2: Submit and Review Assessment

```
1. GET /api/v2/assessments/questions/04-rag-q1
   → Retrieve question details and rubric

2. POST /api/v2/assessments/submit
   → Submit written answer
   → Receive submission_id and "processing" status

3. Wait 5-10 seconds (or poll)

4. GET /api/v2/assessments/feedback/{submission_id}
   → Retrieve detailed feedback, score, strengths, improvements

5. (Optional) POST /api/v2/assessments/submit
   → Re-submit improved answer (attempt 2 of 3)
```

### Workflow 3: Check Quota Before Request

```
1. GET /api/v2/usage/quota
   → Check remaining paths/assessments

2. If remaining > 0:
   POST /api/v2/adaptive/path OR POST /api/v2/assessments/submit

3. If remaining = 0:
   Display upgrade prompt to user
```

---

## Testing Endpoints

### Test Authentication
```bash
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password123"}'

# Response includes JWT token
```

### Test Premium Gating (Should Return 403)
```bash
curl -X POST https://api.example.com/api/v2/adaptive/path \
  -H "Authorization: Bearer <free_user_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh":false}'

# Expected: 403 Forbidden with PREMIUM_REQUIRED error
```

### Test Adaptive Path Generation
```bash
curl -X POST https://api.example.com/api/v2/adaptive/path \
  -H "Authorization: Bearer <premium_user_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh":false,"include_reasoning":true}'

# Expected: 200 OK with recommendations array
```

### Test Assessment Submission
```bash
curl -X POST https://api.example.com/api/v2/assessments/submit \
  -H "Authorization: Bearer <premium_user_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id":"04-rag-q1",
    "answer_text":"RAG is best for scenarios requiring up-to-date information or when dealing with large, frequently changing knowledge bases..."
  }'

# Expected: 202 Accepted with submission_id
```

### Test Rate Limiting (11th Path Request)
```bash
# After making 10 adaptive path requests
curl -X POST https://api.example.com/api/v2/adaptive/path \
  -H "Authorization: Bearer <premium_user_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh":false}'

# Expected: 429 Rate Limit Exceeded with quota details
```

---

## Versioning & Backward Compatibility

**Current Version**: v2 (Phase 2 - Hybrid Intelligence)

**Phase 1 Compatibility**: All `/api/v1/*` endpoints remain unchanged and LLM-free. Phase 2 does not modify Phase 1 contracts.

**Future Versioning**: If breaking changes are required, a new `/api/v3/*` namespace will be created. `/api/v2/*` will be maintained for at least 12 months after deprecation notice.

**Deprecation Policy**:
1. 90-day advance notice for endpoint deprecation
2. 12-month compatibility window with deprecation warnings
3. Clear migration guides provided

---

**API Contracts Complete. See [quickstart.md](../quickstart.md) for development setup.**
