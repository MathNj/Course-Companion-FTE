---
id: 002
title: Create Implementation Plan
stage: plan
date: 2026-01-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-course-companion-fte
branch: 001-course-companion-fte
user: Najma-LP
command: /sp.plan
labels: ["plan", "architecture", "sdd", "zero-backend-llm", "dual-frontend"]
links:
  spec: specs/001-course-companion-fte/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-course-companion-fte/plan.md
 - specs/001-course-companion-fte/research.md
 - specs/001-course-companion-fte/data-model.md
 - specs/001-course-companion-fte/contracts/README.md
 - specs/001-course-companion-fte/quickstart.md
tests:
 - Constitutional compliance check (10/10 gates passed)
 - Technical context validation
 - Research questions resolved (7/7)
---

## Prompt

/sp.plan

## Response snapshot

Created comprehensive Implementation Plan for Course Companion FTE with all Phase 0 (Research) and Phase 1 (Design) artifacts.

**Planning Artifacts Created:**

**1. plan.md** (463 lines)
- Technical Context: Python 3.11+, FastAPI, PostgreSQL, Redis, Cloudflare R2, Next.js 14, TypeScript
- Constitution Check: ✅ PASS (10/10 gates) - Zero-Backend-LLM, cost efficiency, SDD, hybrid isolation, educational excellence, security, testing, tech stack, workflow
- Project Structure: Dual-frontend (backend/ + chatgpt-app/ + web-app/) with detailed directory tree
- Complexity Tracking: No violations - all complexity justified by constitutional requirements

**2. research.md** (7 research questions resolved)
- Q1: Zero LLM enforcement → Automated testing with environment mocking
- Q2: ChatGPT prompts structure → Separate files per mode with shared context
- Q3: Content storage → JSON format in Cloudflare R2 with edge caching
- Q4: Database schema → Relational PostgreSQL with separate tables (users, progress, quizzes, streaks)
- Q5: Freemium access control → Middleware-based with subscription tier checks
- Q6: Adaptive learning (Phase 2) → Pattern analysis + Claude Sonnet prompting ($0.018/request)
- Q7: LLM assessments (Phase 2) → Rubric-based prompting with expert validation ($0.014/assessment)
- Technology stack validation: All choices confirmed (FastAPI, Next.js, PostgreSQL, Redis, R2)
- Cost analysis: Phase 1 = $16/month for 10K users ($0.0016/user), Phase 2 = $320/month for 1K premium users ($0.32/user)

**3. data-model.md** (comprehensive entity design)
- 8 entities: User, Subscription, ChapterProgress, Quiz (content), QuizAttempt, Session, Streak, Chapter (content)
- ER diagram with relationships and cardinality
- Full SQL schemas with constraints, indexes, validations
- Data flow diagrams: authentication, content delivery, quiz submission, adaptive learning
- State transition diagrams: subscription states, progress states, quiz attempt states
- Caching strategy: Redis cache keys with TTL (user: 1hr, content: 24hr, progress: 5min)
- Migration strategy: Alembic with rollback plan
- Performance optimization: Query estimates, connection pooling, index coverage

**4. contracts/README.md** (API documentation)
- 19 endpoints total: 15 v1 (deterministic) + 4 v2 (hybrid premium)
- Authentication flow: register → login → JWT token → authenticated requests
- Error responses: Consistent format with HTTP status codes (200, 201, 400, 401, 403, 404, 422, 429, 500, 503)
- Request/response examples: Get chapter, submit quiz, generate adaptive path
- Rate limiting headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- Pagination support for list endpoints
- OpenAPI auto-generation from FastAPI

**5. quickstart.md** (development setup guide)
- 8-section setup guide: clone, backend setup, database setup, frontend setup, ChatGPT app setup, run services, verify, troubleshooting
- Docker Compose for PostgreSQL + Redis
- Environment variables: .env (backend), .env.local (frontend)
- Alembic migrations: Initialize, run, seed data, create test user
- Verification steps: Health check, auth test, content API test, run tests (pytest + jest)
- Troubleshooting: 6 common errors with solutions
- Development workflow: Feature branches, code quality checks, migration creation, commit process
- Useful commands: Database management, Docker management, testing commands

**Constitutional Compliance:**

All 10 constitutional gates passed:

I. Zero-Backend-LLM First ✅
- Phase 1 APIs (/api/v1/*) are deterministic only
- Automated test to verify zero LLM calls
- All intelligence delegated to ChatGPT

II. Cost Efficiency & Scalability ✅
- Phase 1: $0.0016/user/month (below $0.004 target)
- Phase 2: $0.32/user/month (below $0.50 target)
- 99.4% margin at 10K users

III. Spec-Driven Development ✅
- spec.md → plan.md → tasks.md workflow followed
- Full traceability maintained

IV. Hybrid Intelligence Isolation ✅
- /api/v1/* vs /api/v2/* separation
- Only 2 hybrid features (Adaptive Path + LLM Assessments)
- Premium gating enforced

V. Educational Delivery Excellence ✅
- 6 chapters on Generative AI Fundamentals
- 4 Agent Skills documented
- 99%+ consistency target

VI. Agent Skills & MCP Integration ✅
- 4 SKILL.md files planned (concept-explainer, quiz-master, socratic-tutor, progress-motivator)
- 5-section structure defined

VII. Security & Secrets Management ✅
- .env for local, platform secrets for production
- No hardcoded secrets
- OAuth 2.0/JWT authentication

VIII. Testing & Quality Gates ✅
- pytest + Jest + Playwright
- >80% coverage target
- Zero-LLM verification test

IX. Technology Stack Constraints ✅
- All constitutional stack choices confirmed

X. Development Workflow ✅
- Feature branch created (001-course-companion-fte)
- SDD workflow followed

**Technology Decisions:**

**Backend Stack:**
- Python 3.11+ (async/await, type hints)
- FastAPI 0.104+ (auto OpenAPI docs, Pydantic validation)
- PostgreSQL 15+ via Neon (free tier, autoscaling)
- SQLAlchemy 2.0+ (async ORM)
- Redis 7+ via Upstash (serverless, pay-per-request)
- Cloudflare R2 (S3-compatible, zero egress fees)
- Alembic (database migrations)

**Frontend Stack:**
- Next.js 14+ (App Router, React Server Components)
- TypeScript 5.0+ (type safety)
- TailwindCSS 3.0+ + shadcn/ui (consistent UI)
- React Query (server state management)
- Playwright (E2E testing)

**ChatGPT Integration:**
- OpenAI Apps SDK (manifest.yaml + system prompts)
- 4 prompt modes: teach, quiz, socratic, motivation

**Infrastructure:**
- Fly.io or Railway (containerized deployment)
- GitHub Actions (CI/CD)
- Docker Compose (local development)

**Project Structure:**
- backend/ - FastAPI app with v1 (deterministic) and v2 (hybrid) API routes
- chatgpt-app/ - ChatGPT App manifest and prompts
- web-app/ - Next.js 14 application
- content/ - Course content JSON files (uploaded to R2 in production)

## Outcome

- ✅ Impact: Created complete, constitutionally-compliant implementation plan with all Phase 0 and Phase 1 artifacts. Plan enables immediate task generation via /sp.tasks and provides clear architectural direction for all 3 deployment phases.
- 🧪 Tests: Constitutional compliance check (10/10 gates passed). All technology decisions validated against requirements. Cost analysis confirms targets met.
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, contracts/README.md, quickstart.md) totaling 800+ lines of technical documentation
- 🔁 Next prompts: Execute /sp.tasks to generate 150+ implementation tasks, then /sp.implement to begin development
- 🧠 Reflection: Planning successfully balances constitutional requirements (Zero-Backend-LLM, cost efficiency, dual-frontend architecture) with technical pragmatism. All complexity justified by constitutional principles. Research questions resolved with concrete implementation strategies. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. All constitutional gates passed on first attempt. Research questions identified and resolved without clarification needs.
- Graders run and results (PASS/FAIL): Constitutional Check - PASS (10/10 gates). Technical Context Validation - PASS (all required fields filled). Research Completeness - PASS (7/7 questions answered with implementation approaches).
- Prompt variant (if applicable): N/A (initial plan creation)
- Next experiment (smallest change to try): Monitor plan usage during /sp.tasks execution to identify any missing technical details or ambiguous architectural decisions. May need minor updates based on task breakdown discoveries.
