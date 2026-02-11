# Course Companion FTE - Complete Architecture Documentation

> **A Comprehensive Educational Platform for Generative AI Fundamentals**
> **Version**: 2.0.0 | **Last Updated**: 2026-02-11

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [System Architecture](#2-system-architecture)
3. [Backend Architecture](#3-backend-architecture)
4. [Frontend Architecture](#4-frontend-architecture)
5. [ChatGPT App Architecture](#5-chatgpt-app-architecture)
6. [Database Schema](#6-database-schema)
7. [API Reference](#7-api-reference)
8. [Data Flow Diagrams](#8-data-flow-diagrams)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Technology Stack](#10-technology-stack)

---

## 1. Executive Overview

### 1.1 Project Vision

**Course Companion FTE** is a full-featured educational platform that teaches **Generative AI Fundamentals** through a combination of:
- Structured course content (6 chapters)
- Interactive quizzes and assessments
- AI-powered personalized learning paths
- Progress tracking and achievement systems
- Multiple access methods (Web App + ChatGPT App)

### 1.2 Architecture Philosophy

The platform follows a **dual-frontend, shared backend** architecture with three development phases:

```mermaid
graph LR
    subgraph "Phase 1: Zero-Backend-LLM"
        A[Web App] --> B[FastAPI Backend]
        C[ChatGPT App] --> B
        B --> D[PostgreSQL]
        style A fill:#3b82f6
        style B fill:#6366f1
        style C fill:#10a37f
    end

    subgraph "Phase 2: Hybrid Intelligence"
        E[Web App] --> F[FastAPI + LLM]
        G[ChatGPT App] --> F
        F --> H[OpenAI API]
        F --> D
        style E fill:#3b82f6
        style F fill:#8b5cf6
        style G fill:#10a37f
        style H fill:#10a37f
    end

    subgraph "Phase 3: Expansion"
        I[Web App] --> J[Microservices]
        K[ChatGPT App] --> J
        L[Mobile PWA] --> J
        J --> M[Multi-Region]
        style I fill:#3b82f6
        style J fill:#ec4899
        style K fill:#10a37f
        style L fill:#f59e0b
    end
```

### 1.3 Key Features

| Feature | Free Tier | Premium Tier |
|---------|-----------|--------------|
| Chapters 1-3 (Beginner) | ✅ | ✅ |
| Chapters 4-6 (Advanced) | ❌ | ✅ |
| Interactive Quizzes | ✅ | ✅ |
| Progress Tracking | ✅ | ✅ |
| AI Learning Skills | ✅ | ✅ |
| Adaptive Learning Paths | ❌ | ✅ |
| AI-Graded Assessments | ❌ | ✅ |
| Teacher Analytics | ❌ | ✅ |

---

## 2. System Architecture

### 2.1 High-Level Component Diagram

```mermaid
graph TB
    subgraph "Client Applications"
        WEB[🌐 Web App<br/>Next.js 16 + React 19]
        CHATGPT[🤖 ChatGPT App<br/>Gadget Platform]
        MOBILE[📱 Mobile PWA<br/>Offline Ready]
    end

    subgraph "API Gateway Layer"
        FLY[✈️ Fly.io Backend<br/>course-companion-fte.fly.dev]
        GADGET[🎯 Gadget Platform<br/>course-companion-fte-1.gadget.app]
        MCP[MCP Server<br/>Model Context Protocol]
    end

    subgraph "Business Logic Layer"
        AUTH[🔐 Authentication Service<br/>JWT + OAuth2]
        CONTENT[📚 Content Service<br/>Chapters & Quizzes]
        PROG[📊 Progress Tracker<br/>Streaks & Milestones]
        PAYMENT[💳 Payment Service<br/>Stripe Integration]
        AI_SKILLS[🎓 AI Skills Service<br/>4 Teaching Modes]
        SEARCH[🔍 Search Service<br/>Full-Text Search]
        ADAPTIVE[🧠 Adaptive Learning<br/>AI-Powered Paths]
        ASSESS[📝 Assessment Service<br/>AI Grading]
    end

    subgraph "Data Layer"
        POSTGRES[(🐘 PostgreSQL<br/>User Data, Progress)]
        CONTENT_JSON[(📄 Content JSON<br/>Course Materials)]
        REDIS[(⚡ Redis<br/>Cache & Sessions)]
        R2[(📦 Cloudflare R2<br/>Content Storage)]
    end

    subgraph "External Services"
        STRIPE[💳 Stripe API<br/>Payment Processing]
        OPENAI[🧠 OpenAI API<br/>GPT-4o-mini]
        CLOUDFLARE[🌐 Cloudflare<br/>Tunnel & DNS]
    end

    WEB --> FLY
    MOBILE --> FLY
    CHATGPT --> MCP
    MCP --> FLY

    FLY --> AUTH
    FLY --> CONTENT
    FLY --> PROG
    FLY --> PAYMENT
    MCP --> AI_SKILLS
    MCP --> SEARCH
    FLY --> ADAPTIVE
    FLY --> ASSESS

    AUTH --> POSTGRES
    CONTENT --> CONTENT_JSON
    CONTENT --> R2
    PROG --> POSTGRES
    PROG --> REDIS
    PAYMENT --> STRIPE
    ADAPTIVE --> OPENAI
    ASSESS --> OPENAI

    MCP --> CLOUDFLARE
    WEB --> CLOUDFLARE
    CHATGPT --> CLOUDFLARE

    style WEB fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style CHATGPT fill:#10a37f,stroke:#0d8c6e,color:#fff
    style FLY fill:#6366f1,stroke:#4f46e5,color:#fff
    style GADGET fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style POSTGRES fill:#10b981,stroke:#059669,color:#fff
```

### 2.2 Technology Stack Overview

```mermaid
graph TB
    subgraph "Frontend Stack"
        NEXT[Next.js 16<br/>React 19<br/>TypeScript 5.9<br/>Tailwind CSS 4.1<br/>Zustand 4.4]
    end

    subgraph "Backend Stack"
        FAST[FastAPI 0.104<br/>Python 3.11+<br/>SQLAlchemy 2.0<br/>Alembic<br/>Pydantic v2]
    end

    subgraph "ChatGPT App Stack"
        GADGET[Gadget Platform<br/>React Router 7<br/>OpenAI Apps SDK<br/>MCP SDK 1.19]
    end

    subgraph "Infrastructure"
        FLY_IO[Fly.io<br/>Docker<br/>PostgreSQL 16<br/>Redis 7]
        STRIPE[Stripe<br/>Payments]
        OPENAI[OpenAI<br/>LLM API]
    end

    NEXT --> FAST
    GADGET --> FAST
    FAST --> FLY_IO
    FAST --> STRIPE
    FAST --> OPENAI
```

---

## 3. Backend Architecture

### 3.1 Application Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Environment configuration
│   ├── database.py                # Async database connection
│   ├── dependencies.py            # FastAPI dependencies
│   ├── middleware/                # Custom middleware
│   │
│   ├── routers/                   # API route handlers
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── chapters.py           # Chapter endpoints
│   │   ├── quizzes.py            # Quiz endpoints
│   │   ├── progress.py           # Progress tracking
│   │   ├── milestones.py          # Achievement system
│   │   ├── payments.py           # Stripe integration
│   │   └── chat.py               # AI chat completions
│   │
│   ├── api/                       # Versioned API routes
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Auth router re-export
│   │   │   ├── bookmarks.py       # Bookmarks CRUD
│   │   │   └── assessments.py     # Assessments (Phase 2)
│   │   └── v2/                    # Phase 2 endpoints
│   │       ├── adaptive.py        # Adaptive paths
│   │       ├── assessments.py     # AI grading
│   │       ├── teacher.py         # Teacher analytics
│   │       └── usage.py           # Usage tracking
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── base.py               # Base model with TimestampMixin
│   │   ├── user.py               # User account
│   │   ├── progress.py           # ChapterProgress model
│   │   ├── quiz.py               # Quiz & QuizAttempt models
│   │   ├── streak.py             # Streak model
│   │   ├── milestone.py          # Milestone model
│   │   ├── session.py            # Session model
│   │   ├── bookmark.py           # Bookmark model
│   │   ├── note.py               # Note model
│   │   ├── subscription.py       # Subscription model
│   │   ├── llm.py                # Phase 2 LLM models
│   │   └── usage.py              # Usage tracking models
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── user.py               # User DTOs
│   │   ├── chapter.py            # Chapter DTOs
│   │   ├── quiz.py               # Quiz DTOs
│   │   ├── progress.py           # Progress DTOs
│   │   ├── auth.py               # Auth DTOs
│   │   └── payment.py            # Payment DTOs
│   │
│   ├── services/                  # Business logic
│   │   ├── progress_tracker.py   # Progress calculations
│   │   ├── quiz_grader.py        # Quiz grading
│   │   ├── milestone_service.py  # Achievement logic
│   │   ├── content.py            # Content retrieval
│   │   ├── search.py             # Content search
│   │   ├── llm_service.py        # LLM integration
│   │   ├── llm/
│   │   │   ├── client.py         # OpenAI/Anthropic client
│   │   │   ├── adaptive_path_generator.py
│   │   │   ├── assessment_grader.py
│   │   │   └── cost_tracker.py
│   │   ├── stripe_service.py     # Payment processing
│   │   └── rate_limiter.py       # Rate limiting
│   │
│   ├── utils/                    # Utilities
│   │   ├── auth.py               # JWT & password hashing
│   │   ├── cache.py              # Redis client
│   │   ├── storage.py            # Cloudflare R2 client
│   │   └── redis_client.py       # Redis connection
│   │
│   └── static/                   # Static content
│
├── content/                      # Course content (JSON)
│   ├── chapters/                 # Chapter content files
│   ├── quizzes/                  # Quiz content files
│   └── assessments/             # Assessment rubrics
│
├── alembic/                     # Database migrations
│   ├── versions/
│   └── env.py
│
├── scripts/                     # Utility scripts
│   ├── make_users_teachers.py   # User management
│   └── seed_data.py            # Data seeding
│
├── tests/                       # Test suite
│   ├── test_api/
│   ├── test_services/
│   └── test_models/
│
├── pyproject.toml              # Python dependencies
├── Dockerfile.fly              # Docker image for Fly.io
├── fly.toml                    # Fly.io deployment config
└── .env.example               # Environment template
```

### 3.2 Core Backend Components

#### 3.2.1 Main Application (`main.py`)

```python
# FastAPI Application Configuration
app = FastAPI(
    title="Course Companion FTE",
    description="Educational platform for Generative AI",
    version="2.0.0",
    lifespan=lifespan_manager,
    servers=[
        {"url": "https://course-companion-fte.fly.dev", "description": "Production"}
    ]
)

# Middleware Stack
- CORSMiddleware (multi-origin)
- Authentication (JWT)
- Error Handling
- Rate Limiting
- Request Logging
```

#### 3.2.2 Database Models

```mermaid
erDiagram
    USER ||--o{ CHAPTER_PROGRESS : tracks
    USER ||--o{ QUIZ_ATTEMPT : attempts
    USER ||--o{ NOTE : creates
    USER ||--o{ BOOKMARK : saves
    USER ||--|| STREAK : has
    USER ||--o{ MILESTONE : achieves
    USER ||--|| SUBSCRIPTION : has
    USER ||--o{ ADAPTIVE_PATH : generates
    USER ||--o{ ASSESSMENT_SUBMISSION : submits

    CHAPTER ||--o{ CHAPTER_PROGRESS : contains
    CHAPTER ||--o{ QUIZ : has
    CHAPTER ||--o{ BOOKMARK : marks

    QUIZ ||--o{ QUIZ_ATTEMPT : receives

    MILESTONE ||--o{ USER_MILESTONE : earned_by
```

**Key Models:**

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `User` | User accounts | id, email, password_hash, subscription_tier, is_teacher |
| `ChapterProgress` | Per-chapter progress | chapter_id, completion_percentage, completed_sections, time_spent |
| `QuizAttempt` | Quiz submissions | quiz_id, score_percentage, passed, attempt_number, answers |
| `Streak` | Learning streaks | current_streak, longest_streak, total_active_days |
| `Milestone` | Achievements | milestone_type, achieved_at, display_name |
| `Bookmark` | Saved content | chapter_id, section_id, title, folder |
| `Note` | User notes | chapter_id, section_id, content, tags |
| `Subscription` | Payment data | stripe_customer_id, stripe_subscription_id, status |
| `AdaptivePath` | AI learning paths | goals, time_horizon, recommendations (JSON) |
| `AssessmentSubmission` | Open-ended answers | question_id, answer, graded, feedback |
| `LLMUsageLog` | Token tracking | model, prompt_tokens, completion_tokens, cost_usd |

#### 3.2.3 Services Layer

```mermaid
graph TB
    subgraph "Service Layer Architecture"
        REQUEST[API Request] --> AUTH[Authentication Check]
        AUTH --> ROUTER[Route Handler]
        ROUTER --> SERVICE[Business Logic Service]
        SERVICE --> MODEL[Database Model]
        SERVICE --> EXTERNAL[External API]
        MODEL --> RESPONSE[Response]
        EXTERNAL --> RESPONSE
    end

    subgraph "Core Services"
        PROG_SVC[progress_tracker.py<br/>calculate_completion<br/>update_streak<br/>get_summary]
        QUIZ_SVC[quiz_grader.py<br/>grade_quiz<br/>calculate_score<br/>provide_feedback]
        MILE_SVC[milestone_service.py<br/>check_achievements<br/>award_milestone]
        CONTENT_SVC[content.py<br/>get_chapter<br/>get_quiz<br/>cache_content]
        SEARCH_SVC[search.py<br/>keyword_search<br/>rank_results]
        LLM_SVC[llm_service.py<br/>generate_response<br/>track_usage]
    end

    subgraph "Premium Services (Phase 2)"
        ADAPT_SVC[adaptive_path_generator.py<br/>generate_path<br/>personalize_content]
        ASSESS_SVC[assessment_grader.py<br/>grade_submission<br/>provide_feedback]
        COST_TRACK[cost_tracker.py<br/>track_tokens<br/>calculate_costs]
    end

    PROG_SVC --> RESPONSE
    QUIZ_SVC --> RESPONSE
    MILE_SVC --> RESPONSE
    CONTENT_SVC --> RESPONSE
    SEARCH_SVC --> RESPONSE
    LLM_SVC --> RESPONSE
    ADAPT_SVC --> RESPONSE
    ASSESS_SVC --> RESPONSE
```

### 3.3 API Router Details

#### 3.3.1 Authentication Router (`/api/v1/auth`)

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|----------------|
| `/register` | POST | Create user account | ❌ |
| `/login` | POST | Get JWT tokens | ❌ |
| `/refresh` | POST | Refresh access token | ❌ |
| `/me` | GET | Get current user | ✅ |
| `/me` | PUT | Update profile | ✅ |
| `/change-password` | POST | Change password | ✅ |
| `/me` | DELETE | Delete account | ✅ |

#### 3.3.2 Chapters Router (`/api/v1/chapters`)

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/` | GET | List all chapters | Array[ChapterWithProgress] |
| `/{chapter_id}` | GET | Get chapter content | ChapterDetail |
| `/search?q={query}` | GET | Search content | SearchResult[] |
| `/{chapter_id}/next` | GET | Next chapter | ChapterPreview |
| `/{chapter_id}/previous` | GET | Previous chapter | ChapterPreview |

**ChapterWithProgress Structure:**
```typescript
{
  id: string;
  title: string;
  subtitle: string;
  access_tier: "free" | "premium";
  estimated_time: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  user_has_access: boolean;
  user_progress: {
    completion_status: "not_started" | "in_progress" | "completed";
    completion_percentage: number;
    quiz_score: number | null;
  };
}
```

#### 3.3.3 Quizzes Router (`/api/v1/quizzes`)

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/{quiz_id}` | GET | Get quiz questions | Quiz (no answers) |
| `/{quiz_id}/submit` | POST | Submit answers | QuizResult |

**QuizResult Structure:**
```typescript
{
  quiz_id: string;
  score: number;
  score_percentage: number;
  passed: boolean;
  feedback: GradingDetail[];
  correct_count: number;
  total_questions: number;
}
```

#### 3.3.4 Progress Router (`/api/v1/progress`)

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/` | GET | Full progress summary | ProgressSummary |
| `/streak` | GET | Streak information | Streak |
| `/chapters/{chapter_id}` | GET | Chapter progress | ChapterProgress |
| `/chapters/{id}/sections/{section_id}/complete` | POST | Mark section complete | UpdatedProgress |
| `/activity` | POST | Record activity | Success |

**ProgressSummary Structure:**
```typescript
{
  chapters_completed: number;
  total_chapters: number;
  completion_percentage: number;
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  last_activity_date: string;
  quiz_scores: number[];
  chapters: ChapterProgress[];
}
```

#### 3.3.5 Milestones Router (`/api/v1/milestones`)

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/` | GET | Achieved milestones | Milestone[] |
| `/achievable` | GET | Available milestones | Milestone[] |
| `/next?count=3` | GET | Next milestones | Milestone[] |
| `/summary` | GET | Milestone summary | MilestoneSummary |

#### 3.3.6 Payments Router (`/api/v1/payments`)

| Endpoint | Method | Purpose | Integration |
|----------|--------|---------|-------------|
| `/create-checkout-session` | POST | Create Stripe checkout | Stripe API |
| `/subscription-status` | GET | Get subscription info | Database |
| `/cancel-subscription` | POST | Cancel subscription | Stripe API |
| `/webhook` | POST | Stripe webhooks | Stripe Signature |

---

## 4. Frontend Architecture

### 4.1 Application Structure

```
web-app/
├── src/
│   ├── app/                       # Next.js App Router
│   │   ├── layout.tsx             # Root layout with providers
│   │   ├── page.tsx               # Home/Landing page
│   │   ├── globals.css            # Global styles
│   │   │
│   │   ├── (auth)/               # Auth route group
│   │   │   ├── login/page.tsx     # Login page
│   │   │   └── register/page.tsx  # Registration page
│   │   │
│   │   ├── dashboard/            # User dashboard
│   │   │   └── page.tsx
│   │   │
│   │   ├── chapters/             # Chapter routes
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx       # Chapter detail
│   │   │   │   ├── quiz/
│   │   │   │   │   └── page.tsx   # Quiz page
│   │   │   │   └── adaptive-path/
│   │   │   │       └── page.tsx   # AI learning path
│   │   │   │
│   │   ├── quizzes/              # Quiz listing
│   │   │   └── page.tsx
│   │   │
│   │   ├── milestones/           # Achievements
│   │   │   └── page.tsx
│   │   │
│   │   ├── progress/            # Progress tracking
│   │   │   └── page.tsx
│   │   │
│   │   ├── library/              # Content library
│   │   │   └── page.tsx
│   │   │
│   │   ├── pricing/             # Subscription plans
│   │   │   └── page.tsx
│   │   │
│   │   ├── settings/             # User settings
│   │   │   └── page.tsx
│   │   │
│   │   ├── teacher/              # Teacher dashboard
│   │   │   └── page.tsx
│   │   │
│   │   ├── payment/              # Payment flow
│   │   │   ├── checkout/
│   │   │   │   └── page.tsx
│   │   │   ├── success/
│   │   │   │   └── page.tsx
│   │   │   └── cancelled/
│   │   │       └── page.tsx
│   │   │
│   │   ├── assessments/          # Phase 2 assessments
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   │
│   │   ├── offline/             # PWA offline page
│   │   │   └── page.tsx
│   │   │
│   │   └── api/                  # API routes (BFF)
│   │       └── auth/
│   │           └── [...nextauth]
│   │
│   ├── components/              # React components
│   │   ├── ui/                  # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Progress.tsx
│   │   │   └── ...
│   │   │
│   │   ├── Header.tsx          # Navigation header
│   │   ├── Hero.tsx            # Landing hero
│   │   ├── ChapterContent.tsx  # Chapter renderer
│   │   ├── ChapterGrid.tsx     # Chapter cards
│   │   ├── ChapterSidebar.tsx  # Chapter navigation
│   │   ├── AIChat.tsx          # AI chat interface
│   │   ├── AIAssistant.tsx     # Embedded AI
│   │   ├── MilestoneList.tsx   # Achievements list
│   │   ├── PWAInstallPrompt.tsx # PWA install
│   │   │
│   │   ├── bookmarks/          # Bookmark components
│   │   │   ├── BookmarkButton.tsx
│   │   │   └── BookmarkList.tsx
│   │   │
│   │   ├── notes/              # Note components
│   │   │   ├── NoteButton.tsx
│   │   │   ├── NoteEditor.tsx
│   │   │   └── NoteList.tsx
│   │   │
│   │   ├── modals/             # Modal dialogs
│   │   │   ├── PremiumGate.tsx
│   │   │   └── PremiumUpgradeModal.tsx
│   │   │
│   │   ├── search/             # Search components
│   │   │   ├── SearchButton.tsx
│   │   │   └── SearchModal.tsx
│   │   │
│   │   └── interactive/        # Interactive elements
│   │       └── InteractiveComponents.tsx
│   │
│   ├── store/                  # State management (Zustand)
│   │   └── useStore.ts         # Main store with auth, user, progress
│   │
│   ├── lib/                    # Utilities
│   │   ├── api.ts             # API client (axios)
│   │   ├── utils.ts           # Helper functions
│   │   ├── stripe.ts          # Stripe client
│   │   └── pdfExport.ts       # PDF generation
│   │
│   ├── hooks/                  # React hooks
│   │   ├── useSearch.ts       # Search functionality
│   │   └── useProgress.ts     # Progress tracking
│   │
│   └── types/                  # TypeScript types
│       └── index.ts           # Type definitions
│
├── public/                     # Static assets
│   ├── manifest.json          # PWA manifest
│   ├── sw.js                  # Service worker
│   └── icons/                 # App icons
│
├── next.config.js             # Next.js config
├── tailwind.config.ts         # Tailwind config
├── tsconfig.json              # TypeScript config
└── package.json               # Dependencies
```

### 4.2 State Management (Zustand)

```typescript
interface Store {
  // Auth State
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;

  // Progress State
  progress: Progress | null;

  // Premium State
  isPremium: boolean;
  subscriptionTier: "free" | "premium" | "pro" | "team";

  // UI State
  sidebarOpen: boolean;
  searchOpen: boolean;

  // Actions
  login: (email, password) => Promise<void>;
  logout: () => void;
  refreshProgress: () => Promise<void>;
  updateProgress: (chapterId) => Promise<void>;
}
```

### 4.3 API Client (`lib/api.ts`)

**Axios-based API client with:**
- JWT token injection
- Request/response interceptors
- Comprehensive error handling
- Mock fallback for demo mode

**Available Functions:**
```typescript
// Auth
register(email, password)
login(email, password)
getCurrentUser()

// Chapters
getChapters()
getChapter(chapterId)
searchChapters(query)

// Quizzes
getQuiz(quizId)
submitQuiz(quizId, answers)

// Progress
getProgress()
getStreak()
recordActivity(chapterId, sectionId, activityType)
getChapterProgress(chapterId)

// Milestones
getMilestones()
getAchievableMilestones()
getNextMilestones(count)

// Premium (Phase 2)
gradeAssessment(submissionId)
generateLearningPath(goals, timeHorizon)
getPremiumUsage()
getSubscriptionStatus()
```

---

## 5. ChatGPT App Architecture

### 5.1 Application Structure

```
chatgpt-app/
├── api/
│   ├── routes/
│   │   └── mcp/
│   │       ├── GET.ts          # MCP GET endpoint
│   │       ├── POST.ts         # MCP POST endpoint
│   │       └── +scope.ts       # Route scope config
│   ├── mcp.ts                   # MCP server creation
│   └── skills.ts                # AI skills definitions
│
├── web/
│   ├── api.ts                   # Gadget API client
│   ├── root.tsx                 # App root
│   ├── routes.ts                # Route definitions
│   │
│   ├── chatgpt/                 # ChatGPT app components
│   │   ├── root.tsx             # ChatGPT root layout
│   │   ├── HelloGadget.tsx     # Main app router
│   │   ├── ChaptersWidget.tsx  # Chapter browser widget
│   │   └── SkillsWidget.tsx     # Skills selector widget
│   │
│   └── components/             # Shared components
│       └── ui/                  # UI components
│
├── app-manifest.json           # App metadata
├── chatgpt-app-config.yaml     # MCP configuration
├── gpt-config.json            # GPT configuration
├── openapi.yaml               # OpenAPI spec
├── package.json               # Dependencies
└── vite.config.mts           # Vite config
```

### 5.2 MCP Server Architecture

```mermaid
graph TB
    subgraph "MCP Server"
        MCP[MCP Server<br/>@modelcontextprotocol/sdk]

        subgraph "MCP Tools (14 total)"
            GET_CHAP[get_chapters<br/>List all chapters]
            GET_ONE[get_chapter<br/>Get chapter content]
            SEARCH[search_content<br/>Search content]
            GET_QUIZ[get_quiz<br/>Get quiz]
            SUB_QUIZ[submit_quiz<br/>Submit answers]
            GET_PROG[get_progress<br/>Get progress]
            GET_NEXT[get_next_chapter<br/>Next chapter]
            GET_PREV[get_previous_chapter<br/>Previous chapter]
            UP_PROG[update_progress<br/>Record activity]
            CHECK[check_access<br/>Verify premium]
            GET_SKILL[get_skills<br/>List AI skills]
            ACT_SKILL[activate_skill<br/>Switch mode]
            GET_BM[get_bookmarks<br/>List bookmarks]
            CR_BM[create_bookmark<br/>Save bookmark]
            DEL_BM[delete_bookmark<br/>Remove bookmark]
        end

        subgraph "MCP Resources (Widgets)"
            CHAP_W[ui://widget/ChaptersWidget.html<br/>Chapter browser]
            SKILL_W[ui://widget/SkillsWidget.html<br/>Skills selector]
            HELLO_W[ui://widget/HelloGadget.html<br/>Main widget]
        end
    end

    subgraph "Backend Integration"
        BACKEND[FastAPI Backend<br/>course-companion-fte.fly.dev]
        CONTENT[Content JSON<br/>Chapter/Quiz data]
        DB[(Database<br/>User progress)]
    end

    MCP --> GET_CHAP
    MCP --> GET_ONE
    MCP --> SEARCH
    MCP --> GET_QUIZ
    MCP --> SUB_QUIZ
    MCP --> GET_PROG
    MCP --> GET_SKILL
    MCP --> ACT_SKILL

    GET_CHAP --> BACKEND
    GET_ONE --> BACKEND
    SEARCH --> BACKEND
    GET_QUIZ --> BACKEND
    GET_PROG --> BACKEND

    BACKEND --> CONTENT
    BACKEND --> DB

    style MCP fill:#10a37f,stroke:#0d8c6e,color:#fff
    style GET_CHAP fill:#3b82f6,stroke:#1d4ed8,color:#fff
```

### 5.3 AI Skills System

```mermaid
graph TB
    subgraph "AI Skills"
        CONCEPT[💡 Concept Explainer<br/>Simple explanations<br/>Analogies & examples]
        QUIZ_M[🎯 Quiz Master<br/>Test knowledge<br/>Instant feedback]
        SOCRATIC[🤔 Socratic Tutor<br/>Guided learning<br/>Critical thinking]
        MOTIVATE[🔥 Progress Motivator<br/>Stay on track<br/>Celebrations]
    end

    subgraph "Skill Configuration"
        SYS[System Prompts<br/>Teaching approach]
        START[Conversation Starters<br/>Prompt suggestions]
    end

    subgraph "MCP Integration"
        GET_S[get_skills tool<br/>List available skills]
        ACT_S[activate_skill tool<br/>Switch teaching mode]
    end

    CONCEPT --> SYS
    QUIZ_M --> SYS
    SOCRATIC --> SYS
    MOTIVATE --> SYS

    GET_S --> CONCEPT
    GET_S --> QUIZ_M
    GET_S --> SOCRATIC
    GET_S --> MOTIVATE

    ACT_S --> SYS

    style CONCEPT fill:#fbbf24,stroke:#f59e0b,color:#000
    style QUIZ_M fill:#ef4444,stroke:#dc2626,color:#fff
    style SOCRATIC fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style MOTIVATE fill:#f97316,stroke:#ea580c,color:#fff
```

**Skill System Prompts:**

| Skill | System Prompt Focus | Conversation Starters |
|-------|-------------------|---------------------|
| **Concept Explainer** | Simple analogies, real-world comparisons, chunked explanations | "Explain this simply", "Give me an analogy" |
| **Quiz Master** | Questions with immediate feedback, progress tracking | "Quiz me", "Test my knowledge" |
| **Socratic Tutor** | Guiding questions, no direct answers, discovery learning | "Help me figure this out", "Guide me through" |
| **Progress Motivator** | Celebrations, streak tracking, milestone recognition | "How am I doing?", "Motivate me" |

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```mermaid
erDiagram
    %% User Core
    USER {
        uuid id PK
        string email UK
        string password_hash
        string name
        string subscription_tier
        boolean is_teacher
        datetime created_at
        datetime updated_at
        string timezone
    }

    %% Content Models
    CHAPTER {
        string id PK
        string title
        string subtitle
        string description
        text content
        string access_tier
        integer order
        string estimated_time
        string difficulty
    }

    SECTION {
        string id PK
        string chapter_id FK
        string title
        text content
        integer order
    }

    QUIZ {
        uuid id PK
        string chapter_id FK
        jsonb questions
        integer passing_score
        string time_limit
    }

    %% User Progress
    CHAPTER_PROGRESS {
        uuid id PK
        uuid user_id FK
        string chapter_id FK
        integer completion_percentage
        boolean is_completed
        jsonb completed_sections
        integer time_spent_seconds
        datetime last_accessed
        datetime completed_at
    }

    QUIZ_ATTEMPT {
        uuid id PK
        uuid user_id FK
        uuid quiz_id FK
        jsonb answers
        integer score
        integer score_percentage
        boolean passed
        integer attempt_number
        datetime completed_at
    }

    STREAK {
        uuid id PK
        uuid user_id FK
        integer current_streak
        integer longest_streak
        integer total_active_days
        date last_activity_date
        string timezone
    }

    %% Content Organization
    BOOKMARK {
        uuid id PK
        uuid user_id FK
        string chapter_id FK
        string section_id FK
        string title
        string notes
        string folder
        datetime created_at
    }

    NOTE {
        uuid id PK
        uuid user_id FK
        string chapter_id FK
        string section_id FK
        text content
        jsonb tags
        datetime created_at
        datetime updated_at
    }

    %% Achievements
    MILESTONE {
        uuid id PK
        string milestone_type
        string display_name
        string description
        string icon_emoji
        string message
        integer xp_reward
    }

    USER_MILESTONE {
        uuid user_id FK
        uuid milestone_id FK
        datetime achieved_at
    }

    %% Sessions
    SESSION {
        uuid id PK
        uuid user_id FK
        string session_token
        datetime expires_at
        string user_agent
        string ip_address
        datetime created_at
    }

    %% Subscription
    SUBSCRIPTION {
        uuid id PK
        uuid user_id FK
        string stripe_customer_id
        string stripe_subscription_id
        string status
        datetime current_period_start
        datetime current_period_end
        string tier
    }

    %% Phase 2: AI Features
    ADAPTIVE_PATH {
        uuid id PK
        uuid user_id FK
        jsonb goals
        string time_horizon
        jsonb recommendations
        datetime created_at
        datetime expires_at
    }

    ASSESSMENT_SUBMISSION {
        uuid id PK
        uuid user_id FK
        string question_id
        text answer
        boolean graded
        datetime created_at
    }

    ASSESSMENT_FEEDBACK {
        uuid id PK
        uuid submission_id FK
        numeric score
        text feedback
        jsonb rubric_scores
        datetime graded_at
    }

    LLM_USAGE_LOG {
        uuid id PK
        uuid user_id FK
        string model
        integer prompt_tokens
        integer completion_tokens
        float cost_usd
        string feature
        datetime request_timestamp
    }

    PREMIUM_USAGE_QUOTA {
        uuid id PK
        uuid user_id FK
        integer month
        integer year
        integer tokens_used
        integer tokens_limit
    }

    %% Relationships
    USER ||--o{ CHAPTER_PROGRESS : tracks
    USER ||--o{ QUIZ_ATTEMPT : attempts
    USER ||--o{ STREAK : maintains
    USER ||--o{ BOOKMARK : creates
    USER ||--o{ NOTE : writes
    USER ||--o{ USER_MILESTONE : earns
    USER ||--|| SESSION : has
    USER ||--|| SUBSCRIPTION : owns
    USER ||--o{ ADAPTIVE_PATH : generates
    USER ||--o{ ASSESSMENT_SUBMISSION : submits
    USER ||--o{ LLM_USAGE_LOG : consumes
    USER ||--o{ PREMIUM_USAGE_QUOTA : tracked_by

    CHAPTER ||--o{ SECTION : contains
    CHAPTER ||--o{ CHAPTER_PROGRESS : measured_by
    CHAPTER ||--o{ QUIZ : has
    CHAPTER ||--o{ BOOKMARK : references
    CHAPTER ||--o{ NOTE : annotates

    QUIZ ||--o{ QUIZ_ATTEMPT : receives

    ASSESSMENT_SUBMISSION ||--o{ ASSESSMENT_FEEDBACK : receives
```

### 6.2 Key Database Indexes

```sql
-- Performance indexes
CREATE INDEX ix_chapter_progress_user_id ON chapter_progress(user_id);
CREATE INDEX ix_chapter_progress_chapter_id ON chapter_progress(chapter_id);
CREATE INDEX ix_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX ix_quiz_attempts_quiz_id ON quiz_attempts(quiz_id);
CREATE INDEX ix_streaks_user_id ON streaks(user_id);
CREATE INDEX ix_notes_user_id ON notes(user_id);
CREATE INDEX ix_bookmarks_user_id ON bookmarks(user_id);

-- Composite indexes
CREATE INDEX ix_chapter_progress_user_chapter ON chapter_progress(user_id, chapter_id);
CREATE INDEX ix_quiz_attempts_user_quiz ON quiz_attempts(user_id, quiz_id);
CREATE INDEX ix_notes_user_chapter ON notes(user_id, chapter_id);
```

---

## 7. API Reference

### 7.1 Complete Endpoint Listing

#### Authentication Endpoints

```mermaid
graph LR
    subgraph "/api/v1/auth"
        REGISTER[POST /register<br/>Create account]
        LOGIN[POST /login<br/>Get JWT]
        REFRESH[POST /refresh<br/>Refresh token]
        ME[GET /me<br/>Get profile]
        UPDATE[PUT /me<br/>Update profile]
        PWD[POST /change-password<br/>Update password]
        DELETE[DELETE /me<br/>Delete account]
    end

    style REGISTER fill:#10b981,stroke:#059669,color:#fff
    style LOGIN fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style ME fill:#6366f1,stroke:#4f46e5,color:#fff
```

#### Chapter Endpoints

```mermaid
graph LR
    subgraph "/api/v1/chapters"
        LIST[GET /<br/>List all chapters]
        GET_ONE[GET /{id}<br/>Get chapter]
        SEARCH[GET /search<br/>Content search]
        NEXT[GET /{id}/next<br/>Next chapter]
        PREV[GET /{id}/previous<br/>Previous chapter]
    end

    style LIST fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style GET_ONE fill:#6366f1,stroke:#4f46e5,color:#fff
    style SEARCH fill:#8b5cf6,stroke:#7c3aed,color:#fff
```

#### Progress Endpoints

```mermaid
graph LR
    subgraph "/api/v1/progress"
        GET_PROG[GET /<br/>Full summary]
        STREAK[GET /streak<br/>Streak info]
        CHAP_PROG[GET /chapters/{id}<br/>Chapter progress]
        COMPLETE[POST /chapters/{id}/sections/{sid}/complete<br/>Mark complete]
        ACTIVITY[POST /activity<br/>Record activity]
    end

    style GET_PROG fill:#6366f1,stroke:#4f46e5,color:#fff
    style STREAK fill:#f59e0b,stroke:#d97706,color:#fff
    style COMPLETE fill:#10b981,stroke:#059669,color:#fff
```

#### Phase 2 Endpoints

```mermaid
graph LR
    subgraph "/api/v2 - Premium Features"
        ADAPT[POST /adaptive/path<br/>Generate AI path]
        ASSESS[POST /assessments/submit<br/>AI grading]
        TEACHER[GET /teacher/costs<br/>Cost monitoring]
        USAGE[GET /usage/monthly<br/>Usage stats]
    end

    style ADAPT fill:#ec4899,stroke:#db2777,color:#fff
    style ASSESS fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style TEACHER fill:#f59e0b,stroke:#d97706,color:#fff
```

---

## 8. Data Flow Diagrams

### 8.1 User Authentication Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 🌐 Web App
    participant B as ⚙️ Backend
    participant D as 🐘 PostgreSQL
    participant J as 🔑 JWT Service

    U->>F: Enter email/password
    F->>B: POST /api/v1/auth/login
    B->>D: SELECT * FROM users WHERE email = ?
    D-->>B: user_record
    B->>B: Verify password_hash
    B->>J: Generate JWT tokens
    J-->>B: access_token, refresh_token
    B-->>F: { user, tokens }
    F->>F: Store tokens in localStorage
    F->>U: Redirect to dashboard

    Note over U,U: User authenticated & logged in
```

### 8.2 Content Access with Premium Gate

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 🌐 Web App
    participant B as ⚙️ Backend
    participant D as 🐘 Database
    participant S as 💳 Stripe

    U->>F: Click Chapter 4 (Premium)
    F->>B: GET /api/v1/chapters/chapter-4
    B->>D: SELECT subscription FROM users WHERE id = ?
    D-->>B: subscription_tier = 'free'
    B->>B: Check access_tier vs subscription_tier
    B-->>F: 403 Forbidden - Premium Required
    F->>U: Show PremiumGate Modal

    U->>F: Click "Upgrade to Premium"
    F->>B: POST /api/v1/payments/create-checkout-session
    B->>S: Create Stripe Checkout Session
    S-->>B: checkout_url
    B-->>F: { checkout_url }
    F->>U: Redirect to Stripe Checkout

    U->>S: Complete payment
    S->>B: Webhook: checkout.session.completed
    B->>D: UPDATE users SET subscription_tier = 'premium'
    D-->>B: Success
    B->>D: INSERT INTO subscriptions (...)
    D-->>B: Success
    B-->>S: 200 OK
    S->>F: Redirect back to app

    F->>B: GET /api/v1/progress (poll)
    B-->>F: { subscription_tier: 'premium' }
    F->>U: Now has access to Chapter 4!
```

### 8.3 Progress Tracking Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 🌐 Web App
    participant B as ⚙️ Backend
    participant P as 📊 Progress Service
    participant M as 🏆 Milestone Service
    participant D as 🐘 Database
    participant R as ⚡ Redis

    U->>F: Complete chapter section
    F->>B: POST /api/v1/progress/activity
    B->>P: Record activity (chapter_id, section_id)
    P->>P: Calculate completion_percentage
    P->>P: Update completed_sections
    P->>D: UPDATE chapter_progress SET completion_percentage = 100
    P->>D: UPDATE streaks SET last_activity_date = TODAY
    P->>M: Check for milestone achievements
    M->>M: Has user completed 3 chapters?
    M->>D: INSERT INTO user_milestones (milestone_id, achieved_at)
    P->>R: Cache updated progress in Redis
    B-->>F: { progress, new_milestones }
    F->>U: Show completion celebration! 🎉
```

### 8.4 ChatGPT App Integration Flow

```mermaid
sequenceDiagram
    participant C as 🤖 ChatGPT
    participant M as 🎯 MCP Server
    participant B as ⚙️ Backend
    participant O as 🧠 OpenAI API

    C->>M: tools/call: get_chapters()
    M->>B: GET /api/v1/chapters
    B->>M: [{id, title, access_tier, progress}]
    M->>C: { content: "Found 6 chapters", widget_uri: "ChaptersWidget.html" }
    C->>C: Render ChaptersWidget
    C->>M: tools/call: activate_skill(skill_id="concept-explainer")
    M->>M: Load skill system prompt
    M->>C: { "💡 Concept Explainer activated!" }
    C->>C: Apply Concept Explainer persona
    C->>M: tools/call: get_chapter(chapter_id="chapter-1")
    M->>B: GET /api/v1/chapters/chapter-1
    B->>M: Full chapter content
    M->>C: { content: chapter_1_content, widget_uri: "ChaptersWidget.html" }
    C->>C: Explain using Concept Explainer mode
    C->>C: "Let me break this down simply..."
```

### 8.5 Quiz Submission and Grading Flow

```mermaid
sequenceDiagram
    participant U as 👤 Student
    participant F as 🌐 Quiz Page
    participant B as ⚙️ Backend
    participant Q as 📝 Quiz Grader
    participant P as 📊 Progress Service
    participant M as 🏆 Milestone Service
    participant D as 🐘 Database

    U->>F: Submit quiz answers
    F->>B: POST /api/v1/quizzes/{quiz_id}/submit
    B->>Q: Grade quiz (answers, correct_answers)
    Q->>Q: Calculate score_percentage
    Q->>Q: Determine passed/failed
    Q-->>B: { score: 85%, passed: true, feedback }
    B->>P: Update progress with quiz score
    P->>D: UPDATE chapter_progress SET quiz_score = 85
    P->>D: UPDATE chapter_progress SET completion_percentage = 100
    P->>M: Check for quiz milestone (e.g., "First Perfect Score")
    M->>M: Award "Quiz Champion" badge
    M->>D: INSERT INTO user_milestones
    B-->>F: { score, feedback, progress, milestones_earned }
    F->>U: Display results with celebration! 🎉
```

---

## 9. Deployment Architecture

### 9.1 Production Infrastructure

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Fly.io Backend"
            FLY_APP[FastAPI App<br/>course-companion-fte.fly.dev]
            FLY_DB[PostgreSQL<br/>Ha: 2 replicas]
            FLY_REDIS[Redis<br/>Cache layer]
            FLY_CONSOLE[Fly.io Console<br/>Monitoring & Logs]
        end

        subgraph "Gadget Platform"
            GADGET_PROD[ChatGPT App<br/>course-companion-fte-1.gadget.app]
            GADGET_DEV[Development<br/>--development.gadget.app]
            GADGET_MCP[MCP Server<br/>/mcp endpoint]
        end

        subgraph "Web App"
            WEB_APP[Next.js App<br/>course-companion-web.fly.dev]
        end

        subgraph "Infrastructure"
            CLOUD[Cloudflare<br/>DNS + CDN]
            R2[Cloudflare R2<br/>Content Storage]
            CF_TUNNEL[Cloudflare Tunnel<br/>MCP exposure]
        end

        subgraph "External Services"
            STRIPE[Stripe<br/>Payment Processing]
            OPENAI[OpenAI<br/>LLM API]
            CHATGPT[ChatGPT<br/>App Distribution]
        end
    end

    WEB_APP --> FLY_APP
    GADGET_PROD --> FLY_APP
    GADGET_DEV --> FLY_APP
    FLY_APP --> FLY_DB
    FLY_APP --> FLY_REDIS
    FLY_APP --> R2
    FLY_APP --> STRIPE
    FLY_APP --> OPENAI

    FLY_APP --> CLOUD
    GADGET_PROD --> CLOUD
    WEB_APP --> CLOUD

    GADGET_MCP --> CF_TUNNEL

    CHATGPT --> GADGET_PROD

    style FLY_APP fill:#6366f1,stroke:#4f46e5,color:#fff
    style GADGET_PROD fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style WEB_APP fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style FLY_DB fill:#10b981,stroke:#059669,color:#fff
```

### 9.2 Environment Variables

```bash
# Backend (.env)
APP_NAME="Course Companion FTE"
APP_ENV="production"
API_HOST="0.0.0.0"
API_PORT=8000

# Database
DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"

# Redis
REDIS_URL="redis://host:6379"

# JWT
SECRET_KEY="your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=43200
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
CORS_ORIGINS=["https://chat.openai.com","https://chatgpt.com"]

# Stripe
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRICE_ID_FREE="price_..."
STRIPE_PRICE_ID_PREMIUM="price_..."

# OpenAI (Phase 2)
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4o-mini"

# Content Storage
R2_ACCOUNT_ID="..."
R2_ACCESS_KEY_ID="..."
R2_SECRET_ACCESS_KEY="..."
R2_BUCKET_NAME="course-companion-content"
```

### 9.3 Docker Configuration

**Backend Dockerfile** (`Dockerfile.fly`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 10. Technology Stack

### 10.1 Complete Stack Overview

#### Backend Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Framework** | FastAPI 0.104+ | High-performance async API |
| **Runtime** | Python 3.11+ | Language runtime |
| **Database** | PostgreSQL 16 | Primary data store |
| **ORM** | SQLAlchemy 2.0 (async) | Database abstraction |
| **Migrations** | Alembic | Database versioning |
| **Validation** | Pydantic v2 | Request/response validation |
| **Authentication** | JWT (python-jose) | Token-based auth |
| **Password Hashing** | bcrypt (passlib) | Security |
| **Cache** | Redis 5.0+ | Session & response caching |
| **Payment** | Stripe 8.0+ | Subscription management |
| **Storage** | Cloudflare R2 (boto3) | Content delivery |
| **LLM** | OpenAI 1.54+ | AI features (Phase 2) |
| **ASGI Server** | Uvicorn | Production server |
| **Task Queue** | FastAPI BackgroundTasks | Async operations |
| **Testing** | pytest, httpx | Test framework |
| **Deployment** | Docker, Fly.io | Containerization |

#### Frontend Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Framework** | Next.js 16.1+ | React framework |
| **UI** | React 19.2+ | UI library |
| **Language** | TypeScript 5.9+ | Type safety |
| **State** | Zustand 4.4.7 | Client state |
| **Data Fetching** | @tanstack/react-query 5.17+ | Server state |
| **Styling** | Tailwind CSS 3.4+ | Utility-first CSS |
| **Charts** | Chart.js 4.5.1 + react-chartjs-2 | Visualizations |
| **PDF** | jsPDF 4.0.0 + html2canvas | Export notes |
| **Markdown** | react-markdown 10.1.0 | Content rendering |
| **Icons** | Lucide React | Icon library |
| **Payments** | @stripe/stripe-js 8.7.0 | Client-side Stripe |
| **Animations** | Framer Motion 12.29.2 | UI animations |
| **PWA** | next-pwa | Progressive Web App |

#### ChatGPT App Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Platform** | Gadget (@gadgetinc/react) | ChatGPT app hosting |
| **Routing** | React Router 7.12+ | App navigation |
| **SDK** | @gadgetinc/react-chatgpt-apps | ChatGPT integration |
| **MCP** | @modelcontextprotocol/sdk 1.19+ | Protocol implementation |
| **UI** | Radix UI components | Component library |
| **Styling** | Tailwind CSS 4.1.7 | Utility-first CSS |

### 10.2 Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **GitHub Actions** | CI/CD pipeline |
| **Fly.io CLI** | Deployment |
| **Gadget CLI (ggt)** | ChatGPT app deployment |
| **Cloudflare Tunnel** | Local development tunnel |
| **PostgreSQL Client** | Database management |
| **Redis CLI** | Cache management |

### 10.3 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Python Files** | 50+ |
| **Total TypeScript/React Files** | 100+ |
| **API Endpoints** | 40+ |
| **Database Tables** | 15+ |
| **React Components** | 60+ |
| **MCP Tools** | 14 |
| **AI Skills** | 4 |
| **Pages (Web App)** | 20+ |
| **Total Lines of Code** | ~25,000+ |

---

## Appendix

### A. File Structure Reference

#### Backend Key Files
- `backend/app/main.py` - FastAPI application
- `backend/app/config.py` - Configuration management
- `backend/app/database.py` - Database connection
- `backend/app/dependencies.py` - FastAPI dependencies
- `backend/app/services/progress_tracker.py` - Progress logic
- `backend/app/models/` - Database models
- `backend/app/routers/` - API routes
- `backend/content/` - Course content JSON files

#### Frontend Key Files
- `web-app/src/app/layout.tsx` - Root layout
- `web-app/src/app/page.tsx` - Home page
- `web-app/src/store/useStore.ts` - State management
- `web-app/src/lib/api.ts` - API client
- `web-app/src/components/` - React components
- `web-app/src/types/index.ts` - TypeScript types

#### ChatGPT App Key Files
- `chatgpt-app/api/mcp.ts` - MCP server
- `chatgpt-app/api/skills.ts` - Skills definitions
- `chatgpt-app/web/chatgpt/HelloGadget.tsx` - Main app
- `chatgpt-app/web/chatgpt/ChaptersWidget.tsx` - Chapters widget
- `chatgpt-app/web/chatgpt/SkillsWidget.tsx` - Skills widget
- `chatgpt-app/chatgpt-app-config.yaml` - App configuration

### B. Live URLs Reference

| Component | URL | Purpose |
|-----------|-----|---------|
| **Backend API** | `https://course-companion-fte.fly.dev` | FastAPI backend |
| **Health Check** | `https://course-companion-fte.fly.dev/health` | Backend health |
| **API Docs** | `https://course-companion-fte.fly.dev/api/docs` | Swagger UI |
| **ChatGPT App** | `https://course-companion-fte-1.gadget.app` | Production app |
| **MCP Endpoint** | `https://course-companion-fte-1.gadget.app/mcp` | MCP server |
| **Dev ChatGPT App** | `https://course-companion-fte-1--development.gadget.app` | Development |

### C. Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd web-app
npm install
npm run dev

# ChatGPT App
cd chatgpt-app
npm install
ggt dev

# MCP Server (standalone)
cd backend
python mcp_http_server.py

# Database Migrations
cd backend
alembic upgrade head
```

---

**Document Version**: 2.0.0
**Last Updated**: 2026-02-11
**Maintained By**: Course Companion FTE Team

For the most up-to-date architecture documentation, always refer to the source code and this living document.
