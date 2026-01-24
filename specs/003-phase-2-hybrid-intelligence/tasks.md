# Tasks: Phase 2 - Hybrid Intelligence Course Companion

**Feature Branch**: `003-phase-2-hybrid-intelligence`
**Created**: 2026-01-24
**Status**: Ready for Implementation
**Related Artifacts**: [spec.md](./spec.md) | [plan.md](./plan.md) | [data-model.md](./data-model.md) | [contracts/README.md](./contracts/README.md) | [quickstart.md](./quickstart.md)

---

## Task Format Legend

- `- [ ]` = Checkbox for tracking completion
- `T###` = Task ID (sequential)
- `[P]` = Parallelizable (can run concurrently with other [P] tasks in same phase)
- `[US6]` / `[US7]` = User Story label (only for story-specific tasks)
- **NO label** = Setup, Foundational, or Polish tasks (not tied to specific user story)

---

## Phase 1: Setup & Environment (T001-T015)

**Objective**: Configure Phase 2 development environment, dependencies, and tooling.

### Dependencies & Configuration

- [ ] T001 [P] Install Anthropic Python SDK (anthropic==0.40.0) with backend/requirements.txt
- [ ] T002 [P] Install tiktoken library (tiktoken==0.5.2) for token counting with backend/requirements.txt
- [ ] T003 [P] Install pydantic-settings (2.1.0) if not present with backend/requirements.txt
- [ ] T004 Add Phase 2 environment variables to .env.example (ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_TIMEOUT, ANTHROPIC_MAX_RETRIES, LLM_COST_ALERT_THRESHOLD, PREMIUM_ADAPTIVE_PATHS_LIMIT, PREMIUM_ASSESSMENTS_LIMIT, ENABLE_ADAPTIVE_PATHS, ENABLE_LLM_ASSESSMENTS, ENABLE_PHASE2_CACHING) with backend/.env.example
- [ ] T005 Update .gitignore to exclude Anthropic credentials (add .env, .env.local, anthropic_api_key.txt, *.anthropic, cost_logs/, llm_usage_dev.csv) with .gitignore

### Project Structure

- [ ] T006 Create backend/app/api/v2/ directory for Phase 2 routers with backend/app/api/v2/__init__.py
- [ ] T007 Create backend/app/services/llm/ directory for LLM service layer with backend/app/services/llm/__init__.py
- [ ] T008 Create backend/app/prompts/ directory for LLM prompt templates with backend/app/prompts/adaptive_path.txt
- [ ] T009 Create backend/content/assessments/ directory for open-ended questions with backend/content/assessments/README.md
- [ ] T010 Create backend/tests/services/test_llm/ directory for LLM service tests with backend/tests/services/test_llm/__init__.py

### Documentation & Tooling

- [ ] T011 [P] Update backend/README.md with Phase 2 setup instructions (Anthropic API key, new env vars)
- [ ] T012 [P] Create backend/scripts/check_cost_alerts.py for daily cost monitoring with backend/scripts/check_cost_alerts.py
- [ ] T013 [P] Create backend/scripts/create_test_premium_user.py for test user setup with backend/scripts/create_test_premium_user.py
- [ ] T014 [P] Add linting rule to prevent v1/v2 cross-contamination (.flake8 per-file-ignores) with backend/.flake8
- [ ] T015 [P] Create PHASE2_QUICKSTART.md symlink to specs/003-phase-2-hybrid-intelligence/quickstart.md with backend/PHASE2_QUICKSTART.md

---

## Phase 2: Foundational - Database & Schemas (T016-T045)

**Objective**: Implement database models, migrations, Pydantic schemas, and core dependencies.

### Database Models (SQLAlchemy)

- [ ] T016 Create AdaptivePath model with backend/app/models/llm.py (path_id UUID, student_id FK, generated_at, expires_at, recommendations_json JSONB, reasoning TEXT, tokens_input, tokens_output, cost_usd, status VARCHAR(20), followed_at, completed_at)
- [ ] T017 Create AssessmentSubmission model with backend/app/models/llm.py (submission_id UUID, student_id FK, question_id VARCHAR(50), answer_text TEXT, submitted_at, grading_status VARCHAR(20), grading_started_at, grading_completed_at, attempt_number INT, previous_submission_id UUID FK, error_message TEXT)
- [ ] T018 Create AssessmentFeedback model with backend/app/models/llm.py (feedback_id UUID, submission_id FK, quality_score DECIMAL(3,1), strengths_json JSONB, improvements_json JSONB, detailed_feedback TEXT, generated_at, tokens_input, tokens_output, cost_usd, human_reviewed BOOLEAN, human_reviewer_id UUID FK, human_review_notes TEXT)
- [ ] T019 Create LLMUsageLog model with backend/app/models/usage.py (log_id UUID, student_id FK, feature VARCHAR(50), reference_id UUID, request_timestamp, model_version VARCHAR(100), tokens_input INT, tokens_output INT, tokens_total COMPUTED, cost_usd DECIMAL(10,6), latency_ms INT, success BOOLEAN, error_code VARCHAR(50), error_message TEXT, deleted_at TIMESTAMP)
- [ ] T020 Create PremiumUsageQuota model with backend/app/models/usage.py (quota_id UUID, student_id FK, month DATE, reset_date DATE, adaptive_paths_used INT, adaptive_paths_limit INT, assessments_used INT, assessments_limit INT, created_at, updated_at)

### Database Indexes & Constraints

- [ ] T021 Add indexes to AdaptivePath model (idx_adaptive_paths_student_id, idx_adaptive_paths_generated_at DESC, idx_adaptive_paths_status WHERE active, idx_adaptive_paths_student_active composite) with backend/app/models/llm.py
- [ ] T022 Add indexes to AssessmentSubmission model (idx_submissions_student_id, idx_submissions_question_id, idx_submissions_status, idx_submissions_student_question composite DESC) with backend/app/models/llm.py
- [ ] T023 Add indexes to AssessmentFeedback model (idx_feedback_submission_id, idx_feedback_generated_at DESC, idx_feedback_score, idx_feedback_unreviewed WHERE false) with backend/app/models/llm.py
- [ ] T024 Add indexes to LLMUsageLog model (idx_llm_logs_student_id, idx_llm_logs_feature, idx_llm_logs_timestamp DESC, idx_llm_logs_success, idx_llm_logs_active WHERE deleted_at IS NULL) with backend/app/models/usage.py
- [ ] T025 Add indexes to PremiumUsageQuota model (idx_quotas_student_id, idx_quotas_month, idx_quotas_student_month composite, unique constraint student_id+month) with backend/app/models/usage.py

### Alembic Migrations

- [ ] T026 Create migration 002_phase2_adaptive_paths.py for AdaptivePath table with backend/alembic/versions/002_phase2_adaptive_paths.py (upgrade/downgrade functions, all columns, indexes, constraints)
- [ ] T027 Create migration 003_phase2_assessments.py for AssessmentSubmission and AssessmentFeedback tables with backend/alembic/versions/003_phase2_assessments.py (upgrade/downgrade functions, foreign keys, checks)
- [ ] T028 Create migration 004_phase2_usage_tracking.py for LLMUsageLog and PremiumUsageQuota tables with backend/alembic/versions/004_phase2_usage_tracking.py (upgrade/downgrade, computed columns, unique constraints)
- [ ] T029 Test migration upgrade sequence (alembic upgrade head) and verify all 5 Phase 2 tables created with backend/alembic/versions/
- [ ] T030 Test migration downgrade sequence (alembic downgrade 001_phase1_complete) and verify clean rollback with backend/alembic/versions/

### Pydantic Schemas (Request/Response)

- [ ] T031 [P] Create AdaptivePathRequest schema with backend/app/schemas/adaptive.py (force_refresh bool, include_reasoning bool)
- [ ] T032 [P] Create AdaptivePathResponse schema with backend/app/schemas/adaptive.py (path_id, student_id, generated_at, expires_at, status, recommendations list, reasoning, metadata)
- [ ] T033 [P] Create RecommendationSchema with backend/app/schemas/adaptive.py (chapter_id, section_id, priority, reason, estimated_impact, estimated_time_minutes, links)
- [ ] T034 [P] Create AssessmentSubmitRequest schema with backend/app/schemas/assessment.py (question_id, answer_text with 50-5000 char validation)
- [ ] T035 [P] Create AssessmentSubmitResponse schema with backend/app/schemas/assessment.py (submission_id, student_id, question_id, submitted_at, grading_status, estimated_completion_seconds, feedback_url)
- [ ] T036 [P] Create AssessmentFeedbackResponse schema with backend/app/schemas/assessment.py (feedback_id, submission_id, quality_score, strengths list, improvements list, detailed_feedback, metadata with tokens/cost/latency)
- [ ] T037 [P] Create UsageQuotaResponse schema with backend/app/schemas/usage.py (student_id, subscription_tier, month, adaptive_paths used/limit/remaining, assessments used/limit/remaining, reset_date)
- [ ] T038 [P] Create CostBreakdownResponse schema with backend/app/schemas/usage.py (period, total_cost_usd, total_requests, average_cost_per_student, breakdown_by_feature, top_users_by_cost, alerts)

### Core Dependencies & Middleware

- [ ] T039 Create verify_premium() dependency in backend/app/dependencies.py (check JWT subscription_tier='premium', check expiration, raise 403 with upgrade CTA if free-tier)
- [ ] T040 Create verify_quota() dependency in backend/app/dependencies.py (check Redis quota counter, check PostgreSQL if Redis miss, raise 429 if limit exceeded)
- [ ] T041 Extend get_current_user() dependency in backend/app/dependencies.py to extract subscription_tier and subscription_expires_at from JWT claims
- [ ] T042 Create get_db_session() dependency wrapper for Phase 2 (same as Phase 1 but ensure connection pooling configured for LLM concurrency) with backend/app/dependencies.py
- [ ] T043 Create get_redis_client() dependency for cache and quota operations with backend/app/dependencies.py (lazy connection, retry logic, fallback to DB if Redis unavailable)

### Configuration & Settings

- [ ] T044 Create backend/app/config/llm_settings.py with LLMSettings class (load from env: ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_TIMEOUT, ANTHROPIC_MAX_RETRIES, LLM_COST_ALERT_THRESHOLD using pydantic-settings BaseSettings)
- [ ] T045 Create backend/app/config/quota_settings.py with QuotaSettings class (PREMIUM_ADAPTIVE_PATHS_LIMIT=10, PREMIUM_ASSESSMENTS_LIMIT=20, QUOTA_RESET_DAY_OF_MONTH=1 using pydantic-settings BaseSettings)

---

## Phase 3: User Story 6 - Adaptive Learning Paths (T046-T080)

**Objective**: Implement LLM-powered adaptive learning path generation with 24h caching.

### LLM Service Layer (Adaptive Paths)

- [ ] T046 [US6] Create Anthropic client wrapper with backend/app/services/llm/client.py (init with API key, timeout, max_retries, async create_message method, exponential backoff retry logic, error categorization)
- [ ] T047 [US6] Create adaptive path prompt template with backend/app/prompts/adaptive_path.txt (system prompt 200 tokens, few-shot examples 500 tokens, JSON output schema, temperature=0.3)
- [ ] T048 [US6] Create AdaptivePathGenerator service with backend/app/services/llm/adaptive_path_generator.py (generate_path method, collect student performance data, format prompt, call Claude Sonnet, parse JSON recommendations)
- [ ] T049 [US6] Implement student performance data collector with backend/app/services/llm/adaptive_path_generator.py (query quiz scores, time spent, weak areas <60%, strong areas >80%, skipped chapters)
- [ ] T050 [US6] Implement recommendation JSON parser with backend/app/services/llm/adaptive_path_generator.py (validate schema, extract chapter_id/section_id/priority/reason/impact/time, handle malformed responses)
- [ ] T051 [US6] Implement token counter with backend/app/services/llm/cost_tracker.py (use tiktoken cl100k_base encoding, count input/output tokens, calculate cost: input*$3/1M + output*$15/1M)
- [ ] T052 [US6] Implement LLM usage logger with backend/app/services/llm/cost_tracker.py (create LLMUsageLog entry with student_id, feature='adaptive-path', tokens, cost_usd, latency_ms, success, reference_id=path_id)

### Caching & Quota Management (Adaptive Paths)

- [ ] T053 [US6] Create Redis cache manager for adaptive paths with backend/app/services/llm/cache_manager.py (set_adaptive_path with 24h TTL, get_adaptive_path, invalidate_on_quiz_completion if score change >20%)
- [ ] T054 [US6] Create quota checker for adaptive paths with backend/app/services/llm/quota_manager.py (check Redis quota:student_id:YYYY-MM:adaptive_paths, fall back to PostgreSQL if Redis unavailable, return remaining count)
- [ ] T055 [US6] Create quota incrementer for adaptive paths with backend/app/services/llm/quota_manager.py (atomic Redis INCR + PostgreSQL UPDATE, create quota record if not exists for current month, handle race conditions)
- [ ] T056 [US6] Create monthly quota reset cron job with backend/scripts/reset_monthly_quotas.py (runs on 1st of month, creates new PremiumUsageQuota records, sets adaptive_paths_used=0, assessments_used=0, resets Redis TTLs)

### API Endpoints (Adaptive Paths)

- [ ] T057 [US6] Create v2 adaptive router with backend/app/api/v2/adaptive.py (FastAPI APIRouter, prefix="/adaptive", tags=["adaptive-learning"], dependencies=[Depends(verify_premium)])
- [ ] T058 [US6] Implement POST /api/v2/adaptive/path endpoint with backend/app/api/v2/adaptive.py (verify quota, check cache if not force_refresh, generate path, save to DB, cache result, log usage, return AdaptivePathResponse)
- [ ] T059 [US6] Implement GET /api/v2/adaptive/path/{path_id} endpoint with backend/app/api/v2/adaptive.py (query DB by path_id, verify student ownership, return path with progress: followed_at, completed_recommendations, completion_percentage)
- [ ] T060 [US6] Implement GET /api/v2/adaptive/paths endpoint with backend/app/api/v2/adaptive.py (list student's paths, filter by status, pagination limit/offset, return summary with recommendations_count, completion_percentage)
- [ ] T061 [US6] Implement POST /api/v2/adaptive/path/{path_id}/complete endpoint with backend/app/api/v2/adaptive.py (mark recommendation as completed, update progress, return next recommendation if available)

### Error Handling & Graceful Degradation (Adaptive Paths)

- [ ] T062 [US6] Implement insufficient data detection with backend/app/services/llm/adaptive_path_generator.py (check if student has <2 completed quizzes, raise 400 INSUFFICIENT_DATA with required_quizzes, completed_quizzes, next_steps)
- [ ] T063 [US6] Implement LLM service unavailable fallback with backend/app/api/v2/adaptive.py (catch Anthropic API timeout/error, return 503 LLM_SERVICE_UNAVAILABLE with fallback suggestion: review chapters with scores <70%, retry_after_seconds=300)
- [ ] T064 [US6] Implement malformed LLM response handling with backend/app/services/llm/adaptive_path_generator.py (catch JSON parse errors, log as error_code='invalid_response', retry up to max_retries, fall back to error response if all retries fail)
- [ ] T065 [US6] Add request timeout handling with backend/app/services/llm/client.py (set httpx timeout=30s, raise TimeoutError if exceeded, log as error_code='timeout' in LLMUsageLog)

### Testing (Adaptive Paths)

- [ ] T066 [US6] [P] Create unit test for Anthropic client wrapper with backend/tests/services/test_llm/test_client.py (mock API, test retry logic, test error categorization, test timeout handling)
- [ ] T067 [US6] [P] Create unit test for adaptive path generator with backend/tests/services/test_llm/test_adaptive_path_generator.py (mock Claude response, test JSON parsing, test weak areas detection, test recommendation prioritization)
- [ ] T068 [US6] [P] Create unit test for cost tracker with backend/tests/services/test_llm/test_cost_tracker.py (test token counting, test cost calculation $3/$15 per 1M, test LLMUsageLog creation)
- [ ] T069 [US6] [P] Create unit test for cache manager with backend/tests/services/test_llm/test_cache_manager.py (test 24h TTL, test cache hit/miss, test invalidation on quiz completion)
- [ ] T070 [US6] [P] Create unit test for quota manager with backend/tests/services/test_llm/test_quota_manager.py (test Redis counter increment, test PostgreSQL fallback, test monthly reset)
- [ ] T071 [US6] Create integration test for POST /api/v2/adaptive/path with backend/tests/test_v2_hybrid.py (test premium gating, test quota enforcement, test cache hit/miss, test cost logging, mock Claude API)
- [ ] T072 [US6] Create integration test for GET /api/v2/adaptive/path/{path_id} with backend/tests/test_v2_hybrid.py (test ownership verification, test progress tracking, test 404 for invalid path_id)
- [ ] T073 [US6] Create integration test for insufficient data error with backend/tests/test_v2_hybrid.py (create student with <2 quizzes, verify 400 INSUFFICIENT_DATA response)
- [ ] T074 [US6] Create integration test for LLM service unavailable with backend/tests/test_v2_hybrid.py (mock Anthropic timeout, verify 503 response with fallback suggestion)

### Content & Prompt Engineering (Adaptive Paths)

- [ ] T075 [US6] Write adaptive path system prompt with backend/app/prompts/adaptive_path.txt (200 tokens: "You are an expert learning advisor for a Generative AI Fundamentals course. Analyze student performance and generate 3-5 prioritized recommendations...")
- [ ] T076 [US6] Write few-shot examples for adaptive path prompt with backend/app/prompts/adaptive_path.txt (Example 1: high-performing student → advanced topics, Example 2: struggling student → prerequisite review, 500 tokens total)
- [ ] T077 [US6] Define JSON output schema for recommendations with backend/app/prompts/adaptive_path.txt (array of {chapter_id, section_id, priority 1-5, reason, estimated_impact high/medium/low, estimated_time_minutes})
- [ ] T078 [US6] Test prompt quality with manual Claude Sonnet API calls (3 test cases: weak student, strong student, mixed performance, verify recommendations are specific and actionable)
- [ ] T079 [US6] Optimize prompt to reduce token usage with backend/app/prompts/adaptive_path.txt (target <1,200 input tokens + <300 output tokens = $0.0091 per request, remove unnecessary words, compress examples)
- [ ] T080 [US6] Add rate limit headers to adaptive path responses with backend/app/api/v2/adaptive.py (X-RateLimit-Limit-Paths: 10, X-RateLimit-Remaining-Paths, X-RateLimit-Reset-Paths: YYYY-MM-01T00:00:00Z)

---

## Phase 4: User Story 7 - LLM Assessments (T081-T115)

**Objective**: Implement LLM-graded open-ended assessments with detailed feedback.

### Assessment Content

- [ ] T081 [US7] Create 04-rag-assessments.json with backend/content/assessments/04-rag-assessments.json (3 questions: RAG vs fine-tuning, vector database architecture, retrieval optimization, each with question_text, evaluation_criteria, example_excellent_answer, example_poor_answer)
- [ ] T082 [US7] Create 05-fine-tuning-assessments.json with backend/content/assessments/05-fine-tuning-assessments.json (3 questions: when to fine-tune, dataset preparation, fine-tuning tradeoffs)
- [ ] T083 [US7] Create 06-ai-apps-assessments.json with backend/content/assessments/06-ai-apps-assessments.json (3 questions: production architecture, safety guardrails, cost optimization)
- [ ] T084 [US7] Upload assessment questions to Cloudflare R2 with backend/scripts/seed_phase2_content.py (boto3 upload to s3://course-content/assessments/, verify 3 files uploaded)

### LLM Service Layer (Assessments)

- [ ] T085 [US7] Create assessment grading prompt template with backend/app/prompts/assessment_grading.txt (system prompt 300 tokens: "You are an expert evaluator for Generative AI course assessments. Grade student answers using rubric...", temperature=0.4)
- [ ] T086 [US7] Create AssessmentGrader service with backend/app/services/llm/assessment_grader.py (grade_submission method, load rubric from R2, format prompt with question+rubric+answer, call Claude Sonnet, parse feedback JSON)
- [ ] T087 [US7] Implement rubric loader with backend/app/services/llm/assessment_grader.py (fetch question from R2 by question_id, extract evaluation_criteria, example_excellent_answer, example_poor_answer, cache in Redis for 1 hour)
- [ ] T088 [US7] Implement feedback JSON parser with backend/app/services/llm/assessment_grader.py (validate schema: score 0-10, strengths array 1-5 items, improvements array 1-5 items, detailed_feedback string >50 chars)
- [ ] T089 [US7] Implement off-topic detection with backend/app/services/llm/assessment_grader.py (check if answer_text contains keywords related to question topic, flag as off-topic if <20% overlap, return 400 INVALID_SUBMISSION)
- [ ] T090 [US7] Implement answer length validation with backend/app/schemas/assessment.py (Pydantic validator: 50 <= len(answer_text) <= 5000 chars, raise 400 INVALID_ANSWER_LENGTH)

### API Endpoints (Assessments)

- [ ] T091 [US7] Create v2 assessments router with backend/app/api/v2/assessments.py (FastAPI APIRouter, prefix="/assessments", tags=["llm-assessments"], dependencies=[Depends(verify_premium)])
- [ ] T092 [US7] Implement POST /api/v2/assessments/submit endpoint with backend/app/api/v2/assessments.py (verify quota, validate answer length, create AssessmentSubmission with grading_status='pending', trigger async grading task, return 202 Accepted with submission_id)
- [ ] T093 [US7] Implement async grading task with backend/app/api/v2/assessments.py (background task: update grading_status='processing', call AssessmentGrader, create AssessmentFeedback, update grading_status='completed', log usage, handle errors)
- [ ] T094 [US7] Implement GET /api/v2/assessments/feedback/{submission_id} endpoint with backend/app/api/v2/assessments.py (query AssessmentFeedback by submission_id, return 202 if still processing, return 200 with feedback if completed, return 500 if failed)
- [ ] T095 [US7] Implement GET /api/v2/assessments/submissions endpoint with backend/app/api/v2/assessments.py (list student's submissions, filter by question_id/grading_status, pagination, return summary with quality_score, attempt_number)
- [ ] T096 [US7] Implement GET /api/v2/assessments/questions/{question_id} endpoint with backend/app/api/v2/assessments.py (fetch question from R2, return question_text, evaluation_criteria, example_excellent/poor_answers, expected_length, premium_only=true)
- [ ] T097 [US7] Implement GET /api/v2/assessments/questions endpoint with backend/app/api/v2/assessments.py (list all 18 assessment questions, filter by chapter_id, include student_status: attempted, latest_score, attempts_remaining 0-3)

### Retry & Attempt Tracking (Assessments)

- [ ] T098 [US7] Implement attempt number tracking with backend/app/api/v2/assessments.py (check previous_submission_id, increment attempt_number, limit to 3 attempts per question, each attempt counts against quota)
- [ ] T099 [US7] Implement submission history query with backend/app/services/assessment_service.py (get_submission_history for question_id, return all attempts sorted by submitted_at DESC, show score improvement trajectory)
- [ ] T100 [US7] Add attempt number to AssessmentSubmitResponse with backend/app/schemas/assessment.py (include attempt_number, max_attempts=3, attempts_remaining)

### Error Handling & Edge Cases (Assessments)

- [ ] T101 [US7] Implement grading failure handling with backend/app/api/v2/assessments.py (catch exceptions in async grading task, update grading_status='failed', store error_message, return 500 GRADING_FAILED with retry_strategy)
- [ ] T102 [US7] Implement answer too short error with backend/app/api/v2/assessments.py (validate answer_text >=50 chars, return 400 INVALID_ANSWER_LENGTH with current_length, minimum_length=50, maximum_length=5000)
- [ ] T103 [US7] Implement answer too long error with backend/app/api/v2/assessments.py (validate answer_text <=5000 chars, return 400 INVALID_ANSWER_LENGTH)
- [ ] T104 [US7] Implement off-topic submission error with backend/app/api/v2/assessments.py (detect in AssessmentGrader, return 400 INVALID_SUBMISSION with suggestion to review chapter)

### Testing (Assessments)

- [ ] T105 [US7] [P] Create unit test for assessment grader with backend/tests/services/test_llm/test_assessment_grader.py (mock Claude response, test feedback parsing, test rubric loading, test off-topic detection)
- [ ] T106 [US7] [P] Create unit test for answer validation with backend/tests/test_v2_hybrid.py (test 50-5000 char range, test too short error, test too long error)
- [ ] T107 [US7] Create integration test for POST /api/v2/assessments/submit with backend/tests/test_v2_hybrid.py (test premium gating, test quota enforcement, test 202 response, test async grading task)
- [ ] T108 [US7] Create integration test for GET /api/v2/assessments/feedback/{submission_id} with backend/tests/test_v2_hybrid.py (test processing status 202, test completed status 200, test feedback structure)
- [ ] T109 [US7] Create integration test for grading quality with backend/tests/test_v2_hybrid.py (submit excellent answer → expect score 8-10, submit poor answer → expect score 0-4, verify strengths/improvements populated)
- [ ] T110 [US7] Create integration test for retry attempts with backend/tests/test_v2_hybrid.py (submit 3 attempts for same question, verify attempt_number increments, verify all count against quota)

### Prompt Engineering (Assessments)

- [ ] T111 [US7] Write assessment grading system prompt with backend/app/prompts/assessment_grading.txt (300 tokens: "You are an expert evaluator for Generative AI course assessments. Grade student answers using the rubric below. Be encouraging but honest...")
- [ ] T112 [US7] Define feedback JSON schema with backend/app/prompts/assessment_grading.txt (score: 0-10 with 0.1 precision, strengths: array of 1-5 strings, improvements: array of 1-5 strings, detailed_feedback: paragraph 100-500 chars)
- [ ] T113 [US7] Test grading prompt with manual Claude Sonnet API calls (3 test cases: excellent answer, poor answer, off-topic answer, verify scores and feedback are appropriate)
- [ ] T114 [US7] Optimize grading prompt to reduce token usage with backend/app/prompts/assessment_grading.txt (target <1,000 input tokens + <200 output tokens = $0.0066 per submission)
- [ ] T115 [US7] Add rate limit headers to assessment responses with backend/app/api/v2/assessments.py (X-RateLimit-Limit-Assessments: 20, X-RateLimit-Remaining-Assessments, X-RateLimit-Reset-Assessments)

---

## Phase 5: Cost Tracking & Admin (T116-T130)

**Objective**: Implement comprehensive cost tracking, monitoring, and admin dashboard.

### Cost Monitoring

- [ ] T116 Create cost aggregation query service with backend/app/services/usage_manager.py (get_monthly_cost_per_student, get_cost_breakdown_by_feature, get_top_users_by_cost, get_cost_alerts for threshold violations)
- [ ] T117 Create cost alert checker with backend/scripts/check_cost_alerts.py (query students exceeding $0.50/month, send email alerts to admin, log warnings)
- [ ] T118 Implement data retention policy with backend/scripts/cleanup_llm_logs.py (soft delete LLMUsageLog entries >90 days old, set deleted_at=now, retain aggregated metrics)
- [ ] T119 Create monthly cost report generator with backend/scripts/generate_cost_report.py (export CSV with student_id, total_cost, adaptive_paths_count, assessments_count, run on 1st of month via cron)

### Admin Endpoints

- [ ] T120 Create v2 admin router with backend/app/api/v2/admin.py (FastAPI APIRouter, prefix="/admin", tags=["admin"], dependencies=[Depends(verify_admin)])
- [ ] T121 Implement verify_admin() dependency with backend/app/dependencies.py (check JWT role='admin', raise 403 ADMIN_REQUIRED if not admin)
- [ ] T122 Implement GET /api/v2/admin/costs endpoint with backend/app/api/v2/admin.py (query params: start_date, end_date, group_by=feature/student/day, return CostBreakdownResponse)
- [ ] T123 Implement GET /api/v2/admin/costs/summary endpoint with backend/app/api/v2/admin.py (return current month total_cost, average_cost_per_student, requests_count, top_users, alerts)
- [ ] T124 Implement GET /api/v2/admin/quotas endpoint with backend/app/api/v2/admin.py (list all students' quota usage, filter by near_limit >80%, return student_id, adaptive_paths_used/limit, assessments_used/limit)
- [ ] T125 Implement GET /api/v2/admin/feedback/unreviewed endpoint with backend/app/api/v2/admin.py (list AssessmentFeedback where human_reviewed=false, for quality monitoring)

### Usage Quota Endpoint

- [ ] T126 Implement GET /api/v2/usage/quota endpoint with backend/app/api/v2/usage.py (return current student's quota: adaptive_paths used/limit/remaining, assessments used/limit/remaining, reset_date, upgrade_options)
- [ ] T127 Create v2 usage router with backend/app/api/v2/usage.py (FastAPI APIRouter, prefix="/usage", tags=["usage"], dependencies=[Depends(verify_premium)])

### Testing (Cost Tracking & Admin)

- [ ] T128 [P] Create unit test for cost aggregation service with backend/tests/services/test_usage_manager.py (test monthly cost calculation, test feature breakdown, test alert detection)
- [ ] T129 Create integration test for GET /api/v2/admin/costs with backend/tests/test_v2_hybrid.py (test admin-only access, test date filtering, test group_by options, verify cost totals)
- [ ] T130 Create integration test for GET /api/v2/usage/quota with backend/tests/test_v2_hybrid.py (test quota display, test remaining count, verify reset_date)

---

## Phase 6: Testing & Quality (T131-T145)

**Objective**: Comprehensive testing, especially CRITICAL Phase 1/2 isolation test.

### CRITICAL Isolation Test

- [ ] T131 **CRITICAL** Create test_phase_isolation.py with backend/tests/test_phase_isolation.py (mock Anthropic API, call ALL Phase 1 endpoints: GET /api/v1/chapters, GET /api/v1/chapters/{id}, GET /api/v1/quizzes/{id}, POST /api/v1/quizzes/{id}/submit, GET /api/v1/progress, GET /api/v1/progress/quiz-history, ASSERT Anthropic client NEVER called, print "✓ Phase 1 isolation verified: Zero LLM calls from v1 endpoints")
- [ ] T132 **CRITICAL** Verify Phase 1 routers have zero imports from v2 or services/llm with backend/tests/test_phase_isolation.py (static analysis: parse backend/app/api/v1/*.py, assert no "from app.api.v2" or "from app.services.llm" imports)
- [ ] T133 **CRITICAL** Add Phase 1 isolation test to CI/CD pipeline as blocking check with .github/workflows/ci.yml (run pytest backend/tests/test_phase_isolation.py, fail build if test fails)

### Integration Tests

- [ ] T134 [P] Create integration test for premium gating with backend/tests/test_v2_hybrid.py (test free user blocked from adaptive paths, test free user blocked from assessments, verify 403 PREMIUM_REQUIRED with upgrade_url)
- [ ] T135 [P] Create integration test for rate limiting with backend/tests/test_v2_hybrid.py (test 10 adaptive paths succeed then 11th fails with 429, test 20 assessments succeed then 21st fails with 429)
- [ ] T136 [P] Create integration test for cost tracking with backend/tests/test_v2_hybrid.py (test every adaptive path creates LLMUsageLog entry, test every assessment creates LLMUsageLog entry, verify tokens_input/output/cost_usd populated)
- [ ] T137 [P] Create integration test for caching with backend/tests/test_v2_hybrid.py (test adaptive path cached for 24h, test cache hit returns same path_id, test force_refresh bypasses cache, test cache invalidation on quiz completion)
- [ ] T138 Create integration test for subscription expiration with backend/tests/test_v2_hybrid.py (test expired premium subscription blocked from v2 endpoints, verify 403 with expiration message)

### End-to-End Tests

- [ ] T139 Create E2E test for adaptive path workflow with backend/tests/test_e2e.py (create premium user → complete 3 quizzes with varied scores → POST /api/v2/adaptive/path → verify recommendations address weak areas → mark recommendation complete → verify progress updated)
- [ ] T140 Create E2E test for assessment workflow with backend/tests/test_e2e.py (create premium user → GET /api/v2/assessments/questions/04-rag-q1 → POST /api/v2/assessments/submit → poll GET /api/v2/assessments/feedback/{id} until completed → verify quality_score, strengths, improvements returned)
- [ ] T141 Create E2E test for quota enforcement across features with backend/tests/test_e2e.py (premium user requests 10 adaptive paths + 20 assessments → verify both quotas enforced independently → verify quota resets on 1st of next month)

### Performance & Load Tests

- [ ] T142 Create performance test for adaptive path latency with backend/tests/test_performance.py (test p95 latency <5 seconds for 100 concurrent requests, mock Claude API to isolate backend performance)
- [ ] T143 Create performance test for assessment grading latency with backend/tests/test_performance.py (test p95 latency <10 seconds for 100 concurrent requests)
- [ ] T144 Create load test for concurrent premium users with backend/tests/test_performance.py (simulate 100 concurrent premium users using both features, verify no rate limit errors, verify no database deadlocks, verify Redis connection pooling handles load)

### Code Quality

- [ ] T145 Run pytest coverage report and ensure >80% coverage for Phase 2 code with backend/tests/ (pytest --cov=backend/app/api/v2 --cov=backend/app/services/llm --cov=backend/app/models/llm.py --cov=backend/app/models/usage.py --cov-report=html, verify coverage >80%)

---

## Phase 7: Documentation & Deployment (T146-T160)

**Objective**: Production-ready deployment, documentation, and monitoring.

### API Documentation

- [ ] T146 [P] Register v2 routers in main.py with backend/app/main.py (app.include_router(adaptive_router, prefix="/api/v2"), app.include_router(assessments_router, prefix="/api/v2"), app.include_router(admin_router, prefix="/api/v2"), app.include_router(usage_router, prefix="/api/v2"))
- [ ] T147 [P] Update OpenAPI schema with Phase 2 endpoints with backend/app/main.py (FastAPI auto-generates, verify /docs shows v2 endpoints, add examples to docstrings)
- [ ] T148 [P] Add Phase 2 API examples to contracts/README.md with specs/003-phase-2-hybrid-intelligence/contracts/README.md (curl examples for all 11 endpoints, update with actual request/response payloads)

### ChatGPT App Integration

- [ ] T149 Update ChatGPT App manifest with chatgpt-app/manifest.yaml (add new actions: adaptive_path, submit_assessment, get_feedback, list_questions, check_quota, map to /api/v2/* endpoints)
- [ ] T150 Update ChatGPT App shared context with chatgpt-app/prompts/_shared-context.txt (describe Phase 2 features, premium gating, quota limits, when to suggest adaptive paths vs assessments)
- [ ] T151 Update concept-explainer skill with chatgpt-app/prompts/concept-explainer.txt (add action to suggest adaptive path if student struggling: "Based on your questions, you might benefit from a personalized learning path. Premium feature: request /adaptive_path")
- [ ] T152 Update quiz-master skill with chatgpt-app/prompts/quiz-master.txt (add action to suggest LLM assessment: "Ready for deeper evaluation? Premium users can submit open-ended answers for detailed feedback. Try /submit_assessment")

### Docker & Deployment

- [ ] T153 Update backend/Dockerfile to include Phase 2 dependencies with backend/Dockerfile (COPY requirements.txt with anthropic==0.40.0 and tiktoken==0.5.2, RUN pip install --no-cache-dir -r requirements.txt)
- [ ] T154 Update docker-compose.yml with environment variables for Phase 2 with docker-compose.yml (add ANTHROPIC_API_KEY, ANTHROPIC_MODEL, LLM_COST_ALERT_THRESHOLD as env vars, mount backend/app/prompts/)
- [ ] T155 Create production deployment script with backend/scripts/deploy_phase2.sh (run migrations, seed assessment content to R2, restart backend service, verify health endpoint, run smoke tests)
- [ ] T156 Configure Fly.io/Railway secrets for production with fly.toml or railway.json (set ANTHROPIC_API_KEY as secret, set ANTHROPIC_MODEL=claude-sonnet-4-5-20250929, set cost alert email)

### Monitoring & Observability

- [ ] T157 Add Phase 2 metrics to Prometheus/Grafana with backend/app/main.py (track: adaptive_path_requests_total, assessment_submissions_total, llm_cost_usd_total, llm_latency_seconds histogram, quota_limit_reached_total)
- [ ] T158 Create cost monitoring dashboard with grafana/dashboards/phase2-costs.json (panels: total monthly cost, cost per student, cost by feature, top users by cost, cost threshold violations)
- [ ] T159 Set up alerts for cost thresholds with grafana/alerts/phase2-alerts.yml (alert if total monthly cost >$300, alert if any student >$0.50/month, alert if p95 latency >10s)
- [ ] T160 Add health check for Phase 2 features with backend/app/api/v1/health.py (extend health endpoint: check Anthropic API connectivity, check Redis availability, check PostgreSQL Phase 2 tables exist, return {"phase2_enabled": true, "llm_service_healthy": true})

---

## Dependency Graph

### Sequential Dependencies

```
Phase 1 (T001-T015) → Phase 2 (T016-T045)
Phase 2 (T016-T045) → Phase 3 (T046-T080) AND Phase 4 (T081-T115)
Phase 3 (T046-T080) → Phase 6 (T131-T145)
Phase 4 (T081-T115) → Phase 6 (T131-T145)
Phase 2 (T016-T045) → Phase 5 (T116-T130)
Phase 5 (T116-T130) → Phase 6 (T131-T145)
Phase 6 (T131-T145) → Phase 7 (T146-T160)
```

### Parallel Execution Opportunities

- **Phase 1**: T001-T003 (dependency installs), T011-T015 (documentation)
- **Phase 2**: T031-T038 (Pydantic schemas), T066-T070 (unit tests)
- **Phase 3**: T066-T070 (unit tests can run in parallel)
- **Phase 4**: T105-T106 (unit tests can run in parallel)
- **Phase 5**: T128 (unit test independent)
- **Phase 6**: T134-T138 (integration tests can run in parallel)
- **Phase 7**: T146-T148 (documentation tasks)

**NOTE**: Tasks marked `[P]` within the same phase can be executed in parallel. Tasks within US6 (Adaptive Learning) and US7 (LLM Assessments) can run in parallel after Phase 2 foundational work completes.

---

## Acceptance Criteria Summary

**Phase 1/2 Isolation (BLOCKING)**:
- [ ] test_phase_isolation.py MUST PASS (zero Anthropic API calls from /api/v1/* endpoints)
- [ ] No imports of `app.api.v2` or `app.services.llm` in `backend/app/api/v1/*.py`

**User Story 6 (Adaptive Learning Paths)**:
- [ ] Premium users can request adaptive paths (POST /api/v2/adaptive/path)
- [ ] Paths cached for 24h (Redis TTL=86400s)
- [ ] Quota enforced: 10 paths per premium user per month
- [ ] LLM usage logged with tokens and cost for every path generated
- [ ] p95 latency <5 seconds (performance test)
- [ ] Recommendations address student's weak areas (quiz scores <60%)

**User Story 7 (LLM Assessments)**:
- [ ] Premium users can submit open-ended answers (POST /api/v2/assessments/submit)
- [ ] Grading completes within 10 seconds (p95 latency)
- [ ] Quota enforced: 20 assessments per premium user per month
- [ ] LLM usage logged with tokens and cost for every assessment graded
- [ ] Feedback includes quality_score (0-10), strengths (1-5), improvements (1-5), detailed_feedback
- [ ] Students can retry up to 3 times per question

**Premium Gating & Cost Tracking**:
- [ ] Free-tier users blocked from all /api/v2/* endpoints (403 PREMIUM_REQUIRED)
- [ ] Every LLM call creates LLMUsageLog entry (feature, tokens, cost_usd, latency_ms)
- [ ] Average cost per premium user <$0.50/month ($0.25 target with 40% buffer)
- [ ] Admin dashboard shows cost breakdown by feature (GET /api/v2/admin/costs)

**Testing Coverage**:
- [ ] >80% code coverage for Phase 2 modules (pytest --cov)
- [ ] All integration tests passing (premium gating, rate limiting, cost tracking)
- [ ] All E2E workflows passing (adaptive path, assessment, quota enforcement)

---

## Total Task Count: 160

- **Phase 1 (Setup)**: 15 tasks
- **Phase 2 (Foundational)**: 30 tasks
- **Phase 3 (US6 - Adaptive Learning)**: 35 tasks
- **Phase 4 (US7 - LLM Assessments)**: 35 tasks
- **Phase 5 (Cost Tracking & Admin)**: 15 tasks
- **Phase 6 (Testing & Quality)**: 15 tasks
- **Phase 7 (Documentation & Deployment)**: 15 tasks

**Estimated Total Effort**: ~8-10 weeks for 1 full-time developer
- Phase 1: 3-5 days
- Phase 2: 1 week
- Phase 3: 2 weeks
- Phase 4: 2 weeks
- Phase 5: 1 week
- Phase 6: 1.5 weeks
- Phase 7: 1 week

---

**Tasks.md generation complete. Ready for implementation via `/sp.implement` command.**
