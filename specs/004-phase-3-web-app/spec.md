# Feature Specification: Phase 3 - Web Application Course Companion

**Feature Branch**: `004-phase-3-web-app`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "Phase 3: Web Application Course Companion - Build standalone responsive web application providing full feature parity with ChatGPT App plus visual enhancements. Students access all Phase 1 and Phase 2 features through modern web UI. Includes visual progress dashboard, interactive course viewer, quiz interface, adaptive learning path visualization, and assessment submission forms. Responsive design works on mobile and desktop. User Story: US8 (Full Web Application Experience). Tech stack: Next.js 14 (App Router), TypeScript, React 18, TailwindCSS, shadcn/ui, React Query for data fetching, Playwright for E2E testing. Backend: Same APIs from Phase 1 (/api/v1/*) and Phase 2 (/api/v2/*). Target: Feature parity with ChatGPT App plus visual progress dashboard, responsive on all devices."

**Prerequisites**: Phase 1 (Zero-Backend-LLM) must be fully implemented. Phase 2 (Hybrid Intelligence) is optional but recommended for full feature set.

## User Scenarios & Testing

### User Story 8 - Experience Full Learning Platform via Web Application (Priority: P3)

Students access the complete Course Companion learning experience through a modern, responsive web application that works seamlessly on mobile phones, tablets, and desktop computers. The web app provides all functionality available in the ChatGPT App plus visual enhancements like progress dashboards, interactive navigation, and visual representations of learning paths.

**Why this priority**: Web app provides visual richness and accessibility beyond conversational interface. Students who prefer traditional learning platforms can use familiar UI patterns (menus, buttons, dashboards). Priority P3 because core learning functionality (Phase 1) and premium features (Phase 2) must work through ChatGPT App first.

**Independent Test**: Can be fully tested by having a student complete an entire learning journey through the web app only (no ChatGPT): register account, view chapters, take quizzes, track progress, see visualized learning paths, submit assessments, and verify all functionality matches ChatGPT App plus see additional visual enhancements.

**Acceptance Scenarios**:

1. **Given** a new student visits the web app on mobile, **When** they register and log in, **Then** they see a responsive dashboard with course overview, their progress (0%), and a "Start Learning" button that fits perfectly on their screen
2. **Given** a student is viewing Chapter 2 on desktop, **When** they scroll through content, **Then** they see rich formatting (headings, code blocks, diagrams), a floating table of contents sidebar, and estimated reading time progress bar
3. **Given** a student completes a quiz on tablet, **When** they submit answers, **Then** they immediately see results with visual indicators (green checkmarks for correct, red X for wrong), explanations expanded inline, and overall score displayed prominently
4. **Given** a premium student views their dashboard on mobile, **When** they check progress, **Then** they see a visual progress circle (e.g., "67% complete"), streak flame icon with number, and personalized recommendations card highlighting their next suggested action
5. **Given** a student is on a slow connection, **When** they navigate between pages, **Then** they see skeleton loaders indicating content is loading, and previously viewed pages load instantly from cache
6. **Given** a premium student requests adaptive learning path on desktop, **When** recommendations generate, **Then** they see a visual roadmap/flowchart showing suggested chapters with icons, connecting lines, and "Why this?" explanations on hover
7. **Given** a student submits an open-ended assessment on mobile, **When** feedback returns, **Then** they see detailed feedback in an expandable card format with quality score badge, color-coded strengths (green) and improvements (amber), and inline chapter references as clickable links
8. **Given** a free-tier student tries to access Chapter 4 on web app, **When** blocked by freemium gate, **Then** they see an elegant upgrade modal with clear pricing comparison table, benefits list, and one-click upgrade button (not harsh blocking message)

---

### Edge Cases

- **What happens when a student's session expires mid-quiz?** Web app auto-saves quiz progress every 30 seconds to local storage. Upon re-authentication, student sees: "We saved your quiz progress. Resume where you left off?" with a "Resume Quiz" button.

- **How does the web app handle offline scenarios?** When connection is lost, web app shows banner: "You're offline. Previously viewed content is still available. Progress will sync when you reconnect." Students can read cached chapters but cannot take new quizzes or submit assessments until online.

- **What happens when backend APIs are down?** Web app detects API errors and shows friendly error screen: "We're experiencing technical difficulties. Our team has been notified. Please try again in a few minutes. Check status: status.example.com"

- **How does the app handle different screen sizes?** Responsive breakpoints: Mobile (<768px) = single-column stack layout with bottom nav. Tablet (768-1024px) = two-column layout. Desktop (>1024px) = three-column with sidebar navigation. All layouts tested and optimized.

- **What happens when a student has multiple tabs open?** Web app synchronizes state across tabs using broadcast channel. Progress updates in one tab reflect immediately in other tabs. If student logs out in one tab, all tabs redirect to login screen.

- **How does the app handle browser back button?** Back button navigates through app history naturally (chapter → previous chapter, quiz results → quiz questions). Exit confirmation shown if student tries to leave during active quiz: "Quiz in progress. Your answers will be lost. Continue?"

- **What happens when premium features aren't available (Phase 2 not deployed)?** Web app gracefully hides Phase 2 features (adaptive learning path, LLM assessments). Navigation menu shows only available features. No broken links or error messages.

## Requirements

### Functional Requirements

**User Authentication & Onboarding**:
- **FR-001**: Web app MUST provide account registration form with email and password fields
- **FR-002**: Web app MUST provide login form with email and password fields, plus "Forgot Password" link
- **FR-003**: Web app MUST display welcoming onboarding flow for new students explaining course structure and navigation
- **FR-004**: Web app MUST persist authentication state across browser sessions using secure session management
- **FR-005**: Web app MUST provide logout functionality accessible from user menu in header

**Course Content Viewing**:
- **FR-006**: Web app MUST display all 6 course chapters in a browsable course catalog or table of contents
- **FR-007**: Web app MUST render chapter content with rich formatting (headings, paragraphs, code blocks, lists, bold/italic)
- **FR-008**: Web app MUST provide chapter navigation controls (previous, next, back to table of contents)
- **FR-009**: Web app MUST show estimated reading time and reading progress indicator for current chapter
- **FR-010**: Web app MUST support keyword search across all course content with results highlighting
- **FR-011**: Web app MUST display learning objectives at the beginning of each chapter
- **FR-012**: Web app MUST provide responsive reading experience optimized for mobile, tablet, and desktop screen sizes

**Quiz Interface**:
- **FR-013**: Web app MUST display quiz questions in clear, uncluttered format with one question visible at a time or all questions on a single scrollable page (configurable)
- **FR-014**: Web app MUST provide appropriate input controls for each question type (radio buttons for multiple-choice, checkboxes for true/false, text area for short-answer)
- **FR-015**: Web app MUST show quiz progress indicator (e.g., "Question 3 of 10")
- **FR-016**: Web app MUST auto-save quiz progress every 30 seconds to prevent data loss
- **FR-017**: Web app MUST display quiz results with visual indicators for correct/incorrect answers
- **FR-018**: Web app MUST show explanations for each answer inline with results
- **FR-019**: Web app MUST calculate and display quiz score prominently with pass/fail status
- **FR-020**: Web app MUST allow quiz retakes with "Retake Quiz" button

**Progress Dashboard**:
- **FR-021**: Web app MUST display visual progress dashboard showing chapters completed as percentage (e.g., "4/6 chapters complete - 67%")
- **FR-022**: Web app MUST show learning streak count with visual indicator (e.g., flame icon with number)
- **FR-023**: Web app MUST display quiz scores for each completed chapter with visual performance summary
- **FR-024**: Web app MUST show total study time aggregated across all sessions
- **FR-025**: Web app MUST provide milestone celebrations with visual badges or animations
- **FR-026**: Web app MUST display personalized "Next Steps" suggestions based on progress

**Freemium Access Control**:
- **FR-027**: Web app MUST clearly indicate which chapters are free (1-3) vs premium (4-6) in table of contents
- **FR-028**: Web app MUST block access to premium content for free-tier students with elegant upgrade modal
- **FR-029**: Web app MUST display pricing comparison table in upgrade modal showing free vs premium benefits
- **FR-030**: Web app MUST provide one-click upgrade flow directing to payment/subscription page

**Phase 2 Features (if available)**:
- **FR-031**: Web app MUST display adaptive learning path recommendations as visual roadmap or flowchart
- **FR-032**: Web app MUST show reasoning for each recommendation with expandable explanations
- **FR-033**: Web app MUST provide open-ended assessment submission form with text editor (50-500 word limit with character counter)
- **FR-034**: Web app MUST display LLM-graded feedback with quality score badge and color-coded strengths/improvements
- **FR-035**: Web app MUST show usage quota status for premium features (e.g., "7/10 adaptive paths used this month")

**Responsive Design**:
- **FR-036**: Web app MUST render correctly on mobile devices (320px to 768px width)
- **FR-037**: Web app MUST render correctly on tablets (768px to 1024px width)
- **FR-038**: Web app MUST render correctly on desktop screens (1024px and wider)
- **FR-039**: Web app MUST support portrait and landscape orientations on mobile and tablet
- **FR-040**: Web app MUST provide touch-optimized controls for mobile/tablet (larger tap targets, swipe gestures)

**Navigation & Usability**:
- **FR-041**: Web app MUST provide persistent navigation header with logo, course menu, and user account menu
- **FR-042**: Web app MUST include sidebar navigation (desktop) or bottom navigation bar (mobile) for quick access to dashboard, chapters, quizzes, progress
- **FR-043**: Web app MUST support browser back/forward button for natural navigation
- **FR-044**: Web app MUST provide breadcrumb navigation showing current location (e.g., "Home > Chapter 2 > Section 2.3")
- **FR-045**: Web app MUST implement keyboard navigation for accessibility (tab order, enter to activate, escape to close modals)

**Performance & Loading States**:
- **FR-046**: Web app MUST display loading skeletons while content is fetching (not blank screens or spinners alone)
- **FR-047**: Web app MUST cache previously viewed content for instant re-access
- **FR-048**: Web app MUST prefetch next chapter content while student is reading current chapter
- **FR-049**: Web app MUST show real-time progress indicators for long-running operations (e.g., "Generating adaptive path... 50%")
- **FR-050**: Web app MUST load initial page (dashboard or login) within 2 seconds on typical broadband connection

**Error Handling & Offline Support**:
- **FR-051**: Web app MUST display user-friendly error messages for API failures (not technical stack traces)
- **FR-052**: Web app MUST detect offline status and show appropriate messaging
- **FR-053**: Web app MUST allow reading previously viewed content while offline
- **FR-054**: Web app MUST queue progress updates while offline and sync when connection restored
- **FR-055**: Web app MUST prompt user to retry failed operations with clear "Retry" button

**Accessibility**:
- **FR-056**: Web app MUST meet WCAG 2.1 Level AA accessibility standards
- **FR-057**: Web app MUST support screen readers with appropriate ARIA labels and semantic HTML
- **FR-058**: Web app MUST provide sufficient color contrast for readability (minimum 4.5:1 for normal text)
- **FR-059**: Web app MUST allow keyboard-only navigation without requiring mouse
- **FR-060**: Web app MUST provide text alternatives for all images and icons

### Key Entities

*Note: Phase 3 (web app) primarily consumes data from backend APIs. No new data entities are introduced. Web app works with existing entities: Student, Chapter, Quiz, Progress, Subscription, AdaptivePath, AssessmentFeedback (from Phase 1 & 2).*

**UI Components** (not database entities, but key UI elements):
- **Dashboard**: Visual overview of student progress, streaks, and next steps
- **CourseViewer**: Rich-text chapter content renderer with navigation
- **QuizInterface**: Interactive quiz presentation with question controls and results display
- **ProgressChart**: Visual representation of completion percentage and milestones
- **AdaptivePathRoadmap**: Flowchart visualization of personalized recommendations (Phase 2)
- **AssessmentEditor**: Text editor for open-ended answer submission (Phase 2)
- **UpgradeModal**: Pricing comparison and subscription upgrade interface

## Success Criteria

### Measurable Outcomes

**Feature Parity**:
- **SC-001**: Web app provides 100% feature parity with ChatGPT App (all Phase 1 and Phase 2 features accessible)
- **SC-002**: Students can complete full learning journey (registration to course completion) entirely through web app without using ChatGPT App
- **SC-003**: All API endpoints used by ChatGPT App are also used by web app with identical responses

**Responsive Design**:
- **SC-004**: Web app renders without horizontal scrolling or layout breaks on screen widths from 320px to 2560px
- **SC-005**: Touch targets (buttons, links) are minimum 44x44px on mobile for easy tapping
- **SC-006**: Web app loads and is fully interactive within 2 seconds on desktop, 3 seconds on mobile (p95)

**User Experience**:
- **SC-007**: 85% of students successfully complete first chapter reading on first attempt without navigation confusion
- **SC-008**: 90% of students report web app UI is intuitive and easy to use (post-usage survey)
- **SC-009**: Students complete quizzes 30% faster on web app vs ChatGPT App (due to visual presentation and direct input controls)
- **SC-010**: 70% of new registrations occur via web app (vs ChatGPT App) after Phase 3 launch

**Visual Enhancements**:
- **SC-011**: Progress dashboard loads within 1 second and displays accurate real-time data
- **SC-012**: 80% of students check progress dashboard at least weekly (engagement metric)
- **SC-013**: Visual roadmap for adaptive learning paths improves feature adoption by 40% compared to text-only recommendations

**Accessibility**:
- **SC-014**: Web app achieves WCAG 2.1 Level AA compliance (verified by automated and manual audits)
- **SC-015**: Students using screen readers successfully complete learning tasks (registration, chapter reading, quiz taking) with zero critical barriers

**Performance**:
- **SC-016**: Initial page load (dashboard) completes in under 2 seconds for 95% of users (p95)
- **SC-017**: Chapter content loads in under 1 second after navigation click (p95)
- **SC-018**: Web app achieves Lighthouse performance score of 90+ (desktop) and 80+ (mobile)

**Offline & Resilience**:
- **SC-019**: Students can read previously viewed content offline without errors or blank screens
- **SC-020**: Progress synchronizes within 5 seconds after connection restored following offline period
- **SC-021**: Web app handles API errors gracefully with friendly messaging in 100% of error scenarios (no unhandled exceptions shown to users)

**Conversion & Business Impact**:
- **SC-022**: Premium conversion rate increases by 15% after Phase 3 launch (web app upgrade modal more effective than ChatGPT upgrade prompts)
- **SC-023**: 60% of premium subscribers use web app as primary learning interface (vs ChatGPT App)
- **SC-024**: Student retention improves by 20% (measured by 30-day active users) after web app launch

**Cross-Device Experience**:
- **SC-025**: Students who switch between devices (mobile to desktop, or vice versa) experience seamless progress synchronization within 5 seconds
- **SC-026**: 40% of students use multiple devices to access web app during their learning journey
- **SC-027**: Zero reports of progress loss or data inconsistency when switching devices

## Assumptions

1. **Phase 1 API Availability**: All Phase 1 backend APIs (/api/v1/*) are fully operational, stable, and documented with OpenAPI specifications before web app development begins.

2. **Phase 2 Optional**: Web app can launch with only Phase 1 features functional. Phase 2 features (adaptive paths, LLM assessments) are conditionally displayed if available.

3. **Modern Browser Support**: Web app targets modern evergreen browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+). Internet Explorer is not supported.

4. **Stable Backend**: Backend APIs maintain backward compatibility and do not introduce breaking changes during web app development and deployment.

5. **Content Format Compatibility**: Course content (chapters, quizzes) is formatted in a web-friendly structure (markdown or JSON) that can be rendered in HTML.

6. **Authentication Mechanism**: Backend provides JWT-based authentication that web app can use for session management and API requests.

7. **CORS Configuration**: Backend APIs are configured to allow cross-origin requests from web app domain (e.g., app.course-companion.com).

8. **CDN for Assets**: Static assets (images, fonts, CSS/JS bundles) can be served via CDN for optimal global performance.

9. **Mobile-First Users**: Significant portion of students (40%+) will access web app primarily via mobile devices, necessitating mobile-first design approach.

10. **Analytics Tracking**: Web app includes analytics instrumentation to measure user behavior, conversion funnels, and performance metrics for data-driven optimization.

## Out of Scope (Phase 3)

The following features are explicitly excluded from Phase 3:

- **Native Mobile Apps**: No iOS or Android native apps. Web app serves as mobile-responsive alternative (Future)
- **Real-Time Collaboration**: No features for students to learn together synchronously or share progress with peers (Future)
- **Instructor Dashboard**: No tools for instructors to manage courses, view student analytics, or grade manually (Future)
- **Course Authoring Tools**: No in-app content creation or editing. Content managed separately by authors (Future)
- **Advanced Gamification**: Basic progress tracking included, but no leaderboards, badges, or competitive features (Future)
- **Video Content**: Only text-based course content supported. No video lectures or interactive media (Future)
- **Third-Party Integrations**: No LMS integrations (Canvas, Moodle), calendar sync, or social media sharing (Future)
- **Localization**: English-only UI. Multi-language support is Future
- **Offline-First Architecture**: Limited offline support (cached content readable). Full offline-first with service workers is Future
- **Push Notifications**: No browser push notifications for streak reminders or new content alerts (Future)

## Dependencies

**External Systems**:
- **Phase 1 Backend APIs**: All /api/v1/* endpoints must be operational and documented
- **Phase 2 Backend APIs**: Optional /api/v2/* endpoints for premium features (if Phase 2 deployed)
- **Authentication Service**: JWT token issuance and verification from backend
- **Content Delivery**: Course content available via backend APIs (chapters, quizzes, media)

**Pre-Implementation Requirements**:
- Backend API documentation (OpenAPI specification) complete and accurate
- Design system (color palette, typography, component library) defined
- User flow diagrams and wireframes approved
- Responsive breakpoints and layouts specified
- Accessibility requirements reviewed and prioritized

**Infrastructure**:
- Web hosting platform with CDN support for static assets
- SSL/TLS certificates for secure HTTPS connections
- Domain name configured (e.g., app.course-companion.com)
- Analytics platform (Google Analytics, Mixpanel, or similar)
- Error monitoring and logging service (Sentry, LogRocket, or similar)

## Open Questions

*Note: Making informed assumptions for all aspects to avoid [NEEDS CLARIFICATION] markers.*

1. **Design System Preferences**: Should web app use existing design system or create custom theme?
   - **Assumption**: Use shadcn/ui components with custom theme matching brand colors. This provides professional UI components out-of-box while allowing brand customization.

2. **Mobile Navigation Pattern**: Should mobile use bottom tab bar or hamburger menu?
   - **Assumption**: Bottom tab bar navigation for primary sections (Dashboard, Chapters, Quizzes, Progress, Profile) as it's more thumb-friendly on modern large-screen phones. Hamburger menu for secondary actions.

3. **Quiz Presentation**: Should quizzes show one question at a time or all questions on scrollable page?
   - **Assumption**: Default to one question at a time on mobile (less overwhelming, clearer focus), all questions on single page for desktop (easier to review before submitting). User can toggle preference in settings.

## Risks & Mitigations

**Risk 1: Cross-Browser Compatibility Issues**
- **Impact**: Web app may render differently or have bugs in specific browsers (especially Safari), frustrating users
- **Mitigation**: Test on all major browsers (Chrome, Firefox, Safari, Edge) during development. Use progressive enhancement approach. Include automated cross-browser testing in CI/CD. Monitor browser-specific error reports in production.

**Risk 2: Mobile Performance on Low-End Devices**
- **Impact**: Web app may be slow or unresponsive on older or budget smartphones, limiting accessibility
- **Mitigation**: Optimize bundle size (code splitting, lazy loading). Test on low-end devices (older iPhones, budget Android). Use lighthouse performance audits. Implement performance budgets. Consider lite mode for very slow connections.

**Risk 3: ChatGPT App Cannibalization**
- **Impact**: If web app is superior experience, students may abandon ChatGPT App, reducing reach of 800M+ ChatGPT users
- **Mitigation**: Position web app as complementary (visual enhancements) not replacement. Ensure feature parity, not superiority. Maintain ChatGPT App as primary onboarding path. Cross-link between platforms (ChatGPT can suggest "View progress dashboard on web app").

**Risk 4: API Rate Limiting**
- **Impact**: Web app may trigger more API calls than ChatGPT App (due to real-time updates, prefetching), hitting rate limits
- **Mitigation**: Implement aggressive caching strategy. Use optimistic UI updates (show changes immediately, sync in background). Batch multiple requests where possible. Monitor API usage patterns and adjust limits if needed. Consider separate rate limits for web app vs ChatGPT App.

**Risk 5: Inconsistent State Across Devices**
- **Impact**: Student's progress may appear different on web app vs ChatGPT App if sync fails or is delayed
- **Mitigation**: Implement real-time synchronization using WebSockets or polling (every 5 seconds). Show clear sync status indicator ("Syncing..." / "Synced"). Handle conflicts gracefully (last-write-wins with timestamp comparison). Test multi-device scenarios extensively.

**Risk 6: Accessibility Compliance Gaps**
- **Impact**: Failing WCAG 2.1 Level AA could exclude students with disabilities and create legal/ethical issues
- **Mitigation**: Conduct accessibility audit early in development. Use automated tools (axe, Lighthouse) in CI/CD. Include manual testing with screen readers. Consult accessibility expert for review. Prioritize fixes before launch. Provide accessibility feedback channel for users to report issues.

---

**This specification is ready for planning phase via `/sp.plan`.**
