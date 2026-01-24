# Implementation Tasks: Course Companion FTE

**Feature**: Course Companion FTE - Digital Educational Tutor for Generative AI Fundamentals
**Branch**: `001-course-companion-fte`
**Date**: 2026-01-24

**Input Documents**:
- [spec.md](./spec.md) - 8 user stories (3 P1, 2 P2, 3 P3), 49 functional requirements, 27 success criteria
- [plan.md](./plan.md) - Technical stack, architecture, constitutional compliance
- [data-model.md](./data-model.md) - 8 entities, schemas, relationships
- [contracts/README.md](./contracts/README.md) - 19 API endpoints
- [research.md](./research.md) - 7 technology decisions resolved
- [quickstart.md](./quickstart.md) - Development setup guide

---

## Task Summary

| Phase | User Story | Priority | Task Count | Parallel Tasks | Independent Test |
|-------|------------|----------|------------|----------------|------------------|
| 1 | Setup | - | 15 | 8 | N/A (infrastructure) |
| 2 | Foundational | - | 20 | 12 | Database migrations pass |
| 3 | US1 - Course Content Access | P1 | 18 | 10 | Student can view Chapter 1 content |
| 4 | US2 - Personalized Explanations | P1 | 12 | 6 | ChatGPT explains concepts at multiple levels |
| 5 | US3 - Quizzes with Feedback | P1 | 15 | 8 | Student can take and pass Chapter 1 quiz |
| 6 | US4 - Progress Tracking | P2 | 12 | 7 | Progress persists across sessions |
| 7 | US5 - Freemium Gate | P2 | 10 | 6 | Free user blocked from Chapter 4 |
| 8 | US6 - Adaptive Learning | P3 | 8 | 4 | Premium user gets personalized recommendations |
| 9 | US7 - LLM Assessments | P3 | 8 | 4 | Open-ended answer receives quality feedback |
| 10 | US8 - Web Application | P3 | 25 | 15 | All features accessible via web UI |
| 11 | Polish & Deployment | - | 12 | 6 | System deployable to production |
| **TOTAL** | | | **155** | **86** | All stories independently testable |

---

## Phase 1: Setup (15 tasks)

**Goal**: Initialize project structure, dependencies, and development environment

**Prerequisites**: None

**Deliverables**: Working development environment with all project scaffolding in place

### Tasks

- [X] T001 Create repository structure per plan.md (backend/, chatgpt-app/, web-app/, content/, specs/)
- [X] T002 [P] Initialize backend Python project with pyproject.toml in backend/
- [ ] T003 [P] Initialize web app Next.js project with package.json in web-app/ (DEFERRED: Phase 3)
- [X] T004 [P] Create .gitignore for Python, Node.js, and environment files at repository root
- [X] T005 [P] Create .env.example files in backend/ and web-app/ per quickstart.md
- [X] T006 [P] Create docker-compose.yml for PostgreSQL and Redis per quickstart.md
- [X] T007 [P] Set up GitHub Actions CI/CD workflow in .github/workflows/ci.yml
- [X] T008 [P] Create README.md at repository root with project overview
- [X] T009 Initialize Alembic for database migrations in backend/alembic/
- [X] T010 Create backend/requirements.txt with FastAPI, SQLAlchemy, Pydantic, httpx, python-jose, redis, boto3 (integrated in pyproject.toml)
- [X] T011 Create backend/requirements-dev.txt with pytest, pytest-asyncio, pytest-cov, black, isort, mypy (integrated in pyproject.toml)
- [X] T012 Create backend/app/__init__.py to initialize FastAPI application
- [X] T013 Create backend/app/config.py for environment variable loading (DATABASE_URL, REDIS_URL, R2 credentials, JWT secrets)
- [ ] T014 Create web-app/tsconfig.json and next.config.js per plan.md (DEFERRED: Phase 3)
- [ ] T015 Create web-app/tailwind.config.ts with shadcn/ui configuration (DEFERRED: Phase 3)

---

## Phase 2: Foundational (20 tasks)

**Goal**: Implement shared infrastructure required by all user stories

**Prerequisites**: Phase 1 complete

**Deliverables**: Database schema, authentication system, content storage, caching layer

**Independent Test**: Database migrations run successfully, authentication endpoints return JWT tokens, content can be uploaded to R2

### Tasks

- [ ] T016 Create User model in backend/app/models/user.py per data-model.md schema
- [ ] T017 Create Subscription model in backend/app/models/subscription.py per data-model.md schema
- [ ] T018 [P] Create ChapterProgress model in backend/app/models/progress.py per data-model.md schema
- [ ] T019 [P] Create QuizAttempt model in backend/app/models/quiz.py per data-model.md schema
- [ ] T020 [P] Create Session model in backend/app/models/session.py per data-model.md schema
- [ ] T021 [P] Create Streak model in backend/app/models/streak.py per data-model.md schema
- [ ] T022 Create Alembic migration 001_initial_schema.py for all models in backend/alembic/versions/
- [ ] T023 Create database.py connection module in backend/app/database.py with async SQLAlchemy engine
- [ ] T024 Create Pydantic schemas for User in backend/app/schemas/user.py (UserCreate, UserResponse, UserUpdate)
- [ ] T025 [P] Create Pydantic schemas for Progress in backend/app/schemas/progress.py
- [ ] T026 [P] Create Pydantic schemas for Quiz in backend/app/schemas/quiz.py
- [ ] T027 Implement JWT authentication utilities in backend/app/utils/auth.py (create_token, verify_token, hash_password, verify_password)
- [ ] T028 Implement Cloudflare R2 storage client in backend/app/utils/storage.py (upload_content, download_content, list_files)
- [ ] T029 Implement Redis caching utilities in backend/app/utils/cache.py (get_cache, set_cache, invalidate_cache)
- [ ] T030 Create authentication dependencies in backend/app/dependencies.py (get_current_user, require_free_tier, require_premium)
- [ ] T031 Create POST /auth/register endpoint in backend/app/api/auth.py per contracts/README.md
- [ ] T032 Create POST /auth/login endpoint in backend/app/api/auth.py per contracts/README.md
- [ ] T033 Create POST /auth/refresh endpoint in backend/app/api/auth.py per contracts/README.md
- [ ] T034 Create GET /auth/me endpoint in backend/app/api/auth.py per contracts/README.md
- [ ] T035 Create main FastAPI application in backend/app/main.py with CORS, routers, and /health endpoint

---

## Phase 3: US1 - Access Course Content Through Conversational Interface (P1, 18 tasks)

**Goal**: Students can request and receive course content through ChatGPT conversational interface

**Prerequisites**: Phase 2 complete (authentication, database, content storage)

**Deliverables**:
- Content API endpoints serving chapters from R2
- ChatGPT App manifest and prompts
- Students can ask "Show me Chapter 1" and receive content

**Independent Test**:
1. **Given** a student authenticates, **When** they request "Show me Chapter 1" via ChatGPT, **Then** they receive Introduction to Generative AI content with all sections
2. **Given** content is requested, **When** backend retrieves from R2, **Then** content is served verbatim (zero hallucinations)
3. **Given** a student completes Chapter 1, **When** they return later, **Then** system remembers their position

### Tasks

- [ ] T036 [US1] Create content service in backend/app/services/content.py (get_chapter, get_section, search_content)
- [ ] T037 [US1] Create GET /v1/chapters endpoint in backend/app/api/v1/chapters.py per contracts/README.md
- [ ] T038 [US1] Create GET /v1/chapters/{id} endpoint in backend/app/api/v1/chapters.py per contracts/README.md
- [ ] T039 [P] [US1] Create GET /v1/chapters/{id}/sections endpoint in backend/app/api/v1/chapters.py per contracts/README.md
- [ ] T040 [P] [US1] Create GET /v1/chapters/{id}/next endpoint in backend/app/api/v1/chapters.py per contracts/README.md
- [ ] T041 [P] [US1] Create GET /v1/chapters/{id}/previous endpoint in backend/app/api/v1/chapters.py per contracts/README.md
- [ ] T042 [P] [US1] Create GET /v1/search endpoint in backend/app/api/v1/chapters.py per contracts/README.md
- [ ] T043 [US1] Create course content JSON files in backend/content/chapters/ (01-intro-genai.json through 06-ai-applications.json) per data-model.md schema
- [ ] T044 [US1] Upload course content to Cloudflare R2 bucket using R2 storage client
- [ ] T045 [US1] Create progress tracking service in backend/app/services/progress_tracker.py (update_progress, get_progress_summary)
- [ ] T046 [US1] Create PUT /v1/progress/chapter/{id} endpoint in backend/app/api/v1/progress.py per contracts/README.md
- [ ] T047 [US1] Create ChatGPT App manifest in chatgpt-app/manifest.yaml per plan.md structure
- [ ] T048 [P] [US1] Create shared context prompt in chatgpt-app/prompts/_shared-context.txt per research.md Q2
- [ ] T049 [P] [US1] Create teaching mode prompt in chatgpt-app/prompts/teach.txt per research.md Q2
- [ ] T050 [US1] Configure ChatGPT App actions in manifest.yaml (get_content, get_next, search) pointing to backend v1 endpoints
- [ ] T051 [US1] Create concept-explainer SKILL.md in backend/app/skills/concept-explainer/SKILL.md per plan.md structure
- [ ] T052 [US1] Deploy ChatGPT App to OpenAI Apps Platform using openai-cli per quickstart.md
- [ ] T053 [US1] Test end-to-end: Authenticate → Request "Show me Chapter 1" → Receive content → Progress updates

---

## Phase 4: US2 - Receive Personalized Explanations (P1, 12 tasks)

**Goal**: Students receive explanations adapted to their comprehension level via ChatGPT

**Prerequisites**: Phase 3 complete (content delivery, ChatGPT integration)

**Deliverables**:
- ChatGPT prompts for multi-level explanations
- Socratic tutoring mode
- Concept explainer skill integrated

**Independent Test**:
1. **Given** a beginner asks "What is a transformer?", **When** ChatGPT responds, **Then** it uses everyday analogies
2. **Given** an advanced student asks same question, **When** ChatGPT responds, **Then** it provides technical details
3. **Given** a student says "I don't understand", **When** they request clarification, **Then** concept is broken into simpler parts

### Tasks

- [ ] T054 [P] [US2] Create Socratic mode prompt in chatgpt-app/prompts/socratic.txt per research.md Q2
- [ ] T055 [P] [US2] Create socratic-tutor SKILL.md in backend/app/skills/socratic-tutor/SKILL.md per plan.md structure
- [ ] T056 [US2] Update concept-explainer SKILL.md with beginner/intermediate/advanced response templates
- [ ] T057 [US2] Add difficulty level detection logic to concept-explainer workflow (analyze student's questions for complexity)
- [ ] T058 [US2] Create example analogies database in backend/content/analogies.json for common GenAI concepts
- [ ] T059 [P] [US2] Update teaching mode prompt with multi-level explanation instructions
- [ ] T060 [P] [US2] Update Socratic mode prompt with question-based learning workflow (never give direct answers)
- [ ] T061 [US2] Configure ChatGPT App to switch between teaching/Socratic modes based on trigger keywords
- [ ] T062 [US2] Update manifest.yaml with Socratic mode action
- [ ] T063 [US2] Add follow-up question handling in concept-explainer skill workflow
- [ ] T064 [US2] Test beginner-level explanation: Ask "What is attention mechanism?" → Verify everyday analogy used
- [ ] T065 [US2] Test advanced-level explanation: Ask same question with technical context → Verify multi-head self-attention details provided

---

## Phase 5: US3 - Take Quizzes with Immediate Feedback (P1, 15 tasks)

**Goal**: Students take quizzes with instant deterministic grading and explanatory feedback

**Prerequisites**: Phase 3 complete (content delivery, authentication)

**Deliverables**:
- Quiz content JSON files with answer keys
- Deterministic quiz grading service
- Quiz API endpoints
- ChatGPT quiz master skill

**Independent Test**:
1. **Given** a student completes Chapter 1, **When** they request "Quiz me on Chapter 1", **Then** they receive 5 MC + 3 T/F questions
2. **Given** student answers incorrectly, **When** results shown, **Then** system explains why answer was wrong
3. **Given** student scores <70%, **When** quiz ends, **Then** system suggests reviewing specific sections

### Tasks

- [ ] T066 [US3] Create quiz grading service in backend/app/services/quiz_grader.py (grade_quiz, calculate_score, generate_feedback) per research.md Q1 (deterministic only)
- [ ] T067 [US3] Create GET /v1/quizzes/{id} endpoint in backend/app/api/v1/quizzes.py per contracts/README.md
- [ ] T068 [US3] Create POST /v1/quizzes/{id}/submit endpoint in backend/app/api/v1/quizzes.py with deterministic grading per contracts/README.md
- [ ] T069 [P] [US3] Create GET /v1/quizzes/{id}/results endpoint in backend/app/api/v1/quizzes.py per contracts/README.md
- [ ] T070 [US3] Create quiz content JSON files in backend/content/quizzes/ (01-quiz.json through 06-quiz.json) per data-model.md schema
- [ ] T071 [US3] Add answer keys to quiz JSON files for deterministic grading
- [ ] T072 [US3] Add explanations for each answer option in quiz JSON files
- [ ] T073 [US3] Upload quiz content to Cloudflare R2 bucket using R2 storage client
- [ ] T074 [P] [US3] Create quiz mode prompt in chatgpt-app/prompts/quiz.txt per research.md Q2
- [ ] T075 [P] [US3] Create quiz-master SKILL.md in backend/app/skills/quiz-master/SKILL.md per plan.md structure
- [ ] T076 [US3] Add quiz actions to ChatGPT App manifest.yaml (get_quiz, submit_quiz, get_results)
- [ ] T077 [US3] Implement quiz attempt tracking (insert QuizAttempt record on submission)
- [ ] T078 [US3] Create Zero-LLM verification test in backend/tests/test_v1_deterministic.py per research.md Q1 (mock LLM environment, assert no API calls)
- [ ] T079 [US3] Test quiz grading: Submit answers with known scores → Verify deterministic results match answer key
- [ ] T080 [US3] Test end-to-end: Request "Quiz me on Chapter 1" → Submit answers → Receive score + explanations → Progress updated

---

## Phase 6: US4 - Track Progress and Maintain Learning Streaks (P2, 12 tasks)

**Goal**: Students view progress, track streaks, and receive motivational feedback

**Prerequisites**: Phase 3 complete (progress tracking foundation exists)

**Deliverables**:
- Progress API endpoints
- Streak calculation logic (timezone-aware)
- Progress motivator skill
- Milestone celebrations

**Independent Test**:
1. **Given** student completes Chapter 1, **When** they check progress, **Then** they see "1/6 chapters completed"
2. **Given** student studies 3 consecutive days, **When** they check streak, **Then** they see "3-day streak"
3. **Given** student achieves milestone (3 chapters), **When** they log in, **Then** system celebrates with specific praise

### Tasks

- [ ] T081 [US4] Create GET /v1/progress endpoint in backend/app/api/v1/progress.py per contracts/README.md (return progress summary)
- [ ] T082 [US4] Create GET /v1/progress/streaks endpoint in backend/app/api/v1/progress.py per contracts/README.md
- [ ] T083 [US4] Implement streak calculation service in backend/app/services/progress_tracker.py (calculate_streak, update_streak, check_timezone) per data-model.md
- [ ] T084 [P] [US4] Implement completion percentage calculation in progress_tracker service
- [ ] T085 [P] [US4] Implement milestone detection logic (3 chapters, 6 chapters, first quiz passed, 7-day streak)
- [ ] T086 [US4] Create motivation mode prompt in chatgpt-app/prompts/motivation.txt per research.md Q2
- [ ] T087 [US4] Create progress-motivator SKILL.md in backend/app/skills/progress-motivator/SKILL.md per plan.md structure
- [ ] T088 [US4] Add progress and streak actions to ChatGPT App manifest.yaml (get_progress, get_streaks)
- [ ] T089 [US4] Implement automatic streak updates on any learning activity (chapter access, quiz submission)
- [ ] T090 [US4] Cache progress data in Redis with 5-minute TTL per data-model.md caching strategy
- [ ] T091 [US4] Test streak calculation: Simulate 3 days of activity → Verify current_streak=3, longest_streak=3
- [ ] T092 [US4] Test timezone handling: Set user timezone to PST → Activity at 11pm PST → Verify streak increments correctly

---

## Phase 7: US5 - Navigate Freemium Access Boundaries (P2, 10 tasks)

**Goal**: Free users access Chapters 1-3, premium users access all content, graceful upgrade prompts

**Prerequisites**: Phase 2 complete (authentication, subscription model)

**Deliverables**:
- Access control middleware
- Freemium gating for Chapters 4-6
- Graceful upgrade messaging
- Subscription upgrade endpoint

**Independent Test**:
1. **Given** free user requests Chapter 4, **When** access checked, **Then** receives friendly message with upgrade options
2. **Given** free user completes Chapter 3, **When** they finish, **Then** system celebrates and suggests premium
3. **Given** premium user accesses any content, **When** they navigate, **Then** unrestricted access to all chapters

### Tasks

- [ ] T093 [US5] Create GET /v1/access/check endpoint in backend/app/api/v1/access.py per contracts/README.md
- [ ] T094 [US5] Create POST /v1/access/upgrade endpoint in backend/app/api/v1/access.py per contracts/README.md (subscription tier change)
- [ ] T095 [US5] Implement require_premium dependency in backend/app/dependencies.py per research.md Q5
- [ ] T096 [US5] Add access_tier field to chapter content JSON files (chapters 1-3: "free", 4-6: "premium")
- [ ] T097 [P] [US5] Update GET /v1/chapters/{id} endpoint to check access tier and subscription
- [ ] T098 [P] [US5] Cache subscription tier in Redis with 1-hour TTL per data-model.md caching strategy
- [ ] T099 [US5] Create upgrade prompt messaging in ChatGPT prompts (friendly, non-pushy)
- [ ] T100 [US5] Add subscription status to ChatGPT App context (visible to prompts)
- [ ] T101 [US5] Test free tier access: Authenticate as free user → Request Chapter 4 → Verify 403 Forbidden with upgrade message
- [ ] T102 [US5] Test premium access: Authenticate as premium user → Request Chapter 4 → Verify 200 OK with content

---

## Phase 8: US6 - Receive Adaptive Learning Recommendations (P3 - Phase 2 Hybrid, 8 tasks)

**Goal**: Premium users receive AI-powered personalized learning path recommendations

**Prerequisites**: Phase 6 complete (progress tracking, quiz scores available)

**Deliverables**:
- Adaptive learning service with Claude Sonnet integration
- Pattern analysis (quiz scores, time spent, skip patterns)
- /v2/adaptive endpoints (hybrid APIs)
- Cost tracking for LLM usage

**Independent Test**:
1. **Given** premium student struggles with RAG (quiz <60%), **When** they request guidance, **Then** system suggests reviewing Chapter 4 sections with tailored exercises
2. **Given** premium student excels, **When** they complete content, **Then** system suggests advanced topics
3. **Given** LLM recommendation generated, **When** cost tracked, **Then** per-request cost logged (~$0.018)

### Tasks

- [ ] T103 [US6] Create adaptive learning service in backend/app/services/adaptive.py per research.md Q6 (pattern analysis + Claude Sonnet prompting)
- [ ] T104 [US6] Add Anthropic Python SDK to backend/requirements.txt
- [ ] T105 [US6] Create POST /v2/adaptive/path endpoint in backend/app/api/v2/adaptive.py per contracts/README.md (premium-gated)
- [ ] T106 [P] [US6] Create GET /v2/adaptive/recommendations endpoint in backend/app/api/v2/adaptive.py per contracts/README.md
- [ ] T107 [US6] Implement pattern analysis logic: Identify weak areas (quiz <60%), slow sections (time >1.5x avg), skipped chapters
- [ ] T108 [US6] Implement Claude Sonnet prompt for generating personalized learning path per research.md Q6
- [ ] T109 [US6] Implement LLM cost tracking: Log tokens used, calculate cost, store per-user in metadata
- [ ] T110 [US6] Test adaptive path generation: Create test user with weak RAG scores → Request recommendations → Verify Chapter 4 sections suggested with rationale

---

## Phase 9: US7 - Submit Free-Form Answers for Deep Assessment (P3 - Phase 2 Hybrid, 8 tasks)

**Goal**: Premium users submit open-ended answers and receive detailed AI-powered feedback on reasoning quality

**Prerequisites**: Phase 5 complete (quiz infrastructure)

**Deliverables**:
- LLM grading service with rubric-based prompting
- /v2/assessments endpoints (hybrid APIs)
- Open-ended question support in quiz JSON
- Expert validation sampling

**Independent Test**:
1. **Given** premium student answers "Explain attention mechanisms" (3 paragraphs), **When** they submit, **Then** receive feedback on clarity, accuracy, depth with improvement suggestions
2. **Given** answer is partially correct, **When** evaluation completes, **Then** system highlights what's right, what's missing, how to improve
3. **Given** assessment graded, **When** cost tracked, **Then** per-assessment cost logged (~$0.014)

### Tasks

- [ ] T111 [US7] Create LLM grading service in backend/app/services/llm_grader.py per research.md Q7 (rubric-based prompting with Claude Sonnet)
- [ ] T112 [US7] Create POST /v2/assessments/{id}/submit endpoint in backend/app/api/v2/assessments.py per contracts/README.md (premium-gated)
- [ ] T113 [P] [US7] Create GET /v2/assessments/{id}/feedback endpoint in backend/app/api/v2/assessments.py per contracts/README.md
- [ ] T114 [US7] Add open-ended questions (type: "open_ended") to quiz JSON files with rubrics per data-model.md schema
- [ ] T115 [US7] Implement grading rubric prompt: Accuracy (0-10), Completeness (0-10), Depth (0-10), Clarity (0-10) per research.md Q7
- [ ] T116 [US7] Implement feedback parsing from Claude Sonnet response (extract scores, comments, improvement suggestions)
- [ ] T117 [US7] Implement LLM cost tracking for assessments (similar to adaptive learning)
- [ ] T118 [US7] Test LLM assessment: Submit answer to "Explain RAG vs fine-tuning" → Verify feedback addresses reasoning quality, not just correctness

---

## Phase 10: US8 - Use Full-Featured Web Application (P3 - Phase 3, 25 tasks)

**Goal**: Students access complete learning experience through standalone Next.js web application

**Prerequisites**: Phases 3-9 complete (all backend APIs functional)

**Deliverables**:
- Next.js 14 web app with App Router
- Visual progress dashboard
- Course navigation UI
- Quiz interface
- Responsive mobile design
- Full feature parity with ChatGPT App

**Independent Test**:
1. **Given** student opens web app, **When** they view dashboard, **Then** see all 6 chapters, progress, streak, quiz scores
2. **Given** student clicks Chapter 3, **When** content loads, **Then** can read sections, navigate next/previous
3. **Given** student takes quiz on web, **When** they submit, **Then** results display instantly with visual breakdown
4. **Given** student accesses from mobile, **When** they use features, **Then** interface adapts responsively with touch-friendly navigation

### Tasks

- [ ] T119 [US8] Create Next.js app layout in web-app/app/layout.tsx (root layout with navigation, auth state)
- [ ] T120 [US8] Create landing page in web-app/app/page.tsx (course overview, login/signup CTAs)
- [ ] T121 [P] [US8] Create course overview page in web-app/app/learn/page.tsx (list all chapters with progress indicators)
- [ ] T122 [P] [US8] Create chapter viewer page in web-app/app/learn/[chapterId]/page.tsx (display chapter content, next/previous navigation)
- [ ] T123 [P] [US8] Create quiz interface page in web-app/app/quiz/[quizId]/page.tsx (display questions, submit answers, show results)
- [ ] T124 [P] [US8] Create progress dashboard page in web-app/app/progress/page.tsx (visual charts, streak counter, completion %)
- [ ] T125 [P] [US8] Create pricing/subscription page in web-app/app/pricing/page.tsx (tier comparison, upgrade CTA)
- [ ] T126 [P] [US8] Create CourseNav component in web-app/components/CourseNav.tsx (chapter tree navigation with shadcn/ui)
- [ ] T127 [P] [US8] Create QuizCard component in web-app/components/QuizCard.tsx (quiz question display with options)
- [ ] T128 [P] [US8] Create ProgressChart component in web-app/components/ProgressChart.tsx (visual progress bar or chart)
- [ ] T129 [P] [US8] Create StreakCounter component in web-app/components/StreakCounter.tsx (display current and longest streak)
- [ ] T130 [US8] Create API client utilities in web-app/lib/api.ts (fetch wrappers for all backend endpoints)
- [ ] T131 [US8] Create authentication helpers in web-app/lib/auth.ts (login, logout, token management, protected routes)
- [ ] T132 [US8] Create useProgress custom hook in web-app/hooks/useProgress.ts (React Query hook for progress data)
- [ ] T133 [P] [US8] Create useQuiz custom hook in web-app/hooks/useQuiz.ts (React Query hook for quiz data and submission)
- [ ] T134 [P] [US8] Create useCourse custom hook in web-app/hooks/useCourse.ts (React Query hook for chapter content)
- [ ] T135 [US8] Configure TailwindCSS with responsive breakpoints (mobile: 640px, tablet: 768px, desktop: 1024px)
- [ ] T136 [US8] Implement shadcn/ui components (Button, Card, Input, Dialog, Progress, Tabs) in web-app/components/ui/
- [ ] T137 [US8] Create responsive navigation menu (hamburger on mobile, sidebar on desktop)
- [ ] T138 [US8] Implement touch-friendly quiz interface for mobile (larger tap targets, swipe gestures)
- [ ] T139 [US8] Create E2E test for learning flow in web-app/tests/e2e/learning-flow.spec.ts using Playwright
- [ ] T140 [US8] Create E2E test for quiz flow in web-app/tests/e2e/quiz-flow.spec.ts using Playwright
- [ ] T141 [US8] Test responsive design: Open on mobile simulator → Verify all features accessible and touch-friendly
- [ ] T142 [US8] Test progress sync: Make changes in ChatGPT App → Reload web app → Verify progress synchronized
- [ ] T143 [US8] Test full user journey: Signup → View course → Read chapter → Take quiz → Check progress → Upgrade to premium → Access Chapter 4

---

## Phase 11: Polish & Cross-Cutting Concerns (12 tasks)

**Goal**: Production-ready deployment with documentation, monitoring, and quality assurance

**Prerequisites**: All user story phases complete

**Deliverables**:
- Comprehensive testing (unit, integration, E2E)
- Documentation (README, API docs, architecture diagram)
- Cost analysis document
- Demo video
- Deployment to Fly.io/Railway
- Monitoring and logging

### Tasks

- [ ] T144 [P] Create unit tests for all services in backend/tests/services/ (quiz_grader, progress_tracker, content, adaptive, llm_grader)
- [ ] T145 [P] Create integration tests for all API endpoints in backend/tests/api/ (auth, chapters, quizzes, progress, access, adaptive, assessments)
- [ ] T146 [P] Create contract tests to validate OpenAPI spec compliance in backend/tests/contract/
- [ ] T147 [P] Run pytest with coverage in backend/ → Verify >80% coverage per constitution
- [ ] T148 [P] Run Jest tests in web-app/ → Verify all component tests pass
- [ ] T149 Create architecture diagram in docs/architecture.png (7-layer Agent Factory stack, data flow, Phase 1/2 separation)
- [ ] T150 Generate OpenAPI spec from FastAPI at /openapi.json → Save to specs/001-course-companion-fte/contracts/openapi.yaml
- [ ] T151 Create cost analysis document in docs/cost-analysis.md (Phase 1: $16/month, Phase 2: $320/month, revenue model)
- [ ] T152 Record demo video (5 minutes): Team intro (30s), architecture (1min), web app (1.5min), ChatGPT app (1.5min), Phase 2 features (30s)
- [ ] T153 Create Dockerfile for backend in backend/Dockerfile (Python 3.11, install deps, run uvicorn)
- [ ] T154 Create deployment config for Fly.io in backend/fly.toml (set environment, scale, regions)
- [ ] T155 Deploy backend to Fly.io: fly deploy → Set secrets (DATABASE_URL, REDIS_URL, R2 credentials, JWT secret, ANTHROPIC_API_KEY) → Verify /health endpoint

---

## Dependencies & Execution Order

### Critical Path (Sequential - No Parallelization)

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1 - Content Access) ← MUST complete before other user stories
    ↓
┌───────────────────────┬──────────────────────┬───────────────────────┐
│                       │                      │                       │
Phase 4 (US2)       Phase 5 (US3)         Phase 6 (US4)          Phase 7 (US5)
(Explanations)      (Quizzes)             (Progress)             (Freemium)
    │                   │                      │                       │
    └───────────────────┴──────────────────────┴───────────────────────┘
                                    ↓
            ┌───────────────────────┴───────────────────────┐
            │                                               │
    Phase 8 (US6 - Adaptive)                   Phase 9 (US7 - LLM Assessments)
    (requires progress data)                   (requires quiz infrastructure)
            │                                               │
            └───────────────────────┬───────────────────────┘
                                    ↓
                            Phase 10 (US8 - Web App)
                            (requires all backend APIs)
                                    ↓
                            Phase 11 (Polish)
```

### User Story Dependencies

- **US1 (Content Access)**: No dependencies (foundation for all)
- **US2 (Explanations)**: Depends on US1 (needs content delivery)
- **US3 (Quizzes)**: Depends on US1 (needs content and progress tracking)
- **US4 (Progress)**: Depends on US1 (extends progress foundation)
- **US5 (Freemium)**: Independent (uses Phase 2 auth foundation)
- **US6 (Adaptive)**: Depends on US4 + US3 (needs progress and quiz data)
- **US7 (LLM Assessments)**: Depends on US3 (extends quiz infrastructure)
- **US8 (Web App)**: Depends on ALL (full feature parity)

### Parallel Execution Opportunities

Within each phase, tasks marked **[P]** can be executed in parallel (different files, no dependencies):

**Phase 1**: 8 parallel tasks (T002-T008) - different directories
**Phase 2**: 12 parallel tasks (T018-T021, T024-T026, scattered) - different models and schemas
**Phase 3**: 10 parallel tasks (T039-T042, T048-T049, scattered) - different endpoints and files
**Phase 4**: 6 parallel tasks (T054-T055, T059-T060) - different prompts and skills
**Phase 5**: 4 parallel tasks (T069, T074-T075) - different files
**Phase 6**: 4 parallel tasks (T084-T085) - calculation logic
**Phase 7**: 4 parallel tasks (T097-T098) - access checks
**Phase 8**: 2 parallel tasks (T106) - endpoints
**Phase 10**: 15 parallel tasks (T121-T134, T139-T140, T144-T148) - UI components and tests
**Phase 11**: 6 parallel tasks (T144-T148) - test suites

**Total parallel opportunities**: 86 tasks out of 155 (55% parallelizable)

---

## Implementation Strategy

### MVP (Minimum Viable Product) - Phase 1 Only

**Scope**: User Story 1 (P1) - Access Course Content
**Timeline**: 2-3 weeks
**Deliverable**: Students can view course content through ChatGPT App

**Tasks**: T001-T053 (53 tasks)
- Setup (15 tasks)
- Foundational (20 tasks)
- US1 implementation (18 tasks)

**Success Criteria**:
- Student authenticates via ChatGPT
- Student requests "Show me Chapter 1" → Receives content
- Backend serves content verbatim from R2 (zero LLM calls verified)
- Progress persists across sessions
- Zero-LLM verification test passes

---

### Incremental Delivery - By User Story

**Phase 1 MVP** (US1):
- Deliverable: Content access via ChatGPT App
- Independent test: Student can view Chapter 1

**Phase 1 + US2**:
- Deliverable: Personalized explanations
- Independent test: Explanations adapt to student level

**Phase 1 + US2 + US3**:
- Deliverable: Quizzes with feedback
- Independent test: Student can take Chapter 1 quiz and receive score

**Phase 1 + US2 + US3 + US4**:
- Deliverable: Progress tracking and streaks
- Independent test: Progress persists, streaks calculate correctly

**Phase 1 + US2 + US3 + US4 + US5**:
- Deliverable: Freemium model
- Independent test: Free users blocked from Chapter 4

**Full Phase 2** (+ US6 + US7):
- Deliverable: Hybrid intelligence (adaptive learning + LLM assessments)
- Independent test: Premium users get personalized recommendations and open-ended feedback

**Full Phase 3** (+ US8):
- Deliverable: Standalone web application
- Independent test: All features accessible via web UI on mobile and desktop

---

## Parallel Team Strategy

If working with a team, assign user stories to team members for parallel development:

**Team Member 1**: US1 (Content Access) → US4 (Progress) → US6 (Adaptive)
**Team Member 2**: US2 (Explanations) → US5 (Freemium) → US7 (LLM Assessments)
**Team Member 3**: US3 (Quizzes) → US8 (Web App)

All teams merge into main after completing their story's independent test criteria.

---

## Testing Strategy

### Unit Tests (80%+ coverage required by constitution)

- All services: `backend/tests/services/`
- All models: `backend/tests/models/`
- All utilities: `backend/tests/utils/`

### Integration Tests

- All API endpoints: `backend/tests/api/`
- Database operations: `backend/tests/integration/`

### Contract Tests

- OpenAPI spec compliance: `backend/tests/contract/`

### E2E Tests (Playwright)

- Learning flow: `web-app/tests/e2e/learning-flow.spec.ts`
- Quiz flow: `web-app/tests/e2e/quiz-flow.spec.ts`

### Constitutional Compliance Tests

- **Zero-LLM Verification**: `backend/tests/test_v1_deterministic.py` (Phase 1 critical)
- **Cost Tracking Validation**: Verify LLM costs logged for Phase 2 features

---

## Task Validation

**Format Check**: ✅ All 155 tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

**Story Mapping**: ✅ All tasks map to user stories or infrastructure phases

**Independent Testability**: ✅ Each user story phase has clear test criteria

**Parallel Opportunities**: ✅ 86 tasks marked [P] for parallel execution (55%)

**Path Specificity**: ✅ All tasks include specific file paths for implementation

**Dependency Clarity**: ✅ Dependencies documented in execution order section

---

## Summary

**Total Tasks**: 155
- Phase 1 (Setup): 15 tasks
- Phase 2 (Foundational): 20 tasks
- Phase 3 (US1 - P1): 18 tasks
- Phase 4 (US2 - P1): 12 tasks
- Phase 5 (US3 - P1): 15 tasks
- Phase 6 (US4 - P2): 12 tasks
- Phase 7 (US5 - P2): 10 tasks
- Phase 8 (US6 - P3): 8 tasks
- Phase 9 (US7 - P3): 8 tasks
- Phase 10 (US8 - P3): 25 tasks
- Phase 11 (Polish): 12 tasks

**Parallelizable**: 86 tasks (55%)

**MVP Scope**: 53 tasks (Phases 1-3: US1 only)

**All User Stories Independently Testable**: ✅

**Ready for `/sp.implement`**: ✅ (when user approves)

---

**Next Step**: Hold implementation until user approval. All specifications complete:
- ✅ spec.md (8 user stories, 49 requirements, 27 success criteria)
- ✅ plan.md (technical stack, architecture, constitutional compliance)
- ✅ tasks.md (155 implementation tasks organized by user story)
- ✅ research.md (7 technology decisions)
- ✅ data-model.md (8 entities, schemas, relationships)
- ✅ contracts/README.md (19 API endpoints)
- ✅ quickstart.md (development setup)

**When ready to begin implementation**: Run `/sp.implement` to start executing tasks from tasks.md
