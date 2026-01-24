# Research: Course Companion FTE

**Phase**: 0 (Research & Technology Decisions)
**Date**: 2026-01-24
**Purpose**: Resolve technical unknowns and validate technology choices before implementation

## Research Questions

### 1. How do we ensure zero LLM calls in Phase 1 backend?

**Decision**: Implement automated testing with environment mocking

**Rationale**:
- Constitution requires ZERO LLM calls in Phase 1 (disqualification risk)
- Manual code review is insufficient for guaranteed compliance
- Automated tests provide continuous verification during development

**Implementation Approach**:
```python
# tests/test_v1_deterministic.py
def test_zero_llm_calls():
    """Verify Phase 1 APIs make NO LLM calls"""
    with mock_llm_environment() as mock_env:
        # Call all v1 endpoints
        client.get("/api/v1/chapters/1")
        client.post("/api/v1/quizzes/1/submit", json={"answers": [...]})
        client.get("/api/v1/progress")

        # Assert no LLM APIs were called
        assert mock_env.anthropic_calls == 0
        assert mock_env.openai_calls == 0
```

**Alternatives Considered**:
- Static code analysis: Too many false positives/negatives
- Runtime monitoring: Detects violations too late (after deployment)
- Code review only: Human error risk

**Best Practices**:
- Run test in CI/CD pipeline (blocks merging if fails)
- Mock all LLM SDK imports to raise errors if called
- Include test in Phase 1 checklist

---

### 2. What's the best way to structure ChatGPT App system prompts?

**Decision**: Separate prompt files per mode with shared context preamble

**Rationale**:
- Each Agent Skill represents a distinct interaction mode
- Prompts need to be independently testable and maintainable
- Shared preamble ensures consistent grounding in course content

**Implementation Approach**:
```text
chatgpt-app/prompts/
├── _shared-context.txt      # Grounding instructions (all modes)
├── teach.txt                # concept-explainer skill
├── quiz.txt                 # quiz-master skill
├── socratic.txt             # socratic-tutor skill
└── motivation.txt           # progress-motivator skill
```

**Shared Context Template**:
```
You are a Course Companion for Generative AI Fundamentals. You have access to:
- 6 chapters of curated course content (Intro to GenAI, LLMs, Prompting, RAG, Fine-tuning, AI Applications)
- Quiz banks with validated answer keys
- Student progress data

CRITICAL GROUNDING RULES:
- All explanations MUST be grounded in course content
- Never hallucinate information not in the course
- If asked about topics outside the course, politely redirect
- Use the backend API to retrieve content, quizzes, and progress
```

**Alternatives Considered**:
- Single monolithic prompt: Hard to maintain, test, and adapt
- Dynamic prompt generation: Adds complexity and latency
- No shared context: Risk of inconsistent behavior

**Best Practices**:
- Version control prompts with git
- Test each prompt mode independently
- Include examples in prompts (few-shot learning)

---

### 3. How do we structure course content for efficient storage and retrieval?

**Decision**: JSON format with chapter/section hierarchy, stored in Cloudflare R2

**Rationale**:
- JSON is parseable, versioned, and cacheable
- R2 provides S3-compatible API with edge caching (low latency)
- Structured format enables search indexing and content updates

**Content Schema**:
```json
{
  "chapter_id": "01-intro-genai",
  "chapter_number": 1,
  "title": "Introduction to Generative AI",
  "learning_objectives": [
    "Understand what Generative AI is and its applications",
    "Distinguish between different GenAI model types (LLMs, image, multimodal)"
  ],
  "sections": [
    {
      "section_id": "01-what-is-genai",
      "title": "What is Generative AI?",
      "content_markdown": "Generative AI refers to...",
      "examples": ["ChatGPT", "DALL-E", "Stable Diffusion"],
      "key_concepts": ["large language models", "diffusion models"]
    }
  ],
  "prerequisites": [],
  "estimated_time_minutes": 45
}
```

**Quiz Schema**:
```json
{
  "quiz_id": "01-quiz",
  "chapter_id": "01-intro-genai",
  "questions": [
    {
      "question_id": "q1",
      "type": "multiple_choice",
      "question_text": "Which of the following is NOT a type of Generative AI?",
      "options": [
        {"id": "a", "text": "Large Language Models"},
        {"id": "b", "text": "Image Generation Models"},
        {"id": "c", "text": "Rule-Based Expert Systems"},
        {"id": "d", "text": "Multimodal Models"}
      ],
      "correct_answer": "c",
      "explanation": "Rule-based expert systems are not generative; they follow predetermined logic."
    }
  ]
}
```

**Alternatives Considered**:
- Markdown files: Harder to parse and query
- Database storage: More expensive, slower for read-heavy workload
- Git LFS: No edge caching, slower delivery

**Best Practices**:
- Version content files (semantic versioning)
- Cache content at CDN edge (Cloudflare cache)
- Pre-compute search embeddings during content upload

---

### 4. What's the optimal database schema for progress tracking?

**Decision**: Relational schema with separate tables for users, progress, quiz_attempts, and streaks

**Rationale**:
- Relational model ensures data integrity (foreign keys, constraints)
- Separate tables enable efficient queries (e.g., "users with 3+ day streaks")
- PostgreSQL provides JSONB for flexible metadata storage

**Schema Design**:
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- For email/password auth
    subscription_tier VARCHAR(20) DEFAULT 'free',  -- 'free', 'premium', 'pro'
    subscription_expires_at TIMESTAMP,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP
);

-- Progress table
CREATE TABLE chapter_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    chapter_id VARCHAR(50) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    last_section_id VARCHAR(50),
    time_spent_seconds INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    UNIQUE(user_id, chapter_id)
);

-- Quiz attempts table
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quiz_id VARCHAR(50) NOT NULL,
    score DECIMAL(5,2),  -- e.g., 87.50
    total_questions INTEGER,
    answers JSONB,  -- {question_id: selected_answer}
    submitted_at TIMESTAMP DEFAULT NOW(),
    time_taken_seconds INTEGER
);

-- Streaks table
CREATE TABLE streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table (for conversation history)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    interaction_count INTEGER DEFAULT 0,
    metadata JSONB  -- {device, interface: 'chatgpt'|'web', actions: [...]}
);
```

**Alternatives Considered**:
- NoSQL (MongoDB): Harder to enforce data integrity, less mature for transactions
- Single "user_data" JSONB column: Poor query performance, no indexing
- Event sourcing: Over-engineered for this use case

**Best Practices**:
- Use UUIDs for primary keys (avoid enumeration attacks)
- Index foreign keys and frequently queried columns
- Use database migrations (Alembic) for schema changes
- Implement soft deletes for audit trail

---

### 5. How do we handle freemium access control efficiently?

**Decision**: Middleware-based access control with subscription tier checks

**Rationale**:
- Centralized access logic (DRY principle)
- Can be tested independently
- Performance: Single database query with caching

**Implementation Approach**:
```python
# backend/app/dependencies.py
from fastapi import Depends, HTTPException, status
from app.models.user import User

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from JWT token"""
    # Verify JWT and load user from database
    return user

async def require_free_tier(user: User = Depends(get_current_user)) -> User:
    """Allow all users (used for Chapters 1-3)"""
    return user

async def require_premium(user: User = Depends(get_current_user)) -> User:
    """Require premium or pro subscription"""
    if user.subscription_tier not in ['premium', 'pro']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a premium subscription"
        )
    if user.subscription_expires_at and user.subscription_expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Your subscription has expired"
        )
    return user

# Usage in endpoints
@router.get("/api/v1/chapters/4")
async def get_chapter_4(user: User = Depends(require_premium)):
    # Only accessible to premium users
    return content
```

**Alternatives Considered**:
- Route-level decorators: Less flexible, harder to test
- Manual checks in each endpoint: Code duplication, error-prone
- API gateway authorization: Adds infrastructure complexity

**Best Practices**:
- Cache subscription tier in Redis (reduce database queries)
- Return helpful error messages with upgrade links
- Log access denials for analytics (track conversion funnel)

---

### 6. What's the best approach for adaptive learning recommendations (Phase 2)?

**Decision**: Pattern analysis + Claude Sonnet prompt engineering

**Rationale**:
- Pattern analysis provides objective data (quiz scores, time spent, skip patterns)
- Claude Sonnet synthesizes patterns into personalized recommendations
- Cost-effective: Only runs for premium users on explicit request

**Implementation Approach**:
```python
# backend/app/services/adaptive.py
async def generate_adaptive_path(user_id: UUID) -> AdaptivePath:
    # 1. Gather user data
    quiz_scores = await get_quiz_scores(user_id)
    time_data = await get_time_spent_per_section(user_id)
    progress = await get_chapter_completion(user_id)

    # 2. Identify patterns
    weak_areas = [chapter for chapter, score in quiz_scores.items() if score < 60]
    slow_sections = [section for section, time in time_data.items() if time > avg_time * 1.5]
    skipped = [chapter for chapter in CHAPTERS if chapter not in progress]

    # 3. Use Claude Sonnet to generate recommendations
    prompt = f"""
    You are an educational advisor for a Generative AI Fundamentals course.

    Student Performance Data:
    - Weak areas (quiz < 60%): {weak_areas}
    - Slow sections (above average time): {slow_sections}
    - Skipped chapters: {skipped}
    - Overall progress: {len(progress)}/6 chapters

    Generate a personalized learning path with:
    1. Priority focus areas (3-5 sections to review)
    2. Recommended sequence (order of study)
    3. Estimated time to proficiency
    4. Specific exercises or practice questions

    Be encouraging and specific.
    """

    response = await claude.complete(prompt)

    # 4. Track cost
    await log_llm_cost(user_id, tokens=response.usage.total_tokens)

    return AdaptivePath(recommendations=response.text)
```

**Cost Tracking**:
- Claude Sonnet: $3/$15 per million tokens (input/output)
- Estimated 2,000 tokens per request = ~$0.018/request
- Monthly cost (1K premium users, 10 requests/month) = ~$180

**Alternatives Considered**:
- Rule-based recommendations: Less personalized, misses nuanced patterns
- Pre-computed paths: Not adaptive to individual needs
- Local ML model: Requires training data, ongoing maintenance

**Best Practices**:
- Limit to 2-3 recommendations per user per day (cost control)
- Cache recommendations for 24 hours (reduce redundant calls)
- A/B test effectiveness (measure improvement rates)

---

### 7. How do we implement LLM-graded assessments (Phase 2)?

**Decision**: Claude Sonnet with rubric-based prompting and expert validation

**Rationale**:
- Claude Sonnet excels at nuanced evaluation (reasoning quality, depth)
- Rubric ensures consistent grading across submissions
- Expert validation (human-in-the-loop) builds trust

**Grading Prompt Template**:
```python
def grade_open_ended_answer(question: str, student_answer: str, rubric: dict) -> Assessment:
    prompt = f"""
    You are grading a student's answer to an open-ended question on Generative AI Fundamentals.

    Question: {question}

    Student's Answer:
    {student_answer}

    Grading Rubric:
    - Accuracy (0-10): Are the facts correct?
    - Completeness (0-10): Did they address all parts of the question?
    - Depth (0-10): Do they demonstrate deep understanding or just surface knowledge?
    - Clarity (0-10): Is the explanation clear and well-organized?

    Provide:
    1. Score for each rubric dimension
    2. Overall score (out of 40)
    3. Specific feedback on what was done well
    4. Specific feedback on what could be improved
    5. Suggested next steps for learning

    Be constructive and encouraging.
    """

    response = await claude.complete(prompt)

    # Parse response into structured format
    assessment = parse_assessment(response.text)

    # Track cost
    await log_llm_cost(user_id, tokens=response.usage.total_tokens)

    return assessment
```

**Expert Validation Process**:
- Randomly sample 10% of LLM-graded assessments
- Have human expert grade the same submissions
- Measure agreement (target: 90%+ alignment)
- Use disagreements to improve rubric

**Cost Tracking**:
- Estimated 1,500 tokens per assessment = ~$0.014/assessment
- Monthly cost (1K premium users, 10 assessments/month) = ~$140

**Alternatives Considered**:
- GPT-4: Similar cost, slightly lower performance on reasoning evaluation
- Human-only grading: Too expensive and slow
- Automated keyword matching: Misses reasoning quality

**Best Practices**:
- Provide rubric to students upfront (transparency)
- Allow students to request re-grading (with limit: 2/month)
- Continuous improvement: Update rubric based on edge cases

---

## Technology Stack Validation

### Backend: FastAPI + Python 3.11+
**Decision**: Confirmed ✅

**Rationale**:
- FastAPI provides automatic OpenAPI documentation
- Native async/await support (high concurrency)
- Pydantic v2 for request/response validation
- Excellent ecosystem (SQLAlchemy, pytest, Alembic)

**Alternatives**: Django (heavier, more opinionated), Flask (less modern, no async)

### Frontend: Next.js 14 + TypeScript
**Decision**: Confirmed ✅

**Rationale**:
- App Router (React Server Components) for performance
- TypeScript for type safety (reduces bugs)
- Built-in image optimization, routing, and SSR
- shadcn/ui for consistent UI components

**Alternatives**: Create React App (no SSR), Remix (less mature ecosystem)

### Storage: Cloudflare R2
**Decision**: Confirmed ✅

**Rationale**:
- S3-compatible API (easy migration)
- Zero egress fees (major cost savings vs S3)
- Edge caching built-in (low latency globally)

**Alternatives**: AWS S3 (expensive egress), Google Cloud Storage (less global edge)

### Database: PostgreSQL (Neon/Supabase)
**Decision**: Confirmed ✅

**Rationale**:
- Neon: Generous free tier, autoscaling, branching for dev/prod
- Supabase: Real-time features, built-in auth (if needed)
- PostgreSQL: ACID compliance, mature, excellent tooling

**Alternatives**: MySQL (less feature-rich), MongoDB (poor fit for relational data)

### Cache: Redis (Upstash/Redis Cloud)
**Decision**: Confirmed ✅

**Rationale**:
- Upstash: Serverless, pay-per-request (cost-efficient for low traffic)
- Redis Cloud: Free tier (250MB), good for development
- Redis: Fast, simple API, widely supported

**Alternatives**: Memcached (less feature-rich), in-memory cache (doesn't persist)

---

## Cost Analysis (Updated)

### Phase 1 (Zero-Backend-LLM)
| Component | Provider | Monthly Cost (10K users) |
|-----------|----------|--------------------------|
| Cloudflare R2 | Cloudflare | $5 (storage + reads) |
| PostgreSQL | Neon | $0 (free tier sufficient) |
| Redis | Upstash | $0 (free tier sufficient) |
| Compute | Fly.io | $10 (shared-cpu-1x) |
| Domain | Namecheap | $1 (annual / 12) |
| **Total** | | **$16/month** |
| **Per User** | | **$0.0016/user/month** |

✅ **Meets constitutional target**: <$0.004/user/month

### Phase 2 (Hybrid Intelligence - Premium Only)
| Feature | Model | Cost/Request | Monthly (1K users, 10 req/month) |
|---------|-------|--------------|----------------------------------|
| Adaptive Path | Claude Sonnet | $0.018 | $180 |
| LLM Assessment | Claude Sonnet | $0.014 | $140 |
| **Total** | | | **$320/month** |
| **Per Premium User** | | | **$0.32/user/month** |

✅ **Meets constitutional target**: <$0.50/user/month

### Revenue Model (10K total users)
| Tier | Users | Price/Month | Monthly Revenue |
|------|-------|-------------|-----------------|
| Free | 5,000 (50%) | $0 | $0 |
| Premium | 4,500 (45%) | $9.99 | $44,955 |
| Pro | 500 (5%) | $19.99 | $9,995 |
| **Total** | 10,000 | | **$54,950** |

**Net Margin**: $54,950 - $336 = **$54,614/month (99.4% margin)**

---

## Risks and Mitigations

### Risk 1: Phase 1 backend accidentally makes LLM calls
**Mitigation**: Automated test with environment mocking (fails CI/CD if violated)

### Risk 2: ChatGPT App prompt injection attacks
**Mitigation**: Grounding instructions, input sanitization, user report mechanism

### Risk 3: Premium users exceed LLM cost budget
**Mitigation**: Rate limiting (max 10 adaptive/assessments per month), cost alerts

### Risk 4: Cloudflare R2 latency for global users
**Mitigation**: Edge caching, content pre-warming, CDN distribution

### Risk 5: Database connection pool exhaustion (high concurrency)
**Mitigation**: Connection pooling (SQLAlchemy), horizontal scaling (Neon autoscaling)

---

## Next Steps

1. Create `data-model.md` (Phase 1) - detailed entity relationships and schemas
2. Create `contracts/` (Phase 1) - OpenAPI specs for all endpoints
3. Create `quickstart.md` (Phase 1) - local development setup guide
4. Update agent context with new technology decisions
5. Generate `tasks.md` (Phase 2) - 150+ implementation tasks
