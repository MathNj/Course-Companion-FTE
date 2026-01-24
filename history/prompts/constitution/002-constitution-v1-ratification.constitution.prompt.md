---
id: 002
title: Constitution v1.0.0 Ratification - Course Companion FTE
stage: constitution
date: 2026-01-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: constitution
branch: master
user: MathNj
command: create proper constitution
labels: ["constitution", "ratification", "v1.0.0", "governance", "principles"]
links:
  spec: specs/001-course-companion-fte/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md (521 insertions, 38 deletions)
tests:
  - Constitutional compliance verified for all 3 phases
  - 10 gates verified in planning artifacts
---

## Prompt

**Initial Context**: User asked to review proposed constitutional updates that suggested changing the course topic from "Generative AI Fundamentals" to "AI Agent Development", which would have contradicted the entire project specification.

**User Request 1**: "Read @Course-Companion and recommend should i add following updates in the constitution [proposed updates that changed course topic to Option A - AI Agent Development]"

**Assistant Response**: After reading planning artifacts, identified that the proposed update was WRONG and would contradict the specification. Recommended NOT adding those updates. Explained that:
- Project is correctly specified as "Generative AI Fundamentals" course (Option C)
- Agent Factory Architecture is the implementation approach, not the course topic
- No conflict exists between teaching GenAI fundamentals and using agent patterns to build the tutor

**User Request 2**: "create a proper constitution that accurately reflects your Course Companion FTE project as currently specified"

## Response snapshot

Created comprehensive constitution (539 lines) that accurately reflects the Course Companion FTE project with:

**Domain Scope Clarity**:
- Course Topic: Generative AI Fundamentals (6 chapters: Intro to GenAI, LLMs, Prompt Engineering, RAG, Fine-tuning, AI Applications)
- Implementation Approach: Agent Factory Architecture (Zero-Backend-LLM, Agent Skills, MCP integration)
- Delivery Method: Dual-frontend (ChatGPT App + Web App)

**10 Constitutional Gates** (All Mandatory):

I. **Zero-Backend-LLM First (Phase 1)** - NON-NEGOTIABLE
   - Backend makes ZERO LLM calls
   - Automated test verifies no LLM API calls
   - Disqualification risk if violated

II. **Cost Efficiency & Scalability**
   - Phase 1: <$0.004/user/month
   - Phase 2: <$0.50/premium-user/month
   - Phase 3: $0-15/month total infrastructure

III. **Spec-Driven Development (SDD) Workflow**
   - Spec → Plan → Tasks → Implement
   - Full traceability (requirements → tasks → tests)
   - Prompt History Records for all planning sessions

IV. **Hybrid Intelligence Isolation**
   - v1 APIs (deterministic) vs v2 APIs (LLM-powered)
   - No cross-contamination
   - CRITICAL blocking test (test_phase_isolation.py)

V. **Educational Delivery Excellence**
   - 4 mandatory Agent Skills (concept-explainer, quiz-master, socratic-tutor, progress-motivator)
   - 99%+ consistency, 70%+ quiz pass rate, 4+/5 satisfaction
   - Content served verbatim (no hallucination)

VI. **Agent Skills & MCP Integration**
   - All 4 SKILL.md files with complete 5-section structure
   - Backend API integration documented
   - MCP for database, filesystem, external API access

VII. **Security & Secrets Management**
   - Zero hardcoded secrets
   - Environment variables only (.env local, platform secrets production)
   - Rate limiting, OAuth 2.0, JWT authentication

VIII. **Testing & Quality Gates**
   - >80% coverage target
   - Critical blocking tests (Zero-LLM verification, Phase isolation)
   - Backend (pytest), Frontend (Jest + Playwright), E2E, Accessibility (WCAG 2.1 AA)

IX. **Technology Stack Constraints**
   - Backend: Python 3.11+, FastAPI 0.104+, SQLAlchemy 2.0+, PostgreSQL, Redis
   - Frontend: Next.js 14+, TypeScript 5.3+, React 18+, TailwindCSS, shadcn/ui
   - LLM: Claude Sonnet 4.5 (Phase 2 only)

X. **Development Workflow**
   - Feature branches per phase
   - Commit standards (conventional commits)
   - PHR creation after significant AI interactions
   - Constitutional compliance checklist in PRs

**Business Model**:
- Free: Chapters 1-3, basic quizzes
- Premium ($9.99/mo): All 6 chapters
- Pro ($19.99/mo): Premium + Adaptive Learning + LLM Assessments

**Additional Sections**:
- Quality Standards (linting, type checking, formatting, docstrings)
- Performance Standards (API latency, web app load times, database query timeouts)
- Governance (amendment process, compliance enforcement, conflict resolution)

**Committed**: git commit c2a2950 with comprehensive commit message documenting all 10 gates.

## Outcome

- ✅ Impact: Authoritative constitution ratified (v1.0.0) that accurately codifies all planning decisions into enforceable principles
- 🧪 Tests: All 10 constitutional gates verified against existing planning artifacts (Phases 1, 2, 3)
- 📁 Files: 1 file changed (.specify/memory/constitution.md: 521 insertions, 38 deletions - template → full constitution)
- 🔁 Next prompts: Begin Phase 1 implementation following constitution and planning artifacts, or create ADR documenting constitutional principles
- 🧠 Reflection: Successfully prevented incorrect constitutional update that would have contradicted project scope. Constitution now provides clear separation: course topic (GenAI Fundamentals) vs implementation approach (Agent Factory Architecture).

## Evaluation notes (flywheel)

- Failure modes observed: None. User initially received external advice suggesting wrong course topic change, but assistant correctly identified contradiction and proposed accurate constitution.
- Graders run and results (PASS/FAIL): PASS - All 10 constitutional gates align with planning artifacts. No ambiguity between course topic (what's taught) and implementation approach (how it's built).
- Prompt variant (if applicable): N/A - Standard constitution creation workflow
- Next experiment (smallest change to try): Monitor constitutional compliance during Phase 1 implementation. Verify Zero-LLM gate is enforced via automated testing as specified.

## Key Decision Rationale

**Why This Constitution is Correct**:

The constitution accurately reflects the project as specified in all planning artifacts:

1. **Course Topic = Generative AI Fundamentals** (from spec.md, plan.md, PLANNING-COMPLETE.md)
   - 6 chapters explicitly teaching GenAI concepts
   - FR-001: "System MUST serve all 6 chapters of Generative AI Fundamentals course content"
   - User stories describe learning GenAI, not building agents

2. **Implementation Approach = Agent Factory Architecture** (technical detail)
   - Zero-Backend-LLM principle (Phase 1 backend makes ZERO LLM calls)
   - 4 Agent Skills for educational delivery
   - MCP integration for tool access
   - ChatGPT Apps SDK for conversational frontend

3. **No Conflict Exists**:
   - Teaching GenAI ≠ Building an agent-based educational system
   - Analogy: A video player (implementation) can play a cooking tutorial (content)
   - The course teaches students about LLMs, RAG, fine-tuning
   - The tutor uses agents to deliver that education effectively

**Constitutional Principles Established**:
- Zero-Backend-LLM as NON-NEGOTIABLE (disqualification risk)
- Cost discipline (<$0.004/user Phase 1)
- Phase isolation (v1 deterministic, v2 hybrid)
- Educational excellence (4 Agent Skills, 99%+ consistency)
- Spec-Driven Development workflow
- Complete governance and amendment process

**Version**: 1.0.0 (Initial Ratification)
**Status**: Active - Committed to master (c2a2950)
**Supersedes**: Template constitution (placeholder version)

This constitution serves as the authoritative source of truth for all development decisions going forward.
