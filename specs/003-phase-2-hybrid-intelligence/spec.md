# Feature Specification: Phase 2 - Hybrid Intelligence Course Companion

**Feature Branch**: `003-phase-2-hybrid-intelligence`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "Phase 2: Hybrid Intelligence Course Companion - Add LLM-powered premium features to existing Phase 1 system. Premium users receive adaptive learning paths personalized based on quiz performance and time spent (pattern analysis + Claude Sonnet prompting). Premium users submit open-ended answers for LLM-graded assessments with detailed feedback on reasoning quality. Phase 2 features are premium-gated and isolated in /api/v2/* endpoints (separate from Phase 1's deterministic /api/v1/* endpoints). User Stories: US6 (Adaptive Learning Path), US7 (LLM Assessments). Constitutional requirements: Hybrid intelligence isolated from deterministic features, cost tracking per LLM call, premium gating enforced. Tech stack: Claude Sonnet 4.5 (Anthropic API), same backend as Phase 1 (FastAPI, PostgreSQL, Redis). Cost target: <$0.50/premium-user/month for LLM usage."

**Prerequisites**: Phase 1 (Zero-Backend-LLM) must be fully implemented and operational before Phase 2 development begins.

## User Scenarios & Testing

### User Story 6 - Receive Personalized Adaptive Learning Paths (Priority: P2)

Premium-tier students receive personalized learning recommendations based on their performance patterns, quiz scores, and time spent on chapters. The system analyzes their learning data and generates targeted suggestions for improvement using intelligent analysis.

**Why this priority**: Personalization significantly improves learning outcomes by addressing individual knowledge gaps. This is a premium differentiator that justifies subscription value. Priority P2 because Phase 1's core content delivery must work first.

**Independent Test**: Can be fully tested by having a premium student complete several chapters and quizzes with varied performance (e.g., high scores on Chapters 1-2, low score on Chapter 3), then requesting recommendations and verifying they receive a personalized learning path addressing their weak areas.

**Acceptance Scenarios**:

1. **Given** a premium student has completed 3 chapters with quiz scores of 90%, 85%, and 55%, **When** they request "What should I focus on?", **Then** they receive a personalized learning path highlighting Chapter 3 concepts with specific section recommendations
2. **Given** a premium student spent 2x average time on RAG concepts, **When** they request recommendations, **Then** the system suggests reviewing prerequisite concepts (embeddings, vector databases) before continuing
3. **Given** a premium student has skipped Chapter 4, **When** they request a learning path, **Then** the system recommends completing Chapter 4 before moving to Chapter 5 (which depends on RAG understanding)
4. **Given** a premium student asks "Why am I struggling with fine-tuning?", **When** the system analyzes their data, **Then** they receive insights like "Your quiz scores show weak understanding of LLM training fundamentals from Chapter 2. Reviewing that chapter will help."
5. **Given** a free-tier student requests adaptive recommendations, **When** the system responds, **Then** they receive an upgrade prompt: "Personalized learning paths are available with Premium. Upgrade to get AI-powered recommendations tailored to your progress."

---

### User Story 7 - Receive LLM-Graded Assessments with Detailed Feedback (Priority: P2)

Premium-tier students submit open-ended written answers to assessment questions and receive detailed, intelligent feedback evaluating their reasoning quality, depth of understanding, and areas for improvement. This goes beyond simple right/wrong grading to assess comprehension quality.

**Why this priority**: Open-ended assessments measure deeper understanding than multiple-choice quizzes. Detailed feedback accelerates learning by pinpointing specific misconceptions. This is a high-value premium feature. Priority P2 because basic quiz functionality (Phase 1) must exist first.

**Independent Test**: Can be fully tested by having a premium student submit a written answer to an open-ended question (e.g., "Explain when to use RAG vs fine-tuning"), receiving detailed feedback with a quality score, specific strengths identified, and areas for improvement highlighted.

**Acceptance Scenarios**:

1. **Given** a premium student answers "Explain when to use RAG vs fine-tuning", **When** they submit their response, **Then** they receive a quality score (e.g., 7.5/10), strengths identified ("Good understanding of cost tradeoffs"), and improvement areas ("Missing explanation of data privacy considerations")
2. **Given** a premium student submits a superficial answer, **When** grading completes, **Then** they receive feedback: "Your answer covers the basics but lacks depth. Consider discussing: (1) knowledge freshness requirements, (2) data sensitivity, (3) computational costs"
3. **Given** a premium student submits an excellent answer, **When** grading completes, **Then** they receive positive reinforcement: "Excellent analysis! You demonstrated strong understanding of tradeoffs and real-world constraints. Your discussion of cost-benefit analysis shows practical thinking."
4. **Given** a premium student submits an answer with misconceptions, **When** grading completes, **Then** they receive corrective feedback: "You stated that fine-tuning is always better for specialized tasks, but this overlooks RAG's advantages for frequently changing information. Review Chapter 4, Section 3."
5. **Given** a free-tier student attempts to submit an open-ended answer, **When** the system responds, **Then** they receive an upgrade prompt: "Detailed AI feedback on your answers is a Premium feature. Upgrade to receive personalized feedback that deepens your understanding."

---

### Edge Cases

- **What happens when LLM service is temporarily unavailable?** System responds: "I'm currently unable to generate personalized recommendations. Your progress is saved, and you can continue learning with standard content. Try again in a few minutes for adaptive guidance."

- **How does the system handle premium users who downgrade mid-course?** Previously generated adaptive paths remain visible in read-only mode, but new recommendations require re-subscribing to premium. LLM assessment feedback history is preserved.

- **What happens if a student requests recommendations with insufficient data?** System responds: "I need more learning data to provide meaningful recommendations. Complete at least 2 quizzes first, then I can analyze your performance patterns and suggest a personalized path."

- **How does the system handle abusive or nonsensical open-ended answers?** LLM grader detects off-topic or invalid submissions and responds: "Your answer doesn't address the question. Please provide a thoughtful response about [topic]. Review Chapter X if you need a refresher."

- **What happens when LLM costs exceed budget thresholds?** System implements rate limiting: Premium users get up to 10 adaptive path requests and 20 LLM assessments per month. Exceeding limits shows: "You've used your monthly allocation. Additional requests available next month or upgrade to Pro tier for unlimited access."

- **How does the system ensure LLM feedback quality is consistent?** All LLM prompts include rubrics and examples. System monitors feedback quality and flags anomalies (e.g., scores that don't match content quality) for manual review.

## Requirements

### Functional Requirements

**Adaptive Learning Path (US6)**:
- **FR-001**: System MUST analyze student performance patterns including quiz scores, time spent per chapter, skipped sections, and retry attempts
- **FR-002**: System MUST identify weak areas defined as chapters with quiz scores below 60% or time spent exceeding 1.5x average
- **FR-003**: System MUST generate personalized learning recommendations addressing specific knowledge gaps
- **FR-004**: System MUST provide reasoning for each recommendation explaining why specific content is suggested
- **FR-005**: System MUST suggest prerequisite review when students struggle with advanced topics requiring foundational knowledge
- **FR-006**: System MUST limit adaptive path generation to premium-tier students only
- **FR-007**: System MUST generate adaptive paths within 5 seconds of request
- **FR-008**: System MUST present recommendations in priority order (highest impact first)

**LLM Assessments (US7)**:
- **FR-009**: System MUST provide open-ended assessment questions for each chapter (2-3 questions per chapter)
- **FR-010**: System MUST accept student written answers of 50-500 words for open-ended questions
- **FR-011**: System MUST evaluate answer quality using intelligent analysis with scoring rubrics
- **FR-012**: System MUST provide quality scores on a 0-10 scale with explanations
- **FR-013**: System MUST identify specific strengths in student answers (e.g., "Strong explanation of cost tradeoffs")
- **FR-014**: System MUST identify specific areas for improvement (e.g., "Missing discussion of data privacy considerations")
- **FR-015**: System MUST provide constructive feedback that guides students toward better understanding
- **FR-016**: System MUST detect and handle off-topic, nonsensical, or abusive submissions appropriately
- **FR-017**: System MUST limit LLM assessments to premium-tier students only
- **FR-018**: System MUST complete grading and return feedback within 10 seconds

**Premium Gating & Access Control**:
- **FR-019**: System MUST verify premium subscription status before processing any Phase 2 requests
- **FR-020**: System MUST block free-tier users from Phase 2 features with clear upgrade messaging
- **FR-021**: System MUST gracefully degrade when premium subscriptions expire (preserve history, block new requests)
- **FR-022**: System MUST track premium feature usage per student (adaptive paths generated, assessments graded)
- **FR-023**: System MUST enforce rate limits on premium features to control costs (10 paths/month, 20 assessments/month per premium user)

**Cost Tracking & Management**:
- **FR-024**: System MUST log every LLM API call with token count, cost, student ID, and timestamp
- **FR-025**: System MUST calculate per-student LLM costs aggregated monthly
- **FR-026**: System MUST alert administrators when per-student costs exceed $0.50/month threshold
- **FR-027**: System MUST display cost metrics in admin dashboard (total monthly spend, per-student average, feature breakdown)
- **FR-028**: System MUST track cost by feature (adaptive paths vs assessments) for optimization decisions

**Architectural Isolation (Constitutional)**:
- **FR-029**: Phase 2 features MUST use separate API endpoints (/api/v2/*) isolated from Phase 1 deterministic endpoints (/api/v1/*)
- **FR-030**: System MUST NOT allow Phase 2 LLM logic to contaminate Phase 1 deterministic code paths
- **FR-031**: System MUST maintain clear separation in codebase (separate modules, services, routers)
- **FR-032**: System MUST include automated tests verifying Phase 1 endpoints remain LLM-free even after Phase 2 deployment

**Data Privacy & Security**:
- **FR-033**: System MUST NOT send personally identifiable information (PII) to LLM services beyond necessary context
- **FR-034**: System MUST anonymize or pseudonymize student data in LLM prompts where possible
- **FR-035**: System MUST log all data sent to external LLM services for audit purposes
- **FR-036**: System MUST comply with data retention policies (delete LLM request/response logs after 90 days)

**Performance & Scalability**:
- **FR-037**: System MUST handle at least 100 concurrent premium students using Phase 2 features without degradation
- **FR-038**: System MUST cache adaptive path results for 24 hours (regenerate only if new performance data exists)
- **FR-039**: System MUST implement request queuing for LLM calls to handle bursts (max queue depth: 50 requests)
- **FR-040**: System MUST provide real-time status updates for long-running LLM operations (e.g., "Analyzing your learning patterns...")

### Key Entities

- **AdaptivePath**: Represents a personalized learning recommendation. Attributes: path ID, student ID, generation timestamp, recommendations (list), reasoning (explanations), validity period (24 hours), cost (tokens/dollars).

- **Recommendation**: Represents a single suggested learning action. Attributes: chapter ID, section ID, priority (1-5), reason (why suggested), estimated impact (high/medium/low), estimated time.

- **OpenEndedQuestion**: Represents an assessment question. Attributes: question ID, chapter ID, question text, evaluation rubric (criteria), example excellent answer, example poor answer.

- **AssessmentSubmission**: Represents a student's written answer. Attributes: submission ID, student ID, question ID, answer text (50-500 words), submission timestamp, grading status (pending/completed).

- **AssessmentFeedback**: Represents LLM-generated feedback. Attributes: feedback ID, submission ID, quality score (0-10), strengths (list of specific points), improvements (list of specific suggestions), detailed feedback (paragraph), generation timestamp, cost (tokens/dollars).

- **LLMUsageLog**: Represents a single LLM API call. Attributes: log ID, student ID, feature (adaptive-path/assessment), request timestamp, tokens used (input + output), cost (dollars), latency (milliseconds), success status.

- **PremiumUsageQuota**: Represents usage limits per premium student. Attributes: student ID, month, adaptive paths used, adaptive paths limit (10), assessments used, assessments limit (20), reset date.

### Success Criteria

### Measurable Outcomes

**Adaptive Learning Effectiveness**:
- **SC-001**: Students who follow adaptive path recommendations improve quiz scores by average of 15 percentage points on retry attempts
- **SC-002**: 80% of premium students who receive adaptive paths report finding recommendations helpful (post-usage survey)
- **SC-003**: Students complete adaptive learning path suggestions within 7 days of generation in 70% of cases

**LLM Assessment Quality**:
- **SC-004**: LLM-graded assessments correlate with human expert grades within ±1 point (on 0-10 scale) in 90% of cases
- **SC-005**: Students who receive detailed LLM feedback demonstrate improved answer quality on subsequent attempts (measured by score increase)
- **SC-006**: 85% of premium students report LLM feedback is specific and actionable (post-usage survey)

**Premium Feature Adoption**:
- **SC-007**: 40% of premium students use adaptive learning path feature within first 30 days of subscription
- **SC-008**: 60% of premium students submit at least one open-ended assessment per month
- **SC-009**: Premium conversion rate increases by 25% after Phase 2 launch (compared to Phase 1 baseline)

**Cost Management**:
- **SC-010**: Average LLM cost per premium student remains below $0.50/month (target: $0.32/month)
- **SC-011**: Adaptive path generation costs average $0.018 per request (1,800 tokens at Claude Sonnet pricing)
- **SC-012**: LLM assessment grading costs average $0.014 per submission (1,400 tokens at Claude Sonnet pricing)
- **SC-013**: 95% of premium students stay within monthly usage quotas (10 paths, 20 assessments)

**System Performance**:
- **SC-014**: Adaptive paths generate within 5 seconds in 95% of requests (p95 latency)
- **SC-015**: LLM assessments return feedback within 10 seconds in 95% of requests (p95 latency)
- **SC-016**: System maintains 99.5% uptime for Phase 2 features (allowing 3.6 hours downtime per month)

**Constitutional Compliance**:
- **SC-017**: Phase 1 deterministic endpoints (/api/v1/*) remain 100% LLM-free after Phase 2 deployment (verified by automated tests)
- **SC-018**: Phase 2 endpoints (/api/v2/*) are completely isolated from Phase 1 code paths (verified by code structure analysis)
- **SC-019**: All LLM API calls are logged with complete cost tracking (100% audit coverage)

**Security & Privacy**:
- **SC-020**: Zero incidents of PII leakage to LLM services (verified by audit logs)
- **SC-021**: All LLM request/response logs are deleted after 90-day retention period (100% compliance)

## Assumptions

1. **Phase 1 Completion**: Phase 1 (Zero-Backend-LLM) is fully implemented, tested, and operational in production before Phase 2 development begins. All Phase 1 endpoints, user data, and progress tracking are working correctly.

2. **Premium Subscription System**: A premium subscription management system exists (from Phase 1 or separate implementation) that can verify student subscription status and tier levels.

3. **LLM Service Reliability**: Claude Sonnet 4.5 (Anthropic API) provides consistent availability (99.9% SLA) with predictable latency (<5 seconds p95) and stable pricing (~$3 per million input tokens, ~$15 per million output tokens).

4. **Sufficient Learning Data**: Premium students have completed at least 2-3 chapters and quizzes before requesting adaptive paths, providing enough performance data for meaningful analysis.

5. **Content Rubrics Available**: Open-ended assessment questions include evaluation rubrics and example answers (excellent/poor) for consistent LLM grading.

6. **Cost Tolerance**: Business model supports LLM costs of up to $0.50 per premium student per month while maintaining profitability at premium tier pricing (assumed $9.99-19.99/month).

7. **Rate Limit Acceptance**: Premium students accept reasonable monthly usage limits (10 adaptive paths, 20 assessments) as sufficient for effective learning without feeling restricted.

8. **English Language Only**: All adaptive path generation and LLM assessments operate in English. Non-English submissions are out of scope for Phase 2.

9. **No Real-Time Streaming**: LLM responses are delivered as complete results (not streamed token-by-token) to simplify implementation and error handling.

10. **Admin Oversight**: Human administrators monitor LLM cost metrics and usage patterns to detect anomalies, adjust rate limits, and optimize prompts for cost efficiency.

## Out of Scope (Phase 2)

The following features are explicitly excluded from Phase 2:

- **Web Application UI**: Phase 2 continues using ChatGPT App as primary interface. Standalone web UI is Phase 3 (Future)
- **Advanced Analytics Dashboard**: No detailed learning analytics beyond basic usage metrics. Comprehensive analytics are Phase 3+ (Future)
- **Multi-Language Support**: LLM features are English-only. Localization is Future
- **Voice/Audio Assessments**: Only text-based open-ended answers supported. Voice submissions are Future
- **Peer Review**: No peer-to-peer assessment or collaborative learning features (Future)
- **Custom Rubrics**: LLM assessment rubrics are pre-defined by course authors. Students cannot create custom evaluation criteria (Future)
- **Real-Time Tutoring**: No synchronous chat-based tutoring with LLM. Features are asynchronous (request → wait → response) (Future)
- **Content Generation**: LLM does not generate new course content, only analyzes student performance and grades submissions (content generation is out of scope per constitutional principles)
- **Instructor Tools**: No features for instructors to review LLM feedback or override grades (Future)

## Dependencies

**External Systems**:
- **Anthropic API (Claude Sonnet 4.5)**: LLM service for adaptive path generation and assessment grading
- **Phase 1 Infrastructure**: All Phase 1 systems must be operational (backend APIs, database, authentication, content storage, ChatGPT App)
- **PostgreSQL Database**: Extended schema for Phase 2 entities (AdaptivePath, AssessmentSubmission, LLMUsageLog, etc.)
- **Redis Cache**: Caching layer for adaptive path results and rate limiting
- **Admin Monitoring Tools**: Dashboard for viewing LLM cost metrics and usage patterns

**Pre-Implementation Requirements**:
- Open-ended assessment questions must be authored with evaluation rubrics
- LLM prompt templates must be designed and tested for consistent output quality
- Cost monitoring infrastructure must be in place before Phase 2 launch
- Premium subscription verification must be fully functional
- API contract documentation for /api/v2/* endpoints

## Open Questions

*Note: Making informed assumptions for all aspects to avoid [NEEDS CLARIFICATION] markers.*

1. **LLM Assessment Retries**: Can students re-submit open-ended answers multiple times?
   - **Assumption**: Yes, students can re-submit up to 3 times per question. Each submission counts against monthly quota (20 assessments/month). This encourages learning through iteration while controlling costs.

2. **Adaptive Path Regeneration Frequency**: How often can students request updated adaptive paths?
   - **Assumption**: Adaptive paths are cached for 24 hours. Students can request new paths after 24 hours or when significant new performance data exists (e.g., completing new quiz). This balances freshness with cost control.

3. **Data Retention for LLM Logs**: How long should detailed LLM request/response logs be retained?
   - **Assumption**: 90 days for audit and quality monitoring purposes, then automatically deleted for privacy compliance. Aggregated cost metrics (without full request/response) are retained indefinitely for business analytics.

## Risks & Mitigations

**Risk 1: LLM Cost Overruns**
- **Impact**: If usage exceeds projections, LLM costs could erode profitability (target: <$0.50/premium-user/month)
- **Mitigation**: Implement strict rate limits (10 paths, 20 assessments per premium user per month). Monitor costs daily. Adjust limits or pricing if costs exceed thresholds. Consider introducing Pro tier ($19.99/month) with higher limits if demand exists.

**Risk 2: LLM Service Degradation**
- **Impact**: If Anthropic API experiences outages or high latency, Phase 2 features become unusable, frustrating premium users
- **Mitigation**: Implement graceful degradation (show cached results if available). Queue requests during outages with clear status messaging. Design Phase 1 features to remain fully functional independently of Phase 2. Consider fallback to simpler rule-based recommendations if LLM unavailable.

**Risk 3: Inconsistent LLM Feedback Quality**
- **Impact**: If LLM grading is inconsistent or provides unhelpful feedback, students lose trust in premium features
- **Mitigation**: Use detailed prompts with rubrics and examples. Implement automated quality checks (e.g., flag scores that don't match feedback sentiment). Sample 10% of submissions for human review to validate quality. Iterate on prompts based on quality metrics.

**Risk 4: Phase 1/2 Code Contamination**
- **Impact**: If Phase 2 LLM logic leaks into Phase 1 deterministic endpoints, constitutional requirement is violated
- **Mitigation**: Enforce strict architectural separation (/api/v1/* vs /api/v2/* routers). Implement automated tests that fail if Phase 1 endpoints call LLM services. Code review checklist includes "Phase 1/2 isolation verified." Use separate service modules with clear boundaries.

**Risk 5: Premium Conversion Disappointment**
- **Impact**: If Phase 2 features don't significantly boost premium conversion, ROI on development effort is low
- **Mitigation**: Validate feature value through user research before full implementation. A/B test premium messaging highlighting Phase 2 benefits. Track conversion metrics closely post-launch. Be prepared to iterate on features or pricing based on data. Consider limited free trial of Phase 2 features to demonstrate value.

---

**This specification is ready for planning phase via `/sp.plan`.**
