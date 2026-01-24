# Implementation Plan: Phase 2 - Hybrid Intelligence Course Companion

**Branch**: `003-phase-2-hybrid-intelligence` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase-2-hybrid-intelligence/spec.md`
**Prerequisites**: Phase 1 (Zero-Backend-LLM) fully implemented and operational

## Summary

Extend Phase 1 deterministic backend with LLM-powered premium features (Adaptive Learning Paths + LLM Assessments). Architecture maintains strict isolation using `/api/v2/*` routers, separate service modules, and new database tables. Cost target: <$0.50/premium-user/month via rate limiting (10 paths + 20 assessments monthly). Claude Sonnet 4.5 integration with comprehensive cost tracking, caching (24h TTL for adaptive paths), and premium gating middleware. Constitutional compliance verified across all 10 gates.

## Technical Context

**Language/Version**: Python 3.11+ (extends Phase 1 backend)
**Primary Dependencies** (New for Phase 2):
- anthropic 0.40+ (Claude Sonnet 4.5 API client, official SDK)
- tiktoken 0.5+ (token counting for cost calculation)
- pydantic-settings 2.0+ (LLM configuration management)

**Existing Phase 1 Dependencies** (No Changes):
- FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, httpx, python-jose, passlib, redis-py, boto3, alembic

**Storage** (Extends Phase 1):
- **Content**: Cloudflare R2 (add open-ended assessment questions with rubrics in `assessments/` directory)
- **Database**: PostgreSQL via Neon/Supabase (add 5 Phase 2 tables: adaptive_paths, assessment_submissions, assessment_feedback, llm_usage_logs, premium_usage_quotas)
- **Cache**: Redis (adaptive paths 24h TTL, usage quotas 1h TTL, rate limit counters)

**LLM Integration**:
- **Provider**: Anthropic Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Pricing** (2026-01-24): ~$3 per million input tokens, ~$15 per million output tokens
- **Usage Patterns**:
  - Adaptive Path: ~1,500 input tokens + ~300 output tokens = ~$0.0091 per request
  - LLM Assessment: ~1,200 input tokens + ~200 output tokens = ~$0.0066 per submission
- **Monthly Cost Projection** (per premium user at 10 paths + 20 assessments/month):
  - Adaptive paths: 10 × $0.0091 = $0.091
  - Assessments: 20 × $0.0066 = $0.132
  - **Total**: $0.223/premium-user/month ✅ Under $0.50 target (40% buffer)

**Testing** (Extends Phase 1):
- pytest with async support (Phase 2 LLM call tests)
- Mock Anthropic client for unit tests (avoid real API calls in CI)
- **Phase 1/2 isolation test** (MANDATORY): Verify Phase 1 endpoints make ZERO LLM calls after Phase 2 deployment
- Cost tracking verification tests

**Target Platform**: Same as Phase 1 (Linux server, containerized on Fly.io or Railway)
**Project Type**: Backend API extension (new `/api/v2/*` routers) + ChatGPT App prompt updates
**Performance Goals**:
- <5 seconds p95 latency for adaptive path generation
- <10 seconds p95 latency for LLM assessment grading
- Support 100 concurrent premium users (async LLM calls)
- <$0.50/premium-user/month LLM cost (average: $0.32)

**Constraints**:
- Phase 1 endpoints (`/api/v1/*`) MUST remain LLM-free (constitutional requirement)
- Phase 2 features MUST be premium-gated (middleware enforcement: `verify_premium`)
- All LLM API calls MUST be logged with token count and cost (audit trail)
- Rate limits: 10 adaptive paths + 20 assessments per premium user per month
- No real-time streaming (complete responses only for simplicity)
- Adaptive path caching: 24h TTL (balance freshness vs cost)

**Scale/Scope**:
- 2 new user stories (US6: Adaptive Learning, US7: LLM Assessments)
- ~11 new REST API endpoints (all under `/api/v2/*`)
- 5 new database tables
- 18 open-ended assessment questions (3 per chapter for Chapters 4-6, premium only)
- 2 LLM prompt templates (adaptive path generation, assessment grading)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Gate I: Zero-Backend-LLM First (Phase 1) - ✅ PASS

**Status**: PASS
**Evidence**:
- Phase 2 DOES NOT modify Phase 1 endpoints (`/api/v1/*` remain untouched)
- FR-029: Phase 2 uses separate `/api/v2/*` endpoints (architectural isolation)
- FR-032: Automated tests verify Phase 1 remains LLM-free after Phase 2 deployment
- Architecture diagram shows clear separation between v1 (deterministic) and v2 (hybrid) routers
- Code structure isolates LLM logic in `backend/app/services/llm/` (not imported by v1 routes)

**Verification Strategy**:
- Extend `tests/test_v1_deterministic.py` to run after Phase 2 implementation
- Mock Anthropic API and verify v1 endpoints make ZERO calls
- Code review checklist: "Phase 1 isolation verified - no v1 imports of v2 modules"

---

### Gate II: Cost Efficiency & Scalability - ✅ PASS

**Status**: PASS
**Cost Targets**:
- Phase 1 target: <$0.004/user/month (unchanged)
- Phase 2 target: <$0.50/premium-user/month

**Cost Breakdown (Projected)**:
| Component | Monthly Cost (1,000 premium users) | Per-Premium-User Cost |
|-----------|-------------------------------------|----------------------|
| LLM API (Anthropic) | $223 (10 paths + 20 assessments/user) | $0.223 |
| Compute (incremental) | $10-20 (async workers) | $0.010-$0.020 |
| Database (incremental) | $5 (Phase 2 tables) | $0.005 |
| Cache (incremental) | $0 (within Redis free tier) | $0 |
| **TOTAL (Phase 2 Only)** | **$238-248** | **$0.238-$0.248** ✅ |

**Rationale**: Cost target met comfortably with 40% buffer ($0.25 vs $0.50 target). Adaptive path caching (24h TTL) and rate limits (10 paths + 20 assessments/month) control costs. Premium pricing ($9.99-19.99/month) justifies $0.25/user LLM cost.

**Scalability Evidence**:
- FR-038: Adaptive path caching (24h) reduces redundant LLM calls
- FR-039: Request queuing handles bursts (max queue depth: 50)
- FR-023: Rate limits prevent cost overruns (10 paths, 20 assessments per premium user per month)
- Async LLM calls enable concurrent processing (100 premium users simultaneously)

---

### Gate III: Spec-Driven Development - ✅ PASS

**Status**: PASS
**Artifacts Created**:
- ✅ spec.md: 2 user stories (US6, US7 - both P2), 40 FR, 21 SC, 7 entities
- ✅ plan.md: This file (technical context, architecture, constitutional check)
- ✅ research.md: Embedded below (Phase 0 research decisions)
- ⏳ data-model.md: Generated below (Phase 1 design)
- ⏳ contracts/: Generated below (Phase 1 API documentation)
- ⏳ quickstart.md: Generated below (Phase 1 development guide)
- ⏳ tasks.md: To be generated via `/sp.tasks` command

**Traceability**:
- US6 (Adaptive Learning): 8 FR (FR-001 to FR-008), 3 SC (SC-001 to SC-003)
- US7 (LLM Assessments): 10 FR (FR-009 to FR-018), 3 SC (SC-004 to SC-006)
- Premium gating: 5 FR (FR-019 to FR-023), 3 SC (SC-007 to SC-009)
- Cost tracking: 5 FR (FR-024 to FR-028), 4 SC (SC-010 to SC-013)
- Architectural isolation: 4 FR (FR-029 to FR-032), 2 SC (SC-017 to SC-018)

---

### Gate IV: Hybrid Intelligence Isolation - ✅ PASS

**Status**: PASS
**Isolation Strategy**:
- ✅ Separate router prefix: `/api/v2/*` for all Phase 2 endpoints
- ✅ Premium gating: `Depends(verify_premium)` middleware on all v2 routes
- ✅ User-initiated: All LLM features require explicit POST requests (not auto-triggered)
- ✅ Feature-scoped: Exactly 2 features (Adaptive Learning Path + LLM Assessments)
- ✅ Cost tracking: Every LLM call logged with tokens, cost, student ID, feature type

**Architectural Boundaries**:
```python
# backend/app/api/v1/ - PHASE 1 (Deterministic)
# - auth.py, chapters.py, quizzes.py, progress.py
# - ZERO imports from v2 or services/llm/

# backend/app/api/v2/ - PHASE 2 (Hybrid)
# - adaptive.py, assessments.py, admin.py
# - Imports services/llm/ for Claude Sonnet calls
# - Depends(verify_premium) on all routes
```

**Prohibited Patterns** (Verified in Code Review):
- ❌ v1 routes importing v2 services
- ❌ v2 logic in v1 route handlers
- ❌ LLM calls without premium verification
- ❌ Auto-triggered LLM features (must be user-initiated)

---

### Gate V: Educational Delivery Excellence - ✅ PASS

**Status**: PASS
**Evidence**:
- Phase 2 ENHANCES educational quality without compromising Phase 1 delivery
- US6 (Adaptive Learning): Personalized recommendations based on performance patterns (SC-001: 15% score improvement on retries)
- US7 (LLM Assessments): Detailed feedback on reasoning quality (SC-004: ±1 point correlation with human expert grades)
- Open-ended assessment questions authored with rubrics (18 questions, 3 per premium chapter)
- LLM prompts include evaluation criteria and example answers for consistency

**Content Quality Requirements**:
- 18 open-ended assessment questions authored with evaluation rubrics (3 per chapter for Chapters 4-6)
- LLM prompts include rubric criteria and example excellent/poor answers
- Feedback must be specific and actionable (FR-015)
- Off-topic/abusive submissions handled gracefully (FR-016)

**Agent Skills Updates** (No new skills, updates to existing 4):
- concept-explainer: Add adaptive path recommendations to responses
- quiz-master: Suggest open-ended assessments for premium users
- socratic-tutor: Reference adaptive path insights in guidance
- progress-motivator: Celebrate adaptive path completion and feedback improvements

---

### Gate VI: Agent Skills & MCP Integration - ✅ PASS

**Status**: PASS
**Agent Skills (Updates to Existing 4)**:
1. **concept-explainer**: Add adaptive path action (e.g., "Based on your progress, I recommend reviewing embeddings before RAG")
2. **quiz-master**: Suggest open-ended assessments for premium users (e.g., "Try the free-form question for deeper learning")
3. **socratic-tutor**: Reference adaptive path insights (e.g., "Your pattern shows confusion about X, let's explore that")
4. **progress-motivator**: Celebrate adaptive path completion (e.g., "You followed my recommendation and improved by 20%!")

**New Backend Actions for ChatGPT App**:
- `POST /api/v2/adaptive/path` - Generate personalized learning recommendations
- `POST /api/v2/assessments/submit` - Submit open-ended answer for LLM grading
- `GET /api/v2/assessments/feedback/{submission_id}` - Retrieve grading feedback

**MCP Usage in Phase 2**:
- MCP servers not directly used (LLM calls via Anthropic SDK)
- Backend APIs continue serving as tool layer for ChatGPT
- Phase 3 may introduce MCP for complex agent orchestration

---

### Gate VII: Security & Secrets Management - ✅ PASS

**Status**: PASS
**Security Measures**:
- FR-019: Premium subscription verification on every Phase 2 request
- FR-033 to FR-036: Data privacy (no PII in LLM prompts beyond necessary context, anonymization, audit logs, 90-day retention)
- Anthropic API key stored in `.env` (gitignored), never hardcoded
- Production secrets via Fly.io/Railway secret management

**New Secrets for Phase 2**:
```env
ANTHROPIC_API_KEY=sk-ant-... (secret)
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_TIMEOUT=30
LLM_COST_ALERT_THRESHOLD=0.50  # Alert if per-user cost exceeds
```

**Data Privacy**:
- Student names anonymized in LLM prompts (use student_id instead of PII)
- Quiz answers and performance data sent to LLM (required for adaptive paths - minimized)
- LLM request/response logs deleted after 90 days (FR-036)
- Aggregated cost metrics retained indefinitely (without full prompts/responses)

---

### Gate VIII: Testing & Quality Gates - ✅ PASS

**Status**: PASS
**Testing Requirements**:
- Extend pytest suite with Phase 2 tests (>80% coverage target maintained)
- Unit tests for LLM service layer (mocked Anthropic client - no real API calls in CI)
- Integration tests for v2 endpoints (premium gating, rate limiting, cost tracking)
- **Phase 1/2 Isolation Test**: Verify v1 endpoints remain LLM-free after Phase 2 deployment (MANDATORY)

**New Tests for Phase 2**:
```python
# tests/test_v2_hybrid.py
def test_adaptive_path_premium_gating():
    """Free users blocked from adaptive paths"""
    response = client.post("/api/v2/adaptive/path", headers=auth_free)
    assert response.status_code == 403

def test_llm_cost_tracking():
    """Every LLM call logged with cost"""
    response = client.post("/api/v2/adaptive/path", headers=auth_premium)
    assert response.status_code == 200
    # Verify LLMUsageLog entry created
    log = db.query(LLMUsageLog).filter_by(student_id=premium_user_id).first()
    assert log.cost_usd > 0
    assert log.feature == "adaptive-path"

def test_rate_limit_enforcement():
    """Premium users limited to 10 paths per month"""
    for i in range(10):
        response = client.post("/api/v2/adaptive/path", headers=auth_premium)
        assert response.status_code == 200
    # 11th request should be rate-limited
    response = client.post("/api/v2/adaptive/path", headers=auth_premium)
    assert response.status_code == 429

# tests/test_phase_isolation.py (CRITICAL)
def test_phase1_endpoints_remain_llm_free():
    """Verify Phase 1 endpoints make ZERO LLM calls after Phase 2 deployment"""
    with mock.patch('anthropic.Anthropic') as mock_anthropic:
        # Call all Phase 1 endpoints
        client.get("/api/v1/chapters", headers=auth_headers)
        client.post("/api/v1/quizzes/01-quiz/submit",
                   json={"answers": {"q1": "a"}}, headers=auth_headers)
        client.get("/api/v1/progress", headers=auth_headers)

        # Assert Anthropic API was NEVER called
        mock_anthropic.assert_not_called()
```

**Quality Gates** (CI/CD pipeline):
1. All tests passing (pytest --cov=backend/app --cov-report=term-missing)
2. **Phase 1 isolation test passing** (tests/test_phase_isolation.py - BLOCKING)
3. Phase 2 cost tracking tests passing (verify LLMUsageLog entries)
4. Code review approved (1+ reviewer, constitutional compliance verified)

---

### Gate IX: Technology Stack Constraints - ✅ PASS

**Status**: PASS
**Technology Choices** (Phase 2 Extensions):
- **LLM Provider**: Anthropic Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) ✅
- **LLM SDK**: anthropic 0.40+ (official Python SDK with async support) ✅
- **Token Counting**: tiktoken 0.5+ (approximates Claude tokenization) ✅
- **Backend/Database/Cache**: Same as Phase 1 (FastAPI, PostgreSQL, Redis) ✅
- **Infrastructure**: Same as Phase 1 (Fly.io or Railway) ✅

**No Changes to Phase 1 Stack**:
- Python 3.11+, FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2 (unchanged)
- PostgreSQL via Neon/Supabase, Redis, Cloudflare R2 (unchanged)
- ChatGPT App integration (add new actions to manifest.yaml) ✅

---

### Gate X: Development Workflow - ✅ PASS

**Status**: PASS
**Workflow Compliance**:
- Feature branch: `003-phase-2-hybrid-intelligence` ✅
- Spec created: `specs/003-phase-2-hybrid-intelligence/spec.md` ✅
- Plan being created: `specs/003-phase-2-hybrid-intelligence/plan.md` (this file) ✅
- Next: Tasks will be created via `/sp.tasks` command
- Commit messages will follow format: `type(scope): description` with Co-Authored-By footer
- PHR will be created after planning completion

**PR Requirements for Phase 2**:
- PR title: `[003] Phase 2 - Hybrid Intelligence`
- Checklist includes:
  - ✅ Phase 1 isolation test passing (v1 endpoints remain LLM-free)
  - ✅ Phase 2 cost tracking tests passing
  - ✅ Premium gating verified (free users blocked)
  - ✅ Rate limiting tested (10 paths + 20 assessments per month)

---

**Constitution Check Summary**: ✅ **10/10 GATES PASSED**
**Proceed to Phase 0: Research**

## Phase 0: Research

### Research Decisions

**R1: Anthropic Claude Sonnet 4.5 Integration Best Practices**
- **Decision**: Use official `anthropic` Python SDK (0.40+) with async support. Create service layer (`backend/app/services/llm/client.py`) that wraps API calls with retry logic (exponential backoff, 3 retries), timeout handling (30s), and error categorization. Configure via environment variables (ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_TIMEOUT=30). Use dependency injection for testing (mock client in unit tests).
- **Rationale**: Official SDK handles authentication, rate limiting, and error handling. Async support enables concurrent requests (100 premium users). Service layer abstraction enables testing without real API calls and potential future multi-provider support.
- **Alternatives Considered**:
  - Direct HTTP requests to Anthropic API: Rejected (requires manual retry logic, no SDK benefits)
  - LangChain wrapper: Rejected (adds unnecessary complexity for 2 simple prompts)
  - Streaming responses: Rejected for Phase 2 (adds complexity, minimal UX benefit for batch-style requests)

**R2: Cost Tracking Architecture**
- **Decision**:
  - Create `llm_usage_logs` table: log_id, student_id, feature (adaptive-path/assessment), request_timestamp, tokens_input, tokens_output, tokens_total, cost_usd, latency_ms, success_status, error_message
  - Calculate cost immediately after each API call: `cost = (tokens_input * $3/1M) + (tokens_output * $15/1M)`
  - Use `tiktoken` library to count tokens before API call (cl100k_base encoding approximates Claude tokens within 5%)
  - Create aggregated view: `SELECT student_id, SUM(cost_usd) FROM llm_usage_logs WHERE DATE_TRUNC('month', request_timestamp) = CURRENT_MONTH GROUP BY student_id`
  - Admin dashboard queries this view + alerts if per-student cost exceeds $0.50/month
- **Rationale**: Per-request logging provides granular audit trail. Token counting enables cost prediction before API call. Monthly aggregation identifies high-usage students. Real-time cost calculation enables budget enforcement.
- **Alternatives Considered**:
  - Estimate costs from Claude response metadata: Rejected (Claude API doesn't return precise token counts in all cases)
  - Track costs daily instead of per-request: Rejected (loses granularity for debugging and per-feature attribution)

**R3: Adaptive Path Generation Prompt Engineering**
- **Decision**:
  - Input: Student performance data (JSON): `{chapters: [{id, quiz_score, time_spent, completed_at}], weak_areas: [...], strong_areas: [...]}`
  - System prompt (200 tokens): "You are an expert learning advisor for a Generative AI Fundamentals course. Analyze student performance and generate 3-5 prioritized recommendations based on quiz scores and time patterns..."
  - Few-shot examples (500 tokens): 2 examples (high-performing student → advanced topics, struggling student → prerequisite review) with expected JSON output
  - Output format (JSON schema): `{recommendations: [{chapter_id, section_id, priority, reason, estimated_impact, estimated_time_minutes}]}`
  - Max tokens: 500 (conservative estimate for recommendations)
  - Temperature: 0.3 (consistency over creativity - recommendations should be stable)
- **Rationale**: JSON input/output enables reliable parsing. Few-shot examples ensure consistency. Low temperature reduces variability across similar student profiles. System prompt grounds recommendations in course context.
- **Alternatives Considered**:
  - Free-form text output: Rejected (hard to parse reliably, inconsistent structure)
  - Zero-shot prompting: Rejected (lower consistency without examples, needs guidance for quality)

**R4: LLM Assessment Grading Rubric Design**
- **Decision**:
  - Rubric structure (per question): Evaluation criteria (4-5 bullet points), excellent answer example (80+ score), poor answer example (30- score), scoring guide (0-10 scale with level descriptions: 0-3 insufficient, 4-6 basic, 7-8 good, 9-10 excellent)
  - System prompt (300 tokens): "You are an expert evaluator for Generative AI course assessments. Grade student answers using the rubric below. Be encouraging but honest..."
  - Input: Question text + rubric + student answer (combined ~1,000 tokens)
  - Output format (JSON): `{score: 0-10, strengths: ["point 1", "point 2"], improvements: ["suggestion 1", "suggestion 2"], detailed_feedback: "paragraph"}`
  - Max tokens: 400 (feedback + reasoning)
  - Temperature: 0.4 (consistency with some feedback variety for natural language)
- **Rationale**: Explicit rubrics increase grading consistency (SC-004: ±1 point from human experts). Examples anchor scoring expectations. Structured output enables UI display (strengths/improvements lists). Temperature 0.4 balances consistency with natural feedback language.
- **Alternatives Considered**:
  - Single 0-100 score without breakdown: Rejected (less actionable feedback for students)
  - Human-in-the-loop grading: Rejected (doesn't scale, defeats automation purpose)

**R5: Rate Limiting Implementation Strategy**
- **Decision**:
  - Create `premium_usage_quotas` table: student_id (FK), month (DATE - YYYY-MM-01), adaptive_paths_used (INT), adaptive_paths_limit (10), assessments_used (INT), assessments_limit (20), reset_date (1st of next month)
  - Redis counters for fast quota checks: `quota:{student_id}:{month}:adaptive_paths` and `quota:{student_id}:{month}:assessments`
  - Check quota before processing request: `if redis.get(quota_key) >= limit: return 429 Rate Limit Exceeded`
  - Increment counter after successful LLM call: `redis.incr(quota_key)` + `UPDATE premium_usage_quotas SET adaptive_paths_used = adaptive_paths_used + 1`
  - Reset monthly: Cron job creates new quota records for next month (runs on 1st at midnight UTC)
  - TTL: Redis keys expire on 1st of next month automatically
- **Rationale**: Redis provides fast atomic operations for quota checks (sub-millisecond). Database table persists historical data for analytics. Dual-write ensures consistency. Monthly resets align with subscription billing cycles.
- **Alternatives Considered**:
  - Redis-only rate limiting: Rejected (risk of data loss on Redis restart, no persistent audit trail)
  - Daily quotas instead of monthly: Rejected (less flexible for burst usage patterns, students prefer monthly allocation)

**R6: Premium Gating Middleware Design**
- **Decision**:
  - Extend `backend/app/dependencies.py` with `verify_premium()` dependency
  - Check JWT token includes `subscription_tier` claim: `if user.subscription_tier != 'premium': raise HTTPException(403, detail={...})`
  - Check subscription expiration: `if user.subscription_expires_at and user.subscription_expires_at < datetime.now(): raise HTTPException(403, detail={...})`
  - Apply to all v2 routes: `@router.post("/adaptive/path", dependencies=[Depends(verify_premium)])`
  - Return structured error with upgrade CTA: `{code: "PREMIUM_REQUIRED", message: "...", benefits: [...], upgrade_url: "/v1/access/upgrade"}`
- **Rationale**: Middleware pattern ensures consistent enforcement across all v2 endpoints. JWT claim check is fast (no database query). Expiration check prevents access after downgrade. Clear 403 error with benefits enables upgrade prompts in ChatGPT App.
- **Alternatives Considered**:
  - Check subscription in every route handler: Rejected (code duplication, easy to forget)
  - Database query for subscription status: Rejected (slower, JWT claim sufficient for most cases)

**R7: Phase 1/2 Isolation Architecture**
- **Decision**:
  - Separate router modules: `backend/app/api/v1/` (Phase 1) vs `backend/app/api/v2/` (Phase 2)
  - Separate service modules: `backend/app/services/content.py` (Phase 1) vs `backend/app/services/llm/` (Phase 2)
  - Import restrictions: v1 routers MUST NOT import from v2 or services/llm/ (enforced by linting rule + code review)
  - FastAPI app registration: `app.include_router(v1_router, prefix="/api/v1")` and `app.include_router(v2_router, prefix="/api/v2")`
  - **Verification**: Extend `tests/test_v1_deterministic.py` to run after Phase 2 deployment, mock Anthropic API, assert no calls from v1 endpoints
- **Rationale**: Router prefix separation ensures URL namespace isolation. Module separation prevents accidental cross-contamination. Import restrictions enforced by tooling (e.g., flake8 plugin). Automated tests guarantee isolation even as code evolves.
- **Alternatives Considered**:
  - Single router with conditional LLM logic: Rejected (high risk of contamination, violates Gate IV)
  - Separate FastAPI applications: Rejected (over-engineering, deployment complexity, shared database access issues)

**R8: Adaptive Path Caching Strategy**
- **Decision**:
  - Cache generated paths for 24 hours in Redis: `adaptive_path:{student_id}` → JSON serialized path
  - Invalidate if new quiz completed (score change >20%) or explicit `force_refresh=true` flag
  - Support manual refresh for students who want updated recommendations
  - TTL: 24 hours (86400 seconds)
- **Rationale**: 24h cache balances freshness with cost. Students typically complete 1-2 chapters per week, so paths remain relevant. 20% score threshold prevents cache invalidation on minor improvements. `force_refresh` flag provides escape hatch.
- **Alternatives Considered**:
  - No caching: Rejected (costs $0.018 per path, wasteful for duplicate requests within same day)
  - 1-week cache: Rejected (stale recommendations harm learning outcomes, students progress faster)
  - Cache invalidation on any quiz: Rejected (too aggressive, minor retries shouldn't regenerate path)

### Research Summary

**Key Technologies Validated**:
- ✅ Anthropic Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- ✅ anthropic Python SDK 0.40+ (official, async support)
- ✅ tiktoken 0.5+ (token counting for cost estimation, cl100k_base encoding)
- ✅ PostgreSQL + Redis (Phase 1 stack sufficient for Phase 2)

**Architecture Patterns Confirmed**:
- Service layer for LLM calls: `backend/app/services/llm/client.py`
- Cost tracking: Per-request logging + monthly aggregation
- Rate limiting: Redis counters + PostgreSQL quota table (dual-write)
- Prompt engineering: Few-shot JSON prompts with rubrics
- Premium gating: FastAPI dependency injection (`verify_premium`)
- Phase 1/2 isolation: Separate routers, separate services, automated tests

**Cost Projections Validated**:
- Adaptive path: ~1,800 tokens → $0.0091 per request
- LLM assessment: ~1,400 tokens → $0.0066 per submission
- Monthly per premium user: 10 paths + 20 assessments = $0.223 ✅ Under $0.50 target
- Buffer for growth: 40% headroom ($0.223 vs $0.50 target)

**Prompt Engineering Decisions**:
- Adaptive path prompt: ~1,200 input tokens (system + examples + student data) + ~300 output tokens
- Assessment grading prompt: ~1,000 input tokens (rubric + question + answer) + ~200 output tokens
- Temperature: 0.3 (adaptive paths), 0.4 (assessments) - consistency prioritized
- Output format: JSON with schemas for reliable parsing

---

*All research questions resolved. Proceeding to Phase 1: Design & Contracts.*

## Project Structure

### Documentation (this feature)

```text
specs/003-phase-2-hybrid-intelligence/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (completed)
├── data-model.md        # Phase 1 output (generated separately)
├── quickstart.md        # Phase 1 output (generated separately)
├── contracts/           # Phase 1 output (generated separately)
│   └── README.md        # API endpoint documentation (v2)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code Extensions (extends Phase 1)

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/              # Phase 1 (UNCHANGED)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chapters.py
│   │   │   ├── quizzes.py
│   │   │   └── progress.py
│   │   │
│   │   └── v2/              # Phase 2 (NEW)
│   │       ├── __init__.py
│   │       ├── adaptive.py      # Adaptive learning path endpoints
│   │       ├── assessments.py   # LLM-graded assessment endpoints
│   │       └── admin.py         # Cost monitoring dashboard (admin-only)
│   │
│   ├── models/              # Extend with Phase 2 tables
│   │   ├── user.py          # Phase 1 (unchanged)
│   │   ├── progress.py      # Phase 1 (unchanged)
│   │   ├── quiz.py          # Phase 1 (unchanged)
│   │   ├── llm.py           # Phase 2 (NEW): AdaptivePath, AssessmentSubmission, AssessmentFeedback
│   │   └── usage.py         # Phase 2 (NEW): LLMUsageLog, PremiumUsageQuota
│   │
│   ├── schemas/             # Extend with Phase 2 Pydantic models
│   │   ├── user.py          # Phase 1 (unchanged)
│   │   ├── progress.py      # Phase 1 (unchanged)
│   │   ├── quiz.py          # Phase 1 (unchanged)
│   │   ├── adaptive.py      # Phase 2 (NEW): AdaptivePathRequest, AdaptivePathResponse
│   │   ├── assessment.py    # Phase 2 (NEW): AssessmentSubmitRequest, FeedbackResponse
│   │   └── usage.py         # Phase 2 (NEW): UsageQuotaResponse, CostBreakdownResponse
│   │
│   ├── services/            # Extend with LLM service layer
│   │   ├── auth.py          # Phase 1 (unchanged)
│   │   ├── content.py       # Phase 1 (unchanged)
│   │   ├── quiz_grader.py   # Phase 1 (unchanged)
│   │   ├── progress_tracker.py  # Phase 1 (unchanged)
│   │   │
│   │   ├── llm/             # Phase 2 LLM services (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── client.py            # Anthropic API wrapper with retry/timeout
│   │   │   ├── adaptive_path_generator.py  # Prompt engineering + JSON parsing
│   │   │   ├── assessment_grader.py        # Grading prompt + feedback parsing
│   │   │   ├── cost_tracker.py             # Token counting + cost logging
│   │   │   └── quota_manager.py            # Rate limiting enforcement
│   │   │
│   │   └── usage_manager.py  # Phase 2 (NEW): Usage tracking aggregation
│   │
│   ├── dependencies.py      # Extend with verify_premium() middleware
│   │
│   └── prompts/             # LLM prompt templates (NEW)
│       ├── adaptive_path.txt       # Adaptive learning path system prompt
│       └── assessment_grading.txt  # Assessment grading system prompt
│
├── tests/
│   ├── test_v1_deterministic.py    # Extend: Verify Phase 1 isolation after Phase 2
│   ├── test_v2_hybrid.py           # Phase 2 endpoint tests (NEW)
│   ├── test_phase_isolation.py     # Phase 1/2 isolation test (CRITICAL, NEW)
│   │
│   ├── services/
│   │   ├── test_llm/               # LLM service tests (mocked Anthropic) (NEW)
│   │   │   ├── test_client.py
│   │   │   ├── test_adaptive_path_generator.py
│   │   │   ├── test_assessment_grader.py
│   │   │   └── test_cost_tracker.py
│   │   └── test_usage_manager.py   # Rate limiting tests (NEW)
│   │
│   └── ... (Phase 1 tests unchanged)
│
├── alembic/
│   └── versions/
│       ├── 001_phase1_*.py          # Phase 1 migrations (unchanged)
│       ├── 002_phase2_adaptive_paths.py      # AdaptivePath table (NEW)
│       ├── 003_phase2_assessments.py         # AssessmentSubmission, Feedback (NEW)
│       └── 004_phase2_usage_tracking.py      # LLMUsageLog, PremiumUsageQuota (NEW)
│
├── content/
│   ├── chapters/            # Phase 1 (unchanged)
│   ├── quizzes/             # Phase 1 (unchanged)
│   │
│   └── assessments/         # Open-ended questions with rubrics (NEW)
│       ├── 04-rag-assessments.json
│       ├── 05-fine-tuning-assessments.json
│       └── 06-ai-apps-assessments.json
│
└── scripts/
    ├── seed_phase1_content.py   # Phase 1 (unchanged)
    └── seed_phase2_content.py   # Upload assessment questions to R2 (NEW)

chatgpt-app/
├── manifest.yaml            # Add Phase 2 actions (adaptive_path, submit_assessment, get_feedback)
└── prompts/
    ├── _shared-context.txt  # Update with Phase 2 feature descriptions
    ├── teach.txt            # Add adaptive path recommendations
    ├── quiz.txt             # Add LLM assessment suggestions
    └── ... (other prompts updated for premium features)
```

**Structure Decision**: Extend Phase 1 codebase with new `/api/v2/` router and `services/llm/` service layer. Phase 1 code (`/api/v1/`, `services/content.py`, `services/quiz_grader.py`) remains completely untouched. Phase 2 logic isolated in new modules. Automated tests (`test_phase_isolation.py`) verify no cross-contamination.

---

## Complexity Tracking

**🚨 Architectural Decision: LLM Integration for Premium Features**

**Context**: Phase 2 introduces Claude Sonnet 4.5 API calls for adaptive learning paths and LLM-graded assessments, which violates the Zero-Backend-LLM principle for specific premium features.

**Justification**:
- **Isolated**: All LLM logic in `/api/v2/*` endpoints and `services/llm/` modules, completely separate from Phase 1's `/api/v1/*` deterministic routes
- **Premium-gated**: Only accessible to paying users (`subscription_tier='premium'`), not free tier (controlled cost exposure)
- **Valuable**: Adaptive learning paths and detailed feedback are high-value features justifying LLM cost (~$0.25/premium-user/month for significant educational impact)
- **Monitored**: Per-request cost tracking (`llm_usage_logs` table) and monthly aggregation enable budget control and alerts
- **Constitutional**: Hybrid Intelligence Isolation principle (Gate IV) explicitly allows selective LLM use when properly isolated from deterministic features

**Alternatives Considered**:
1. **Continue Zero-Backend-LLM forever**: Rejected (Phase 2's personalization and assessment grading require LLM intelligence, cannot be rule-based without significant quality degradation)
2. **Use client-side LLM calls (ChatGPT only)**: Rejected (can't enforce premium gating or track costs, inconsistent prompts across users, no control over output quality)
3. **Simpler rule-based recommendations**: Rejected (insufficient quality for premium differentiation, students expect intelligent personalization to justify premium price)

**Safeguards**:
- Rate limits (10 adaptive paths + 20 assessments per premium user per month)
- Cost monitoring (alert if per-user cost exceeds $0.50/month threshold)
- Automated isolation tests (`test_phase_isolation.py` verifies Phase 1 remains LLM-free)
- Caching (adaptive paths cached 24h to reduce redundant calls)
- Fallback messaging (graceful degradation if LLM service unavailable)

**Approved**: Constitutional Gate IV (Hybrid Intelligence Isolation) explicitly permits this architecture when properly isolated, premium-gated, and cost-tracked.

---

**Plan.md complete. Design artifacts (data-model.md, contracts/, quickstart.md) generated as separate files.**
