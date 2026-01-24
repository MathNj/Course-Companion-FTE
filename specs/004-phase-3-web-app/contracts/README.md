# Component Contracts: Phase 3 - Web Application Course Companion

**Date**: 2026-01-24
**Feature**: Phase 3 - Web Application Course Companion
**Purpose**: Define reusable UI components, props interfaces, accessibility requirements, and usage examples

## Overview

This document specifies 30+ React components organized into three categories:
1. **Layout Components**: Structural components for responsive design
2. **Feature Components**: Domain-specific components (dashboard, chapters, quizzes, progress)
3. **Base UI Components**: shadcn/ui components (buttons, cards, dialogs, forms)

Each component includes:
- TypeScript props interface
- Accessibility (a11y) requirements (WCAG 2.1 Level AA)
- Responsive behavior
- Usage examples with code snippets

---

## Layout Components

### 1. Header

Top navigation bar with logo, user menu, and responsive design.

**Props**:
```typescript
interface HeaderProps {
  user?: User;               // Current authenticated user (undefined if not logged in)
  onLogout?: () => void;     // Logout callback
  className?: string;        // Additional CSS classes
}
```

**Accessibility**:
- Navigation landmark (`<nav role="navigation">`)
- Keyboard navigation (Tab order: logo → nav items → user menu)
- User menu: `aria-haspopup="true"`, `aria-expanded` state
- Logout button: `aria-label="Log out"`

**Responsive**:
- Mobile (<768px): Logo + hamburger menu (opens sidebar)
- Tablet (768-1024px): Logo + condensed nav + user avatar
- Desktop (>1024px): Logo + full nav + user menu with name

**Usage**:
```tsx
import { Header } from '@/components/layouts/Header';

<Header
  user={currentUser}
  onLogout={() => signOut()}
/>
```

---

### 2. Sidebar

Desktop sidebar navigation with chapter list, progress summary, and quick links.

**Props**:
```typescript
interface SidebarProps {
  currentPath: string;       // Current route (highlight active item)
  collapsed?: boolean;       // Collapsed state (icon-only)
  onToggle?: () => void;     // Toggle collapsed state
  className?: string;
}
```

**Accessibility**:
- Navigation landmark (`<nav aria-label="Main navigation">`)
- Current page indicated: `aria-current="page"`
- Keyboard navigation: Arrow keys to navigate, Enter to activate
- Focus management: Focus visible on keyboard navigation

**Responsive**:
- Mobile: Not rendered (BottomNav used instead)
- Tablet: Icon-only sidebar (collapsed by default)
- Desktop: Full sidebar with text labels

**Usage**:
```tsx
import { Sidebar } from '@/components/layouts/Sidebar';

<Sidebar
  currentPath={pathname}
  collapsed={sidebarCollapsed}
  onToggle={() => toggleSidebar()}
/>
```

---

### 3. BottomNav

Mobile bottom navigation bar with 4 primary tabs.

**Props**:
```typescript
interface BottomNavProps {
  activeTab: 'dashboard' | 'chapters' | 'progress' | 'profile';
  onTabChange: (tab: string) => void;
  className?: string;
}
```

**Accessibility**:
- Navigation landmark (`<nav role="navigation" aria-label="Mobile navigation">`)
- Each tab: `role="tab"`, `aria-selected` state
- Tab icons with text labels (not icon-only)
- Minimum touch target: 44x44px

**Responsive**:
- Mobile (<768px): Always visible (fixed bottom)
- Tablet (>768px): Hidden (Sidebar used instead)

**Usage**:
```tsx
import { BottomNav } from '@/components/layouts/BottomNav';

<BottomNav
  activeTab="dashboard"
  onTabChange={(tab) => router.push(`/${tab}`)}
/>
```

---

### 4. MobileLayout, TabletLayout, DesktopLayout

Responsive layout wrappers that conditionally render based on screen size.

**Props**:
```typescript
interface LayoutProps {
  children: React.ReactNode;
  header?: React.ReactNode;  // Custom header (optional)
  footer?: React.ReactNode;  // Custom footer (optional)
}
```

**Accessibility**:
- Semantic HTML: `<header>`, `<main>`, `<footer>`
- Skip to main content link (keyboard users)
- Focus management on route change

**Responsive**:
- MobileLayout: Single-column stack, bottom nav, no sidebar
- TabletLayout: Two-column, icon sidebar, condensed header
- DesktopLayout: Three-column, full sidebar, full header

**Usage**:
```tsx
import { MobileLayout, TabletLayout, DesktopLayout } from '@/components/layouts';

// Conditional rendering based on breakpoint
const isMobile = useMediaQuery('(max-width: 768px)');
const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1024px)');

{isMobile && <MobileLayout>{children}</MobileLayout>}
{isTablet && <TabletLayout>{children}</TabletLayout>}
{!isMobile && !isTablet && <DesktopLayout>{children}</DesktopLayout>}
```

---

## Feature Components: Dashboard

### 5. ProgressSummary

Visual overview of course progress with circular progress chart.

**Props**:
```typescript
interface ProgressSummaryProps {
  progress: ProgressSummary;  // From backend API
  className?: string;
}
```

**Accessibility**:
- Progress chart: `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`
- Text alternative: "67% complete - 4 of 6 chapters"
- Color is not sole indicator (use icons + text)

**Responsive**:
- Mobile: Single-column stack (chart above text)
- Desktop: Two-column (chart left, stats right)

**Usage**:
```tsx
import { ProgressSummary } from '@/components/features/dashboard/ProgressSummary';

const { data: progress } = useProgress();

<ProgressSummary progress={progress} />
```

---

### 6. StreakDisplay

Learning streak counter with flame icon and milestone celebrations.

**Props**:
```typescript
interface StreakDisplayProps {
  streak: Streak;
  showMilestone?: boolean;   // Show celebration if milestone reached
  className?: string;
}
```

**Accessibility**:
- Icon with text label: `<span aria-label="Current streak">🔥 7 days</span>`
- Milestone celebration: Announced via screen reader (aria-live region)
- Animation: `prefers-reduced-motion` media query respected

**Responsive**:
- Mobile: Icon + number (compact)
- Desktop: Icon + number + "days in a row" text

**Usage**:
```tsx
import { StreakDisplay } from '@/components/features/dashboard/StreakDisplay';

const { data: streak } = useStreak();

<StreakDisplay streak={streak} showMilestone={true} />
```

---

### 7. NextStepsCard

Personalized recommendation card showing next suggested action.

**Props**:
```typescript
interface NextStepsCardProps {
  recommendation: {
    title: string;           // e.g., "Continue Chapter 3"
    description: string;     // e.g., "You're 60% through Prompt Engineering"
    action: string;          // e.g., "Resume Reading"
    href: string;            // e.g., "/chapters/03-prompting"
  };
  className?: string;
}
```

**Accessibility**:
- Card as link (entire card clickable): `<a href={href}>...</a>`
- Action button: `aria-label` with full context
- Focus indicator on keyboard navigation

**Responsive**:
- Mobile: Full-width card
- Desktop: Card with hover effect (subtle lift)

**Usage**:
```tsx
import { NextStepsCard } from '@/components/features/dashboard/NextStepsCard';

<NextStepsCard
  recommendation={{
    title: "Start Chapter 4: RAG",
    description: "Dive into Retrieval-Augmented Generation",
    action: "Start Chapter",
    href: "/chapters/04-rag"
  }}
/>
```

---

### 8. MilestonesBadges

Display earned badges with hover tooltips showing achievement details.

**Props**:
```typescript
interface MilestonesBadgesProps {
  milestones: MilestoneEvent[];
  maxDisplay?: number;       // Max badges to show (default: 5)
  className?: string;
}
```

**Accessibility**:
- Badge images: `alt` text with achievement title
- Tooltip on hover: `aria-describedby` for screen readers
- Keyboard accessible: Focus on badges, Escape to close tooltip

**Responsive**:
- Mobile: Grid (2 columns)
- Desktop: Grid (5 columns) or horizontal list

**Usage**:
```tsx
import { MilestonesBadges } from '@/components/features/dashboard/MilestonesBadges';

<MilestonesBadges
  milestones={userMilestones}
  maxDisplay={5}
/>
```

---

## Feature Components: Chapters

### 9. ChapterViewer

Full chapter content renderer with markdown parsing and rich formatting.

**Props**:
```typescript
interface ChapterViewerProps {
  chapter: Chapter;
  onProgressUpdate?: (sectionId: string, timeSpent: number) => void;
  className?: string;
}
```

**Accessibility**:
- Semantic headings: `<h1>` (chapter title), `<h2>` (section titles), `<h3>` (subsections)
- Code blocks: Syntax highlighting with sufficient contrast (4.5:1 ratio)
- Images: `alt` text or descriptive `aria-label`
- Link text: Descriptive (not "click here")

**Responsive**:
- Mobile: Single-column, full-width text (max-width: 100%)
- Tablet: Single-column, max-width: 720px
- Desktop: Single-column, max-width: 800px, centered

**Usage**:
```tsx
import { ChapterViewer } from '@/components/features/chapters/ChapterViewer';

const { data: chapter } = useChapter('01-intro-genai');

<ChapterViewer
  chapter={chapter}
  onProgressUpdate={(sectionId, timeSpent) => updateProgress(sectionId, timeSpent)}
/>
```

---

### 10. ChapterNavigation

Previous/Next navigation buttons with chapter titles.

**Props**:
```typescript
interface ChapterNavigationProps {
  previousChapter?: { id: string; title: string };
  nextChapter?: { id: string; title: string };
  onNavigate?: (chapterId: string) => void;
  className?: string;
}
```

**Accessibility**:
- Button labels: "Previous: Introduction to Generative AI"
- Disabled state: `disabled` attribute + `aria-disabled="true"`
- Keyboard navigation: Tab to buttons, Enter to activate

**Responsive**:
- Mobile: Stacked buttons (Previous above Next)
- Desktop: Horizontal (Previous left, Next right)

**Usage**:
```tsx
import { ChapterNavigation } from '@/components/features/chapters/ChapterNavigation';

<ChapterNavigation
  previousChapter={{ id: '01', title: 'Introduction to Generative AI' }}
  nextChapter={{ id: '03', title: 'Prompt Engineering' }}
  onNavigate={(id) => router.push(`/chapters/${id}`)}
/>
```

---

### 11. TableOfContents

Floating sidebar table of contents with current section highlighting.

**Props**:
```typescript
interface TableOfContentsProps {
  sections: Section[];
  currentSectionId?: string; // Currently viewed section
  onSectionClick?: (sectionId: string) => void;
  className?: string;
}
```

**Accessibility**:
- Navigation landmark: `<nav aria-label="Table of contents">`
- Current section: `aria-current="location"`
- Keyboard: Arrow keys to navigate, Enter to jump to section

**Responsive**:
- Mobile: Hidden (collapse into dropdown)
- Tablet: Sticky sidebar (right side)
- Desktop: Sticky sidebar (right side, wider)

**Usage**:
```tsx
import { TableOfContents } from '@/components/features/chapters/TableOfContents';

<TableOfContents
  sections={chapter.sections}
  currentSectionId="01-what-is-genai"
  onSectionClick={(id) => scrollToSection(id)}
/>
```

---

### 12. ReadingProgress

Visual progress bar showing reading completion percentage.

**Props**:
```typescript
interface ReadingProgressProps {
  currentSection: number;   // 1-indexed
  totalSections: number;
  estimatedTimeRemaining?: number; // Minutes
  className?: string;
}
```

**Accessibility**:
- Progress bar: `role="progressbar"`, `aria-valuenow`, `aria-label="Reading progress: 40%"`
- Text alternative: "Section 3 of 8 - About 15 minutes remaining"

**Responsive**:
- Mobile: Compact bar (icon + percentage)
- Desktop: Full bar with text

**Usage**:
```tsx
import { ReadingProgress } from '@/components/features/chapters/ReadingProgress';

<ReadingProgress
  currentSection={3}
  totalSections={8}
  estimatedTimeRemaining={15}
/>
```

---

### 13. MarkdownRenderer

Markdown-to-HTML renderer with syntax highlighting and custom components.

**Props**:
```typescript
interface MarkdownRendererProps {
  content: string;          // Markdown content
  className?: string;
}
```

**Accessibility**:
- Code blocks: Syntax highlighting with WCAG AA contrast
- Links: Open external links in new tab with `rel="noopener noreferrer"`
- Tables: `<caption>` for table descriptions

**Responsive**:
- Mobile: Horizontal scroll for wide code blocks or tables
- Desktop: Full-width rendering

**Usage**:
```tsx
import { MarkdownRenderer } from '@/components/features/chapters/MarkdownRenderer';

<MarkdownRenderer content={section.content_markdown} />
```

---

## Feature Components: Quizzes

### 14. QuizInterface

Full quiz interface with questions, input controls, and submission.

**Props**:
```typescript
interface QuizInterfaceProps {
  quiz: Quiz;
  initialAnswers?: QuizAnswerInput; // Auto-saved answers
  onSubmit: (answers: QuizAnswerInput) => void;
  isSubmitting?: boolean;
  className?: string;
}
```

**Accessibility**:
- Form: `<form role="form" aria-label="Quiz">`
- Required fields: `aria-required="true"`
- Error messages: `aria-describedby` linking to error text
- Submit button: Disabled during submission with loading indicator

**Responsive**:
- Mobile: One question at a time (pagination)
- Desktop: All questions on single scrollable page

**Usage**:
```tsx
import { QuizInterface } from '@/components/features/quizzes/QuizInterface';

const { mutate: submitQuiz, isLoading } = useQuizSubmit();
const savedAnswers = useQuizStore((state) => state.savedAnswers['01-quiz']);

<QuizInterface
  quiz={quiz}
  initialAnswers={savedAnswers}
  onSubmit={(answers) => submitQuiz({ quiz_id: '01-quiz', answers })}
  isSubmitting={isLoading}
/>
```

---

### 15. QuestionCard

Single quiz question with appropriate input control (radio, checkbox, textarea).

**Props**:
```typescript
interface QuestionCardProps {
  question: Question;
  value?: string | boolean; // Current answer
  onChange: (value: string | boolean) => void;
  showFeedback?: boolean;   // Show correct/incorrect after submission
  feedback?: QuestionFeedback;
  className?: string;
}
```

**Accessibility**:
- Fieldset + legend: `<fieldset><legend>{question_text}</legend></fieldset>`
- Radio buttons: `role="radiogroup"`, each option `role="radio"`
- Textareas: `aria-label` or visible label
- Feedback: Color + icon (not color alone), `aria-live="polite"` for dynamic updates

**Responsive**:
- Mobile: Full-width inputs, stacked options
- Desktop: Horizontal options for radio buttons (if 2-4 options)

**Usage**:
```tsx
import { QuestionCard } from '@/components/features/quizzes/QuestionCard';

<QuestionCard
  question={question}
  value={answers[question.question_id]}
  onChange={(value) => updateAnswer(question.question_id, value)}
  showFeedback={submitted}
  feedback={result?.grading_details[question.question_id]}
/>
```

---

### 16. QuizResults

Results summary with score, pass/fail status, and per-question feedback.

**Props**:
```typescript
interface QuizResultsProps {
  result: QuizResult;
  quiz: Quiz;               // Original quiz for question text
  onRetake?: () => void;
  className?: string;
}
```

**Accessibility**:
- Status alert: `role="alert"` for pass/fail message
- Score: `aria-label="Score: 85 out of 100 - Passed"`
- Retake button: Clear label "Retake quiz to improve your score"

**Responsive**:
- Mobile: Stacked (score above feedback list)
- Desktop: Score in prominent card, feedback below

**Usage**:
```tsx
import { QuizResults } from '@/components/features/quizzes/QuizResults';

<QuizResults
  result={quizResult}
  quiz={quiz}
  onRetake={() => router.push(`/quizzes/${quiz.quiz_id}`)}
/>
```

---

### 17. AnswerFeedback

Per-question feedback with correct/incorrect indicator and explanation.

**Props**:
```typescript
interface AnswerFeedbackProps {
  question: Question;
  feedback: QuestionFeedback;
  userAnswer: string | boolean;
  className?: string;
}
```

**Accessibility**:
- Correct/incorrect icon + text (not icon alone)
- Explanation: Expandable details with `aria-expanded` state
- Color contrast: Green (#10b981) and red (#ef4444) meet WCAG AA

**Responsive**:
- Mobile: Compact (icon + summary, expand for full explanation)
- Desktop: Full explanation visible by default

**Usage**:
```tsx
import { AnswerFeedback } from '@/components/features/quizzes/AnswerFeedback';

<AnswerFeedback
  question={question}
  feedback={result.grading_details.q1}
  userAnswer={answers.q1}
/>
```

---

### 18. QuizProgress

Quiz progress indicator (e.g., "Question 3 of 10" or progress bar).

**Props**:
```typescript
interface QuizProgressProps {
  currentQuestion: number;  // 1-indexed
  totalQuestions: number;
  answeredCount?: number;   // Questions answered (not submitted)
  variant?: 'bar' | 'text'; // Display variant
  className?: string;
}
```

**Accessibility**:
- Progress bar: `role="progressbar"`, `aria-valuenow`, `aria-label="Quiz progress"`
- Text variant: Screen reader friendly "Question 3 of 10"

**Responsive**:
- Mobile: Compact bar or text
- Desktop: Full bar with text

**Usage**:
```tsx
import { QuizProgress } from '@/components/features/quizzes/QuizProgress';

<QuizProgress
  currentQuestion={3}
  totalQuestions={10}
  answeredCount={7}
  variant="bar"
/>
```

---

## Feature Components: Progress

### 19. ProgressChart

Visual chart (circular or bar) showing completion percentage.

**Props**:
```typescript
interface ProgressChartProps {
  percentage: number;       // 0-100
  label?: string;           // e.g., "Overall Progress"
  variant?: 'circular' | 'bar';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```

**Accessibility**:
- Chart: `role="img"`, `aria-label="Overall progress: 67%"`
- Text alternative always present
- Color + text (not color alone for status)

**Responsive**:
- Mobile: Smaller size (sm or md)
- Desktop: Larger size (md or lg)

**Usage**:
```tsx
import { ProgressChart } from '@/components/features/progress/ProgressChart';

<ProgressChart
  percentage={67}
  label="Course Completion"
  variant="circular"
  size="lg"
/>
```

---

### 20. ChapterProgressList

List of all chapters with completion status, quiz scores, and access indicators.

**Props**:
```typescript
interface ChapterProgressListProps {
  chapters: ChapterListItem[];
  onChapterClick?: (chapterId: string) => void;
  className?: string;
}
```

**Accessibility**:
- List: `<ul role="list">` (semantic HTML)
- Chapter items: Interactive elements with `aria-label` including status
- Locked chapters: `aria-disabled="true"`, visual lock icon + text

**Responsive**:
- Mobile: Single-column list, stacked info
- Tablet: Two-column grid
- Desktop: Three-column grid or wide single-column

**Usage**:
```tsx
import { ChapterProgressList } from '@/components/features/progress/ChapterProgressList';

const { data: chapters } = useChapters();

<ChapterProgressList
  chapters={chapters}
  onChapterClick={(id) => router.push(`/chapters/${id}`)}
/>
```

---

### 21. PerformanceInsights

Analytics card showing quiz averages, time spent, and trends.

**Props**:
```typescript
interface PerformanceInsightsProps {
  progress: ProgressSummary;
  className?: string;
}
```

**Accessibility**:
- Data tables: `<table>` with `<caption>`
- Trend indicators: Icon + text (e.g., "↑ 12% improvement")
- Numbers: `aria-label` for context (e.g., "Average quiz score: 85%")

**Responsive**:
- Mobile: Stacked cards (one metric per card)
- Desktop: Grid (3-4 metrics side-by-side)

**Usage**:
```tsx
import { PerformanceInsights } from '@/components/features/progress/PerformanceInsights';

<PerformanceInsights progress={progressSummary} />
```

---

## Feature Components: Adaptive Learning (Phase 2)

### 22. AdaptivePathRoadmap

Visual flowchart showing personalized learning path with connecting lines.

**Props**:
```typescript
interface AdaptivePathRoadmapProps {
  path: AdaptivePath;
  onChapterClick?: (chapterId: string) => void;
  className?: string;
}
```

**Accessibility**:
- SVG flowchart: `role="img"`, `aria-label="Your personalized learning path"`
- Nodes: Interactive elements with chapter title + reason
- Keyboard: Tab to nodes, Enter to open chapter

**Responsive**:
- Mobile: Vertical list (simplified, no connecting lines)
- Tablet: Simplified flowchart (fewer visual elements)
- Desktop: Full flowchart with connecting lines and hover tooltips

**Usage**:
```tsx
import { AdaptivePathRoadmap } from '@/components/features/adaptive/AdaptivePathRoadmap';

const { data: path } = useAdaptivePath();

<AdaptivePathRoadmap
  path={path}
  onChapterClick={(id) => router.push(`/chapters/${id}`)}
/>
```

---

### 23. RecommendationCard

Single recommendation card with reason, difficulty match, and benefit.

**Props**:
```typescript
interface RecommendationCardProps {
  recommendation: PathRecommendation;
  onAccept?: () => void;
  className?: string;
}
```

**Accessibility**:
- Card as article: `<article aria-labelledby="rec-title">`
- Difficulty badge: Color + icon + text
- Accept button: Clear action "Start Chapter 4: RAG"

**Responsive**:
- Mobile: Full-width card
- Desktop: Card with hover effect

**Usage**:
```tsx
import { RecommendationCard } from '@/components/features/adaptive/RecommendationCard';

<RecommendationCard
  recommendation={rec}
  onAccept={() => router.push(`/chapters/${rec.chapter_id}`)}
/>
```

---

### 24. PathVisualization

Interactive visualization of learning path (graph or timeline).

**Props**:
```typescript
interface PathVisualizationProps {
  recommendations: PathRecommendation[];
  currentChapter?: string;  // Highlight current position
  variant?: 'graph' | 'timeline';
  className?: string;
}
```

**Accessibility**:
- SVG with semantic structure: `<svg role="img" aria-label="Learning path visualization">`
- Interactive nodes: `role="button"`, keyboard accessible
- Fallback: Text-based list for screen readers

**Responsive**:
- Mobile: Timeline variant (vertical)
- Desktop: Graph variant (nodes and edges)

**Usage**:
```tsx
import { PathVisualization } from '@/components/features/adaptive/PathVisualization';

<PathVisualization
  recommendations={path.recommendations}
  currentChapter="02-llms"
  variant="timeline"
/>
```

---

## Feature Components: Assessments (Phase 2)

### 25. AssessmentEditor

Rich text editor for open-ended assessment answers with character counter.

**Props**:
```typescript
interface AssessmentEditorProps {
  question: string;
  value: string;
  onChange: (value: string) => void;
  minWords?: number;        // Default: 50
  maxWords?: number;        // Default: 500
  className?: string;
}
```

**Accessibility**:
- Textarea: `aria-label` with question text
- Character counter: `aria-live="polite"` for updates
- Validation errors: `aria-describedby` linking to error message

**Responsive**:
- Mobile: Full-screen editor on focus
- Desktop: Resizable textarea

**Usage**:
```tsx
import { AssessmentEditor } from '@/components/features/assessments/AssessmentEditor';

<AssessmentEditor
  question="Explain the difference between RAG and fine-tuning"
  value={answer}
  onChange={setAnswer}
  minWords={50}
  maxWords={500}
/>
```

---

### 26. FeedbackViewer

Display LLM-graded feedback with quality score, strengths, and improvements.

**Props**:
```typescript
interface FeedbackViewerProps {
  feedback: AssessmentFeedback;
  onRevisit?: (chapterId: string) => void;
  className?: string;
}
```

**Accessibility**:
- Quality score: `role="status"`, `aria-label="Quality score: 85 out of 100"`
- Strengths/improvements: Color-coded + icons (green/amber)
- Chapter references: Links with descriptive text

**Responsive**:
- Mobile: Stacked sections (score, strengths, improvements, references)
- Desktop: Grid layout (score prominent, sections side-by-side)

**Usage**:
```tsx
import { FeedbackViewer } from '@/components/features/assessments/FeedbackViewer';

<FeedbackViewer
  feedback={assessmentFeedback}
  onRevisit={(id) => router.push(`/chapters/${id}`)}
/>
```

---

### 27. QualityScoreBadge

Visual badge showing assessment quality score (0-100).

**Props**:
```typescript
interface QualityScoreBadgeProps {
  score: number;            // 0-100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;      // Show "Quality Score" text
  className?: string;
}
```

**Accessibility**:
- Badge: `role="status"`, `aria-label="Quality score: 85%"`
- Color + text (not color alone): 0-59 (red), 60-79 (amber), 80-100 (green)

**Responsive**:
- Mobile: Smaller size (sm or md)
- Desktop: Larger size (md or lg)

**Usage**:
```tsx
import { QualityScoreBadge } from '@/components/features/assessments/QualityScoreBadge';

<QualityScoreBadge score={85} size="lg" showLabel={true} />
```

---

### 28. CharacterCounter

Live character/word counter for text inputs with validation feedback.

**Props**:
```typescript
interface CharacterCounterProps {
  current: number;          // Current word count
  min?: number;             // Minimum required
  max?: number;             // Maximum allowed
  unit?: 'words' | 'characters';
  className?: string;
}
```

**Accessibility**:
- Counter: `aria-live="polite"` for live updates
- Validation state: Color + icon + text (e.g., "50 / 500 words ✓")

**Responsive**:
- Mobile: Compact (just numbers)
- Desktop: Full text (e.g., "250 words (50-500 required)")

**Usage**:
```tsx
import { CharacterCounter } from '@/components/features/assessments/CharacterCounter';

const wordCount = answer.trim().split(/\s+/).length;

<CharacterCounter
  current={wordCount}
  min={50}
  max={500}
  unit="words"
/>
```

---

## Feature Components: Upgrade

### 29. UpgradeModal

Modal dialog showing premium upgrade benefits and call-to-action.

**Props**:
```typescript
interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  trigger?: 'chapter_locked' | 'feature_gated' | 'manual';
  className?: string;
}
```

**Accessibility**:
- Dialog: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` (modal title)
- Focus trap: Focus stays inside modal when open
- Close button: `aria-label="Close upgrade modal"`
- Escape key: Closes modal

**Responsive**:
- Mobile: Full-screen modal
- Desktop: Centered modal (max-width: 600px)

**Usage**:
```tsx
import { UpgradeModal } from '@/components/features/upgrade/UpgradeModal';

<UpgradeModal
  isOpen={upgradeModalOpen}
  onClose={() => setUpgradeModalOpen(false)}
  trigger="chapter_locked"
/>
```

---

### 30. PricingTable

Comparison table showing free vs premium features with pricing.

**Props**:
```typescript
interface PricingTableProps {
  onSelectPlan?: (tier: 'free' | 'premium') => void;
  currentTier?: 'free' | 'premium';
  className?: string;
}
```

**Accessibility**:
- Table: `<table>` with `<caption>` "Feature comparison"
- Headers: `<th scope="col">` for column headers
- Current plan: `aria-current="true"` on selected tier

**Responsive**:
- Mobile: Stacked cards (free above premium)
- Desktop: Side-by-side columns

**Usage**:
```tsx
import { PricingTable } from '@/components/features/upgrade/PricingTable';

<PricingTable
  onSelectPlan={(tier) => initiateUpgrade(tier)}
  currentTier="free"
/>
```

---

### 31. FeatureComparison

List of features with checkmarks showing free vs premium availability.

**Props**:
```typescript
interface FeatureComparisonProps {
  features: {
    name: string;
    free: boolean;
    premium: boolean;
    description?: string;
  }[];
  className?: string;
}
```

**Accessibility**:
- List: `<ul role="list">`
- Checkmarks/X: Icon + text (e.g., "✓ Included" or "✗ Not included")
- Tooltip descriptions: `aria-describedby` for additional context

**Responsive**:
- Mobile: Single-column list
- Desktop: Two-column grid

**Usage**:
```tsx
import { FeatureComparison } from '@/components/features/upgrade/FeatureComparison';

const features = [
  { name: 'Chapters 1-3', free: true, premium: true },
  { name: 'Chapters 4-6', free: false, premium: true },
  { name: 'Adaptive Learning Path', free: false, premium: true },
];

<FeatureComparison features={features} />
```

---

## Base UI Components (shadcn/ui)

These components are from shadcn/ui library (Radix UI + Tailwind). Copied into codebase for full control.

### 32. Button

**Props**: Standard button props + variants (default, destructive, outline, ghost, link)
**Accessibility**: Native `<button>` with proper `aria-label` when icon-only
**Usage**: See [shadcn/ui Button docs](https://ui.shadcn.com/docs/components/button)

### 33. Card

**Props**: Container component with header, content, footer sections
**Accessibility**: Semantic `<article>` or `<section>` with proper headings
**Usage**: See [shadcn/ui Card docs](https://ui.shadcn.com/docs/components/card)

### 34. Dialog (Modal)

**Props**: Open/close state, trigger, content
**Accessibility**: Radix Dialog primitive (WCAG AA compliant)
**Usage**: See [shadcn/ui Dialog docs](https://ui.shadcn.com/docs/components/dialog)

### 35. Skeleton

**Props**: Variant (text, circle, rectangle), loading state
**Accessibility**: `aria-busy="true"`, `aria-label="Loading..."`
**Usage**: See [shadcn/ui Skeleton docs](https://ui.shadcn.com/docs/components/skeleton)

### 36. Progress

**Props**: Value (0-100), max, aria-label
**Accessibility**: Native `<progress>` with ARIA attributes
**Usage**: See [shadcn/ui Progress docs](https://ui.shadcn.com/docs/components/progress)

### 37. Badge

**Props**: Variant (default, secondary, destructive, outline)
**Accessibility**: `role="status"` when showing dynamic status
**Usage**: See [shadcn/ui Badge docs](https://ui.shadcn.com/docs/components/badge)

### 38. Input

**Props**: Standard input props, type, placeholder, disabled
**Accessibility**: Associated `<label>`, `aria-invalid` on error
**Usage**: See [shadcn/ui Input docs](https://ui.shadcn.com/docs/components/input)

### 39. Textarea

**Props**: Standard textarea props, rows, maxLength
**Accessibility**: Associated `<label>`, `aria-describedby` for hints
**Usage**: See [shadcn/ui Textarea docs](https://ui.shadcn.com/docs/components/textarea)

### 40. RadioGroup

**Props**: Options, value, onChange
**Accessibility**: Radix RadioGroup (WCAG AA compliant)
**Usage**: See [shadcn/ui Radio Group docs](https://ui.shadcn.com/docs/components/radio-group)

### 41. Checkbox

**Props**: Checked, onChange, label
**Accessibility**: Radix Checkbox (WCAG AA compliant)
**Usage**: See [shadcn/ui Checkbox docs](https://ui.shadcn.com/docs/components/checkbox)

### 42. Select

**Props**: Options, value, onChange, placeholder
**Accessibility**: Radix Select (WCAG AA compliant, keyboard navigation)
**Usage**: See [shadcn/ui Select docs](https://ui.shadcn.com/docs/components/select)

### 43. Toast

**Props**: Title, description, variant (default, destructive)
**Accessibility**: `role="status"`, `aria-live="polite"`, auto-dismiss
**Usage**: See [shadcn/ui Toast docs](https://ui.shadcn.com/docs/components/toast)

---

## Responsive Design Tokens

### Breakpoints

```typescript
// tailwind.config.ts
export const breakpoints = {
  sm: '640px',   // Small tablets
  md: '768px',   // Tablets
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
};
```

### Usage in Tailwind

```tsx
// Mobile-first: default styles for mobile, add md: and lg: for larger
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* 1 column on mobile, 2 on tablet, 3 on desktop */}
</div>
```

---

## Accessibility Checklist (WCAG 2.1 Level AA)

All components MUST meet these requirements:

- [ ] **Keyboard Navigation**: Tab order logical, Enter/Space activate buttons
- [ ] **Focus Indicators**: Visible focus outline (not removed with `outline: none`)
- [ ] **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- [ ] **ARIA Labels**: Interactive elements have descriptive labels
- [ ] **Semantic HTML**: Use `<button>`, `<nav>`, `<main>`, not `<div onClick>`
- [ ] **Error Messages**: Errors announced via `aria-live` or `aria-describedby`
- [ ] **Form Validation**: Required fields marked with `aria-required`
- [ ] **Images**: All images have `alt` text or `aria-label`
- [ ] **Headings**: Logical heading hierarchy (h1 → h2 → h3, no skips)
- [ ] **Screen Reader Testing**: Test with NVDA (Windows) or VoiceOver (Mac)

---

**Component Contracts Complete. Ready for quickstart guide.**
