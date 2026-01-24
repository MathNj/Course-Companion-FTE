# Course Companion FTE Constitution

**Project**: Digital Full-Time Equivalent Educational Tutor for Generative AI Fundamentals Course

## Sync Impact Report

- **Version**: 1.0.0 (Initial Ratification)
- **Status**: Active
- **Scope**: All phases (Phase 1: Zero-Backend-LLM, Phase 2: Hybrid Intelligence, Phase 3: Web Application)
- **Rationale**: Establishes foundational principles for building a cost-efficient, educationally excellent AI tutor using Agent Factory Architecture with phased deployment strategy.

---

## Domain Scope & Mission

### Course Topic & Educational Mission

**Course Topic**: Generative AI Fundamentals

The Course Companion FTE delivers comprehensive education on Generative AI Fundamentals through an AI-powered tutoring system. The curriculum covers 6 chapters:

1. **Introduction to Generative AI** - Core concepts, history, current landscape
2. **Large Language Models (LLMs)** - Transformer architecture, training, tokenization
3. **Prompt Engineering** - Effective prompting patterns, advanced techniques, security
4. **Retrieval-Augmented Generation (RAG)** - Architecture, embeddings, vector databases
5. **Fine-Tuning LLMs** - When to fine-tune, methods (LoRA, QLoRA), evaluation
6. **Building AI Applications** - Agent architecture, production considerations

**Educational Level**: Beginner to intermediate practitioners seeking foundational knowledge in Generative AI.

**Delivery Method**: Dual-frontend architecture
- Primary: ChatGPT conversational interface (Phases 1-2)
- Secondary: Standalone web application (Phase 3)

**Implementation Approach**: Agent Factory Architecture with Zero-Backend-LLM principle (Phase 1), selective hybrid intelligence (Phase 2), and responsive web UI (Phase 3).

### Business Model

- **Free Tier**: Chapters 1-3, basic quizzes, progress tracking
- **Premium Tier** ($9.99/month): All 6 chapters, full progress tracking
- **Pro Tier** ($19.99/month): Premium + Adaptive Learning + LLM Assessments

---

## Core Principles (Constitutional Gates)

### I. Zero-Backend-LLM First (Phase 1) - NON-NEGOTIABLE

**Status**: MANDATORY | **Disqualification Risk**: Automatic project failure if violated

Phase 1 backend APIs MUST make ZERO calls to LLM services. All intelligent reasoning is delegated to the conversational frontend (ChatGPT App via OpenAI Apps SDK).

**Requirements**:
- Backend serves content verbatim from pre-authored materials (no generation)
- Quiz grading uses deterministic answer key lookup (no LLM evaluation)
- Navigation uses rule-based logic (no LLM recommendations)
- Search uses keyword matching or pre-computed embeddings (no LLM reasoning)

**Verification**:
- Automated test MUST verify zero LLM API calls in Phase 1 backend
- Test runs in CI/CD as blocking check
- Mock all LLM endpoints and assert none are called during Phase 1 API tests

**Rationale**: Ensures 99.9%+ consistency, eliminates hallucination risk, minimizes cost, and demonstrates deterministic architecture mastery before adding complexity.

**API Endpoints (All Deterministic)**:
- `/api/v1/chapters/*` - Content delivery
- `/api/v1/quizzes/*` - Quiz delivery and grading
- `/api/v1/progress/*` - Progress tracking
- `/api/v1/access/*` - Access control
- `/api/v1/search/*` - Content search

---

### II. Cost Efficiency & Scalability

**Status**: MANDATORY | **Target**: <$0.004/user/month (Phase 1), <$0.50/user/month (Phase 2 premium)

**Phase 1 Cost Structure** (Zero-Backend-LLM):
- Compute: $10-20/month (Fly.io or Railway)
- Database: $0-25/month (Neon or Supabase free → paid tier)
- Cache: $0-10/month (Upstash or Redis Cloud free → paid tier)
- Storage: $5/month (Cloudflare R2 for course content)
- **Total**: $15-60/month for 10K users = **$0.0015-0.006/user/month** ✅

**Phase 2 Cost Structure** (Hybrid Intelligence):
- LLM Calls: ~$320/month for 1K premium users (10 adaptive paths + 20 assessments/user/month)
- **Per-user**: $0.32/user/month (well under $0.50 target) ✅

**Phase 3 Cost Structure** (Web Application):
- Frontend Hosting: $0-20/month (Vercel free tier → Pro if needed)
- **Per-user**: $0-0.002/user/month ✅

**Requirements**:
- Prioritize free tiers (Neon, Upstash, Vercel) with pay-as-you-grow
- Implement caching aggressively (Redis for content, CDN for static assets)
- Track LLM costs per-request in Phase 2 (log tokens, cost, student_id)
- Alert when per-student costs exceed thresholds ($0.50/month for premium users)

**Verification**:
- Cost analysis documented in planning artifacts
- Production monitoring with cost dashboards
- Monthly cost reviews with per-user calculations

---

### III. Spec-Driven Development (SDD) Workflow

**Status**: MANDATORY | **Workflow**: Spec → Plan → Tasks → Implement

**Process**:
1. **Specification** (`/sp.specify`): User stories, functional requirements, success criteria
2. **Planning** (`/sp.plan`): Technical context, architecture decisions, constitutional compliance
3. **Task Breakdown** (`/sp.tasks`): Granular implementation tasks with acceptance criteria
4. **Implementation** (`/sp.implement`): Execute tasks, create tests, validate requirements
5. **Documentation** (`/sp.adr`): Architectural Decision Records for significant choices

**Traceability**:
- Every functional requirement maps to 1+ tasks
- Every task references user story (e.g., `[US1]`)
- Every acceptance scenario has automated test
- Every architectural decision documented as ADR

**Requirements**:
- No implementation before specification approval
- All changes must reference spec requirements
- Breaking changes require spec amendment
- Prompt History Records (PHRs) for all planning sessions

**Verification**:
- Artifact existence checks (spec.md, plan.md, tasks.md present)
- Traceability matrix (requirements → tasks → tests)
- PHR completeness (all user inputs recorded)

---

### IV. Hybrid Intelligence Isolation

**Status**: MANDATORY | **Constraint**: Phase 1 and Phase 2 must remain completely isolated

**Architecture**:
- **Phase 1**: `/api/v1/*` routes (deterministic only, ZERO LLM calls)
- **Phase 2**: `/api/v2/*` routes (LLM-powered, premium-gated)
- **Separation**: No cross-contamination (v1 routes MUST NOT call LLM services)

**Allowed Hybrid Features** (Max 2 in Phase 2):
1. **Adaptive Learning Path** - Personalized recommendations via Claude Sonnet
2. **LLM Assessments** - Open-ended question grading with detailed feedback

**Requirements**:
- Separate FastAPI routers (`app/api/v1/` vs `app/api/v2/`)
- Separate service modules (`app/services/content.py` vs `app/services/llm/`)
- Import restrictions: v1 MUST NOT import from v2 or `services/llm/`
- Premium gating: All `/api/v2/*` routes protected with `verify_premium` middleware
- Cost tracking: Every LLM call logged (tokens, cost, student_id, timestamp)

**CRITICAL Test** (Blocking in CI/CD):
```python
# backend/tests/test_phase_isolation.py
def test_v1_routes_make_zero_llm_calls():
    """Verify Phase 1 endpoints remain LLM-free"""
    # Mock Anthropic API to detect any calls
    # Exercise all /api/v1/* endpoints
    # Assert ZERO LLM API calls occurred
```

**Verification**:
- Automated isolation test passes
- Static analysis prevents v1/v2 cross-imports
- Code review confirms separation

---

### V. Educational Delivery Excellence

**Status**: MANDATORY | **Quality Target**: 99%+ consistency, 70%+ quiz pass rate, 4+/5 satisfaction

**Content Quality**:
- 6 chapters on Generative AI Fundamentals
- 30-40 sections total with learning objectives
- Pre-authored by domain experts (no LLM generation)
- Served verbatim (no modification, no hallucination)
- Estimated time per chapter: 45-90 minutes

**Quiz Design**:
- 8 questions per chapter (5 MC + 3 T/F in Phase 1)
- 2 open-ended questions per chapter (Phase 2, LLM-graded)
- Answer keys validated by experts
- Passing score: 70%+
- Immediate feedback with explanations

**Agent Skills** (4 mandatory):
1. **concept-explainer** - Multi-level explanations (beginner/intermediate/advanced)
2. **quiz-master** - Guided quiz experience with encouragement
3. **socratic-tutor** - Guide through questions, not answers
4. **progress-motivator** - Celebrate achievements, maintain engagement

**Success Metrics**:
- 99.9%+ uptime (<43 minutes downtime/month)
- 70%+ quiz pass rate across all students
- 4+/5 average satisfaction rating
- 50%+ course completion rate (free tier)

**Verification**:
- Content accuracy audits (expert review)
- Quiz calibration (human grading comparison)
- User surveys (satisfaction, perceived quality)
- Analytics (completion rates, time-on-task)

---

### VI. Agent Skills & MCP Integration

**Status**: MANDATORY | **Requirement**: All 4 Agent Skills with complete structure

**SKILL.md Structure** (5 sections):
1. **Metadata**: Name, trigger keywords, version
2. **Purpose**: Clear description of skill's educational role
3. **Workflow**: Step-by-step procedures (numbered list)
4. **Response Templates**: Example outputs for different scenarios
5. **Key Principles**: Design guidelines (e.g., "never give direct answer in socratic-tutor")

**Agent Skills**:

**concept-explainer** (Trigger: "explain", "what is", "how does")
- Identify learner level (beginner/intermediate/advanced)
- Select appropriate analogy from knowledge base
- Explain in 3 parts: analogy → definition → example
- Check understanding with follow-up question

**quiz-master** (Trigger: "quiz", "test me", "practice")
- Call GET `/api/v1/quizzes/{id}` to retrieve questions
- Present one question at a time
- After submission, show result + explanation
- Encourage on wrong answers, celebrate on correct
- Track streaks, celebrate milestones

**socratic-tutor** (Trigger: "help me think", "I'm stuck", "hint")
- Never give direct answer
- Ask guiding questions to surface misconceptions
- Wait for student response before continuing
- Build on what student knows
- Celebrate when student reaches insight

**progress-motivator** (Trigger: "my progress", "streak", "how am I doing")
- Call GET `/api/v1/progress` to fetch data
- Calculate milestones (chapters done, quizzes passed, streak)
- Celebrate with specific praise (not generic)
- Suggest next achievable goal
- Encourage return tomorrow for streak

**MCP Integration**:
- Database access (read/write progress, subscriptions)
- File system access (read course content, answer keys)
- External API access (backend APIs via HTTP)

**Verification**:
- All 4 SKILL.md files present in `backend/skills/`
- Each skill has complete 5-section structure
- No unresolved placeholders
- Skills reference backend APIs explicitly

---

### VII. Security & Secrets Management

**Status**: MANDATORY | **Requirement**: Zero hardcoded secrets, environment variables only

**Secrets** (Never Commit):
- Database credentials (PostgreSQL connection string)
- Redis connection string
- Cloudflare R2 access keys (S3-compatible)
- Anthropic API key (Phase 2 only)
- JWT signing secret (32+ character random string)
- OAuth client secrets (if using social login)

**Management**:
- **Local Development**: `.env` file (gitignored, never committed)
- **Repository**: `.env.example` with placeholder values (committed)
- **Production**: Platform-specific secret management
  - Fly.io: `fly secrets set KEY=value`
  - Railway: Environment variables UI
  - Vercel: Environment variables UI (frontend)

**Authentication**:
- OAuth 2.0 for social login (Google, GitHub optional)
- JWT tokens for API authentication (httpOnly cookies for web app)
- Password hashing: bcrypt or Argon2 (never plain text)

**Rate Limiting**:
- Per-user quotas (10 adaptive paths + 20 assessments/month for premium)
- API rate limits (100 requests/minute per user)
- Redis counters for quota tracking

**Security Audits**:
- Automated secret scanning (TruffleHog, GitGuardian)
- Dependency vulnerability scanning (Snyk, Dependabot)
- OWASP Top 10 checklist review

**Verification**:
- No secrets in git history (audit with `git log -p -S 'API_KEY'`)
- `.env.example` committed, `.env` gitignored
- Production secrets configured in platform

---

### VIII. Testing & Quality Gates

**Status**: MANDATORY | **Coverage Target**: >80% for business logic

**Backend Testing** (pytest):
- **Unit Tests**: Business logic, data models, utilities
- **Integration Tests**: API endpoints, database queries, Redis caching
- **Contract Tests**: OpenAPI spec validation (request/response schemas)
- **Critical Tests** (Blocking in CI/CD):
  - Zero-LLM verification (Phase 1)
  - Phase isolation test (Phase 2)
  - Authentication flow
  - Freemium access control

**Frontend Testing** (Jest + Playwright):
- **Unit Tests**: React components, utility functions, state management
- **Integration Tests**: Page flows, API integration, form validation
- **E2E Tests** (Playwright):
  - Complete learning flow (login → chapter → quiz → results)
  - Responsive design (mobile, tablet, desktop breakpoints)
  - Accessibility (WCAG 2.1 Level AA compliance)
- **Visual Regression**: Percy or Chromatic for UI changes

**ChatGPT App Testing**:
- Manual testing in ChatGPT interface (all Agent Skills)
- Backend API contract validation (actions call correct endpoints)
- Error handling (graceful degradation if API down)

**Quality Gates** (CI/CD):
- All tests pass (pytest, Jest, Playwright)
- Coverage >80% (measured by pytest-cov, Jest coverage)
- Zero-LLM verification passes (Phase 1 blocking check)
- Phase isolation test passes (Phase 2 blocking check)
- Linting passes (ruff for Python, ESLint for TypeScript)
- Type checking passes (mypy for Python, TypeScript strict mode)

**Verification**:
- CI/CD pipeline configured (GitHub Actions or GitLab CI)
- Coverage reports generated and tracked
- All critical tests marked as blocking

---

### IX. Technology Stack Constraints

**Status**: MANDATORY | **Stack**: Python + FastAPI (backend), Next.js + TypeScript (web frontend), OpenAI Apps SDK (ChatGPT frontend)

**Backend** (Python 3.11+):
- **Framework**: FastAPI 0.104+ (async, automatic OpenAPI docs)
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Validation**: Pydantic v2 (type safety)
- **Database**: PostgreSQL 15+ via Neon or Supabase
- **Cache**: Redis 7+ via Upstash or Redis Cloud
- **Storage**: Cloudflare R2 (S3-compatible)
- **Testing**: pytest, pytest-asyncio, httpx test client

**Web Frontend** (TypeScript 5.3+):
- **Framework**: Next.js 14+ (App Router, React Server Components)
- **UI Library**: React 18+
- **Styling**: TailwindCSS 3.4+, shadcn/ui (Radix UI primitives)
- **State Management**:
  - React Query 5.0+ (server state, caching, prefetching)
  - Zustand 4.4+ (UI state, sidebar, theme)
- **Testing**: Vitest (unit), Playwright 1.40+ (E2E), axe-core (accessibility)
- **Deployment**: Vercel (zero-config, edge CDN, automatic SSL)

**ChatGPT Frontend**:
- **Platform**: OpenAI Apps Platform
- **SDK**: OpenAI Apps SDK (manifest.yaml + system prompts)
- **Architecture**: Conversational interface with backend API actions

**Phase 2 LLM** (Hybrid Intelligence):
- **Model**: Anthropic Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **SDK**: anthropic 0.40+ (Python)
- **Token Counting**: tiktoken 0.5+ (cost tracking)

**Rationale**:
- Python + FastAPI: Proven async performance, excellent API tooling, large ecosystem
- Next.js 14: Latest App Router, React Server Components, optimal DX
- Claude Sonnet: Best price/performance for educational reasoning ($5/MTok input, $15/MTok output)
- PostgreSQL: ACID compliance for user data, JSON support for flexible schemas
- Redis: Sub-millisecond caching, session management, rate limiting counters

**Verification**:
- `requirements.txt` or `pyproject.toml` (backend dependencies)
- `package.json` (frontend dependencies)
- Version constraints enforced in dependency files

---

### X. Development Workflow

**Status**: MANDATORY | **Branching Strategy**: Feature branches + main

**Git Workflow**:
- **Main Branch**: Production-ready code, protected
- **Feature Branches**: Named `{number}-{feature-name}` (e.g., `002-phase-1-zero-backend-llm`)
- **Branch Per Phase**: Separate branches for Phase 1, 2, 3
- **Merge Strategy**: Squash merge to main after review

**SDD Workflow** (Per Feature):
1. **Specify**: Create `specs/{feature}/spec.md` via `/sp.specify`
2. **Plan**: Create `specs/{feature}/plan.md` via `/sp.plan`
3. **Tasks**: Create `specs/{feature}/tasks.md` via `/sp.tasks`
4. **Implement**: Execute tasks, write tests, validate requirements
5. **Document**: Create ADRs for architectural decisions (`/sp.adr`)
6. **Record**: Create Prompt History Records (PHRs) in `history/prompts/{feature}/`

**Commit Standards**:
- **Format**: `<type>(<scope>): <description>`
- **Types**: feat, fix, docs, test, refactor, chore
- **Examples**:
  - `feat(phase-1): Add deterministic quiz grading endpoint`
  - `test(phase-2): Add Phase 1/2 isolation verification test`
  - `docs(planning): Complete Phase 3 specification`
- **Footer**: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>` (AI-assisted work)

**Code Review**:
- All PRs require review before merge
- Constitutional compliance checklist (all 10 gates)
- Test coverage maintained or improved
- No new secrets or credentials committed

**Prompt History Records (PHRs)**:
- Created after every significant AI interaction
- Stored in `history/prompts/{feature}/`
- Naming: `{id}-{slug}.{stage}.prompt.md`
- Stages: `spec`, `plan`, `tasks`, `red`, `green`, `refactor`, `explainer`, `misc`, `general`, `constitution`

**Verification**:
- `.git/` directory configured
- Feature branches created per phase
- Commit messages follow convention
- PHRs present for all planning sessions

---

## Quality Standards

### Code Quality

**Backend (Python)**:
- Linting: ruff (replaces flake8, isort, black)
- Type checking: mypy with strict mode
- Formatting: ruff format (black-compatible)
- Docstrings: Google style for public functions
- Max complexity: 10 (measured by radon)

**Frontend (TypeScript)**:
- Linting: ESLint with `@typescript-eslint` plugin
- Type checking: TypeScript strict mode enabled
- Formatting: Prettier
- Component structure: Co-location (component + test + styles in same directory)
- Max props: 7 per component (use composition for complex components)

**Testing**:
- Test coverage: >80% for business logic
- Test naming: `test_<function_name>_<scenario>_<expected_result>`
- Fixtures: Shared fixtures in `conftest.py` (pytest) or setup files (Jest)
- Mocking: Use `unittest.mock` (Python) or `jest.mock` (TypeScript)

---

## Performance Standards

**API Latency** (p95):
- Content endpoints: <100ms (deterministic)
- Quiz grading: <500ms (rule-based)
- Progress tracking: <200ms (database writes)
- LLM assessments: <5s (Phase 2, network-bound)

**Web Application**:
- Initial page load: <2s (p95)
- Lighthouse scores: >90 performance (desktop), >80 (mobile)
- Bundle size: <200KB gzipped (enforced by CI)
- Accessibility: WCAG 2.1 Level AA (axe-core zero violations)

**Database**:
- Query timeout: 5s (fail fast)
- Connection pooling: 10-20 connections
- Index all foreign keys and frequently queried columns

**Caching**:
- Content: 1 hour TTL (R2 → Redis → Client)
- Progress: 5 minutes TTL (PostgreSQL → Redis)
- Adaptive paths: 24 hours TTL (reduce LLM costs)

---

## Governance

### Amendment Process

**Minor Changes** (version bump: x.y.0 → x.y.1):
- Clarifications, typo fixes, non-breaking updates
- Single approver required (tech lead)
- No downstream impact

**Major Changes** (version bump: x.0.0 → (x+1).0.0):
- New principles, breaking changes, scope modifications
- Team consensus required (all stakeholders)
- Migration plan documented
- ADR created explaining rationale

### Compliance Enforcement

- All PRs verify constitutional compliance (10 gates)
- CI/CD blocks merges that violate mandatory gates
- Code review checklist includes constitution items
- Quarterly constitution review (relevance check)

### Conflict Resolution

- Constitution supersedes all other practices
- In ambiguity, favor simplicity and cost efficiency
- When in doubt, ask clarifying questions (AskUserQuestion tool)
- Document decisions as ADRs

---

**Version**: 1.0.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-01-24

**Status**: Active - All 10 constitutional gates verified for Phases 1, 2, and 3 planning artifacts.

---

## See Also

- [Planning Summary](../../PLANNING-COMPLETE.md) - Complete overview of all 3 phases
- [Phase 1 Specification](../../specs/001-course-companion-fte/spec.md) - User requirements
- [Phase 1 Implementation Plan](../../specs/001-course-companion-fte/plan.md) - Technical design
- [Agent Factory Architecture](../../The Agent Factory Architecture_ Building Digital FTEs v1.md) - Architectural reference
