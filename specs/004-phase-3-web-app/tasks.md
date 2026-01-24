# Implementation Tasks: Phase 3 - Web Application Course Companion

**Branch**: `004-phase-3-web-app`
**Date**: 2026-01-24
**Total Tasks**: 220
**Estimated Timeline**: 8-10 weeks (2 developers)

---

## Task Format

Every task follows: `- [ ] T### [P?] [US8?] Description with frontend/path/to/file.tsx`

- **Checkbox**: `- [ ]` (unchecked)
- **Task ID**: T001, T002, T003... (sequential)
- **[P] marker**: ONLY if task can run in parallel with others
- **[US8] label**: For User Story 8 tasks, NO label for Setup/Foundational/Polish/Testing/Deployment
- **Description**: Clear action with exact file path

---

## Dependency Graph

```
Phase 1: Setup & Environment (T001-T020)
  ↓
Phase 2: Foundational - Layouts & Core Components (T021-T050)
  ↓
Phase 3: User Story 8 - Web Application Features (T051-T180)
  ├─ Authentication & Onboarding (T051-T060)
  ├─ Course Content Viewing (T061-T080)
  ├─ Quiz Interface (T081-T100)
  ├─ Progress Dashboard (T101-T115)
  ├─ Freemium Access Control (T116-T125)
  ├─ Phase 2 Features (Optional) (T126-T140)
  ├─ Responsive Design (T141-T150)
  ├─ Navigation & Usability (T151-T160)
  ├─ Performance & Loading (T161-T170)
  └─ Error Handling & Offline (T171-T180)
  ↓
Phase 4: Testing & Quality (T181-T200)
  ↓
Phase 5: Documentation & Deployment (T201-T220)
```

---

## Phase 1: Setup & Environment (T001-T020)

### Repository & Project Initialization

- [ ] T001 [P] Initialize Next.js 14 project with TypeScript, TailwindCSS, and App Router in frontend/
- [ ] T002 [P] Configure TypeScript strict mode and path aliases in frontend/tsconfig.json
- [ ] T003 [P] Install React Query 5.0+ and Zustand 4.4+ for state management in frontend/package.json
- [ ] T004 [P] Install shadcn/ui and initialize with default theme in frontend/components/ui/
- [ ] T005 [P] Install NextAuth.js 4.24+ for authentication in frontend/package.json
- [ ] T006 [P] Install Zod 3.22+ for schema validation in frontend/package.json
- [ ] T007 [P] Install Vitest and React Testing Library for unit tests in frontend/package.json
- [ ] T008 [P] Install Playwright 1.40+ for E2E testing in frontend/package.json
- [ ] T009 [P] Install axe-core for accessibility testing in frontend/package.json

### Configuration Files

- [ ] T010 Configure TailwindCSS theme with custom colors and breakpoints in frontend/tailwind.config.ts
- [ ] T011 Configure Next.js with image optimization and performance settings in frontend/next.config.js
- [ ] T012 Configure ESLint with jsx-a11y plugin for accessibility linting in frontend/.eslintrc.json
- [ ] T013 Configure Prettier with Tailwind plugin for code formatting in frontend/.prettierrc
- [ ] T014 Create environment variables template in frontend/.env.example
- [ ] T015 Create local environment variables file in frontend/.env.local (gitignored)

### Testing & CI/CD Setup

- [ ] T016 Configure Vitest for component unit tests in frontend/vitest.config.ts
- [ ] T017 Configure Playwright for E2E tests across browsers in frontend/playwright.config.ts
- [ ] T018 Create test setup file with React Testing Library in frontend/tests/setup.ts
- [ ] T019 Create GitHub Actions workflow for CI/CD in .github/workflows/ci.yml
- [ ] T020 Configure Vercel deployment settings in frontend/vercel.json

---

## Phase 2: Foundational - Layouts & Core Components (T021-T050)

### Directory Structure

- [ ] T021 Create directory structure for app routes in frontend/app/
- [ ] T022 Create directory structure for components in frontend/components/
- [ ] T023 Create directory structure for lib utilities in frontend/lib/
- [ ] T024 Create directory structure for tests in frontend/tests/
- [ ] T025 Create directory structure for public assets in frontend/public/

### Base UI Components (shadcn/ui)

- [ ] T026 [P] Install Button component from shadcn/ui in frontend/components/ui/button.tsx
- [ ] T027 [P] Install Card component from shadcn/ui in frontend/components/ui/card.tsx
- [ ] T028 [P] Install Dialog component from shadcn/ui in frontend/components/ui/dialog.tsx
- [ ] T029 [P] Install Input component from shadcn/ui in frontend/components/ui/input.tsx
- [ ] T030 [P] Install Textarea component from shadcn/ui in frontend/components/ui/textarea.tsx
- [ ] T031 [P] Install Skeleton component from shadcn/ui in frontend/components/ui/skeleton.tsx
- [ ] T032 [P] Install Progress component from shadcn/ui in frontend/components/ui/progress.tsx
- [ ] T033 [P] Install Badge component from shadcn/ui in frontend/components/ui/badge.tsx
- [ ] T034 [P] Install RadioGroup component from shadcn/ui in frontend/components/ui/radio-group.tsx
- [ ] T035 [P] Install Checkbox component from shadcn/ui in frontend/components/ui/checkbox.tsx
- [ ] T036 [P] Install Select component from shadcn/ui in frontend/components/ui/select.tsx
- [ ] T037 [P] Install Toast component from shadcn/ui in frontend/components/ui/toast.tsx

### Core Utilities & State Management

- [ ] T038 Create API client with axios and auth interceptor in frontend/lib/api/client.ts
- [ ] T039 Create React Query configuration and cache setup in frontend/lib/api/queryClient.ts
- [ ] T040 Create React Query key definitions in frontend/lib/api/queryKeys.ts
- [ ] T041 Create Zustand UI store for theme and sidebar state in frontend/lib/stores/uiStore.ts
- [ ] T042 Create Zustand quiz store for auto-save state in frontend/lib/stores/quizStore.ts
- [ ] T043 Create Zustand offline store for offline sync in frontend/lib/stores/offlineStore.ts
- [ ] T044 Create utility function for className merging in frontend/lib/utils/cn.ts
- [ ] T045 Create date/time formatter utilities in frontend/lib/utils/formatters.ts
- [ ] T046 Create localStorage wrapper utilities in frontend/lib/utils/storage.ts

### TypeScript Types & Schemas

- [ ] T047 [P] Create authentication types in frontend/lib/types/auth.ts
- [ ] T048 [P] Create chapter types in frontend/lib/types/chapter.ts
- [ ] T049 [P] Create quiz types in frontend/lib/types/quiz.ts
- [ ] T050 [P] Create progress types in frontend/lib/types/progress.ts

---

## Phase 3: User Story 8 - Web Application Features (T051-T180)

### Authentication & Onboarding (FR-001 to FR-005)

- [ ] T051 [US8] Create NextAuth.js configuration with JWT provider in frontend/app/api/auth/[...nextauth]/route.ts
- [ ] T052 [US8] Create login form with email/password validation in frontend/app/(auth)/login/page.tsx
- [ ] T053 [US8] Create registration form with email/password/name fields in frontend/app/(auth)/register/page.tsx
- [ ] T054 [US8] Create password reset request form in frontend/app/(auth)/reset-password/page.tsx
- [ ] T055 [US8] Create Zod schema for login validation in frontend/lib/schemas/auth.ts
- [ ] T056 [US8] Create Zod schema for registration validation in frontend/lib/schemas/auth.ts
- [ ] T057 [US8] Create onboarding flow component with welcome screens in frontend/components/features/onboarding/OnboardingFlow.tsx
- [ ] T058 [US8] Create session persistence hook using NextAuth in frontend/lib/hooks/useAuth.ts
- [ ] T059 [US8] Create logout functionality in user menu in frontend/components/layouts/Header.tsx
- [ ] T060 [US8] Create authentication middleware for protected routes in frontend/middleware.ts

### Layout Components (Responsive Foundation)

- [ ] T061 Create root layout with providers in frontend/app/layout.tsx
- [ ] T062 Create auth layout (no sidebar) in frontend/app/(auth)/layout.tsx
- [ ] T063 Create app layout (with sidebar/header/footer) in frontend/app/(app)/layout.tsx
- [ ] T064 Create Header component with logo and user menu in frontend/components/layouts/Header.tsx
- [ ] T065 Create Sidebar component for desktop navigation in frontend/components/layouts/Sidebar.tsx
- [ ] T066 Create BottomNav component for mobile navigation in frontend/components/layouts/BottomNav.tsx
- [ ] T067 Create responsive layout wrapper (mobile/tablet/desktop) in frontend/components/layouts/ResponsiveLayout.tsx
- [ ] T068 Create skip-to-content link for accessibility in frontend/components/layouts/SkipToContent.tsx

### Course Content Viewing (FR-006 to FR-012)

- [ ] T069 [US8] Create API client function for fetching chapter list in frontend/lib/api/chapters.ts
- [ ] T070 [US8] Create API client function for fetching single chapter in frontend/lib/api/chapters.ts
- [ ] T071 [US8] Create React Query hook for chapter list in frontend/lib/hooks/useChapters.ts
- [ ] T072 [US8] Create React Query hook for single chapter with prefetching in frontend/lib/hooks/useChapter.ts
- [ ] T073 [US8] Create chapter list page with table of contents in frontend/app/(app)/chapters/page.tsx
- [ ] T074 [US8] Create chapter viewer page with markdown rendering in frontend/app/(app)/chapters/[id]/page.tsx
- [ ] T075 [US8] Create ChapterViewer component with rich formatting in frontend/components/features/chapters/ChapterViewer.tsx
- [ ] T076 [US8] Create MarkdownRenderer component with syntax highlighting in frontend/components/features/chapters/MarkdownRenderer.tsx
- [ ] T077 [US8] Create ChapterNavigation component (prev/next buttons) in frontend/components/features/chapters/ChapterNavigation.tsx
- [ ] T078 [US8] Create TableOfContents component (floating sidebar) in frontend/components/features/chapters/TableOfContents.tsx
- [ ] T079 [US8] Create ReadingProgress component (progress bar) in frontend/components/features/chapters/ReadingProgress.tsx
- [ ] T080 [US8] Create chapter search functionality across all content in frontend/components/features/chapters/ChapterSearch.tsx

### Quiz Interface (FR-013 to FR-020)

- [ ] T081 [US8] Create API client function for fetching quiz in frontend/lib/api/quizzes.ts
- [ ] T082 [US8] Create API client function for submitting quiz in frontend/lib/api/quizzes.ts
- [ ] T083 [US8] Create React Query hook for quiz data in frontend/lib/hooks/useQuiz.ts
- [ ] T084 [US8] Create React Query mutation for quiz submission in frontend/lib/hooks/useQuizSubmit.ts
- [ ] T085 [US8] Create Zod schema for quiz submission validation in frontend/lib/schemas/quiz.ts
- [ ] T086 [US8] Create quiz interface page in frontend/app/(app)/quizzes/[id]/page.tsx
- [ ] T087 [US8] Create quiz results page in frontend/app/(app)/quizzes/[id]/results/page.tsx
- [ ] T088 [US8] Create QuizInterface component with question pagination in frontend/components/features/quizzes/QuizInterface.tsx
- [ ] T089 [US8] Create QuestionCard component (radio/checkbox/textarea) in frontend/components/features/quizzes/QuestionCard.tsx
- [ ] T090 [US8] Create QuizProgress component (question counter) in frontend/components/features/quizzes/QuizProgress.tsx
- [ ] T091 [US8] Create QuizResults component with score display in frontend/components/features/quizzes/QuizResults.tsx
- [ ] T092 [US8] Create AnswerFeedback component (correct/incorrect indicators) in frontend/components/features/quizzes/AnswerFeedback.tsx
- [ ] T093 [US8] Implement quiz auto-save every 30 seconds using Zustand in frontend/lib/hooks/useQuizAutoSave.ts
- [ ] T094 [US8] Implement quiz resume from auto-saved state in frontend/components/features/quizzes/QuizInterface.tsx
- [ ] T095 [US8] Implement quiz submission with optimistic updates in frontend/lib/hooks/useQuizSubmit.ts
- [ ] T096 [US8] Create quiz retake functionality in frontend/components/features/quizzes/QuizResults.tsx
- [ ] T097 [US8] Create quiz exit confirmation dialog in frontend/components/features/quizzes/QuizExitDialog.tsx
- [ ] T098 [US8] Create quiz types (Chapter, Progress, Adaptive) in frontend/lib/types/quiz.ts
- [ ] T099 [US8] Create adaptive path types in frontend/lib/types/adaptive.ts
- [ ] T100 [US8] Create assessment types in frontend/lib/types/assessment.ts

### Progress Dashboard (FR-021 to FR-026)

- [ ] T101 [US8] Create API client function for fetching progress summary in frontend/lib/api/progress.ts
- [ ] T102 [US8] Create API client function for fetching streak data in frontend/lib/api/progress.ts
- [ ] T103 [US8] Create React Query hook for progress summary in frontend/lib/hooks/useProgress.ts
- [ ] T104 [US8] Create React Query hook for streak data in frontend/lib/hooks/useStreak.ts
- [ ] T105 [US8] Create dashboard page with progress overview in frontend/app/(app)/dashboard/page.tsx
- [ ] T106 [US8] Create progress detail page in frontend/app/(app)/progress/page.tsx
- [ ] T107 [US8] Create ProgressSummary component with circular chart in frontend/components/features/dashboard/ProgressSummary.tsx
- [ ] T108 [US8] Create StreakDisplay component with flame icon in frontend/components/features/dashboard/StreakDisplay.tsx
- [ ] T109 [US8] Create NextStepsCard component with recommendations in frontend/components/features/dashboard/NextStepsCard.tsx
- [ ] T110 [US8] Create MilestonesBadges component with earned badges in frontend/components/features/dashboard/MilestonesBadges.tsx
- [ ] T111 [US8] Create ProgressChart component (circular/bar variants) in frontend/components/features/progress/ProgressChart.tsx
- [ ] T112 [US8] Create ChapterProgressList component with completion status in frontend/components/features/progress/ChapterProgressList.tsx
- [ ] T113 [US8] Create PerformanceInsights component with analytics in frontend/components/features/progress/PerformanceInsights.tsx
- [ ] T114 [US8] Implement milestone celebration animations in frontend/components/features/dashboard/MilestoneCelebration.tsx
- [ ] T115 [US8] Implement total study time tracking in frontend/lib/hooks/useStudyTime.ts

### Freemium Access Control (FR-027 to FR-030)

- [ ] T116 [US8] Create chapter access check utility based on subscription tier in frontend/lib/utils/access.ts
- [ ] T117 [US8] Create UpgradeModal component with pricing table in frontend/components/features/upgrade/UpgradeModal.tsx
- [ ] T118 [US8] Create PricingTable component (free vs premium) in frontend/components/features/upgrade/PricingTable.tsx
- [ ] T119 [US8] Create FeatureComparison component with checkmarks in frontend/components/features/upgrade/FeatureComparison.tsx
- [ ] T120 [US8] Implement premium chapter blocking in chapter viewer in frontend/app/(app)/chapters/[id]/page.tsx
- [ ] T121 [US8] Create upgrade CTA button in chapter list in frontend/components/features/chapters/ChapterList.tsx
- [ ] T122 [US8] Create free/premium badge indicator in UI in frontend/components/ui/tier-badge.tsx
- [ ] T123 [US8] Implement upgrade modal trigger on premium feature access in frontend/lib/hooks/useUpgradeModal.ts
- [ ] T124 [US8] Create one-click upgrade flow redirect in frontend/components/features/upgrade/UpgradeButton.tsx
- [ ] T125 [US8] Create subscription tier check hook in frontend/lib/hooks/useSubscription.ts

### Phase 2 Features - Adaptive Learning (FR-031, FR-032, FR-035)

- [ ] T126 [US8] Create API client for adaptive path generation in frontend/lib/api/adaptive.ts
- [ ] T127 [US8] Create React Query hook for adaptive path in frontend/lib/hooks/useAdaptivePath.ts
- [ ] T128 [US8] Create adaptive path page in frontend/app/(app)/adaptive/page.tsx
- [ ] T129 [US8] Create AdaptivePathRoadmap component with flowchart in frontend/components/features/adaptive/AdaptivePathRoadmap.tsx
- [ ] T130 [US8] Create RecommendationCard component with reasoning in frontend/components/features/adaptive/RecommendationCard.tsx
- [ ] T131 [US8] Create PathVisualization component (graph/timeline) in frontend/components/features/adaptive/PathVisualization.tsx
- [ ] T132 [US8] Create usage quota display component in frontend/components/features/adaptive/UsageQuota.tsx
- [ ] T133 [US8] Implement graceful degradation when Phase 2 APIs unavailable in frontend/lib/hooks/useFeatureFlag.ts

### Phase 2 Features - LLM Assessments (FR-033, FR-034, FR-035)

- [ ] T134 [US8] Create API client for assessment submission in frontend/lib/api/assessments.ts
- [ ] T135 [US8] Create React Query mutation for assessment submission in frontend/lib/hooks/useAssessmentSubmit.ts
- [ ] T136 [US8] Create assessment submission page in frontend/app/(app)/assessments/[id]/page.tsx
- [ ] T137 [US8] Create assessment feedback page in frontend/app/(app)/assessments/feedback/[id]/page.tsx
- [ ] T138 [US8] Create AssessmentEditor component with word counter in frontend/components/features/assessments/AssessmentEditor.tsx
- [ ] T139 [US8] Create FeedbackViewer component with quality score in frontend/components/features/assessments/FeedbackViewer.tsx
- [ ] T140 [US8] Create CharacterCounter component for text limits in frontend/components/features/assessments/CharacterCounter.tsx

### Responsive Design (FR-036 to FR-040)

- [ ] T141 [US8] Implement mobile responsive styles (320px-768px) in all components using Tailwind
- [ ] T142 [US8] Implement tablet responsive styles (768px-1024px) in all components using Tailwind
- [ ] T143 [US8] Implement desktop responsive styles (1024px+) in all components using Tailwind
- [ ] T144 [US8] Create responsive breakpoint hook in frontend/lib/hooks/useMediaQuery.ts
- [ ] T145 [US8] Test portrait and landscape orientations on mobile in frontend/tests/e2e/responsive.spec.ts
- [ ] T146 [US8] Optimize touch targets (44x44px minimum) for mobile in frontend/components/
- [ ] T147 [US8] Implement swipe gestures for mobile navigation in frontend/components/layouts/BottomNav.tsx
- [ ] T148 [US8] Test responsive layout on real devices (iOS/Android) in frontend/tests/e2e/mobile.spec.ts
- [ ] T149 [US8] Create responsive grid layouts for chapter list in frontend/components/features/chapters/ChapterList.tsx
- [ ] T150 [US8] Create responsive modal dialogs (full-screen on mobile) in frontend/components/ui/responsive-dialog.tsx

### Navigation & Usability (FR-041 to FR-045)

- [ ] T151 [US8] Implement breadcrumb navigation in frontend/components/layouts/Breadcrumbs.tsx
- [ ] T152 [US8] Implement browser back/forward button support in all pages
- [ ] T153 [US8] Create keyboard navigation support (Tab, Enter, Escape) in all interactive elements
- [ ] T154 [US8] Create focus management on route change in frontend/lib/hooks/useFocusManagement.ts
- [ ] T155 [US8] Implement search functionality in header in frontend/components/layouts/SearchBar.tsx
- [ ] T156 [US8] Create user account menu dropdown in frontend/components/layouts/UserMenu.tsx
- [ ] T157 [US8] Create site-wide navigation context in frontend/lib/contexts/NavigationContext.tsx
- [ ] T158 [US8] Implement active route highlighting in sidebar in frontend/components/layouts/Sidebar.tsx
- [ ] T159 [US8] Create navigation shortcuts (keyboard) in frontend/lib/hooks/useKeyboardShortcuts.ts
- [ ] T160 [US8] Test keyboard-only navigation flow in frontend/tests/e2e/keyboard-nav.spec.ts

### Performance & Loading States (FR-046 to FR-050)

- [ ] T161 [US8] Create skeleton loaders for all pages in frontend/components/ui/skeleton.tsx
- [ ] T162 [US8] Implement React Query caching (5 min for chapters) in frontend/lib/api/queryClient.ts
- [ ] T163 [US8] Implement prefetching next chapter in frontend/lib/hooks/useChapter.ts
- [ ] T164 [US8] Implement code splitting with next/dynamic in frontend/app/
- [ ] T165 [US8] Optimize images with next/image in frontend/components/
- [ ] T166 [US8] Create loading progress indicator for long operations in frontend/components/ui/loading-progress.tsx
- [ ] T167 [US8] Implement optimistic updates for quiz submissions in frontend/lib/hooks/useQuizSubmit.ts
- [ ] T168 [US8] Test initial page load <2 seconds in frontend/tests/performance/load-time.spec.ts
- [ ] T169 [US8] Run Lighthouse performance audit (target: 90+ desktop) in frontend/tests/performance/lighthouse.spec.ts
- [ ] T170 [US8] Implement bundle size monitoring in frontend/.github/workflows/bundle-size.yml

### Error Handling & Offline Support (FR-051 to FR-055)

- [ ] T171 [US8] Create user-friendly error pages (404, 500) in frontend/app/error.tsx
- [ ] T172 [US8] Create error boundary component in frontend/components/ErrorBoundary.tsx
- [ ] T173 [US8] Implement offline detection in frontend/lib/hooks/useOnlineStatus.ts
- [ ] T174 [US8] Create offline banner component in frontend/components/layouts/OfflineBanner.tsx
- [ ] T175 [US8] Implement React Query cache persistence to localStorage in frontend/lib/api/queryClient.ts
- [ ] T176 [US8] Implement offline quiz submission queueing in frontend/lib/stores/offlineStore.ts
- [ ] T177 [US8] Create retry mechanism for failed API calls in frontend/lib/api/client.ts
- [ ] T178 [US8] Test offline content access in frontend/tests/e2e/offline.spec.ts
- [ ] T179 [US8] Create API error toast notifications in frontend/components/ui/toast.tsx
- [ ] T180 [US8] Implement sync status indicator in frontend/components/layouts/SyncStatus.tsx

---

## Phase 4: Testing & Quality (T181-T200)

### Unit Tests (Vitest + React Testing Library)

- [ ] T181 Create unit test for Header component in frontend/tests/components/Header.test.tsx
- [ ] T182 Create unit test for Sidebar component in frontend/tests/components/Sidebar.test.tsx
- [ ] T183 Create unit test for ProgressSummary component in frontend/tests/components/ProgressSummary.test.tsx
- [ ] T184 Create unit test for ChapterViewer component in frontend/tests/components/ChapterViewer.test.tsx
- [ ] T185 Create unit test for QuizInterface component in frontend/tests/components/QuizInterface.test.tsx
- [ ] T186 Create unit test for QuestionCard component in frontend/tests/components/QuestionCard.test.tsx
- [ ] T187 Create unit test for UpgradeModal component in frontend/tests/components/UpgradeModal.test.tsx
- [ ] T188 Run unit test coverage report (target: >80%) in frontend/tests/coverage.spec.ts

### E2E Tests (Playwright)

- [ ] T189 Create E2E test for authentication flow in frontend/tests/e2e/auth.spec.ts
- [ ] T190 Create E2E test for chapter reading flow in frontend/tests/e2e/chapter-reading.spec.ts
- [ ] T191 Create E2E test for quiz taking flow in frontend/tests/e2e/quiz-taking.spec.ts
- [ ] T192 Create E2E test for progress dashboard in frontend/tests/e2e/progress-dashboard.spec.ts
- [ ] T193 Create E2E test for freemium upgrade flow in frontend/tests/e2e/upgrade-flow.spec.ts
- [ ] T194 Create E2E test for full user journey (registration to completion) in frontend/tests/e2e/user-journey.spec.ts

### Accessibility Tests (axe-core)

- [ ] T195 Create accessibility test for dashboard page in frontend/tests/a11y/dashboard.test.ts
- [ ] T196 Create accessibility test for chapter viewer in frontend/tests/a11y/chapter-viewer.test.ts
- [ ] T197 Create accessibility test for quiz interface in frontend/tests/a11y/quiz-interface.test.ts
- [ ] T198 Run automated accessibility audit with axe-core in frontend/tests/a11y/axe-audit.spec.ts
- [ ] T199 Conduct manual screen reader testing (NVDA/JAWS) and document results
- [ ] T200 Fix all critical accessibility issues (WCAG 2.1 Level AA compliance)

---

## Phase 5: Documentation & Deployment (T201-T220)

### Documentation

- [ ] T201 Create frontend README with setup instructions in frontend/README.md
- [ ] T202 Create component documentation with usage examples in frontend/COMPONENTS.md
- [ ] T203 Create API client documentation in frontend/API_DOCUMENTATION.md
- [ ] T204 Create deployment guide for Vercel in frontend/DEPLOYMENT.md
- [ ] T205 Create troubleshooting guide in frontend/TROUBLESHOOTING.md
- [ ] T206 Document accessibility features and WCAG compliance in frontend/ACCESSIBILITY.md
- [ ] T207 Create Storybook for component library (optional) in frontend/.storybook/

### Production Readiness

- [ ] T208 Configure production environment variables in Vercel dashboard
- [ ] T209 Set up Vercel Analytics for performance monitoring
- [ ] T210 Set up Sentry for error tracking in frontend/lib/sentry.ts
- [ ] T211 Configure CSP headers for security in frontend/next.config.js
- [ ] T212 Optimize production build bundle size (<500KB initial) in frontend/next.config.js
- [ ] T213 Test production build locally with npm run build && npm start
- [ ] T214 Run final Lighthouse audit on production build (target: 90+ desktop, 80+ mobile)

### Deployment

- [ ] T215 Deploy to Vercel preview environment (staging)
- [ ] T216 Test full user journey on Vercel preview deployment
- [ ] T217 Configure custom domain (app.course-companion.example.com) in Vercel
- [ ] T218 Deploy to Vercel production environment
- [ ] T219 Monitor production metrics (Vercel Analytics, Sentry) for 48 hours
- [ ] T220 Create post-launch checklist and handoff documentation

---

## Parallel Execution Opportunities

### Phase 1 (Setup) - All Parallelizable
- T001-T009: Install dependencies (9 tasks, can run together)
- T026-T037: Install shadcn/ui components (12 tasks, independent)

### Phase 2 (Foundational) - Partial Parallelization
- T047-T050: Create TypeScript types (4 tasks, independent)

### Phase 3 (Features) - Parallelizable by Feature Area
- Authentication (T051-T060): Sequential (auth flow dependencies)
- Layouts (T061-T068): Sequential (layout hierarchy)
- Chapters (T069-T080): Partially parallel (API → Hooks → Components)
- Quizzes (T081-T100): Partially parallel (API → Hooks → Components)
- Progress (T101-T115): Partially parallel (API → Hooks → Components)
- Freemium (T116-T125): Sequential (access control dependencies)
- Adaptive/Assessments (T126-T140): Parallel if Phase 2 features independent
- Responsive (T141-T150): Can run in parallel after components exist
- Navigation (T151-T160): Sequential (navigation flow dependencies)
- Performance (T161-T170): Parallel (independent optimizations)
- Error Handling (T171-T180): Partially parallel

### Phase 4 (Testing) - Highly Parallelizable
- T181-T188: Unit tests (8 tasks, independent)
- T189-T194: E2E tests (6 tasks, independent)
- T195-T200: Accessibility tests (6 tasks, independent)

### Phase 5 (Documentation) - Parallelizable
- T201-T207: Documentation (7 tasks, independent)

---

## Estimated Timeline (2 Developers)

| Phase | Tasks | Duration | Notes |
|-------|-------|----------|-------|
| Phase 1: Setup | T001-T020 | 1 week | Can parallelize, mostly configuration |
| Phase 2: Foundational | T021-T050 | 1.5 weeks | Base components and utilities |
| Phase 3: User Story 8 | T051-T180 | 5 weeks | Core feature implementation |
| - Authentication | T051-T060 | 3 days | |
| - Layouts | T061-T068 | 2 days | |
| - Chapters | T069-T080 | 5 days | |
| - Quizzes | T081-T100 | 5 days | |
| - Progress | T101-T115 | 4 days | |
| - Freemium | T116-T125 | 3 days | |
| - Phase 2 Features | T126-T140 | 4 days | Optional, can defer |
| - Responsive | T141-T150 | 3 days | |
| - Navigation | T151-T160 | 3 days | |
| - Performance | T161-T170 | 3 days | |
| - Error Handling | T171-T180 | 3 days | |
| Phase 4: Testing | T181-T200 | 1.5 weeks | Parallel with Phase 3 (TDD) |
| Phase 5: Documentation | T201-T220 | 1 week | Final polish and deployment |
| **Total** | **220 tasks** | **8-10 weeks** | 2 developers, full-time |

---

## MVP Scope (Minimum Viable Product)

For fastest time-to-market, prioritize these tasks:

**Critical Path (MVP in 4 weeks)**:
- Phase 1: All tasks (T001-T020) - 1 week
- Phase 2: All tasks (T021-T050) - 1.5 weeks
- Phase 3: Authentication (T051-T060), Layouts (T061-T068), Chapters (T069-T080), Quizzes (T081-T100), Progress (T101-T115), Freemium (T116-T125) - 2.5 weeks
- Phase 4: Critical E2E tests (T189-T194), Accessibility (T195-T200) - 1 week
- Phase 5: Deployment (T208-T220) - 3 days

**Deferred to Post-MVP**:
- Phase 2 Features (T126-T140) - Can launch without adaptive paths/assessments
- Advanced Navigation (T159-T160) - Keyboard shortcuts nice-to-have
- Performance Optimizations (T165-T170) - If meeting <2s load target
- Storybook (T207) - Internal tooling, not user-facing

---

## Notes

- **Task IDs are sequential and immutable** - Do not renumber when tasks complete
- **[P] marker indicates parallelizable tasks** - Can be worked on simultaneously by multiple developers
- **[US8] label indicates User Story 8 tasks** - Direct functional requirements from spec
- **File paths are exact and absolute** - Every task specifies the full path to the file being created/modified
- **Dependencies are implicit** - Tasks are ordered such that earlier tasks satisfy dependencies for later tasks
- **Testing follows TDD** - Unit tests can be written alongside components (Phase 3 + Phase 4 overlap)
- **Responsive design is integrated** - Mobile-first approach means responsive styles added during component creation

---

**End of tasks.md - Total 220 tasks defined. Ready for implementation via `/sp.implement`.**
