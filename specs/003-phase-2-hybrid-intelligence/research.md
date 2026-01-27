# Research Document: Phase 2 - Hybrid Intelligence

**Feature**: Phase 2 - Hybrid Intelligence Course Companion
**Date**: 2026-01-27
**Status**: Complete

## Overview

This document consolidates research findings for implementing Phase 2 hybrid intelligence features (Adaptive Learning Paths and LLM-Graded Assessments) while maintaining strict architectural isolation from Phase 1 deterministic endpoints.

---

## Decision 1: Anthropic API Integration Pattern

**Decision**: Use Anthropic Python SDK (anthic>=0.40) with Messages API for Claude Sonnet 4.5

**Rationale**:
- Official SDK with comprehensive error handling
- Built-in retry logic for transient failures
- Streaming support (future enhancement potential)
- Token counting utilities for cost tracking
- Type hints for better IDE support

**Alternatives Considered**:
- **Direct HTTP calls**: Rejected due to manual error handling, retry logic, and token counting complexity
- **LangChain/AutoGen**: Rejected as over-engineered for 2 simple features, adds dependency bloat
- **Azure OpenAI proxy**: Rejected due to additional latency and cost overhead

**Implementation Pattern**:
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2000,
    temperature=0.3,  # Lower temp for consistent educational output
    messages=[...]
)
```

**Cost Tracking**:
```python
# Input tokens: response.usage.input_tokens
# Output tokens: response.usage.output_tokens
# Cost calculation tracked in LLMUsageLog table
```

---

## Decision 2: Database Schema Extension Strategy

**Decision**: Extend existing PostgreSQL schema with 6 new tables for Phase 2 entities

**Rationale**:
- Maintain single database for simplicity (Phase 1 already uses PostgreSQL)
- ACID compliance for critical LLM usage tracking
- JSON support for flexible recommendation/feedback storage
- Foreign key relationships ensure referential integrity

**Alternatives Considered**:
- **Separate MongoDB for LLM logs**: Rejected due to additional infrastructure complexity and migration overhead
- **SQLite for LLM logs**: Rejected due to concurrency limitations for multi-user production

**New Tables**:
1. `adaptive_paths` - Generated personalized learning recommendations
2. `recommendations` - Individual suggestion items within paths
3. `open_ended_questions` - Assessment question catalog
4. `assessment_submissions` - Student answer submissions
5. `assessment_feedback` - LLM-generated grading results
6. `llm_usage_logs` - Cost tracking and audit logs
7. `premium_usage_quotas` - Rate limiting per premium user

**Migration Strategy**:
- Use Alembic migrations for version control
- Incremental migration (add tables without altering Phase 1 schema)
- Backwards compatible (Phase 1 continues working during migration)

---

## Decision 3: Redis Caching Strategy for LLM Results

**Decision**: Cache adaptive paths for 24 hours with invalidation on new quiz data

**Rationale**:
- Cost optimization (reduce LLM calls by 60-70% estimated)
- Quiz performance changes infrequently (students take 1-3 days per chapter)
- 24-hour TTL balances freshness with cost
- Cache key: `adaptive_path:{user_id}` with version based on last quiz timestamp

**Alternatives Considered**:
- **No caching**: Rejected due to excessive LLM costs (estimated 3-5x higher)
- **Longer TTL (7 days)**: Rejected due to stale recommendations after progress
- **Client-side caching**: Rejected due to cache invalidation complexity

**Implementation**:
```python
cache_key = f"adaptive_path:{user_id}"
cache_version = int(last_quiz_timestamp / 86400)  # Daily version

cached_path = await redis.get(f"{cache_key}:{cache_version}")
if cached_path:
    return json.loads(cached_path)

# Generate new path
new_path = await generate_adaptive_path(user_id)
await redis.setex(f"{cache_key}:{cache_version}", 86400, json.dumps(new_path))
return new_path
```

---

## Decision 4: Premium Gating Middleware Architecture

**Decision**: FastAPI dependency injection for premium verification with role-based access control

**Rationale**:
- Leverages existing authentication infrastructure (JWT tokens from Phase 1)
- Clean separation via dependency injection (testable, reusable)
- Automatic enforcement on all `/api/v2/*` routes
- Graceful upgrade prompts for free-tier users

**Alternatives Considered**:
- **Decorator-based gating**: Rejected due to less explicit dependency chain
- **Route-level checks in each endpoint**: Rejected due to code duplication
- **Separate auth service for v2**: Rejected due to additional complexity

**Implementation**:
```python
from app.dependencies import get_current_user, verify_premium_subscription

@router.post("/adaptive-path")
async def generate_adaptive_path(
    current_user: User = Depends(get_current_user),
    _premium_verified: None = Depends(verify_premium_subscription),
    db: AsyncSession = Depends(get_db)
):
    # User is guaranteed premium here
    pass
```

**Upgrade Response**:
```json
{
  "detail": "Personalized learning paths are available with Premium. Upgrade to get AI-powered recommendations tailored to your progress.",
  "upgrade_url": "https://course-companion-fte.fly.dev/api/v1/payments/create-checkout-session"
}
```

---

## Decision 5: Rate Limiting Implementation

**Decision**: Redis-based per-user quota tracking with monthly reset

**Rationale**:
- Shared state across multiple backend instances (horizontal scaling)
- Atomic INCR operations prevent race conditions
- Automatic expiration (monthly reset)
- Sub-millisecond latency

**Alternatives Considered**:
- **PostgreSQL-based tracking**: Rejected due to row locking contention under load
- **In-memory (Python) counters**: Rejected due to state loss on restart
- **API gateway rate limiting**: Rejected due to external dependency

**Implementation**:
```python
async def check_premium_quota(user_id: int, feature: str) -> bool:
    month_key = datetime.utcnow().strftime("%Y-%m")
    key = f"quota:{feature}:{user_id}:{month_key}"

    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 2678400)  # 31 days

    limits = {"adaptive_path": 10, "assessment": 20}
    return current <= limits[feature]
```

**Quota Exceeded Response**:
```json
{
  "detail": "You've used your monthly allocation of 10 adaptive learning paths. Additional requests available next month or upgrade to Pro tier for unlimited access.",
  "quota": {"used": 10, "limit": 10, "resets_at": "2026-02-01T00:00:00Z"}
}
```

---

## Decision 6: Cost Tracking and Alerting

**Decision**: Dual-layer cost tracking (per-request log + monthly aggregation)

**Rationale**:
- **Per-request logging**: Real-time cost visibility, audit trail, debugging
- **Monthly aggregation**: Efficient querying for admin dashboard, trend analysis
- Alert thresholds at $0.40/user (80% of $0.50 budget) for proactive response

**Alternatives Considered**:
- **External SaaS monitoring (Datadog)**: Rejected due to additional cost
- **Only aggregate tracking**: Rejected due to lack of granular debugging data
- **Client-side cost estimation**: Rejected due to trust issues (users could manipulate)

**Implementation**:
```python
async def log_llm_usage(
    user_id: int,
    feature: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int
):
    cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)

    # Detailed log
    await db.execute(insert(LLMUsageLog).values(
        user_id=user_id,
        feature=feature,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        latency_ms=latency_ms,
        timestamp=datetime.utcnow()
    ))

    # Check monthly aggregation
    monthly_cost = await get_monthly_cost(user_id)
    if monthly_cost > 0.40:
        await send_cost_alert(user_id, monthly_cost)
```

---

## Decision 7: LLM Prompt Engineering Strategy

**Decision**: Use structured prompts with JSON output parsing and rubric-based evaluation

**Rationale**:
- JSON output enables programmatic parsing (recommendations, feedback)
- Rubrics ensure consistent grading quality
- Few-shot examples reduce hallucination risk
- Temperature 0.3 for deterministic educational content

**Alternatives Considered**:
- **Free-form text parsing**: Rejected due to fragility and parsing errors
- **Higher temperature (0.7-0.9)**: Rejected due to inconsistent grading
- **Function calling (tools)**: Rejected due to complexity and cost overhead

**Adaptive Path Prompt Template**:
```python
prompt = f"""
You are an expert educational analyst for a Generative AI course. Analyze the student's performance data and generate personalized learning recommendations.

Student Performance Data:
{json.dumps(performance_data, indent=2)}

Course Structure:
{json.dumps(course_structure, indent=2)}

Generate 3-5 prioritized recommendations in JSON format:
{{
  "recommendations": [
    {{
      "chapter_id": 1,
      "section_id": "3.2",
      "priority": 1,
      "reason": "Specific explanation...",
      "estimated_impact": "high",
      "estimated_time_minutes": 45
    }}
  ]
}}

Focus on weak areas (quiz scores below 60%) and prerequisite gaps.
"""
```

**Assessment Grading Prompt Template**:
```python
prompt = f"""
You are an expert educator for Generative AI. Grade the student's answer using the provided rubric.

Question: {question.text}

Rubric:
- Knowledge accuracy (0-3 points): {rubric.accuracy}
- Depth of understanding (0-3 points): {rubric.depth}
- Clarity of explanation (0-2 points): {rubric.clarity}
- Real-world examples (0-2 points): {rubric.examples}

Student Answer:
{submission.answer_text}

Provide feedback in JSON format:
{{
  "total_score": 7.5,
  "rubric_scores": {{
    "accuracy": 2.5,
    "depth": 2.0,
    "clarity": 1.5,
    "examples": 1.5
  }},
  "strengths": ["Strong explanation of cost tradeoffs"],
  "improvements": ["Missing discussion of data privacy considerations"],
  "detailed_feedback": "Comprehensive paragraph...",
  "off_topic": false
}}

Be constructive and specific. If answer is off-topic or nonsensical, set off_topic=true.
"""
```

---

## Decision 8: Phase 1/2 Architectural Isolation Enforcement

**Decision**: Separate FastAPI routers, service modules, and automated CI/CD tests

**Rationale**:
- Constitutional requirement (Zero-Backend-LLM for Phase 1)
- Prevents accidental cross-contamination during development
- CI/CD test blocks merges if isolation violated

**Implementation Structure**:
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/          # Phase 1: Deterministic only
│   │   │   ├── chapters.py
│   │   │   ├── quizzes.py
│   │   │   └── progress.py
│   │   └── v2/          # Phase 2: LLM-powered
│   │       ├── adaptive_paths.py
│   │       └── assessments.py
│   ├── services/
│   │   ├── content.py       # Phase 1: Content serving
│   │   ├── quiz.py          # Phase 1: Quiz grading
│   │   └── llm/             # Phase 2: LLM services
│   │       ├── adaptive_path.py
│   │       └── assessment.py
│   └── middleware/
│       └── premium_gating.py  # Phase 2: Premium verification

```

**Automated Isolation Test**:
```python
# tests/test_phase_isolation.py
def test_v1_routes_make_zero_llm_calls():
    """FAILS if any /api/v1/* endpoint calls LLM services"""
    from unittest.mock import patch
    from app.api.v1.chapters import router as v1_router
    from app.api.v1.quizzes import router as v1_quiz_router

    # Mock Anthropic client to detect any calls
    with patch('app.services.llm.adaptive_path.anthropic.Anthropic') as mock_llm:
        # Exercise all v1 endpoints
        client = TestClient(app)
        client.get("/api/v1/chapters")
        client.get("/api/v1/quizzes/1")
        client.get("/api/v1/progress")

        # Assert ZERO LLM calls
        assert mock_llm.call_count == 0, "Phase 1 MUST NOT call LLM services"

def test_v2_import_isolation():
    """FAILS if v1 modules import from v2 or services/llm/"""
    import ast
    import os

    v1_files = []
    for root, dirs, files in os.walk("app/api/v1"):
        for file in files:
            if file.endswith(".py"):
                v1_files.append(os.path.join(root, file))

    for file_path in v1_files:
        with open(file_path) as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not alias.name.startswith("app.api.v2"), \
                            f"{file_path} illegally imports from v2"
                        assert not alias.name.startswith("app.services.llm"), \
                            f"{file_path} illegally imports from LLM services"
```

---

## Decision 9: Error Handling and Graceful Degradation

**Decision**: Structured error responses with fallback to Phase 1 functionality

**Rationale**:
- LLM services can be temporarily unavailable (API outages, rate limits)
- Students should continue learning with Phase 1 content during degradation
- Clear communication prevents frustration

**Error Response Patterns**:
```json
// LLM Service Unavailable (503)
{
  "detail": "I'm currently unable to generate personalized recommendations. Your progress is saved, and you can continue learning with standard content. Try again in a few minutes for adaptive guidance.",
  "error_code": "LLM_SERVICE_UNAVAILABLE",
  "retry_after": 60
}

// Insufficient Data for Recommendations (400)
{
  "detail": "I need more learning data to provide meaningful recommendations. Complete at least 2 quizzes first, then I can analyze your performance patterns and suggest a personalized path.",
  "error_code": "INSUFFICIENT_DATA",
  "required_quizzes": 2
}

// Monthly Quota Exceeded (429)
{
  "detail": "You've used your monthly allocation of 10 adaptive learning paths. Additional requests available next month or upgrade to Pro tier for unlimited access.",
  "error_code": "QUOTA_EXCEEDED",
  "quota": {"used": 10, "limit": 10, "resets_at": "2026-02-01T00:00:00Z"}
}
```

---

## Decision 10: Testing Strategy for LLM Features

**Decision**: Three-layer testing with mock LLM responses for unit/integration tests

**Rationale**:
- **Unit tests**: Mock LLM responses (deterministic, fast, cost-free)
- **Integration tests**: Real LLM calls in staging environment (quality validation)
- **E2E tests**: Full user flows with mock LLM responses (workflow validation)

**Test Layers**:
```python
# Unit Tests (Mock LLM)
@pytest.mark.asyncio
async def test_generate_adaptive_path_with_mock():
    with patch('app.services.llm.adaptive_path.anthropic.Anthropic') as mock_llm:
        mock_llm.return_value = MockLLMResponse(
            recommendations=[...],
            usage=MockUsage(input_tokens=1800, output_tokens=500)
        )
        path = await generate_adaptive_path(user_id=1)
        assert len(path.recommendations) == 3

# Integration Tests (Real LLM in staging)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_adaptive_path_quality():
    response = await client.post("/api/v2/adaptive-path", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 2

# E2E Tests (User journey)
@pytest.mark.e2e
async def test_premium_user_adaptive_flow():
    # Login as premium user
    # Complete quiz with low score
    # Request adaptive path
    # Verify recommendations address weak area
    pass
```

**LLM Response Validation**:
- Check for valid JSON structure
- Validate score ranges (0-10)
- Ensure feedback is constructive (no negative language)
- Detect off-topic responses

---

## Summary of Key Decisions

| Decision | Choice | Impact |
|----------|--------|--------|
| LLM API | Anthropic Python SDK | Official support, cost tracking |
| Database | Extend PostgreSQL (7 new tables) | Single DB, ACID compliance |
| Caching | Redis 24-hour TTL | 60-70% cost reduction |
| Premium Gating | FastAPI dependency injection | Clean, testable, reusable |
| Rate Limiting | Redis per-user quotas | Horizontal scaling support |
| Cost Tracking | Per-request + monthly aggregation | Real-time + trend analysis |
| Prompt Strategy | JSON output + rubrics | Consistent quality, parsing |
| Isolation | Separate routers + CI/CD tests | Constitutional compliance |
| Error Handling | Graceful degradation to Phase 1 | Continuous learning experience |
| Testing | Mocked unit + real integration | Fast validation + quality assurance |

---

## Next Steps

1. **Generate data-model.md**: Define SQLAlchemy models for 7 new tables
2. **Generate API contracts**: OpenAPI specs for `/api/v2/*` endpoints
3. **Create quickstart.md**: Developer setup guide for Phase 2
4. **Update plan.md**: Fill technical context with research findings
5. **Execute Phase 1/2 isolation test**: Verify constitutional compliance

---

**Status**: ✅ Research complete, all technical decisions finalized
**Date**: 2026-01-27
