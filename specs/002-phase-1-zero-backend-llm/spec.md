# Feature Specification: Phase 1 - Zero-Backend-LLM Course Companion

**Feature Branch**: `002-phase-1-zero-backend-llm`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "Phase 1: Zero-Backend-LLM Course Companion - Build a deterministic backend API and ChatGPT App for delivering course content on Generative AI Fundamentals. Students access content, take quizzes (rule-based grading), track progress, and navigate freemium gating through conversational interface. ZERO backend LLM calls (constitutional requirement). Includes 4 Agent Skills (concept-explainer, quiz-master, socratic-tutor, progress-motivator). Course covers 6 chapters: Introduction to GenAI, LLMs, Prompt Engineering, RAG, Fine-tuning, AI Applications. Free tier: Chapters 1-3. Premium tier: Chapters 4-6. User Stories: US1 (Content Access), US2 (Explanations), US3 (Quizzes), US4 (Progress Tracking), US5 (Freemium Gating). Tech stack: Python 3.11+, FastAPI, PostgreSQL, Redis, Cloudflare R2, ChatGPT Apps SDK. Cost target: <$0.004/user/month."

## User Scenarios & Testing

### User Story 1 - Access Course Content Through Conversational Interface (Priority: P1)

Students interact with the Course Companion through a conversational ChatGPT interface to access course content on Generative AI Fundamentals. Students can request chapters, sections, and navigate through the course material using natural language.

**Why this priority**: This is the foundational capability - without content delivery, there is no educational product. All other features depend on the ability to serve course content.

**Independent Test**: Can be fully tested by having a student request a chapter (e.g., "Show me Chapter 1 on Introduction to Generative AI") and verifying they receive accurate, complete content retrieved from storage.

**Acceptance Scenarios**:

1. **Given** a student starts learning, **When** they request "Show me the first chapter", **Then** they receive Chapter 1 content with all sections and learning objectives
2. **Given** a student is viewing Chapter 1, **When** they request "What's next?", **Then** they receive Chapter 2 content
3. **Given** a student wants specific content, **When** they request "Show me the section on transformer architecture", **Then** they receive the relevant section from Chapter 2
4. **Given** a student searches for content, **When** they request "Find content about RAG", **Then** they receive search results from Chapter 4 with relevant sections highlighted

---

### User Story 2 - Learn Concepts with Personalized Explanations (Priority: P1)

Students request explanations for Generative AI concepts at their comprehension level. The system provides explanations using analogies, examples, and progressive complexity without generating new educational content (all explanations come from pre-authored course materials).

**Why this priority**: Effective learning requires understanding at the right level. Students learn best when explanations match their current knowledge, making this critical for educational effectiveness.

**Independent Test**: Can be fully tested by having students at different levels (beginner, intermediate, advanced) request explanations for the same concept and verifying they receive appropriately-leveled content from pre-authored materials.

**Acceptance Scenarios**:

1. **Given** a beginner student asks "What is a transformer?", **When** the system responds, **Then** they receive a simple analogy-based explanation from the beginner section
2. **Given** an intermediate student asks "What is a transformer?", **When** the system responds, **Then** they receive technical details about architecture from the intermediate section
3. **Given** an advanced student asks "What is a transformer?", **When** the system responds, **Then** they receive formal definitions and research references from the advanced section
4. **Given** a student is confused, **When** they say "I don't understand", **Then** the system provides an alternative explanation at a simpler level

---

### User Story 3 - Take Quizzes with Immediate Feedback (Priority: P1)

Students take quizzes to test their understanding of course material and receive immediate, deterministic grading with explanations for both correct and incorrect answers. All grading is rule-based using pre-defined answer keys.

**Why this priority**: Assessment is essential for learning verification and student motivation. Immediate feedback reinforces learning and helps students identify knowledge gaps quickly.

**Independent Test**: Can be fully tested by having a student complete a quiz (e.g., Chapter 1 quiz with 10 questions), submitting answers, and verifying they receive a deterministic score with explanations for all questions.

**Acceptance Scenarios**:

1. **Given** a student completes Chapter 1, **When** they request "Quiz me on Chapter 1", **Then** they receive 10 questions (5 multiple-choice, 3 true/false, 2 short-answer)
2. **Given** a student submits quiz answers, **When** the system grades them, **Then** they receive a score (e.g., 8/10 = 80%) with pass/fail status (pass ≥ 70%)
3. **Given** a student gets a question wrong, **When** results are shown, **Then** they see the correct answer with an explanation of why their answer was incorrect
4. **Given** a student gets a question right, **When** results are shown, **Then** they see confirmation with reinforcement of the key concept
5. **Given** a student fails a quiz (score < 70%), **When** results are shown, **Then** they receive encouragement and suggestions to review specific sections

---

### User Story 4 - Track Progress and Maintain Learning Streaks (Priority: P1)

Students view their learning progress across chapters, maintain daily learning streaks, and receive milestone celebrations. Progress persists across sessions and devices, motivating continued engagement.

**Why this priority**: Progress tracking and streak gamification are proven motivators for consistent learning habits. Students who see their progress are more likely to complete courses.

**Independent Test**: Can be fully tested by having a student complete activities over multiple days (e.g., Chapter 1 on Day 1, Chapter 2 on Day 2) and verifying progress percentage, streak count, and milestone celebrations are accurate.

**Acceptance Scenarios**:

1. **Given** a student completes Chapter 1, **When** they check progress, **Then** they see "1/6 chapters completed (17%)" with a visual indicator
2. **Given** a student studies on consecutive days, **When** they check their streak, **Then** they see "5-day streak!" with encouragement to continue
3. **Given** a student breaks their streak, **When** they check progress, **Then** they see "Streak ended. Start fresh today!" without negative messaging
4. **Given** a student reaches a milestone (e.g., 3 chapters), **When** progress updates, **Then** they receive a celebration message: "Halfway there! You've mastered the fundamentals."
5. **Given** a student logs in from a different device, **When** they check progress, **Then** they see the same progress and streak as on their original device

---

### User Story 5 - Navigate Freemium Content Gating (Priority: P1)

Free-tier students access Chapters 1-3 without restrictions. When attempting to access premium content (Chapters 4-6), they receive a graceful upgrade prompt explaining the value of premium access without blocking their current learning.

**Why this priority**: Freemium gating enables sustainable monetization while providing value to all users. Clear, respectful communication of premium benefits encourages upgrades without frustrating free users.

**Independent Test**: Can be fully tested by having a free-tier student request Chapter 4 and verifying they receive a polite upgrade message with clear premium benefits, while premium students access Chapter 4 without interruption.

**Acceptance Scenarios**:

1. **Given** a free-tier student requests Chapter 1, 2, or 3, **When** the system responds, **Then** they receive full content access without any upgrade prompts
2. **Given** a free-tier student requests Chapter 4, **When** the system responds, **Then** they receive a message: "Chapter 4 (RAG) is part of our Premium content. Upgrade to unlock advanced topics like RAG, Fine-tuning, and AI Applications."
3. **Given** a premium student requests any chapter (1-6), **When** the system responds, **Then** they receive full content access without any restrictions
4. **Given** a free-tier student asks "What's included in premium?", **When** the system responds, **Then** they receive a list: "Premium includes Chapters 4-6, progress tracking, and personalized learning paths."
5. **Given** a free-tier student upgrades to premium, **When** they request Chapter 4, **Then** they immediately receive full access without delay

---

### Edge Cases

- **What happens when a student requests content that doesn't exist?** System responds: "I don't have a chapter on [topic]. Our course covers: Introduction to GenAI, LLMs, Prompt Engineering, RAG, Fine-tuning, and AI Applications. Which would you like to explore?"

- **How does the system handle concurrent sessions?** If a student is logged in on multiple devices, progress updates are synchronized within 5 seconds across all sessions.

- **What happens when a student's premium subscription expires?** Access to Chapters 4-6 is immediately revoked with a renewal reminder. Previously completed progress on premium chapters remains visible but content becomes inaccessible.

- **How does the system handle ambiguous requests?** If a student's request is unclear (e.g., "Tell me about AI"), the system asks clarifying questions: "Would you like to learn about: (A) Introduction to Generative AI, (B) Large Language Models, or (C) AI Applications?"

- **What happens during backend outages?** ChatGPT displays a cached error message: "I'm temporarily unable to access course content. Please try again in a few minutes. Your progress is safely saved."

- **How does the system handle rapid quiz retakes?** Students can retake quizzes unlimited times. Each attempt is tracked separately with timestamps. Progress reflects the highest score achieved.

- **What happens when course content is updated?** Students always receive the latest version of content. If they're mid-chapter when updates occur, they see updated content on next access with a notification: "This chapter was recently updated with new examples."

## Requirements

### Functional Requirements

**Content Delivery**:
- **FR-001**: System MUST serve 6 chapters of Generative AI Fundamentals course content: (1) Introduction to GenAI, (2) Large Language Models, (3) Prompt Engineering, (4) RAG, (5) Fine-tuning, (6) AI Applications
- **FR-002**: System MUST organize each chapter into sections with learning objectives, estimated reading time, and difficulty level
- **FR-003**: System MUST support navigation commands: "next chapter", "previous chapter", "go to Chapter X", "show table of contents"
- **FR-004**: System MUST provide search functionality across all course content using keyword matching
- **FR-005**: System MUST deliver content retrieved from cloud storage (not generated by backend LLM)

**Agent Skills (Conversational Modes)**:
- **FR-006**: System MUST implement 4 Agent Skills as conversational modes: concept-explainer, quiz-master, socratic-tutor, progress-motivator
- **FR-007**: System MUST activate concept-explainer mode when student requests explanations using keywords: "explain", "what is", "how does", "define"
- **FR-008**: System MUST activate quiz-master mode when student requests quizzes using keywords: "quiz", "test me", "practice", "quiz me on"
- **FR-009**: System MUST activate socratic-tutor mode when student requests guidance using keywords: "help me think", "I'm stuck", "hint", "guide me"
- **FR-010**: System MUST activate progress-motivator mode when student requests progress using keywords: "my progress", "streak", "how am I doing"
- **FR-011**: All Agent Skills MUST use pre-authored content from course materials (no LLM-generated educational content)

**Quiz System**:
- **FR-012**: System MUST provide one quiz per chapter (6 quizzes total) with 10 questions each: 5 multiple-choice, 3 true/false, 2 short-answer
- **FR-013**: System MUST grade quizzes deterministically using pre-defined answer keys (no LLM grading in Phase 1)
- **FR-014**: System MUST calculate quiz scores as percentage correct (e.g., 8/10 = 80%)
- **FR-015**: System MUST apply pass threshold of 70% for quiz completion
- **FR-016**: System MUST provide explanations for both correct and incorrect answers using pre-authored explanations
- **FR-017**: System MUST allow unlimited quiz retakes with each attempt tracked separately
- **FR-018**: System MUST track highest quiz score achieved per chapter for progress calculation

**Progress Tracking**:
- **FR-019**: System MUST track chapter completion percentage (number of chapters completed / 6)
- **FR-020**: System MUST track quiz performance per chapter (highest score achieved)
- **FR-021**: System MUST calculate daily learning streaks based on student activity (any interaction = active day)
- **FR-022**: System MUST persist progress across sessions and devices using user accounts
- **FR-023**: System MUST display progress summary: chapters completed, quiz scores, current streak, total study time
- **FR-024**: System MUST celebrate milestones: 3 chapters completed, 7-day streak, 14-day streak, course completion
- **FR-025**: System MUST be timezone-aware for streak calculations (student's local midnight, not server time)

**Freemium Access Control**:
- **FR-026**: System MUST allow free-tier users to access Chapters 1-3 without restrictions
- **FR-027**: System MUST block free-tier users from accessing Chapters 4-6 with a graceful upgrade prompt
- **FR-028**: System MUST allow premium-tier users to access all 6 chapters without restrictions
- **FR-029**: System MUST verify subscription status on every content request using user authentication
- **FR-030**: System MUST provide clear upgrade messaging explaining premium benefits when free users request premium content

**User Authentication**:
- **FR-031**: System MUST support user registration with email and password
- **FR-032**: System MUST authenticate users and issue session tokens for subsequent requests
- **FR-033**: System MUST associate all progress and quiz data with authenticated user accounts
- **FR-034**: System MUST support password reset via email verification
- **FR-035**: System MUST enforce secure password requirements (minimum 8 characters, mix of letters and numbers)

**Constitutional Requirement**:
- **FR-036**: Backend APIs MUST make ZERO calls to LLM services (OpenAI, Anthropic, etc.) during Phase 1
- **FR-037**: System MUST serve all content, explanations, and quiz feedback from pre-authored materials stored in cloud storage
- **FR-038**: System MUST include automated verification test that detects any LLM API calls and fails if found

**Performance & Scalability**:
- **FR-039**: System MUST respond to content requests within 1 second (p95 latency)
- **FR-040**: System MUST cache frequently accessed content (chapters, quizzes) to reduce storage API calls
- **FR-041**: System MUST support at least 10,000 concurrent student sessions without degradation

### Key Entities

- **Student**: Represents a learner using the course. Attributes: email, password (hashed), subscription tier (free/premium), timezone, registration date, last active timestamp.

- **Chapter**: Represents one of 6 course chapters. Attributes: chapter ID, title, subtitle, sections (list), learning objectives, estimated time, difficulty level, access tier (free/premium).

- **Section**: Represents a subdivision of a chapter. Attributes: section ID, title, content (markdown), estimated time, order within chapter.

- **Quiz**: Represents assessment for a chapter. Attributes: quiz ID, chapter ID, questions (list of 10), answer key, passing score threshold (70%).

- **Question**: Represents a single quiz question. Attributes: question ID, question text, type (multiple-choice/true-false/short-answer), correct answer(s), explanation for correct answer, explanation for common wrong answers.

- **QuizAttempt**: Represents a student's quiz submission. Attributes: attempt ID, student ID, quiz ID, answers submitted, score (percentage), passed (boolean), timestamp, grading details (per-question feedback).

- **ChapterProgress**: Represents a student's progress on a chapter. Attributes: student ID, chapter ID, completion status (not started/in progress/completed), quiz score (highest), time spent, last accessed timestamp.

- **Streak**: Represents a student's learning streak. Attributes: student ID, current streak (days), longest streak (days), last activity date, timezone.

- **Subscription**: Represents a student's subscription. Attributes: student ID, tier (free/premium), start date, expiration date, payment status, upgrade/downgrade history.

## Success Criteria

### Measurable Outcomes

**Content Access**:
- **SC-001**: Students can request and receive any chapter content within 1 second of asking
- **SC-002**: 95% of student requests for specific chapters are understood and fulfilled on first attempt
- **SC-003**: Students can complete reading a full chapter (average 45 minutes) without interruptions or errors

**Quiz Performance**:
- **SC-004**: Students can complete a 10-question quiz and receive graded results within 30 seconds
- **SC-005**: Quiz grading is 100% consistent (same answers always produce same score) across all attempts
- **SC-006**: 90% of students receive helpful explanations for wrong answers that clarify misconceptions

**Progress Tracking**:
- **SC-007**: Student progress syncs across devices within 5 seconds of any activity
- **SC-008**: Streak calculations are accurate across all timezones with 0% error rate
- **SC-009**: 80% of students who see milestone celebrations return to learn the next day

**Freemium Conversion**:
- **SC-010**: Free-tier students can complete Chapters 1-3 without any payment prompts until they request premium content
- **SC-011**: Premium upgrade messaging clearly communicates value without frustrating users (measured by <5% complaint rate)
- **SC-012**: 10% of free-tier students who see upgrade prompts convert to premium within 7 days

**System Performance**:
- **SC-013**: System handles 10,000 concurrent students with <100ms API response time (p95)
- **SC-014**: System achieves 99.9% uptime (less than 43 minutes downtime per month)
- **SC-015**: Infrastructure costs remain below $0.004 per student per month (target: $40/month for 10,000 students)

**Constitutional Compliance**:
- **SC-016**: Automated test verifies ZERO LLM API calls in backend throughout all Phase 1 operations
- **SC-017**: 100% of educational content, explanations, and quiz feedback comes from pre-authored course materials

**User Experience**:
- **SC-018**: 85% of students successfully navigate to their desired chapter on first conversational request
- **SC-019**: Students complete account registration and access first chapter within 5 minutes of starting
- **SC-020**: 90% of students report the conversational interface feels natural and helpful (post-usage survey)

## Assumptions

1. **Content Pre-Authoring**: All course content (6 chapters, quizzes, explanations) will be authored by subject matter experts before implementation begins and stored in cloud storage (Cloudflare R2).

2. **ChatGPT App Platform**: OpenAI's ChatGPT Apps platform is stable and supports the required actions (API calls to our backend) without significant limitations.

3. **Student Intent Recognition**: ChatGPT's natural language understanding is sufficient to recognize student requests and route them to appropriate Agent Skills without custom NLP models.

4. **Authentication Integration**: ChatGPT Apps platform supports OAuth 2.0 or similar authentication mechanisms to link ChatGPT users with our backend user accounts.

5. **Storage Reliability**: Cloud storage (Cloudflare R2) provides reliable content delivery with acceptable latency (<500ms) for serving course materials.

6. **Subscription Management**: Students can upgrade from free to premium tier via an external payment system (e.g., Stripe) that integrates with our backend.

7. **Device Synchronization**: Students use persistent accounts (not anonymous sessions), enabling progress synchronization across devices.

8. **Timezone Detection**: System can reliably detect or allow students to set their timezone for accurate streak calculations.

9. **Content Stability**: Course content updates are infrequent (monthly or less), minimizing cache invalidation complexity.

10. **No Offline Support**: Phase 1 requires internet connectivity; no offline learning capabilities are provided.

## Out of Scope (Phase 1)

The following features are explicitly excluded from Phase 1 and reserved for future phases:

- **LLM-Generated Content**: No adaptive learning paths, personalized recommendations, or LLM-graded open-ended assessments (Phase 2)
- **Web Application**: No standalone web UI; Phase 1 focuses exclusively on ChatGPT App interface (Phase 3)
- **Community Features**: No student forums, discussion boards, or peer interactions (Future)
- **Advanced Analytics**: No detailed learning analytics dashboard, only basic progress metrics (Future)
- **Mobile Apps**: No native iOS/Android apps; ChatGPT App serves as mobile interface (Future)
- **Multi-Language Support**: Course content is English-only in Phase 1 (Future)
- **Instructor Tools**: No content authoring tools, course management, or instructor analytics (Future)
- **Certificates**: No completion certificates or credentials issued (Future)
- **Third-Party Integrations**: No LMS integrations (Canvas, Moodle, etc.) in Phase 1 (Future)

## Dependencies

**External Systems**:
- **Cloudflare R2**: Cloud object storage for course content (chapters, quizzes, media)
- **PostgreSQL Database**: Relational database for user data, progress, quiz attempts, subscriptions
- **Redis Cache**: In-memory cache for frequently accessed content and session data
- **OpenAI ChatGPT Apps**: Platform for conversational interface and natural language interaction
- **Email Service**: Transactional email provider for account verification and password resets (e.g., SendGrid, AWS SES)

**Pre-Implementation Requirements**:
- Course content must be authored and stored in R2 before development begins
- ChatGPT App manifest and system prompts must be defined
- Database schema must be designed based on key entities
- API contracts (OpenAPI specification) must be documented

## Open Questions

*Note: Maximum 3 [NEEDS CLARIFICATION] markers allowed. Making informed assumptions for all other aspects.*

1. **Subscription Payment Integration**: How will students upgrade from free to premium tier?
   - **Assumption**: Integration with payment provider (Stripe/PayPal) will be handled via a separate payment service that updates subscription status in our database. Phase 1 focuses on subscription verification, not payment processing itself.

2. **Email Verification Requirement**: Should students verify their email before accessing content?
   - **Assumption**: Email verification is required for account security but won't block immediate content access to free chapters. Students can start learning immediately after registration, with verification email sent in background.

3. **Session Timeout Policy**: How long should student sessions remain active before re-authentication?
   - **Assumption**: Sessions remain active for 30 days of inactivity, balancing security and user convenience. Students are automatically logged out after 30 days and must re-authenticate.

## Risks & Mitigations

**Risk 1: ChatGPT Platform Limitations**
- **Impact**: If ChatGPT Apps platform restricts API calls or rate limits, content delivery could be degraded
- **Mitigation**: Design backend APIs to be platform-agnostic (standard REST), enabling future migration to web app (Phase 3) if needed. Monitor OpenAI platform announcements closely.

**Risk 2: Content Authoring Delays**
- **Impact**: If course content is not ready when implementation begins, development will be blocked
- **Mitigation**: Begin content authoring in parallel with specification phase. Use placeholder content for initial development and testing.

**Risk 3: Zero-LLM Verification Complexity**
- **Impact**: Ensuring absolutely ZERO LLM calls requires careful testing and monitoring
- **Mitigation**: Implement automated test that mocks LLM endpoints and fails if any calls are detected. Include this test in CI/CD pipeline as a blocking check.

**Risk 4: Freemium Conversion Rate**
- **Impact**: If free-to-premium conversion is too low, business model may not be sustainable
- **Mitigation**: Design upgrade messaging carefully with user testing. Track conversion metrics from day 1. Adjust messaging based on data. Phase 1 focuses on delivering value to free users first.

**Risk 5: Progress Synchronization Delays**
- **Impact**: If progress doesn't sync quickly across devices, students may see stale data causing confusion
- **Mitigation**: Use Redis for real-time progress caching. Implement optimistic updates (show progress immediately, sync to database asynchronously). Test cross-device scenarios thoroughly.

---

**This specification is ready for planning phase via `/sp.plan`.**
