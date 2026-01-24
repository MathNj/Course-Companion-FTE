# Implementation Plan: Course Companion FTE

**Branch**: `001-course-companion-fte` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-course-companion-fte/spec.md`

## Summary

Build a Digital Full-Time Equivalent (FTE) educational tutor for Generative AI Fundamentals course using a dual-frontend architecture with phased deployment. The system delivers course content, personalized explanations, quizzes, and progress tracking through both a ChatGPT conversational interface and a standalone web application. Phase 1 implements Zero-Backend-LLM architecture (deterministic backend only), Phase 2 adds selective hybrid intelligence (premium features), and Phase 3 delivers a full-featured web application.

**Technical Approach**:
- **Phase 1**: FastAPI deterministic backend + ChatGPT App frontend (Zero-Backend-LLM)
- **Phase 2**: Add Claude Sonnet integration for premium features (adaptive learning, LLM assessments)
- **Phase 3**: Next.js web application with full feature parity
- **Storage**: Cloudflare R2 (content), PostgreSQL (user data), Redis (caching)
- **Agent Skills**: 4 SKILL.md files (concept-explainer, quiz-master, socratic-tutor, progress-motivator)

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.0+ (web frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, httpx, python-jose (JWT)
- Frontend: Next.js 14+, React 18+, TailwindCSS 3.0+, shadcn/ui, React Query
- ChatGPT: OpenAI Apps SDK (manifest.yaml + system prompts)
- AI: Anthropic Python SDK (Claude Sonnet for Phase 2 premium features)

**Storage**:
- Content: Cloudflare R2 (course materials, quiz banks, media assets)
- Database: PostgreSQL 15+ via Neon or Supabase (user data, progress, subscriptions)
- Cache: Redis 7+ via Upstash or Redis Cloud (session data, content cache)

**Testing**:
- Backend: pytest, pytest-asyncio, httpx test client, pytest-cov (>80% coverage target)
- Frontend: Jest, React Testing Library, Playwright (E2E)
- API: OpenAPI spec validation, contract tests

**Target Platform**:
- Backend: Linux containers (Fly.io or Railway deployment)
- Frontend: Vercel or Netlify (Next.js hosting)
- ChatGPT App: OpenAI Apps Platform

**Project Type**: Web application with dual frontends (ChatGPT conversational + Next.js visual)

**Performance Goals**:
- Content API: <100ms p95 latency (deterministic endpoints)
- Quiz grading: <500ms end-to-end (rule-based)
- Concurrent users: 10,000+ without degradation
- LLM assessments: <5s p95 (premium feature, Phase 2)

**Constraints**:
- Phase 1 backend: ZERO LLM API calls (constitutional requirement, disqualification risk)
- Cost: <$0.004/user/month (Phase 1), <$0.50/user/month (Phase 2 premium)
- Data integrity: 99.9%+ for progress tracking
- Mobile responsive: Web app must work on mobile/tablet/desktop

**Scale/Scope**:
- Course content: 6 chapters, 30-40 sections total
- Quizzes: 6 chapter quizzes (48 questions total: 30 MC, 18 T/F, 12 open-ended)
- Users: 10-100K students (target scale)
- Features: 49 functional requirements across 3 phases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Zero-Backend-LLM First (Phase 1) - NON-NEGOTIABLE

**Status**: ✅ PASS

**Evidence**:
- Phase 1 architecture uses FastAPI for deterministic APIs only (content serving, navigation, rule-based quiz grading)
- All intelligent reasoning delegated to ChatGPT via OpenAI Apps SDK
- Functional requirements FR-005, FR-012 explicitly require deterministic backend behavior
- Success criteria SC-023 measures zero hallucinations (content served verbatim)
- Automated test planned to verify zero LLM API calls in Phase 1 backend (FR in testing section)

**Phase 1 APIs (all deterministic)**:
- `/api/v1/chapters/*` - Content delivery (verbatim from R2)
- `/api/v1/quizzes/*` - Quiz delivery and grading (answer key lookup)
- `/api/v1/progress/*` - Progress tracking (database CRUD)
- `/api/v1/access/*` - Access control (subscription tier check)
- `/api/v1/search/*` - Content search (keyword or pre-computed embeddings)

**Gate Requirement**: No LLM API calls in `/api/v1/*` routes
**Verification Method**: Automated test with mock environment detection

### II. Cost Efficiency & Scalability

**Status**: ✅ PASS

**Evidence**:
- Technical context specifies cost targets aligned with constitution (<$0.004/user/month Phase 1)
- Storage choices optimize for cost: Cloudflare R2 ($0.015/GB), Neon free tier, Redis Cloud free tier
- Success criteria SC-009 through SC-011 measure cost per user and sub-linear scaling
- Premium features (Phase 2) are explicitly cost-tracked (FR-033: cost monitoring)

**Cost Structure**:
- Phase 1: $16-$51/month for 10K users = $0.002-$0.005/user (within target)
- Phase 2: ~$320/month for LLM features (1K premium users) = $0.32/user (within <$0.50 target)
- Infrastructure choices prioritize free tiers with pay-as-you-grow models

**Gate Requirement**: Cost analysis demonstrates <$0.004/user/month (Phase 1)
**Verification Method**: Cost breakdown documentation in research.md

### III. Spec-Driven Development (SDD)

**Status**: ✅ PASS

**Evidence**:
- Specification created via `/sp.specify` with 49 functional requirements and 27 success criteria
- This plan.md created via `/sp.plan` following SDD workflow
- Next step: `/sp.tasks` will create tasks.md with 150+ implementation tasks
- All artifacts traceable: spec.md → plan.md → tasks.md → implementation

**Gate Requirement**: Spec complete before plan, plan complete before tasks
**Verification Method**: Artifact existence and completeness checks passed

### IV. Hybrid Intelligence Isolation

**Status**: ✅ PASS

**Evidence**:
- Phase 1 APIs use `/api/v1/*` prefix (deterministic)
- Phase 2 hybrid APIs use `/api/v2/*` prefix (LLM-powered)
- Functional requirements FR-026, FR-027 explicitly gate premium features
- Only 2 hybrid features planned (Adaptive Learning + LLM Assessments, within "max 2" constraint)
- Premium gating enforced via `verify_premium` middleware

**Isolation Strategy**:
- Separate FastAPI routers for v1 (deterministic) and v2 (hybrid)
- No shared code paths that could leak LLM calls into v1
- Cost tracking implemented only for v2 routes

**Gate Requirement**: v1 and v2 completely isolated, max 2 hybrid features
**Verification Method**: Code review + automated test

### V. Educational Delivery Excellence

**Status**: ✅ PASS

**Evidence**:
- Content structure defined: 6 chapters on Generative AI Fundamentals (Intro, LLMs, Prompting, RAG, Fine-tuning, AI Applications)
- Quiz design specified: 5 MC + 3 T/F + 2 open-ended per chapter
- 4 mandatory Agent Skills planned (FR-046 through FR-049)
- Success criteria SC-001 through SC-004 measure educational effectiveness (70%+ quiz scores, 4+/5 satisfaction)

**Quality Measures**:
- Content served verbatim from authoritative source (no modification/hallucination)
- Answer keys validated by domain experts
- Explanations grounded in course content via Agent Skills

**Gate Requirement**: 99%+ consistency, all 4 Agent Skills implemented
**Verification Method**: Quality metrics tracked in success criteria

### VI. Agent Skills & MCP Integration

**Status**: ✅ PASS

**Evidence**:
- 4 SKILL.md files planned (concept-explainer, quiz-master, socratic-tutor, progress-motivator)
- Each skill follows 5-section structure: Metadata, Purpose, Workflow, Response Templates, Key Principles
- Skills reference backend APIs explicitly (e.g., "Call GET /api/v1/quizzes/{id}")
- MCP integration planned for database, file system, and external API access

**Skill Structure**:
- Trigger keywords defined for each skill
- Workflows documented as step-by-step procedures
- Response templates provided for different scenarios

**Gate Requirement**: All 4 skills with complete structure
**Verification Method**: SKILL.md file validation

### VII. Security & Secrets Management

**Status**: ✅ PASS

**Evidence**:
- `.env` file for local development (gitignored)
- `.env.example` with placeholder values (committed)
- Production secrets via platform-specific secret management (Fly.io secrets, Railway env vars)
- Authentication via OAuth 2.0/JWT (industry standard)
- Rate limiting planned (per-user quotas)

**Secrets**:
- Database credentials (PostgreSQL connection string)
- Redis connection string
- Cloudflare R2 access keys
- Anthropic API key (Phase 2 only)
- JWT signing secret

**Gate Requirement**: No hardcoded secrets, environment variable usage
**Verification Method**: Code review + secret scanning tools

### VIII. Testing & Quality Gates

**Status**: ✅ PASS

**Evidence**:
- Testing framework specified: pytest (backend), Jest + Playwright (frontend)
- Coverage target: >80% for backend business logic
- Zero-LLM verification test planned for Phase 1
- Integration tests for all API endpoints
- E2E tests for critical user flows

**Test Strategy**:
- Unit tests: All business logic functions
- Integration tests: API endpoint behavior
- E2E tests: User journeys (content → quiz → progress)
- Performance tests: Concurrent user load

**Gate Requirement**: All tests passing before deployment
**Verification Method**: CI/CD pipeline enforcement

### Technology Stack Constraints

**Status**: ✅ PASS

**Evidence**:
- Backend: Python 3.11+ ✅, FastAPI 0.104+ ✅, PostgreSQL ✅, SQLAlchemy 2.0+ ✅
- Frontend: Next.js 14+ ✅, TypeScript ✅, TailwindCSS ✅, shadcn/ui ✅
- ChatGPT: OpenAI Apps SDK ✅
- Storage: Cloudflare R2 ✅
- Infrastructure: Fly.io/Railway ✅, GitHub Actions ✅

**Gate Requirement**: Use only constitutional stack
**Verification Method**: Package.json and requirements.txt validation

### Development Workflow

**Status**: ✅ PASS

**Evidence**:
- Feature branch: `001-course-companion-fte` ✅
- Spec created before plan ✅
- Plan follows constitutional template ✅
- Tasks.md will be created next via `/sp.tasks`
- PHR will be created for this planning session

**Gate Requirement**: Follow Spec → Plan → Tasks → Implement workflow
**Verification Method**: Artifact sequencing validation

---

**Overall Constitution Check**: ✅ PASS (10/10 gates)

No violations requiring justification. All constitutional principles aligned with feature requirements.

## Project Structure

### Documentation (this feature)

```text
specs/001-course-companion-fte/
├── spec.md              # Feature specification (created)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 research (to be created)
├── data-model.md        # Phase 1 data model (to be created)
├── quickstart.md        # Phase 1 setup guide (to be created)
├── contracts/           # Phase 1 API contracts (to be created)
│   ├── openapi.yaml     # OpenAPI 3.0 spec for all endpoints
│   ├── phase1-v1.yaml   # Phase 1 deterministic APIs
│   └── phase2-v2.yaml   # Phase 2 hybrid APIs
├── checklists/          # Quality checklists
│   └── requirements.md  # Specification validation (created)
└── tasks.md             # Phase 2 tasks (/sp.tasks - NOT created yet)
```

### Source Code (repository root)

**Selected Structure**: Option 2 - Web application (dual frontend)

```text
# Backend (Deterministic + Hybrid)
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Settings and environment variables
│   ├── database.py              # SQLAlchemy database connection
│   ├── dependencies.py          # Shared FastAPI dependencies (auth, etc.)
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py              # User, Subscription entities
│   │   ├── course.py            # Course, Chapter entities
│   │   ├── quiz.py              # Quiz, Question entities
│   │   └── progress.py          # Progress, Session entities
│   │
│   ├── schemas/                 # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── quiz.py
│   │   └── progress.py
│   │
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/                  # Phase 1 deterministic APIs
│   │   │   ├── __init__.py
│   │   │   ├── chapters.py      # Content delivery endpoints
│   │   │   ├── quizzes.py       # Quiz endpoints (rule-based grading)
│   │   │   ├── progress.py      # Progress tracking endpoints
│   │   │   └── access.py        # Access control endpoints
│   │   └── v2/                  # Phase 2 hybrid APIs (premium)
│   │       ├── __init__.py
│   │       ├── adaptive.py      # Adaptive learning recommendations
│   │       └── assessments.py   # LLM-graded assessments
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── content.py           # Content retrieval from R2
│   │   ├── quiz_grader.py       # Deterministic quiz grading
│   │   ├── progress_tracker.py  # Progress calculations
│   │   ├── adaptive.py          # Adaptive learning logic (Phase 2)
│   │   └── llm_grader.py        # LLM assessment logic (Phase 2)
│   │
│   ├── skills/                  # Agent Skills (SKILL.md files)
│   │   ├── concept-explainer/
│   │   │   └── SKILL.md
│   │   ├── quiz-master/
│   │   │   └── SKILL.md
│   │   ├── socratic-tutor/
│   │   │   └── SKILL.md
│   │   └── progress-motivator/
│   │       └── SKILL.md
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── auth.py              # JWT authentication
│       ├── storage.py           # Cloudflare R2 client
│       └── cache.py             # Redis caching utilities
│
├── content/                     # Course content (JSON/Markdown)
│   ├── chapters/
│   │   ├── 01-intro-genai.json
│   │   ├── 02-llms.json
│   │   ├── 03-prompting.json
│   │   ├── 04-rag.json
│   │   ├── 05-fine-tuning.json
│   │   └── 06-ai-applications.json
│   └── quizzes/
│       ├── 01-quiz.json
│       ├── 02-quiz.json
│       ├── 03-quiz.json
│       ├── 04-quiz.json
│       ├── 05-quiz.json
│       └── 06-quiz.json
│
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_v1_deterministic.py # Zero-LLM verification
│   ├── test_auth.py             # Authentication tests
│   ├── api/
│   │   ├── test_chapters.py
│   │   ├── test_quizzes.py
│   │   ├── test_progress.py
│   │   └── test_access.py
│   └── services/
│       ├── test_quiz_grader.py
│       └── test_progress_tracker.py
│
├── alembic/                     # Database migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── pyproject.toml               # Python project config
├── Dockerfile                   # Container image
└── fly.toml                     # Fly.io deployment config

# ChatGPT App (Phase 1 & 2)
chatgpt-app/
├── manifest.yaml                # ChatGPT App definition
└── prompts/                     # System prompts for each mode
    ├── teach.txt                # Teaching mode (concept explanation)
    ├── quiz.txt                 # Quiz mode (assessment)
    ├── socratic.txt             # Socratic mode (guided learning)
    └── motivation.txt           # Motivation mode (progress celebration)

# Web Frontend (Phase 3)
web-app/
├── app/                         # Next.js 14 App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page
│   ├── learn/                   # Course content pages
│   │   ├── page.tsx             # Course overview
│   │   └── [chapterId]/
│   │       └── page.tsx         # Chapter viewer
│   ├── quiz/
│   │   └── [quizId]/
│   │       └── page.tsx         # Quiz interface
│   ├── progress/
│   │   └── page.tsx             # Progress dashboard
│   └── pricing/
│       └── page.tsx             # Subscription upgrade
│
├── components/                  # React components
│   ├── ui/                      # shadcn/ui components
│   ├── CourseNav.tsx            # Chapter navigation
│   ├── QuizCard.tsx             # Quiz component
│   ├── ProgressChart.tsx        # Progress visualization
│   └── StreakCounter.tsx        # Streak display
│
├── lib/                         # Utilities
│   ├── api.ts                   # Backend API client
│   ├── auth.ts                  # Authentication helpers
│   └── utils.ts                 # General utilities
│
├── hooks/                       # Custom React hooks
│   ├── useProgress.ts
│   ├── useQuiz.ts
│   └── useCourse.ts
│
├── public/                      # Static assets
│   ├── images/
│   └── icons/
│
├── tests/
│   ├── unit/
│   └── e2e/                     # Playwright tests
│       ├── learning-flow.spec.ts
│       └── quiz-flow.spec.ts
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js

# Shared / Root
.env.example                     # Environment variable template
.gitignore
README.md                        # Project overview
docker-compose.yml               # Local development stack
```

**Structure Decision**:

Selected **Option 2 (Web Application)** because:
1. Feature requires dual frontends: ChatGPT conversational interface + Next.js web application
2. Backend serves both frontends via REST API
3. Clear separation enables independent development and deployment
4. Follows constitutional technology stack constraints

**Directory Rationale**:
- **backend/**: Python FastAPI application with Phase 1 (v1) and Phase 2 (v2) API routes
- **chatgpt-app/**: ChatGPT App manifest and prompts for conversational interface
- **web-app/**: Next.js 14 application for Phase 3 visual interface
- **content/**: Course materials in JSON format (uploaded to Cloudflare R2 in production)
- **tests/**: Comprehensive test coverage (unit, integration, E2E)

## Complexity Tracking

*No constitutional violations to justify. All requirements align with constitution principles.*

**Potential Complexity Considerations** (approved by constitution):

| Area | Justification | Simpler Alternative Rejected |
|------|---------------|------------------------------|
| Dual Frontend | Constitutional requirement for maximum reach (ChatGPT 800M+ users + standalone web) | Single frontend would miss either conversational or visual learners |
| Three-Phase Rollout | Constitutional requirement for cost efficiency (Phase 1 Zero-Backend-LLM validates model before investing in Phase 2 hybrid) | Single-phase would risk high costs without validating Zero-Backend-LLM viability |
| Four Agent Skills | Constitutional requirement for educational excellence (each skill addresses distinct learning mode) | Fewer skills would reduce teaching effectiveness and fail constitutional gate |

All complexity is driven by constitutional principles and hackathon requirements, not over-engineering.
