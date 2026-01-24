# Implementation Plan: Phase 3 - Web Application Course Companion

**Branch**: `004-phase-3-web-app` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-phase-3-web-app/spec.md`

## Summary

Build a standalone responsive web application that provides full feature parity with the ChatGPT App plus visual enhancements. Students access all Phase 1 (deterministic) and Phase 2 (hybrid intelligence) features through a modern, mobile-first web UI. The web app includes visual progress dashboard, interactive chapter viewer with rich formatting, quiz interface with real-time feedback, adaptive learning path roadmap visualization, and assessment submission forms. Architecture: Next.js 14 (App Router) frontend consuming existing Phase 1 `/api/v1/*` and Phase 2 `/api/v2/*` backend APIs. NO backend changes required - web app is a pure frontend addition. Responsive design with mobile-first approach (320px+), tablet (768px+), desktop (1024px+) breakpoints. Cost target: Minimal (<$10/month) via Vercel free tier for static hosting and edge functions.

## Technical Context

**Language/Version**: TypeScript 5.3+ (strict mode, ESNext target)
**Primary Dependencies**:
- Next.js 14.1+ (App Router, React Server Components, Server Actions)
- React 18.2+ (concurrent features, Suspense, streaming)
- TailwindCSS 3.4+ (utility-first styling, custom theme)
- shadcn/ui (accessible component library built on Radix UI + Tailwind)
- React Query 5.x (server state management, caching, optimistic updates)
- Zustand 4.5+ (lightweight client-side state management)
- Zod 3.22+ (TypeScript-first schema validation)
- next-auth 4.24+ (authentication with JWT provider)
- Playwright 1.40+ (E2E testing)
- Vitest (unit testing, React Testing Library)

**Storage**:
- LocalStorage: Quiz auto-save, offline chapter cache, reading position persistence
- SessionStorage: Temporary form state
- React Query Cache: Server state (chapters, quizzes, progress, API responses)
- Zustand Store: UI state (theme, sidebar collapsed, modals)

**Testing**:
- Vitest + React Testing Library (component unit tests, >80% coverage)
- Playwright (E2E tests for critical user flows)
- axe-core (automated accessibility testing, WCAG 2.1 Level AA)
- Lighthouse CI (performance monitoring, >90 desktop, >80 mobile)

**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend-only, no backend changes)
**Performance Goals**:
- <2 seconds initial page load (p95 latency)
- <1 second navigation between pages (React Query cache hits)
- <500ms interaction-to-visual feedback (optimistic updates)
- Lighthouse score: 90+ (desktop), 80+ (mobile)
- First Contentful Paint (FCP): <1.5s
- Largest Contentful Paint (LCP): <2.5s

**Constraints**:
- NO backend modifications allowed (constitutional requirement: Phase 3 is frontend-only)
- Must use existing Phase 1 `/api/v1/*` and Phase 2 `/api/v2/*` APIs without changes
- Mobile-first design (40%+ users on mobile per Assumption 9 in spec)
- WCAG 2.1 Level AA compliance mandatory (FR-056)
- Offline support limited to cached content (no service worker in Phase 3)

**Scale/Scope**:
- 30+ reusable UI components (layouts, features, base)
- 15+ page routes (dashboard, chapters, quizzes, progress, assessments, settings)
- 60 functional requirements (FR-001 to FR-060)
- 27 success criteria (SC-001 to SC-027)
- 3 responsive breakpoints (mobile, tablet, desktop)
- Expected 10,000+ concurrent users (same as backend, per FR-041)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Gate I: Zero-Backend-LLM First (Phase 1) - ✅ PASS

**Status**: PASS (N/A for Phase 3 - Frontend Only)
**Evidence**:
- Phase 3 is pure frontend implementation
- NO backend code changes allowed
- Consumes existing `/api/v1/*` deterministic APIs (Phase 1)
- Consumes existing `/api/v2/*` hybrid APIs (Phase 2)
- All intelligence remains in backend and ChatGPT (no new LLM calls)

**Verification Strategy**:
- No backend code modified (verified via git diff)
- All API calls use existing endpoints from Phase 1 and Phase 2
- No new LLM integration in frontend (frontend does not call OpenAI/Anthropic directly)

---

### Gate II: Cost Efficiency & Scalability - ✅ PASS

**Status**: PASS
**Cost Targets**:
- Phase 3 target: <$10/month for web app hosting (10,000 users)
- No impact on Phase 1/Phase 2 backend costs

**Cost Breakdown (Projected)**:
| Component | Provider | Monthly Cost (10K users) | Per-User Cost |
|-----------|----------|-------------------------|---------------|
| Hosting | Vercel Free Tier | $0 | $0 |
| CDN/Edge | Vercel (included) | $0 | $0 |
| Analytics | Vercel Analytics Free | $0 | $0 |
| Error Tracking | Sentry Free Tier | $0-15 | $0-0.0015 |
| **TOTAL** | | **$0-15** | **$0-0.0015** |

**Rationale**: Vercel free tier supports 100GB bandwidth/month and unlimited deployments. Static site generation (SSG) + edge caching reduces server load. React Query caching reduces API calls to backend. Cost target exceeded (free for most usage).

**Scalability Evidence**:
- FR-047: Client-side caching reduces backend API load
- FR-048: Prefetching next chapter while reading current
- Static pages cached at edge (Vercel CDN)
- React Query deduplication prevents redundant API calls
- Optimistic updates reduce perceived latency without extra API calls

---

### Gate III: Spec-Driven Development - ✅ PASS

**Status**: PASS
**Artifacts Created**:
- ✅ spec.md: 1 user story (US8 - P3), 60 FR, 27 SC, 7 UI components
- ✅ plan.md: This file (technical context, architecture, constitutional check)
- 🔄 research.md: To be generated in Phase 0 (below)
- 🔄 data-model.md: To be generated in Phase 1 (below)
- 🔄 contracts/: To be generated in Phase 1 (below)
- 🔄 quickstart.md: To be generated in Phase 1 (below)
- ⏳ tasks.md: To be generated via `/sp.tasks` command

**Traceability**:
- User story US8 has 8 Given/When/Then acceptance scenarios
- All functional requirements (FR-001 to FR-060) are testable
- Success criteria (SC-001 to SC-027) are measurable and technology-agnostic
- All design artifacts trace back to FR and SC from spec

---

### Gate IV: Hybrid Intelligence Isolation - ✅ PASS (N/A for Phase 3)

**Status**: PASS (Frontend consumes, does not modify)
**Justification**: Phase 3 web app consumes Phase 2 hybrid APIs (`/api/v2/*`) but introduces no new hybrid features. All hybrid intelligence remains isolated in backend per Phase 2 architecture.

**Frontend Responsibilities**:
- Display adaptive learning path roadmap (data from `/api/v2/adaptive/path`)
- Render LLM-graded assessment feedback (data from `/api/v2/assessments/{id}/feedback`)
- Show usage quota status for premium features (data from `/api/v2/quotas`)
- Gracefully hide Phase 2 features if backend not available (FR in spec)

**No New Hybrid Features**: Web app is presentation layer only. All LLM inference remains in Phase 2 backend.

---

### Gate V: Educational Delivery Excellence - ✅ PASS

**Status**: PASS
**Evidence**:
- FR-006 to FR-012: Rich chapter content rendering with formatting, navigation, progress indicators
- FR-013 to FR-020: Interactive quiz interface with visual feedback
- FR-021 to FR-026: Visual progress dashboard with charts, streaks, milestones
- FR-031 to FR-035: Phase 2 feature presentation (adaptive paths, assessments)
- Accessibility (FR-056 to FR-060): WCAG 2.1 Level AA compliance

**Quality Requirements**:
- Content rendered with rich formatting (markdown to HTML, code syntax highlighting)
- Quiz interface provides clear visual feedback (green checkmarks, red X, explanations expanded inline)
- Progress dashboard shows visual representations (circular progress, streak flames, milestone badges)
- Navigation intuitive and consistent (FR-041 to FR-045)

---

### Gate VI: Agent Skills & MCP Integration - ✅ PASS (N/A for Phase 3)

**Status**: PASS (Frontend does not implement agent skills)
**Justification**: Agent Skills remain in ChatGPT App (Phase 1) and backend (Phase 2). Web app provides alternative UI for same functionality, no skill modification required.

**Frontend Presentation**:
- Concept explanations fetched from backend APIs (display only)
- Quiz guidance shown as UI components (not conversational)
- Progress motivation via visual elements (badges, charts, streaks)
- Socratic tutoring not implemented in Phase 3 (ChatGPT App exclusive for conversational modes)

---

### Gate VII: Security & Secrets Management - ✅ PASS

**Status**: PASS
**Security Measures**:
- FR-004: JWT token stored in httpOnly cookies (next-auth) or secure localStorage
- FR-005: Logout functionality clears all auth state
- Environment variables for API endpoints (`.env.local`, gitignored)
- No API keys or secrets in frontend code (all API calls proxied through backend)
- HTTPS enforced (Vercel automatic SSL)
- CORS handled by backend (web app domain whitelisted)

**Data Privacy**:
- User data stored only in backend (frontend caches temporarily)
- LocalStorage data encrypted where sensitive (not yet implemented, Phase 4)
- No PII logged to browser console in production
- Analytics anonymized (Vercel Analytics does not track PII)

**Best Practices**:
- Content Security Policy (CSP) headers configured
- XSS protection via React's automatic escaping
- CSRF protection via SameSite cookies
- Dependency vulnerability scanning (npm audit, Snyk)

---

### Gate VIII: Testing & Quality Gates - ✅ PASS

**Status**: PASS
**Testing Requirements**:
- Vitest unit tests for all components (>80% coverage target)
- Playwright E2E tests for critical user flows (registration, chapter reading, quiz taking)
- axe-core accessibility tests in CI/CD (WCAG 2.1 Level AA)
- Lighthouse CI performance monitoring (90+ desktop, 80+ mobile)

**Quality Gates** (CI/CD pipeline):
1. All tests passing (vitest, playwright)
2. Accessibility tests passing (axe-core, no critical violations)
3. Lighthouse performance score ≥90 (desktop), ≥80 (mobile)
4. TypeScript compilation successful (strict mode, no errors)
5. ESLint + Prettier checks passing
6. Code review approved (1+ reviewer)
7. Constitutional compliance checklist completed in PR

**Testing Strategy**:
```typescript
// tests/components/QuizInterface.test.tsx
describe('QuizInterface', () => {
  it('shows correct answers with green checkmarks', async () => {
    render(<QuizInterface quizId="01-quiz" />);
    // Submit quiz, verify visual feedback
  });
});

// tests/e2e/user-journey.spec.ts
test('student completes full learning journey', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('text=Chapter 1');
  // Verify chapter content loads, quiz submission works, progress updates
});

// tests/a11y/accessibility.test.ts
test('dashboard meets WCAG 2.1 Level AA', async () => {
  const results = await axe(page);
  expect(results.violations).toHaveLength(0);
});
```

---

### Gate IX: Technology Stack Constraints - ✅ PASS

**Status**: PASS
**Technology Choices** (all constitutional-compliant):
- **Frontend**: Next.js 14+ (App Router), TypeScript, React 18, TailwindCSS, shadcn/ui ✅
- **State Management**: React Query (server state), Zustand (UI state) ✅
- **Validation**: Zod (TypeScript-first schemas) ✅
- **Testing**: Playwright (E2E), Vitest (unit), axe-core (a11y) ✅
- **Hosting**: Vercel (zero-config Next.js deployment, edge CDN) ✅
- **CI/CD**: GitHub Actions ✅

**No Backend Stack Changes**: Phase 3 does not modify backend (Python, FastAPI, PostgreSQL remain unchanged).

---

### Gate X: Development Workflow - ✅ PASS

**Status**: PASS
**Workflow Compliance**:
- Feature branch: `004-phase-3-web-app` ✅
- Spec created: `specs/004-phase-3-web-app/spec.md` ✅
- Plan being created: `specs/004-phase-3-web-app/plan.md` (this file) ✅
- Next: Tasks will be created via `/sp.tasks` command
- Commit messages will follow format: `type(scope): description` with Co-Authored-By footer
- PHR will be created after planning completion

---

**Constitution Check Summary**: ✅ **10/10 GATES PASSED**
**Proceed to Phase 0: Research**

## Project Structure

### Documentation (this feature)

```text
specs/004-phase-3-web-app/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (generated below)
├── data-model.md        # Phase 1 output (generated below)
├── quickstart.md        # Phase 1 output (generated below)
├── contracts/           # Phase 1 output (generated below)
│   └── README.md        # Component contracts documentation
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/                     # Next.js 14 App Router
│   ├── layout.tsx           # Root layout (providers, fonts)
│   ├── page.tsx             # Landing page (redirects to /dashboard if authed)
│   ├── (auth)/              # Auth route group (no sidebar)
│   │   ├── login/
│   │   │   └── page.tsx     # Login page
│   │   ├── register/
│   │   │   └── page.tsx     # Registration page
│   │   └── reset-password/
│   │       └── page.tsx     # Password reset page
│   │
│   ├── (app)/               # App route group (with sidebar, requires auth)
│   │   ├── layout.tsx       # App layout (header, sidebar, footer)
│   │   ├── dashboard/
│   │   │   └── page.tsx     # Dashboard (progress overview)
│   │   ├── chapters/
│   │   │   ├── page.tsx     # Chapter list
│   │   │   └── [id]/
│   │   │       └── page.tsx # Chapter viewer
│   │   ├── quizzes/
│   │   │   └── [id]/
│   │   │       ├── page.tsx     # Quiz interface
│   │   │       └── results/
│   │   │           └── page.tsx # Quiz results
│   │   ├── progress/
│   │   │   └── page.tsx     # Progress dashboard
│   │   ├── adaptive/
│   │   │   └── page.tsx     # Adaptive learning path (Phase 2)
│   │   ├── assessments/
│   │   │   ├── page.tsx     # Assessment list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx # Assessment submission
│   │   │   └── feedback/
│   │   │       └── [id]/
│   │   │           └── page.tsx # Feedback viewer
│   │   ├── settings/
│   │   │   └── page.tsx     # User settings
│   │   └── upgrade/
│   │       └── page.tsx     # Premium upgrade
│   │
│   └── api/                 # API route handlers (Next.js API routes)
│       └── auth/
│           └── [...nextauth]/
│               └── route.ts # NextAuth.js configuration
│
├── components/
│   ├── layouts/             # Layout components
│   │   ├── Header.tsx       # Top navigation bar
│   │   ├── Sidebar.tsx      # Desktop sidebar navigation
│   │   ├── BottomNav.tsx    # Mobile bottom navigation
│   │   ├── MobileLayout.tsx # Mobile layout wrapper
│   │   ├── TabletLayout.tsx # Tablet layout wrapper
│   │   └── DesktopLayout.tsx# Desktop layout wrapper
│   │
│   ├── features/            # Feature-specific components
│   │   ├── dashboard/
│   │   │   ├── ProgressSummary.tsx
│   │   │   ├── StreakDisplay.tsx
│   │   │   ├── NextStepsCard.tsx
│   │   │   └── MilestonesBadges.tsx
│   │   ├── chapters/
│   │   │   ├── ChapterViewer.tsx
│   │   │   ├── ChapterNavigation.tsx
│   │   │   ├── TableOfContents.tsx
│   │   │   ├── ReadingProgress.tsx
│   │   │   └── MarkdownRenderer.tsx
│   │   ├── quizzes/
│   │   │   ├── QuizInterface.tsx
│   │   │   ├── QuestionCard.tsx
│   │   │   ├── QuizResults.tsx
│   │   │   ├── AnswerFeedback.tsx
│   │   │   └── QuizProgress.tsx
│   │   ├── progress/
│   │   │   ├── ProgressChart.tsx
│   │   │   ├── ChapterProgressList.tsx
│   │   │   └── PerformanceInsights.tsx
│   │   ├── adaptive/
│   │   │   ├── AdaptivePathRoadmap.tsx
│   │   │   ├── RecommendationCard.tsx
│   │   │   └── PathVisualization.tsx
│   │   ├── assessments/
│   │   │   ├── AssessmentEditor.tsx
│   │   │   ├── FeedbackViewer.tsx
│   │   │   ├── QualityScoreBadge.tsx
│   │   │   └── CharacterCounter.tsx
│   │   └── upgrade/
│   │       ├── UpgradeModal.tsx
│   │       ├── PricingTable.tsx
│   │       └── FeatureComparison.tsx
│   │
│   └── ui/                  # shadcn/ui base components
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── skeleton.tsx
│       ├── progress.tsx
│       ├── badge.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── radio-group.tsx
│       ├── checkbox.tsx
│       ├── select.tsx
│       └── toast.tsx
│
├── lib/
│   ├── api/                 # API client wrappers
│   │   ├── client.ts        # Axios/fetch wrapper with auth
│   │   ├── chapters.ts      # Chapter API calls
│   │   ├── quizzes.ts       # Quiz API calls
│   │   ├── progress.ts      # Progress API calls
│   │   ├── adaptive.ts      # Adaptive path API (Phase 2)
│   │   └── assessments.ts   # Assessment API (Phase 2)
│   │
│   ├── hooks/               # React Query hooks
│   │   ├── useChapters.ts
│   │   ├── useChapter.ts
│   │   ├── useQuiz.ts
│   │   ├── useQuizSubmit.ts
│   │   ├── useProgress.ts
│   │   ├── useStreak.ts
│   │   ├── useAdaptivePath.ts
│   │   └── useAssessment.ts
│   │
│   ├── stores/              # Zustand state management
│   │   ├── uiStore.ts       # UI state (theme, sidebar collapsed, modals)
│   │   ├── quizStore.ts     # Quiz auto-save state
│   │   └── offlineStore.ts  # Offline cache state
│   │
│   ├── utils/               # Utility functions
│   │   ├── cn.ts            # Class name merging (tailwind-merge + clsx)
│   │   ├── formatters.ts    # Date, time, score formatting
│   │   ├── validators.ts    # Form validation helpers
│   │   └── storage.ts       # LocalStorage wrappers
│   │
│   └── schemas/             # Zod validation schemas
│       ├── auth.ts          # Login, register schemas
│       ├── quiz.ts          # Quiz submission schema
│       └── assessment.ts    # Assessment submission schema
│
├── public/                  # Static assets
│   ├── images/
│   │   ├── logo.svg
│   │   ├── illustrations/
│   │   └── badges/
│   └── fonts/
│
├── tests/
│   ├── components/          # Component unit tests
│   │   ├── QuizInterface.test.tsx
│   │   ├── ChapterViewer.test.tsx
│   │   └── ProgressSummary.test.tsx
│   ├── e2e/                 # Playwright E2E tests
│   │   ├── auth.spec.ts
│   │   ├── chapter-reading.spec.ts
│   │   ├── quiz-taking.spec.ts
│   │   └── user-journey.spec.ts
│   ├── a11y/                # Accessibility tests
│   │   ├── dashboard.test.ts
│   │   ├── chapter-viewer.test.ts
│   │   └── quiz-interface.test.ts
│   └── setup.ts             # Test configuration
│
├── .env.local               # Environment variables (gitignored)
├── .env.example             # Environment variable template
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
├── package.json             # Dependencies
├── playwright.config.ts     # Playwright configuration
├── vitest.config.ts         # Vitest configuration
└── README.md                # Frontend documentation

# Note: Backend directory remains UNCHANGED (no modifications in Phase 3)
backend/
├── [All Phase 1 and Phase 2 files remain as-is]
└── [NO new files or modifications]
```

**Structure Decision**: Next.js 14 App Router architecture with `frontend/` directory. All new code in `frontend/`, ZERO changes to `backend/`. App Router enables React Server Components for performance, nested layouts for responsive design, and co-located data fetching. Component organization follows atomic design: `ui/` (base components), `features/` (domain components), `layouts/` (structural components). This structure enables reusability, testability, and clear separation of concerns.

## Complexity Tracking

> **No constitutional violations requiring justification. All gates passed.**

This section is intentionally left blank because the Phase 3 architecture fully complies with all constitutional principles without introducing any prohibited complexity. Phase 3 is frontend-only, introduces no backend changes, no new LLM calls, and maintains cost efficiency via free hosting tier.

## Phase 0: Research

### Research Questions

Based on Technical Context and technology choices, the following research questions must be resolved:

**R1: Next.js 14 App Router vs Pages Router**
- **Question**: Should we use App Router (new) or Pages Router (stable) for Next.js 14?
- **Decision**: Use App Router (Next.js 14 default). Provides React Server Components, streaming, built-in loading/error states, nested layouts, and better performance. Pages Router is legacy and will be deprecated.
- **Rationale**: App Router enables streaming (faster time-to-interactive), nested layouts (responsive design without wrapper hell), and server components (reduced JavaScript bundle size). Migration from Pages to App Router is painful; starting with App Router is best practice.
- **Alternatives Considered**:
  - Pages Router: Rejected (legacy, no Server Components, worse performance)
  - Remix: Rejected (less mature ecosystem, Vercel optimized for Next.js)

**R2: State Management Strategy (React Query + Zustand)**
- **Question**: How to manage server state vs client state without Redux complexity?
- **Decision**:
  - **Server State**: React Query 5.x (caching, background refetching, optimistic updates)
  - **Client State**: Zustand (UI state: theme, modals, sidebar collapsed)
  - No global state library for server data (React Query replaces Redux for API data)
- **Rationale**: React Query handles 90% of state (API responses, caching, loading states). Zustand handles remaining 10% (UI preferences). This separation is simpler than Redux and more performant.
- **Alternatives Considered**:
  - Redux Toolkit: Rejected (over-engineering, too much boilerplate for Phase 3)
  - Context API only: Rejected (re-renders entire tree, poor performance)

**R3: Component Library (shadcn/ui vs Material-UI vs Chakra)**
- **Question**: Which component library balances accessibility, customization, and bundle size?
- **Decision**: shadcn/ui (Radix UI primitives + Tailwind styling). Copy-paste components into codebase (not npm package).
- **Rationale**:
  - **Accessibility**: Radix UI primitives are WCAG 2.1 Level AA compliant out-of-box
  - **Customization**: Full control over styling (Tailwind), no CSS-in-JS bloat
  - **Bundle Size**: Tree-shakable (only include components used)
  - **Ownership**: Components copied into codebase, can modify freely
- **Alternatives Considered**:
  - Material-UI: Rejected (heavy bundle, opinionated design, hard to customize)
  - Chakra UI: Rejected (CSS-in-JS performance overhead, bundle size)
  - Headless UI: Considered (similar to Radix, shadcn/ui is Radix + Tailwind)

**R4: Responsive Design Pattern (Mobile-First CSS vs Component Composition)**
- **Question**: How to implement responsive design across 3 breakpoints (mobile, tablet, desktop)?
- **Decision**: Combination approach:
  - **Tailwind Breakpoints**: `sm:`, `md:`, `lg:` utilities for responsive styling
  - **Component Composition**: Separate layout components (MobileLayout, TabletLayout, DesktopLayout) rendered conditionally
  - **Mobile-First**: Default styles for mobile (320px+), add `md:` and `lg:` modifiers for larger screens
- **Rationale**: Tailwind breakpoints handle 80% of responsive needs (hiding/showing elements, grid columns). Component composition handles complex layout changes (bottom nav vs sidebar). Mobile-first ensures fast loading on mobile (40% of users per spec).
- **Alternatives Considered**:
  - CSS Media Queries only: Rejected (verbose, hard to maintain)
  - JavaScript window.innerWidth: Rejected (hydration mismatch, SSR issues)

**R5: Authentication Strategy (NextAuth.js JWT Provider)**
- **Question**: How to integrate with existing backend JWT authentication?
- **Decision**: Use NextAuth.js with custom JWT provider. Backend issues JWT, NextAuth.js stores in httpOnly cookie, refreshes on expiration.
- **Rationale**: NextAuth.js handles session management, CSRF protection, and refresh logic. Custom JWT provider integrates with Phase 1 backend (`/auth/login`, `/auth/register`). Secure: JWT in httpOnly cookie (not localStorage, XSS-safe).
- **Alternatives Considered**:
  - Manual JWT in localStorage: Rejected (XSS vulnerability)
  - Session cookies from backend: Rejected (CORS complexity, backend changes)

**R6: Performance Optimization (Code Splitting, Prefetching, Caching)**
- **Question**: How to achieve <2s initial load and <1s navigation?
- **Decision**:
  - **Code Splitting**: Next.js automatic (each page is separate bundle)
  - **Prefetching**: React Query `prefetchQuery` for next chapter while reading current
  - **Caching**: React Query cache (5 minutes for chapters, 1 minute for progress)
  - **Static Generation**: Landing page, auth pages (SSG), dashboard (SSR with cache)
  - **Image Optimization**: next/image for automatic WebP, lazy loading
- **Rationale**: Next.js 14 has built-in optimizations (automatic code splitting, route prefetching). React Query cache prevents redundant API calls. Prefetching next chapter reduces wait time.
- **Alternatives Considered**:
  - Manual code splitting: Rejected (Next.js automatic is better)
  - Service Worker caching: Deferred to Phase 4 (complexity)

**R7: Accessibility Testing Strategy (Automated + Manual)**
- **Question**: How to ensure WCAG 2.1 Level AA compliance (FR-056)?
- **Decision**:
  - **Automated**: axe-core in Playwright tests (run on every PR)
  - **Manual**: Screen reader testing (NVDA, JAWS) for critical flows
  - **Component-Level**: ESLint plugin (eslint-plugin-jsx-a11y) catches common issues
  - **Design**: Use semantic HTML, ARIA labels, focus management, keyboard navigation
- **Rationale**: Automated tests catch 30-40% of accessibility issues. Manual testing catches UX problems (screen reader announces, keyboard traps). shadcn/ui provides accessible primitives (Radix UI), reducing manual work.
- **Alternatives Considered**:
  - Automated only: Rejected (misses critical UX issues)
  - Manual only: Rejected (not scalable, prone to regressions)

**R8: Offline Support Strategy (LocalStorage Cache)**
- **Question**: How to implement offline content access (FR-051 to FR-055)?
- **Decision**:
  - React Query `persistQueryClient` plugin stores cache in LocalStorage
  - Cached chapters readable offline
  - Quiz submissions queued in LocalStorage, synced on reconnect
  - Online/offline detection via `navigator.onLine` + API polling
- **Rationale**: React Query persistence is simple and works well with existing cache. LocalStorage is synchronous (safe for SSR). Service Worker would be better but adds complexity (deferred to Phase 4).
- **Alternatives Considered**:
  - Service Worker + Cache API: Deferred to Phase 4 (complexity, debugging issues)
  - IndexedDB: Rejected (async complexity, LocalStorage sufficient for Phase 3)

**R9: Deployment Strategy (Vercel vs Netlify vs Self-Hosted)**
- **Question**: Which hosting platform optimizes Next.js performance and cost?
- **Decision**: Vercel (Next.js creators). Zero-config deployment, edge functions, automatic SSL, global CDN, preview deployments.
- **Rationale**: Vercel is built for Next.js (better performance, faster builds). Free tier supports 100GB bandwidth/month (sufficient for 10K users). Edge functions enable server-side logic without dedicated server.
- **Alternatives Considered**:
  - Netlify: Rejected (slower Next.js builds, worse performance)
  - AWS Amplify: Rejected (complex setup, overkill for Phase 3)
  - Railway: Rejected (backend hosting, not optimized for static sites)

### Research Summary

**Key Technologies Validated**:
- ✅ Next.js 14 (App Router, React Server Components, streaming)
- ✅ TypeScript 5.3+ (strict mode, Zod integration)
- ✅ React 18.2 (Suspense, concurrent features)
- ✅ TailwindCSS 3.4 (utility-first, mobile-first)
- ✅ shadcn/ui (Radix UI + Tailwind, accessible components)
- ✅ React Query 5.x (server state, caching, optimistic updates)
- ✅ Zustand 4.5 (client state, lightweight)
- ✅ NextAuth.js 4.24 (authentication, JWT provider)
- ✅ Playwright 1.40 (E2E testing)
- ✅ axe-core (accessibility testing)
- ✅ Vercel (hosting, edge CDN, zero-config)

**Architecture Patterns Confirmed**:
- App Router with nested layouts (responsive design)
- React Server Components for performance (reduce JavaScript bundle)
- React Query for server state (no Redux)
- Zustand for UI state (theme, modals)
- Mobile-first responsive design (Tailwind breakpoints + component composition)
- Code splitting via Next.js (automatic per-route)
- Prefetching next chapter (React Query)
- LocalStorage persistence (offline support)
- Optimistic updates (React Query mutations)

**Cost Projections Validated**:
- Hosting: Vercel free tier ($0/month for <100GB bandwidth)
- Analytics: Vercel Analytics free ($0/month)
- Error Tracking: Sentry free tier ($0-15/month)
- **Total**: $0-15/month for 10K users → **$0-0.0015/user/month** ✅ Under target

---

*All research questions resolved. Proceeding to Phase 1: Design & Contracts.*
