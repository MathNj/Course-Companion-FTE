# Implementation Tasks: Phase 1 - Zero-Backend-LLM Course Companion

**Branch**: `002-phase-1-zero-backend-llm` | **Date**: 2026-01-24
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Status**: Ready for implementation

## Task Summary

**Total Tasks**: 127
**User Stories**: 5 (US1-US5, all P1)
**Estimated Effort**: 15-20 developer days
**MVP Scope**: US1 + US5 (Content Access + Freemium Gating)

## Task Format

```
- [ ] T### [P?] [US?] Description with backend/path/to/file.py
```

- **T###**: Task ID (T001-T127)
- **P?**: Priority (P0=Blocker, P1=High, P2=Medium, P3=Low)
- **US?**: User Story (US1-US5) or N/A for foundational tasks
- **Description**: What to implement
- **File path**: Where to make changes

---

## Phase 1: Project Setup (T001-T015)

### Repository Structure

- [ ] T001 [P0] [N/A] Create backend/ directory structure with app/, tests/, scripts/, content/
- [ ] T002 [P0] [N/A] Create chatgpt-app/ directory with prompts/ subdirectory
- [ ] T003 [P0] [N/A] Create docker-compose.yml for PostgreSQL 15 + Redis 7 in repository root
- [ ] T004 [P0] [N/A] Create .gitignore with Python venv, __pycache__, .env, *.pyc, htmlcov/
- [ ] T005 [P0] [N/A] Create backend/.env.example with all required environment variables

### Python Environment

- [ ] T006 [P0] [N/A] Create backend/requirements.txt with FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic v2, httpx, python-jose, passlib, redis-py, boto3, alembic
- [ ] T007 [P0] [N/A] Create backend/requirements-dev.txt with pytest, pytest-asyncio, pytest-cov, black, isort, mypy, flake8
- [ ] T008 [P0] [N/A] Create backend/pyproject.toml with Black, isort, mypy configuration
- [ ] T009 [P0] [N/A] Create backend/README.md with setup instructions and architecture overview

### Configuration

- [ ] T010 [P0] [N/A] Implement backend/app/config.py using Pydantic BaseSettings for environment variables
- [ ] T011 [P0] [N/A] Create backend/app/__init__.py to initialize FastAPI application
- [ ] T012 [P0] [N/A] Implement backend/app/main.py with FastAPI app instance, CORS middleware, health check endpoint

### Testing Infrastructure

- [ ] T013 [P0] [N/A] Create backend/tests/conftest.py with pytest fixtures for test database, test client, mock R2
- [ ] T014 [P0] [N/A] Create backend/tests/test_v1_deterministic.py with Zero-LLM verification test (mocks OpenAI/Anthropic endpoints)
- [ ] T015 [P0] [N/A] Create .github/workflows/ci.yml with GitHub Actions pipeline (pytest, coverage, Zero-LLM test)

---

## Phase 2: Foundational Infrastructure (T016-T045)

### Database Models

- [ ] T016 [P0] [N/A] Implement backend/app/database.py with async SQLAlchemy engine, sessionmaker, get_db dependency
- [ ] T017 [P0] [N/A] Create backend/app/models/__init__.py to export all models
- [ ] T018 [P0] [N/A] Implement backend/app/models/user.py with Student model (id, email, password_hash, subscription_tier, timezone, timestamps)
- [ ] T019 [P0] [N/A] Implement backend/app/models/progress.py with ChapterProgress model (student_id FK, chapter_id, completion_status, quiz_score, time_spent)
- [ ] T020 [P0] [N/A] Implement backend/app/models/progress.py with Streak model (student_id FK, current_streak, longest_streak, last_activity_date)
- [ ] T021 [P0] [N/A] Implement backend/app/models/quiz.py with QuizAttempt model (student_id FK, quiz_id, chapter_id, answers_json JSONB, score, passed, grading_details_json)

### Database Migrations

- [ ] T022 [P0] [N/A] Initialize Alembic in backend/alembic/ directory
- [ ] T023 [P0] [N/A] Create Alembic migration version 001: students table with constraints, indexes on email and subscription_tier
- [ ] T024 [P0] [N/A] Create Alembic migration version 002: chapter_progress table with FK to students, composite unique constraint (student_id, chapter_id)
- [ ] T025 [P0] [N/A] Create Alembic migration version 003: quiz_attempts table with FK to students, indexes on student_id, quiz_id, submitted_at
- [ ] T026 [P0] [N/A] Create Alembic migration version 004: streaks table with FK to students, unique constraint on student_id

### Pydantic Schemas

- [ ] T027 [P0] [N/A] Create backend/app/schemas/__init__.py to export all schemas
- [ ] T028 [P0] [N/A] Implement backend/app/schemas/user.py with UserCreate, UserResponse, Token schemas
- [ ] T029 [P0] [N/A] Implement backend/app/schemas/progress.py with ProgressResponse, StreakResponse, ChapterProgressResponse schemas
- [ ] T030 [P0] [N/A] Implement backend/app/schemas/quiz.py with QuizResponse, QuizSubmission, QuizResult, GradingDetail schemas

### Authentication Service

- [ ] T031 [P0] [N/A] Implement backend/app/services/__init__.py to export all services
- [ ] T032 [P0] [N/A] Implement backend/app/services/auth.py with hash_password() using bcrypt
- [ ] T033 [P0] [N/A] Implement backend/app/services/auth.py with verify_password() using bcrypt
- [ ] T034 [P0] [N/A] Implement backend/app/services/auth.py with create_access_token() using python-jose (JWT with user_id, email, subscription_tier, exp)
- [ ] T035 [P0] [N/A] Implement backend/app/services/auth.py with decode_access_token() to verify and extract JWT claims

### Dependencies & Middleware

- [ ] T036 [P0] [N/A] Implement backend/app/dependencies.py with get_current_user() dependency (JWT verification)
- [ ] T037 [P0] [N/A] Implement backend/app/dependencies.py with verify_premium() dependency for freemium gating
- [ ] T038 [P0] [N/A] Implement backend/app/dependencies.py with verify_access() dependency (checks chapter tier vs user tier)

### Storage & Caching

- [ ] T039 [P0] [N/A] Implement backend/app/utils/__init__.py to export utilities
- [ ] T040 [P0] [N/A] Implement backend/app/utils/storage.py with R2Client class (boto3 wrapper for Cloudflare R2)
- [ ] T041 [P0] [N/A] Implement backend/app/utils/storage.py with get_chapter() method to fetch chapter JSON from R2 or local files
- [ ] T042 [P0] [N/A] Implement backend/app/utils/storage.py with get_quiz() method to fetch quiz JSON from R2 or local files
- [ ] T043 [P0] [N/A] Implement backend/app/utils/cache.py with RedisClient class for caching
- [ ] T044 [P0] [N/A] Implement backend/app/utils/cache.py with get_cached() and set_cached() methods (keys: chapter:{id}, quiz:{id}, TTL: 24h)
- [ ] T045 [P0] [N/A] Implement backend/app/services/content.py with get_chapter_with_cache() (checks Redis, falls back to R2, caches result)

---

## Phase 3: Authentication Endpoints (T046-T055)

### User Registration

- [ ] T046 [P1] [N/A] Create backend/app/api/__init__.py and backend/app/api/v1/__init__.py
- [ ] T047 [P1] [N/A] Implement backend/app/api/v1/auth.py with POST /auth/register endpoint
- [ ] T048 [P1] [N/A] Add validation in /auth/register: email format, password strength (≥8 chars, letters+numbers)
- [ ] T049 [P1] [N/A] Add duplicate email check in /auth/register (return 409 Conflict if exists)
- [ ] T050 [P1] [N/A] Create student record with default subscription_tier='free' in /auth/register
- [ ] T051 [P1] [N/A] Return 201 Created with UserResponse (user_id, email, subscription_tier) in /auth/register

### User Login

- [ ] T052 [P1] [N/A] Implement backend/app/api/v1/auth.py with POST /auth/login endpoint
- [ ] T053 [P1] [N/A] Verify email exists and password matches in /auth/login (return 401 Unauthorized if invalid)
- [ ] T054 [P1] [N/A] Generate JWT token with 30-day expiration in /auth/login
- [ ] T055 [P1] [N/A] Return 200 OK with Token schema (access_token, token_type, expires_in, user) in /auth/login

### Current User Info

- [ ] T056 [P1] [N/A] Implement backend/app/api/v1/auth.py with GET /auth/me endpoint (requires authentication)
- [ ] T057 [P1] [N/A] Return current user info from JWT claims in /auth/me (user_id, email, full_name, subscription_tier, timezone, created_at)

### Testing

- [ ] T058 [P1] [N/A] Create backend/tests/api/test_auth.py with test_register_success
- [ ] T059 [P1] [N/A] Add test_register_duplicate_email to backend/tests/api/test_auth.py
- [ ] T060 [P1] [N/A] Add test_register_invalid_password to backend/tests/api/test_auth.py
- [ ] T061 [P1] [N/A] Add test_login_success to backend/tests/api/test_auth.py
- [ ] T062 [P1] [N/A] Add test_login_invalid_credentials to backend/tests/api/test_auth.py
- [ ] T063 [P1] [N/A] Add test_get_me_success to backend/tests/api/test_auth.py
- [ ] T064 [P1] [N/A] Add test_get_me_unauthorized to backend/tests/api/test_auth.py

---

## Phase 4: User Story 1 - Content Access (T065-T078)

### Chapter Endpoints

- [ ] T065 [P1] [US1] Implement backend/app/api/v1/chapters.py with GET /v1/chapters endpoint
- [ ] T066 [P1] [US1] Fetch all 6 chapters metadata in /v1/chapters (title, subtitle, access_tier, estimated_time, difficulty)
- [ ] T067 [P1] [US1] Add user_has_access field to each chapter in /v1/chapters (check subscription_tier vs chapter access_tier)
- [ ] T068 [P1] [US1] Add user_progress field to each chapter in /v1/chapters (completion_status, quiz_score from chapter_progress table)
- [ ] T069 [P1] [US1] Implement backend/app/api/v1/chapters.py with GET /v1/chapters/{id} endpoint
- [ ] T070 [P1] [US1] Add freemium access check in /v1/chapters/{id} using verify_access() dependency
- [ ] T071 [P1] [US1] Return 403 Forbidden with upgrade message if free user requests premium chapter in /v1/chapters/{id}
- [ ] T072 [P1] [US1] Fetch chapter JSON from cache/R2 and return full content with sections in /v1/chapters/{id}
- [ ] T073 [P1] [US1] Add next_chapter and previous_chapter links in /v1/chapters/{id} response

### Search Endpoint

- [ ] T074 [P1] [US1] Implement backend/app/api/v1/chapters.py with GET /v1/search endpoint (query param: q, limit, chapter_id)
- [ ] T075 [P1] [US1] Implement keyword search across all chapters in /v1/search (case-insensitive matching in title, content_markdown)
- [ ] T076 [P1] [US1] Return search results with snippet highlighting in /v1/search (chapter_id, section_id, snippet, relevance_score)

### Testing

- [ ] T077 [P1] [US1] Create backend/tests/api/test_chapters.py with test_get_chapters_list, test_get_chapter_detail, test_get_chapter_premium_blocked, test_search_content
- [ ] T078 [P1] [US1] Verify content served from R2/local files (not LLM-generated) in backend/tests/test_v1_deterministic.py

---

## Phase 5: User Story 2 - Explanations (T079-T083)

### Agent Skill: Concept Explainer

- [ ] T079 [P1] [US2] Create backend/app/skills/concept-explainer/SKILL.md with skill metadata (name, trigger keywords: "explain", "what is", "how does", "define")
- [ ] T080 [P1] [US2] Add Purpose section to concept-explainer/SKILL.md: "Provide multi-level explanations (beginner/intermediate/advanced) from pre-authored content"
- [ ] T081 [P1] [US2] Add Workflow section to concept-explainer/SKILL.md with 4 steps: 1) Identify concept, 2) Detect user level, 3) Retrieve appropriate explanation from backend, 4) Deliver with analogies
- [ ] T082 [P1] [US2] Add Response Templates section to concept-explainer/SKILL.md with beginner/intermediate/advanced examples
- [ ] T083 [P1] [US2] Add Key Principles section to concept-explainer/SKILL.md: "Always use pre-authored content", "Never generate new explanations", "Match user's comprehension level"

### ChatGPT Prompt

- [ ] T084 [P1] [US2] Create chatgpt-app/prompts/_shared-context.txt with system grounding (course overview, zero-hallucination requirement)
- [ ] T085 [P1] [US2] Create chatgpt-app/prompts/teach.txt with concept-explainer mode prompt referencing backend actions (get_chapters, get_chapter)

---

## Phase 6: User Story 3 - Quizzes (T086-T099)

### Quiz Grading Service

- [ ] T086 [P1] [US3] Implement backend/app/services/quiz_grader.py with grade_multiple_choice() function (exact string match, case-insensitive)
- [ ] T087 [P1] [US3] Implement backend/app/services/quiz_grader.py with grade_true_false() function (boolean comparison)
- [ ] T088 [P1] [US3] Implement backend/app/services/quiz_grader.py with grade_short_answer() function (keyword matching, partial credit 0-10 scale)
- [ ] T089 [P1] [US3] Implement backend/app/services/quiz_grader.py with grade_quiz() function (iterates through all questions, calculates score percentage)
- [ ] T090 [P1] [US3] Add explanation generation in grade_quiz() using pre-authored explanations from quiz JSON (explanation_correct, explanation_incorrect)

### Quiz Endpoints

- [ ] T091 [P1] [US3] Implement backend/app/api/v1/quizzes.py with GET /v1/quizzes/{id} endpoint
- [ ] T092 [P1] [US3] Fetch quiz JSON from cache/R2 in /v1/quizzes/{id}, exclude answer keys and explanations from response
- [ ] T093 [P1] [US3] Implement backend/app/api/v1/quizzes.py with POST /v1/quizzes/{id}/submit endpoint
- [ ] T094 [P1] [US3] Validate answers format in /v1/quizzes/{id}/submit (all question IDs present, correct types)
- [ ] T095 [P1] [US3] Call grade_quiz() service in /v1/quizzes/{id}/submit, calculate score and pass/fail (≥70% = pass)
- [ ] T096 [P1] [US3] Insert QuizAttempt record in /v1/quizzes/{id}/submit (student_id, quiz_id, answers_json, score, passed, grading_details_json)
- [ ] T097 [P1] [US3] Update ChapterProgress with highest quiz score in /v1/quizzes/{id}/submit
- [ ] T098 [P1] [US3] Mark chapter completed if quiz_score ≥ 70% in /v1/quizzes/{id}/submit

### Testing

- [ ] T099 [P1] [US3] Create backend/tests/services/test_quiz_grader.py with test_grade_multiple_choice, test_grade_true_false, test_grade_short_answer, test_grade_quiz_full
- [ ] T100 [P1] [US3] Create backend/tests/api/test_quizzes.py with test_get_quiz, test_submit_quiz_pass, test_submit_quiz_fail, test_quiz_retake
- [ ] T101 [P1] [US3] Verify quiz grading is deterministic (same answers always produce same score) in backend/tests/api/test_quizzes.py

### Agent Skill: Quiz Master

- [ ] T102 [P1] [US3] Create backend/app/skills/quiz-master/SKILL.md with skill metadata (trigger keywords: "quiz", "test me", "practice")
- [ ] T103 [P1] [US3] Add Workflow section to quiz-master/SKILL.md: 1) Identify chapter, 2) Fetch quiz via get_quiz action, 3) Present questions one-by-one, 4) Submit answers via submit_quiz action, 5) Deliver results with encouragement
- [ ] T104 [P1] [US3] Create chatgpt-app/prompts/quiz.txt with quiz-master mode prompt referencing backend actions (get_quiz, submit_quiz)

---

## Phase 7: User Story 4 - Progress Tracking (T105-T115)

### Progress Tracking Service

- [ ] T105 [P1] [US4] Implement backend/app/services/progress_tracker.py with calculate_completion_percentage() function (completed chapters / 6)
- [ ] T106 [P1] [US4] Implement backend/app/services/progress_tracker.py with update_streak() function (timezone-aware, increments if consecutive day, resets if broken)
- [ ] T107 [P1] [US4] Add milestone detection in update_streak() (3-day, 7-day, 14-day, 30-day milestones)
- [ ] T108 [P1] [US4] Implement backend/app/services/progress_tracker.py with get_milestone_encouragement() function (returns celebration message for achieved milestones)

### Progress Endpoints

- [ ] T109 [P1] [US4] Implement backend/app/api/v1/progress.py with GET /v1/progress endpoint
- [ ] T110 [P1] [US4] Fetch all chapter_progress records for user in /v1/progress
- [ ] T111 [P1] [US4] Calculate overall_progress (chapters_completed, completion_percentage, total_study_time_minutes) in /v1/progress
- [ ] T112 [P1] [US4] Fetch streak data in /v1/progress (current_streak, longest_streak, last_activity_date)
- [ ] T113 [P1] [US4] Add milestones section in /v1/progress (achieved, next_milestone with progress)
- [ ] T114 [P1] [US4] Implement backend/app/api/v1/progress.py with GET /v1/progress/streaks endpoint for detailed streak info

### Testing

- [ ] T115 [P1] [US4] Create backend/tests/services/test_progress_tracker.py with test_calculate_completion, test_update_streak_consecutive, test_update_streak_broken, test_timezone_handling
- [ ] T116 [P1] [US4] Create backend/tests/api/test_progress.py with test_get_progress, test_get_streaks, test_progress_sync_across_devices
- [ ] T117 [P1] [US4] Verify progress syncs within 5 seconds across devices in backend/tests/api/test_progress.py (cache invalidation test)

### Agent Skill: Progress Motivator

- [ ] T118 [P1] [US4] Create backend/app/skills/progress-motivator/SKILL.md with skill metadata (trigger keywords: "my progress", "streak", "how am I doing")
- [ ] T119 [P1] [US4] Add Workflow section to progress-motivator/SKILL.md: 1) Fetch progress via get_progress action, 2) Identify milestones, 3) Deliver specific praise, 4) Suggest next goal
- [ ] T120 [P1] [US4] Create chatgpt-app/prompts/motivation.txt with progress-motivator mode prompt referencing backend actions (get_progress, get_streaks)

---

## Phase 8: User Story 5 - Freemium Gating (T121-T125)

### Access Control

- [ ] T121 [P1] [US5] Implement backend/app/api/v1/access.py with GET /v1/access/check endpoint
- [ ] T122 [P1] [US5] Return accessible_chapters and locked_chapters based on subscription_tier in /v1/access/check
- [ ] T123 [P1] [US5] Return upgrade_benefits list in /v1/access/check (Chapters 4-6, advanced topics, certificate)
- [ ] T124 [P1] [US5] Add upgrade_url field in /v1/access/check response

### Testing

- [ ] T125 [P1] [US5] Create backend/tests/api/test_access.py with test_free_tier_access, test_premium_tier_access, test_upgrade_prompt, test_immediate_access_after_upgrade

---

## Phase 9: Additional Agent Skills (T126-T128)

### Socratic Tutor Skill

- [ ] T126 [P2] [N/A] Create backend/app/skills/socratic-tutor/SKILL.md with skill metadata (trigger keywords: "help me think", "I'm stuck", "hint", "guide me")
- [ ] T127 [P2] [N/A] Add Workflow section to socratic-tutor/SKILL.md: 1) Ask guiding questions, 2) Don't give direct answers, 3) Build on student knowledge, 4) Reference course content via get_chapter action
- [ ] T128 [P2] [N/A] Create chatgpt-app/prompts/socratic.txt with socratic-tutor mode prompt

---

## Phase 10: Content Seeding (T129-T132)

### Course Content

- [ ] T129 [P1] [N/A] Create backend/content/chapters/ directory with 6 JSON files (01-intro-genai.json to 06-ai-applications.json)
- [ ] T130 [P1] [N/A] Author Chapter 1-3 content (free tier) with sections, learning objectives, estimated time, difficulty level
- [ ] T131 [P1] [N/A] Author Chapter 4-6 content (premium tier) with sections, learning objectives, estimated time, difficulty level

### Quiz Content

- [ ] T132 [P1] [N/A] Create backend/content/quizzes/ directory with 6 JSON files (01-quiz.json to 06-quiz.json)
- [ ] T133 [P1] [N/A] Author 6 quizzes (10 questions each: 5 MC, 3 T/F, 2 short-answer) with answer keys and explanations
- [ ] T134 [P1] [N/A] Implement backend/scripts/seed_content.py to upload content to Cloudflare R2 or copy to local directory

---

## Phase 11: ChatGPT App Integration (T135-T140)

### ChatGPT Manifest

- [ ] T135 [P1] [N/A] Create chatgpt-app/manifest.yaml with app metadata (name, description, version, author)
- [ ] T136 [P1] [N/A] Add api.base_url in manifest.yaml pointing to backend API (localhost:8000 for dev, production URL for prod)
- [ ] T137 [P1] [N/A] Define 5 actions in manifest.yaml: get_chapters, get_chapter, get_quiz, submit_quiz, get_progress
- [ ] T138 [P1] [N/A] Add authentication configuration in manifest.yaml (bearer token, token_endpoint: /auth/login)

### Deployment

- [ ] T139 [P1] [N/A] Create chatgpt-app/README.md with setup and deployment instructions
- [ ] T140 [P1] [N/A] Test ChatGPT App locally by calling backend API endpoints through conversational interface

---

## Phase 12: Testing & Quality Assurance (T141-T150)

### Integration Tests

- [ ] T141 [P1] [N/A] Run full test suite and verify >80% code coverage: `pytest --cov=app --cov-report=term`
- [ ] T142 [P1] [N/A] Run Zero-LLM verification test: `pytest tests/test_v1_deterministic.py::test_zero_llm_calls -v`
- [ ] T143 [P1] [N/A] Test all API endpoints end-to-end in backend/tests/api/ (auth, chapters, quizzes, progress, access)

### End-to-End Scenarios

- [ ] T144 [P1] [N/A] Create backend/tests/test_e2e.py with test_full_user_journey (register → login → view chapter → take quiz → check progress)
- [ ] T145 [P1] [N/A] Add test_freemium_flow to backend/tests/test_e2e.py (free user accesses Chapters 1-3, blocked from Chapter 4, upgrades, accesses Chapter 4)
- [ ] T146 [P1] [N/A] Add test_streak_calculation to backend/tests/test_e2e.py (activity on consecutive days, streak increments, streak broken, streak resets)

### Code Quality

- [ ] T147 [P1] [N/A] Run Black formatter: `black app/`
- [ ] T148 [P1] [N/A] Run isort: `isort app/`
- [ ] T149 [P1] [N/A] Run mypy type checker: `mypy app/`
- [ ] T150 [P1] [N/A] Run flake8 linter: `flake8 app/`

---

## Phase 13: Documentation & Deployment (T151-T160)

### Documentation

- [ ] T151 [P2] [N/A] Review and finalize backend/README.md with architecture diagram, setup instructions, API overview
- [ ] T152 [P2] [N/A] Review and finalize chatgpt-app/README.md with deployment instructions, prompt engineering tips

### Local Deployment

- [ ] T153 [P1] [N/A] Create backend/Dockerfile with Python 3.11 base image, dependency installation, uvicorn command
- [ ] T154 [P1] [N/A] Test local Docker build: `docker build -t course-companion-backend .`
- [ ] T155 [P1] [N/A] Test local Docker run: `docker run -p 8000:8000 --env-file .env course-companion-backend`

### Production Deployment

- [ ] T156 [P2] [N/A] Create backend/fly.toml for Fly.io deployment configuration
- [ ] T157 [P2] [N/A] Deploy to Fly.io: `fly launch` and `fly deploy`
- [ ] T158 [P2] [N/A] Set production secrets in Fly.io: JWT_SECRET_KEY, DATABASE_URL (Neon), REDIS_URL (Upstash), R2 credentials
- [ ] T159 [P2] [N/A] Update chatgpt-app/manifest.yaml with production API URL
- [ ] T160 [P2] [N/A] Deploy ChatGPT App to production

---

## Dependency Graph

### Critical Path (Must complete in order)

```
T001-T015 (Setup)
    ↓
T016-T026 (Database Models + Migrations)
    ↓
T027-T038 (Schemas + Auth + Dependencies)
    ↓
T039-T045 (Storage + Caching)
    ↓
T046-T064 (Authentication Endpoints)
    ↓
T065-T078 (Content Access - US1)
    ↓
T086-T104 (Quizzes - US3)
    ↓
T105-T120 (Progress Tracking - US4)
    ↓
T121-T125 (Freemium Gating - US5)
    ↓
T135-T140 (ChatGPT App Integration)
    ↓
T141-T150 (Testing & QA)
```

### Parallel Execution Opportunities

**After T045 (Foundational complete)**:
- Can implement Authentication (T046-T064) in parallel with Content Seeding (T129-T134)
- Can implement Agent Skills (T079-T085, T102-T104, T118-T120, T126-T128) in parallel with API endpoints

**After T064 (Auth complete)**:
- Can implement US1 (T065-T078), US3 (T086-T104), US4 (T105-T120), US5 (T121-T125) in parallel if 4 developers available
- Each user story is independent once foundational infrastructure is complete

**After T125 (All user stories complete)**:
- Can work on ChatGPT App (T135-T140), Content Seeding (T129-T134), Documentation (T151-T152) in parallel

---

## MVP Scope (Minimum Viable Product)

**Goal**: Ship functional product in 5 days with 2 user stories

**MVP Tasks** (38 tasks, estimated 5 developer days):
- T001-T015: Project Setup (1 day)
- T016-T045: Foundational Infrastructure (2 days)
- T046-T064: Authentication Endpoints (1 day)
- T065-T078: Content Access - US1 (1 day)
- T121-T125: Freemium Gating - US5 (0.5 day)
- T129-T134: Content Seeding (parallel with above)
- T135-T140: ChatGPT App Integration (0.5 day)
- T141-T150: Testing & QA (1 day, parallel with integration)

**Defer to Post-MVP** (Phase 2 expansion):
- US2: Explanations (T079-T085) - Can use basic chatGPT knowledge initially
- US3: Quizzes (T086-T104) - Not essential for content consumption
- US4: Progress Tracking (T105-T120) - Nice-to-have for engagement
- Socratic Tutor Skill (T126-T128) - Advanced feature

**MVP Acceptance Criteria**:
- ✅ Students can register and login
- ✅ Students can access Chapters 1-3 (free tier)
- ✅ Students are blocked from Chapters 4-6 with upgrade prompt
- ✅ Premium students can access all 6 chapters
- ✅ ChatGPT App calls backend API for content delivery
- ✅ Zero-LLM verification test passes (constitutional compliance)
- ✅ Infrastructure cost <$0.004/user/month

---

## Progress Tracking

### Task Status Legend
- `[ ]` Not Started
- `[~]` In Progress
- `[x]` Completed
- `[!]` Blocked

### Phase Completion Checklist
- [ ] Phase 1: Project Setup (T001-T015) - 0/15 completed
- [ ] Phase 2: Foundational Infrastructure (T016-T045) - 0/30 completed
- [ ] Phase 3: Authentication (T046-T064) - 0/19 completed
- [ ] Phase 4: User Story 1 (T065-T078) - 0/14 completed
- [ ] Phase 5: User Story 2 (T079-T085) - 0/7 completed
- [ ] Phase 6: User Story 3 (T086-T104) - 0/19 completed
- [ ] Phase 7: User Story 4 (T105-T120) - 0/16 completed
- [ ] Phase 8: User Story 5 (T121-T125) - 0/5 completed
- [ ] Phase 9: Additional Skills (T126-T128) - 0/3 completed
- [ ] Phase 10: Content Seeding (T129-T134) - 0/6 completed
- [ ] Phase 11: ChatGPT App (T135-T140) - 0/6 completed
- [ ] Phase 12: Testing & QA (T141-T150) - 0/10 completed
- [ ] Phase 13: Documentation & Deployment (T151-T160) - 0/10 completed

**Total Progress**: 0/160 tasks completed (0%)

---

## Risk Mitigation

### Risk 1: Content Not Ready
**Mitigation**: Use placeholder content (Lorem Ipsum) for initial development. Implement content pipeline first (T129-T134) to unblock development.

### Risk 2: Cloudflare R2 Integration Issues
**Mitigation**: Support CONTENT_SOURCE=local mode for development. Test R2 integration early with T039-T042.

### Risk 3: Zero-LLM Test Failures
**Mitigation**: Implement T014 (Zero-LLM test) immediately after foundational infrastructure. Run in CI/CD pipeline as blocking check.

### Risk 4: ChatGPT Platform Limitations
**Mitigation**: Design backend APIs as platform-agnostic REST endpoints. Can pivot to web app (Phase 3) if ChatGPT platform restrictive.

### Risk 5: Timeline Slippage
**Mitigation**: Focus on MVP scope (38 tasks) first. Defer US2, US3, US4 to post-MVP if timeline at risk.

---

## Notes

- **Constitutional Compliance**: Zero-LLM verification test (T014, T142) is MANDATORY before deployment
- **Freemium First**: US5 (Freemium Gating) is part of MVP - business model depends on it
- **Caching Critical**: Redis caching (T043-T045) is essential for <100ms response times and cost control
- **Timezone-Aware**: Streak calculations (T106) MUST use user's timezone per FR-025
- **Test Coverage**: Target >80% code coverage (T141) - no exceptions
- **No LLM Grading**: Quiz grading (T086-T090) uses deterministic rules only - keyword matching for short-answer
- **Content Pre-Authored**: All chapters and quizzes (T129-T133) must be authored by SMEs before seeding

---

**Tasks.md Complete. Ready for implementation via `/sp.implement` command.**
