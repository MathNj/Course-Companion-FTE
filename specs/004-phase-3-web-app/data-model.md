# Data Model: Phase 3 - Web Application Course Companion

**Date**: 2026-01-24
**Feature**: Phase 3 - Web Application Course Companion
**Purpose**: Define frontend data structures, TypeScript interfaces, state management schemas, and data flows

## Overview

Phase 3 web app is a **presentation layer** that consumes backend APIs. This document defines:
1. TypeScript interfaces mirroring backend API responses
2. Client-side state management (React Query cache, Zustand stores)
3. Form validation schemas (Zod)
4. LocalStorage schemas (offline cache, quiz auto-save)

**Important**: Web app does NOT introduce new data entities. All entities defined in Phase 1 and Phase 2 data models. This document maps backend entities to frontend TypeScript types.

## TypeScript Interfaces (API Response Types)

### Authentication Types

```typescript
// lib/types/auth.ts

export interface User {
  user_id: string;           // UUID from backend
  email: string;
  full_name?: string;
  subscription_tier: 'free' | 'premium';
  subscription_expires_at?: string; // ISO 8601 date
  timezone: string;          // IANA timezone (e.g., "America/New_York")
  created_at: string;        // ISO 8601 timestamp
  last_active_at: string;    // ISO 8601 timestamp
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  timezone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;        // Seconds (typically 2592000 = 30 days)
  user: User;
}

export interface TokenPayload {
  user_id: string;
  email: string;
  subscription_tier: 'free' | 'premium';
  exp: number;               // Unix timestamp
}
```

---

### Chapter Types

```typescript
// lib/types/chapter.ts

export interface Section {
  section_id: string;        // e.g., "01-what-is-genai"
  title: string;
  order: number;
  estimated_time_minutes: number;
  content_markdown: string;  // Raw markdown content
}

export interface Chapter {
  chapter_id: string;        // e.g., "01-intro-genai"
  chapter_number: number;    // 1-6
  title: string;
  subtitle: string;
  access_tier: 'free' | 'premium';
  estimated_time_minutes: number;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  learning_objectives: string[];
  sections: Section[];
}

export interface ChapterListItem {
  chapter_id: string;
  chapter_number: number;
  title: string;
  subtitle: string;
  access_tier: 'free' | 'premium';
  estimated_time_minutes: number;
  difficulty_level: string;
  user_has_access: boolean;  // Computed by backend
  user_progress: {
    completion_status: 'not_started' | 'in_progress' | 'completed';
    quiz_score?: number;     // 0-100 or null
  } | null;
}

export interface ChapterListResponse {
  chapters: ChapterListItem[];
  total_chapters: number;
  user_subscription: 'free' | 'premium';
}
```

---

### Quiz Types

```typescript
// lib/types/quiz.ts

export type QuestionType = 'multiple-choice' | 'true-false' | 'short-answer';

export interface Question {
  question_id: string;       // e.g., "q1"
  question_text: string;
  type: QuestionType;
  options?: string[];        // For multiple-choice
  correct_answer?: string | boolean; // Not sent to frontend (answer key on backend)
  explanation_correct?: string;
  explanation_incorrect?: string;
  keywords?: string[];       // For short-answer
}

export interface Quiz {
  quiz_id: string;           // e.g., "01-quiz"
  chapter_id: string;
  passing_score: number;     // Typically 70
  questions: Question[];     // Without correct_answer field (security)
}

export interface QuizSubmission {
  answers: Record<string, string | boolean>; // { q1: "a", q2: false, q3: "RAG uses..." }
}

export interface QuestionFeedback {
  correct: boolean;
  explanation: string;
  score?: number;            // For short-answer (0-10 scale)
  feedback?: string;         // Additional feedback for short-answer
}

export interface QuizResult {
  quiz_id: string;
  score: number;             // 0-100
  passed: boolean;           // true if score >= passing_score
  grading_details: Record<string, QuestionFeedback>; // { q1: {...}, q2: {...} }
  submitted_at: string;      // ISO 8601 timestamp
}

export interface QuizAttempt {
  id: string;                // UUID
  quiz_id: string;
  chapter_id: string;
  score: number;
  passed: boolean;
  submitted_at: string;
}
```

---

### Progress Types

```typescript
// lib/types/progress.ts

export interface ChapterProgress {
  chapter_id: string;
  completion_status: 'not_started' | 'in_progress' | 'completed';
  quiz_score?: number;       // 0-100 or null
  time_spent_minutes: number;
  last_accessed_at: string;  // ISO 8601
  completed_at?: string;     // ISO 8601 or null
}

export interface Streak {
  current_streak: number;
  longest_streak: number;
  last_activity_date: string; // ISO 8601 date (YYYY-MM-DD)
}

export interface ProgressSummary {
  chapters_completed: number; // 0-6
  total_chapters: number;     // 6
  completion_percentage: number; // 0-100
  overall_quiz_average: number;  // 0-100
  total_time_spent_minutes: number;
  streak: Streak;
  next_recommended_chapter?: string; // chapter_id or null
}

export interface MilestoneEvent {
  type: 'streak' | 'chapter_complete' | 'quiz_perfect' | 'course_complete';
  title: string;
  description: string;
  achieved_at: string;       // ISO 8601
  badge_url?: string;        // URL to badge image
}
```

---

### Adaptive Learning Path Types (Phase 2)

```typescript
// lib/types/adaptive.ts

export interface PathRecommendation {
  chapter_id: string;
  chapter_title: string;
  reason: string;            // Why this chapter is recommended
  difficulty_match: 'perfect' | 'stretch' | 'review';
  estimated_benefit: string; // e.g., "Fill knowledge gap in RAG fundamentals"
}

export interface AdaptivePath {
  student_id: string;
  recommendations: PathRecommendation[];
  generated_at: string;      // ISO 8601
  reasoning: string;         // Overall explanation
}

export interface UsageQuota {
  feature: 'adaptive_path' | 'assessment_grading';
  used: number;
  limit: number;
  reset_at: string;          // ISO 8601
}
```

---

### Assessment Types (Phase 2)

```typescript
// lib/types/assessment.ts

export interface AssessmentSubmission {
  chapter_id: string;
  question: string;
  answer_text: string;       // 50-500 words
}

export interface AssessmentFeedback {
  assessment_id: string;
  chapter_id: string;
  question: string;
  student_answer: string;
  quality_score: number;     // 0-100
  strengths: string[];       // Array of positive aspects
  improvements: string[];    // Array of improvement suggestions
  chapter_references: {
    chapter_id: string;
    section_id?: string;
    reason: string;          // Why revisit this
  }[];
  graded_at: string;         // ISO 8601
}
```

---

## Client-Side State Management

### React Query Cache Keys

```typescript
// lib/api/queryKeys.ts

export const queryKeys = {
  // Authentication
  currentUser: ['auth', 'me'] as const,

  // Chapters
  chapters: ['chapters'] as const,
  chapter: (id: string) => ['chapters', id] as const,

  // Quizzes
  quiz: (id: string) => ['quizzes', id] as const,
  quizResults: (chapterId: string) => ['quizzes', 'results', chapterId] as const,

  // Progress
  progress: ['progress'] as const,
  streak: ['progress', 'streak'] as const,
  chapterProgress: (chapterId: string) => ['progress', 'chapter', chapterId] as const,

  // Phase 2 (Adaptive Learning)
  adaptivePath: ['adaptive', 'path'] as const,
  quotas: ['adaptive', 'quotas'] as const,

  // Phase 2 (Assessments)
  assessment: (id: string) => ['assessments', id] as const,
  assessmentFeedback: (id: string) => ['assessments', 'feedback', id] as const,
};
```

### React Query Configuration

```typescript
// lib/api/queryClient.ts

import { QueryClient } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,        // 5 minutes (chapters, quizzes)
      cacheTime: 24 * 60 * 60 * 1000,  // 24 hours
      retry: 2,                         // Retry failed requests 2 times
      refetchOnWindowFocus: true,       // Refetch on tab focus
      refetchOnReconnect: true,         // Refetch when internet reconnects
    },
    mutations: {
      retry: 1,                         // Retry mutations once
    },
  },
});

// Persist cache to LocalStorage for offline support
if (typeof window !== 'undefined') {
  const localStoragePersister = createSyncStoragePersister({
    storage: window.localStorage,
  });

  persistQueryClient({
    queryClient,
    persister: localStoragePersister,
    maxAge: 24 * 60 * 60 * 1000,       // 24 hours
  });
}
```

---

### Zustand Stores (UI State)

#### UI Store (Theme, Sidebar, Modals)

```typescript
// lib/stores/uiStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // Theme
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;

  // Sidebar (desktop)
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // Modals
  upgradeModalOpen: boolean;
  setUpgradeModalOpen: (open: boolean) => void;

  // Mobile bottom navigation
  activeTab: 'dashboard' | 'chapters' | 'progress' | 'profile';
  setActiveTab: (tab: 'dashboard' | 'chapters' | 'progress' | 'profile') => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),

      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      upgradeModalOpen: false,
      setUpgradeModalOpen: (open) => set({ upgradeModalOpen: open }),

      activeTab: 'dashboard',
      setActiveTab: (tab) => set({ activeTab: tab }),
    }),
    {
      name: 'ui-state',  // LocalStorage key
    }
  )
);
```

#### Quiz Store (Auto-Save State)

```typescript
// lib/stores/quizStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface QuizState {
  // Auto-saved answers
  savedAnswers: Record<string, Record<string, string | boolean>>; // { quiz_id: { q1: "a", q2: false } }
  saveAnswer: (quizId: string, questionId: string, answer: string | boolean) => void;
  clearQuizAnswers: (quizId: string) => void;

  // Last save timestamp
  lastSaved: Record<string, string>; // { quiz_id: ISO timestamp }
}

export const useQuizStore = create<QuizState>()(
  persist(
    (set) => ({
      savedAnswers: {},
      saveAnswer: (quizId, questionId, answer) =>
        set((state) => ({
          savedAnswers: {
            ...state.savedAnswers,
            [quizId]: {
              ...state.savedAnswers[quizId],
              [questionId]: answer,
            },
          },
          lastSaved: {
            ...state.lastSaved,
            [quizId]: new Date().toISOString(),
          },
        })),
      clearQuizAnswers: (quizId) =>
        set((state) => {
          const { [quizId]: _, ...restAnswers } = state.savedAnswers;
          const { [quizId]: __, ...restSaved } = state.lastSaved;
          return { savedAnswers: restAnswers, lastSaved: restSaved };
        }),
      lastSaved: {},
    }),
    {
      name: 'quiz-autosave', // LocalStorage key
    }
  )
);
```

#### Offline Store (Offline Cache State)

```typescript
// lib/stores/offlineStore.ts

import { create } from 'zustand';

interface OfflineState {
  isOnline: boolean;
  setOnline: (online: boolean) => void;

  pendingMutations: {
    id: string;
    type: 'quiz_submit' | 'progress_update';
    payload: any;
    timestamp: string;
  }[];
  addPendingMutation: (type: string, payload: any) => void;
  removePendingMutation: (id: string) => void;
  clearPendingMutations: () => void;
}

export const useOfflineStore = create<OfflineState>((set) => ({
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  setOnline: (online) => set({ isOnline: online }),

  pendingMutations: [],
  addPendingMutation: (type, payload) =>
    set((state) => ({
      pendingMutations: [
        ...state.pendingMutations,
        {
          id: crypto.randomUUID(),
          type: type as 'quiz_submit' | 'progress_update',
          payload,
          timestamp: new Date().toISOString(),
        },
      ],
    })),
  removePendingMutation: (id) =>
    set((state) => ({
      pendingMutations: state.pendingMutations.filter((m) => m.id !== id),
    })),
  clearPendingMutations: () => set({ pendingMutations: [] }),
}));
```

---

## Form Validation Schemas (Zod)

### Authentication Forms

```typescript
// lib/schemas/auth.ts

import { z } from 'zod';

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
});

export const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
  full_name: z.string().optional(),
  timezone: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
```

### Quiz Submission Form

```typescript
// lib/schemas/quiz.ts

import { z } from 'zod';

export const quizAnswerSchema = z.record(
  z.string(), // question_id
  z.union([z.string(), z.boolean()]) // answer (string for MC/SA, boolean for T/F)
);

export const quizSubmissionSchema = z.object({
  quiz_id: z.string().min(1, 'Quiz ID is required'),
  answers: quizAnswerSchema,
});

export type QuizAnswerInput = z.infer<typeof quizAnswerSchema>;
export type QuizSubmissionInput = z.infer<typeof quizSubmissionSchema>;
```

### Assessment Submission Form (Phase 2)

```typescript
// lib/schemas/assessment.ts

import { z } from 'zod';

export const assessmentSchema = z.object({
  chapter_id: z.string().min(1, 'Chapter ID is required'),
  question: z.string().min(1, 'Question is required'),
  answer_text: z
    .string()
    .min(50, 'Answer must be at least 50 words')
    .max(500, 'Answer must not exceed 500 words')
    .refine((text) => {
      const wordCount = text.trim().split(/\s+/).length;
      return wordCount >= 50 && wordCount <= 500;
    }, 'Answer must be between 50 and 500 words'),
});

export type AssessmentInput = z.infer<typeof assessmentSchema>;
```

---

## LocalStorage Schemas

### Cached Chapter Content

```typescript
// LocalStorage key: "chapter-cache-{chapter_id}"
// Value: JSON string

interface CachedChapter {
  chapter: Chapter;          // Full chapter data
  cachedAt: string;          // ISO 8601 timestamp
  expiresAt: string;         // ISO 8601 timestamp (24 hours from cachedAt)
}
```

### Reading Position

```typescript
// LocalStorage key: "reading-position-{chapter_id}"
// Value: JSON string

interface ReadingPosition {
  chapter_id: string;
  section_id: string;        // Current section being read
  scrollPosition: number;    // Scroll Y position (pixels)
  lastUpdated: string;       // ISO 8601 timestamp
}
```

### Quiz Auto-Save

```typescript
// LocalStorage key: "quiz-autosave" (managed by Zustand)
// Value: JSON string (Zustand persisted state)

// See useQuizStore above
```

---

## Data Flow Diagrams

### Chapter Viewing Flow

```
┌─────────┐         ┌────────────┐         ┌──────────────┐         ┌─────────┐
│ Browser │         │ React Query│         │ API Client   │         │ Backend │
└────┬────┘         └─────┬──────┘         └──────┬───────┘         └────┬────┘
     │                    │                       │                      │
     │ Navigate to        │                       │                      │
     │ /chapters/01       │                       │                      │
     ├───────────────────>│                       │                      │
     │                    │                       │                      │
     │                    │ Check cache           │                      │
     │                    │ (queryKey: ['chapters', '01'])                │
     │                    │                       │                      │
     │                    │ MISS                  │                      │
     │                    │                       │                      │
     │                    │ Fetch chapter         │                      │
     │                    ├──────────────────────>│                      │
     │                    │                       │                      │
     │                    │                       │ GET /v1/chapters/01  │
     │                    │                       │ Authorization: Bearer
     │                    │                       ├─────────────────────>│
     │                    │                       │                      │
     │                    │                       │<─────────────────────┤
     │                    │                       │ 200 OK {chapter}     │
     │                    │                       │                      │
     │                    │<──────────────────────┤                      │
     │                    │ Chapter data          │                      │
     │                    │                       │                      │
     │                    │ Cache (5 min TTL)     │                      │
     │                    │                       │                      │
     │<───────────────────┤                       │                      │
     │ Render chapter     │                       │                      │
     │                    │                       │                      │
     │                    │ Prefetch next chapter │                      │
     │                    │ (queryKey: ['chapters', '02'])                │
     │                    ├──────────────────────>│                      │
     │                    │                       ├─────────────────────>│
     │                    │                       │                      │
```

### Quiz Submission Flow (with Auto-Save)

```
┌─────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐    ┌─────────┐
│ Browser │    │ QuizStore │    │ React Query│    │ API      │    │ Backend │
└────┬────┘    └─────┬─────┘    └─────┬──────┘    └────┬─────┘    └────┬────┘
     │               │                 │                │               │
     │ Type answer   │                 │                │               │
     │ (q1: "a")     │                 │                │               │
     ├──────────────>│                 │                │               │
     │               │                 │                │               │
     │               │ saveAnswer()    │                │               │
     │               │ (auto-save to   │                │               │
     │               │  LocalStorage)  │                │               │
     │               │                 │                │               │
     │ Click Submit  │                 │                │               │
     ├──────────────────────────────────>│                │               │
     │               │                 │                │               │
     │               │                 │ Mutation       │               │
     │               │                 │ (optimistic)   │               │
     │               │                 │                │               │
     │               │                 │ POST /v1/quizzes/01/submit     │
     │               │                 ├───────────────>│               │
     │               │                 │                │               │
     │               │                 │                │ POST /v1/...  │
     │               │                 │                ├──────────────>│
     │               │                 │                │               │
     │               │                 │                │<──────────────┤
     │               │                 │                │ 200 {result}  │
     │               │                 │                │               │
     │               │                 │<───────────────┤               │
     │               │                 │ QuizResult     │               │
     │               │                 │                │               │
     │<──────────────────────────────────┤                │               │
     │ Show results  │                 │                │               │
     │               │                 │                │               │
     │               │ clearQuizAnswers()               │               │
     │               │ (remove autosave)                │               │
     │               │                 │                │               │
```

### Offline Sync Flow

```
┌─────────┐    ┌──────────────┐    ┌────────────┐    ┌─────────┐
│ Browser │    │ OfflineStore │    │ React Query│    │ Backend │
└────┬────┘    └──────┬───────┘    └─────┬──────┘    └────┬────┘
     │                │                   │                │
     │ navigator.onLine = false          │                │
     ├───────────────>│                   │                │
     │                │                   │                │
     │                │ setOnline(false)  │                │
     │                │                   │                │
     │ Submit quiz    │                   │                │
     │ (offline)      │                   │                │
     ├────────────────────────────────────>│                │
     │                │                   │                │
     │                │                   │ API call fails │
     │                │                   │ (offline)      │
     │                │                   │                │
     │                │ addPendingMutation()               │
     │                │ (save to queue)   │                │
     │<───────────────┤                   │                │
     │ Show "Queued"  │                   │                │
     │                │                   │                │
     │ navigator.onLine = true           │                │
     ├───────────────>│                   │                │
     │                │                   │                │
     │                │ setOnline(true)   │                │
     │                │                   │                │
     │                │ Retry pending mutations            │
     │                ├──────────────────>│                │
     │                │                   │                │
     │                │                   │ POST /v1/...   │
     │                │                   ├───────────────>│
     │                │                   │                │
     │                │                   │<───────────────┤
     │                │                   │ 200 OK         │
     │                │                   │                │
     │                │ removePendingMutation()            │
     │<───────────────┤                   │                │
     │ Show "Synced"  │                   │                │
```

---

## Performance Optimizations

### Caching Strategy

| Data Type | React Query Key | Stale Time | Cache Time | Refetch Strategy |
|-----------|----------------|------------|------------|------------------|
| Chapters | `['chapters', id]` | 5 min | 24 hours | On mount + window focus |
| Quizzes | `['quizzes', id]` | 5 min | 24 hours | On mount only |
| Progress | `['progress']` | 1 min | 1 hour | On mount + mutations |
| Streak | `['progress', 'streak']` | 1 min | 1 hour | On mount + mutations |
| Adaptive Path | `['adaptive', 'path']` | 10 min | 24 hours | On mount only (expensive) |
| Assessment Feedback | `['assessments', 'feedback', id]` | Infinity | 24 hours | Never (immutable) |

### Prefetching Strategy

```typescript
// lib/hooks/useChapter.ts

export function useChapter(chapterId: string) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.chapter(chapterId),
    queryFn: () => fetchChapter(chapterId),
  });

  // Prefetch next chapter
  useEffect(() => {
    if (query.data) {
      const nextChapterId = getNextChapterId(chapterId); // e.g., "01" -> "02"
      if (nextChapterId) {
        queryClient.prefetchQuery({
          queryKey: queryKeys.chapter(nextChapterId),
          queryFn: () => fetchChapter(nextChapterId),
        });
      }
    }
  }, [query.data, chapterId, queryClient]);

  return query;
}
```

### Optimistic Updates

```typescript
// lib/hooks/useQuizSubmit.ts

export function useQuizSubmit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (submission: QuizSubmission) => submitQuiz(submission),

    // Optimistic update
    onMutate: async (submission) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.progress });

      // Snapshot previous value
      const previousProgress = queryClient.getQueryData(queryKeys.progress);

      // Optimistically update progress (assume passed)
      queryClient.setQueryData(queryKeys.progress, (old: any) => ({
        ...old,
        chapters_completed: old.chapters_completed + 1,
        completion_percentage: ((old.chapters_completed + 1) / 6) * 100,
      }));

      return { previousProgress };
    },

    // On error, rollback
    onError: (err, submission, context) => {
      queryClient.setQueryData(queryKeys.progress, context?.previousProgress);
    },

    // Always refetch after success or error
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.progress });
    },
  });
}
```

---

## Data Retention & Privacy

### LocalStorage Data

| Key | Data Type | Retention | Cleared On |
|-----|-----------|-----------|------------|
| `ui-state` | UI preferences (theme, sidebar) | Indefinite | User clears browser data |
| `quiz-autosave` | Quiz answers | Until submission or 7 days | Quiz submission or manual clear |
| `react-query-cache` | API responses | 24 hours | Automatic expiration |
| `reading-position-{id}` | Chapter scroll position | 30 days | Manual clear |

### Data Privacy Considerations

- **No PII in LocalStorage**: User email, password, or personal data NEVER stored client-side
- **JWT tokens**: Stored in httpOnly cookies (NextAuth.js) or secure SessionStorage, NOT LocalStorage
- **Analytics**: Anonymized via Vercel Analytics (no user tracking)
- **Error Logging**: Sanitize error messages before sending to Sentry (no tokens or user data)

---

**Data Model Complete. Ready for component contract definition.**
