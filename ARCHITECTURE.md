# Course Companion FTE - Complete Architecture Diagram

## Table of Contents
1. [High-Level System Architecture](#high-level-system-architecture)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [ChatGPT App Architecture](#chatgpt-app-architecture)
5. [Database Schema](#database-schema)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Deployment Architecture](#deployment-architecture)
8. [Security & Authentication](#security--authentication)
9. [API Endpoints](#api-endpoints)

---

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web App<br/>Next.js 16 + React 19]
        CHATGPT[ChatGPT App<br/>Gadget Framework]
        MOBILE[Mobile<br/>PWA Ready]
    end

    subgraph "API Gateway Layer"
        GADGET[Gadget Platform<br/>course-companion-fte-1.gadget.app]
        MCP[MCP Server<br/>/mcp endpoint]
        FLY[Fly.io Backend<br/>course-companion-fte.fly.dev]
    end

    subgraph "Application Layer"
        AUTH[Auth Service<br/>JWT + OAuth]
        CONTENT[Content Service<br/>Chapters, Quizzes]
        PROGRESS[Progress Tracker<br/>Streaks, Milestones]
        PAYMENT[Payment Service<br/>Stripe Integration]
        AI[AI Skills Service<br/>4 Teaching Modes]
        SEARCH[Search Service<br/>Content Search]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL<br/>User Data, Progress)]
        CONTENT_JSON[(Content JSON<br/>Chapters, Quizzes)]
        REDIS[(Redis<br/>Cache)]
        STRIPE[Stripe API<br/>Payment Processing]
    end

    subgraph "External Services"
        OPENAI[OpenAI API<br/>GPT-4o-mini]
        CLOUDFLARE[Cloudflare Tunnel<br/>MCP Exposure]
    end

    WEB --> FLY
    MOBILE --> FLY
    CHATGPT --> MCP
    MCP --> FLY

    FLY --> AUTH
    FLY --> CONTENT
    FLY --> PROGRESS
    FLY --> PAYMENT
    MCP --> AI

    AUTH --> POSTGRES
    CONTENT --> CONTENT_JSON
    CONTENT --> POSTGRES
    PROGRESS --> POSTGRES
    PROGRESS --> REDIS
    PAYMENT --> STRIPE
    AI --> OPENAI

    MCP --> CLOUDFLARE

    style WEB fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style CHATGPT fill:#10a37f,stroke:#0d8c6e,color:#fff
    style FLY fill:#6366f1,stroke:#4f46e5,color:#fff
    style GADGET fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style POSTGRES fill:#4ade80,stroke:#22c55e,color:#000
    style OPENAI fill:#10a37f,stroke:#0d8c6e,color:#fff
```

---

## Backend Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN[main.py<br/>Application Entry]
        CONFIG[config.py<br/>Configuration Management]
        DB[database.py<br/>Async DB Connection]
        DEPS[dependencies.py<br/>FastAPI Dependencies]
    end

    subgraph "API Routers - v1"
        AUTH_V1[auth.py<br/>Register, Login, Token]
        CHAP_V1[chapters.py<br/>CRUD Operations]
        QUIZ_V1[quizzes.py<br/>Quiz Management]
        PROG_V1[progress.py<br/>Progress Tracking]
        PAY_V1[payments.py<br/>Stripe Integration]
        MILE_V1[milestones.py<br/>Achievements]
        CHAT_V1[chat.py<br/>AI Chat]
        BOOK_V1[bookmarks.py<br/>Content Bookmarks]
        NOTES_V1[notes.py<br/>User Notes]
    end

    subgraph "API Routers - v2"
        ADAPT_V2[adaptive.py<br/>Learning Paths]
        TEACH_V2[teacher.py<br/>Teacher Dashboard]
        USAGE_V2[usage.py<br/>Usage Tracking]
        ASSESS_V2[assessments.py<br/>AI Grading]
    end

    subgraph "Business Logic Services"
        PROG_SVC[progress_tracker.py<br/>Progress Calculation]
        MILE_SVC[milestone_service.py<br/>Achievement Logic]
        QUIZ_SVC[quiz_grader.py<br/>Quiz Evaluation]
        STRIPE_SVC[stripe_service.py<br/>Payment Processing]
        CONTENT_SVC[content.py<br/>Content Management]
        LLM_SVC[llm_service.py<br/>AI Integration]
        SEARCH_SVC[search.py<br/>Content Search]
    end

    subgraph "Data Models"
        USER_M[User Model]
        CHAP_M[ChapterProgress Model]
        QUIZ_M[Quiz Model]
        NOTE_M[Note Model]
        BOOK_M[Bookmark Model]
        STREAK_M[Streak Model]
        SUB_M[Subscription Model]
    end

    subgraph "Utilities"
        CACHE[cache.py<br/>Redis Client]
        VALIDATORS[validators.py<br/>Data Validation]
        HELPERS[helpers.py<br/>Utility Functions]
    end

    MAIN --> AUTH_V1
    MAIN --> CHAP_V1
    MAIN --> QUIZ_V1
    MAIN --> PROG_V1
    MAIN --> PAY_V1
    MAIN --> MILE_V1
    MAIN --> CHAT_V1
    MAIN --> BOOK_V1
    MAIN --> NOTES_V1
    MAIN --> ADAPT_V2
    MAIN --> TEACH_V2
    MAIN --> USAGE_V2
    MAIN --> ASSESS_V2

    AUTH_V1 --> PROG_SVC
    CHAP_V1 --> CONTENT_SVC
    QUIZ_V1 --> QUIZ_SVC
    PROG_V1 --> PROG_SVC
    MILE_V1 --> MILE_SVC
    PAY_V1 --> STRIPE_SVC
    CHAT_V1 --> LLM_SVC

    PROG_SVC --> USER_M
    PROG_SVC --> CHAP_M
    QUIZ_SVC --> QUIZ_M
    CONTENT_SVC --> CHAP_M

    AUTH_V1 --> CACHE
    PROG_V1 --> CACHE

    style MAIN fill:#ef4444,stroke:#dc2626,color:#fff
    style PROG_SVC fill:#f59e0b,stroke:#d97706,color:#fff
    style USER_M fill:#10b981,stroke:#059669,color:#fff
```

---

## Frontend Architecture

```mermaid
graph TB
    subgraph "Next.js Application Structure"
        ROOT[app/<br/>Root Layout]
        LAYOUT[layout.tsx<br/>Global Layout]
        PAGE[page.tsx<br/>Home Page]
        HEADER[components/Header.tsx<br/>Navigation]
        SIDEBAR[components/ChapterSidebar.tsx<br/>Chapter Nav]
    end

    subgraph "Pages (App Router)"
        HOME[page.tsx<br/>Landing Page]
        DASH[dashboard/page.tsx<br/>Student Dashboard]
        CHAP[chapters/[id]/page.tsx<br/>Chapter View]
        QUIZ[chapters/[id]/quiz/page.tsx<br/>Quiz Page]
        LIB[library/page.tsx<br/>Content Library]
        MILE[milestones/page.tsx<br/>Achievements]
        PROG[progress/page.tsx<br/>Progress Tracking]
        TEACH[teacher/page.tsx<br/>Teacher Dashboard]
        PRICING[pricing/page.tsx<br/>Subscription Plans]
        SETTINGS[settings/page.tsx<br/>User Settings]
    end

    subgraph "Components"
        UI[ui/<br/>Base Components]
        BOOK[bookmarks/<br/>Bookmark Components]
        NOTE[notes/<br/>Note Components]
        MODAL[modals/<br/>Dialog Components]
        SEARCH[search/<br/>Search Components]
        INTER[interactive/<br/>Interactive Components]
        AI[AIChat.tsx<br/>AI Assistant]
    end

    subgraph "State Management"
        STORE[useStore.ts<br/>Zustand Store]
        AUTH_STORE[authSlice<br/>Authentication]
        USER_STORE[userSlice<br/>User Data]
        PROG_STORE[progressSlice<br/>Progress]
        SUB_STORE[subscriptionSlice<br/>Subscription]
    end

    subgraph "Services"
        API[api.ts<br/>API Client]
        AUTH_API[auth.ts<br/>Auth Service]
        CHAP_API[chapters.ts<br/>Chapter Service]
        QUIZ_API[quizzes.ts<br/>Quiz Service]
        PROG_API[progress.ts<br/>Progress Service]
    end

    ROOT --> LAYOUT
    LAYOUT --> HEADER
    LAYOUT --> PAGE

    HOME --> DASH
    DASH --> CHAP
    CHAP --> QUIZ
    DASH --> LIB
    DASH --> MILE
    DASH --> PROG
    DASH --> TEACH
    HOME --> PRICING
    DASH --> SETTINGS

    CHAP --> SIDEBAR
    CHAP --> AI
    CHAP --> NOTE
    CHAP --> BOOK

    DASH --> STORE
    STORE --> AUTH_STORE
    STORE --> USER_STORE
    STORE --> PROG_STORE
    STORE --> SUB_STORE

    DASH --> API
    CHAP --> CHAP_API
    QUIZ --> QUIZ_API
    PROG --> PROG_API

    style ROOT fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style STORE fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style DASH fill:#f59e0b,stroke:#d97706,color:#fff
```

---

## ChatGPT App Architecture

```mermaid
graph TB
    subgraph "ChatGPT Application"
        GADGET_APP[Gadget App<br/>course-companion-fte-1]
        ROUTES[api/routes/<br/>MCP Endpoints]
        MCP_SVR[MCP Server<br/>@modelcontextprotocol/sdk]
        WIDGETS[web/chatgpt/<br/>UI Widgets]
    end

    subgraph "MCP Tools"
        GET_CHAP[get_chapters<br/>List All Chapters]
        GET_ONE[get_chapter<br/>Chapter Content]
        SEARCH[search_content<br/>Content Search]
        GET_QUIZ[get_quiz<br/>Quiz Questions]
        SUB_QUIZ[submit_quiz<br/>Submit Answers]
        GET_PROG[get_progress<br/>User Progress]
        GET_SKILL[get_skills<br/>AI Skills]
        ACT_SKILL[activate_skill<br/>Switch Mode]
    end

    subgraph "AI Skills System"
        CONCEPT[💡 Concept Explainer<br/>Simple Explanations]
        QUIZ_M[🎯 Quiz Master<br/>Test Knowledge]
        SOCRATIC[🤔 Socratic Tutor<br/>Guided Learning]
        MOTIVATE[🔥 Progress Motivator<br/>Stay on Track]
    end

    subgraph "Widgets"
        CHAP_W[ChaptersWidget<br/>Chapter Browser]
        SKILL_W[SkillsWidget<br/>Skill Selector]
        HELLO[HelloGadget<br/>Main Widget]
    end

    subgraph "Integration"
        BACKEND_API[FastAPI Backend<br/>course-companion-fte.fly.dev]
        PROD_DB[Production Database]
        TUNNEL[Cloudflare Tunnel<br/>Public Exposure]
    end

    GADGET_APP --> ROUTES
    ROUTES --> MCP_SVR
    MCP_SVR --> GET_CHAP
    MCP_SVR --> GET_ONE
    MCP_SVR --> SEARCH
    MCP_SVR --> GET_QUIZ
    MCP_SVR --> SUB_QUIZ
    MCP_SVR --> GET_PROG
    MCP_SVR --> GET_SKILL
    MCP_SVR --> ACT_SKILL

    GET_SKILL --> CONCEPT
    GET_SKILL --> QUIZ_M
    GET_SKILL --> SOCRATIC
    GET_SKILL --> MOTIVATE

    GET_CHAP --> CHAP_W
    GET_SKILL --> SKILL_W

    GET_CHAP --> BACKEND_API
    GET_ONE --> BACKEND_API
    SEARCH --> BACKEND_API
    GET_QUIZ --> BACKEND_API
    SUB_QUIZ --> BACKEND_API
    GET_PROG --> BACKEND_API

    BACKEND_API --> PROD_DB

    MCP_SVR --> TUNNEL

    style GADGET_APP fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style MCP_SVR fill:#10a37f,stroke:#0d8c6e,color:#fff
    style CHAP_W fill:#3b82f6,stroke:#1d4ed8,color:#fff
```

---

## Database Schema

```mermaid
erDiagram
    USER ||--o{ CHAPTER_PROGRESS : tracks
    USER ||--o{ QUIZ_ATTEMPT : attempts
    USER ||--o{ NOTE : creates
    USER ||--o{ BOOKMARK : saves
    USER ||--o{ STREAK : has
    USER ||--|| SUBSCRIPTION : subscribes

    CHAPTER ||--o{ CHAPTER_PROGRESS : contains
    CHAPTER ||--o{ QUIZ : has
    CHAPTER ||--o{ BOOKMARK : marks
    CHAPTER ||--o{ NOTE : annotates

    USER {
        uuid id PK
        string email UK
        string password_hash
        string name
        boolean is_teacher
        string subscription_tier
        datetime created_at
        datetime updated_at
    }

    CHAPTER {
        string id PK
        string title
        string description
        string content
        string access_tier
        integer order
        string estimated_time
        string difficulty
    }

    CHAPTER_PROGRESS {
        uuid id PK
        uuid user_id FK
        string chapter_id FK
        integer completion_percentage
        string completion_status
        datetime last_accessed
        integer quiz_score
    }

    QUIZ {
        uuid id PK
        string chapter_id FK
        jsonb questions
        integer passing_score
    }

    QUIZ_ATTEMPT {
        uuid id PK
        uuid user_id FK
        uuid quiz_id FK
        jsonb answers
        integer score
        boolean passed
        datetime completed_at
    }

    NOTE {
        uuid id PK
        uuid user_id FK
        string chapter_id FK
        text content
        jsonb tags
        datetime created_at
    }

    BOOKMARK {
        uuid id PK
        uuid user_id FK
        string chapter_id FK
        string section_id
        datetime created_at
    }

    STREAK {
        uuid id PK
        uuid user_id FK
        integer current_streak
        integer longest_streak
        date last_activity
    }

    MILESTONE {
        uuid id PK
        string name
        string description
        jsonb criteria
        integer xp_reward
    }

    USER_MILESTONE {
        uuid user_id FK
        uuid milestone_id FK
        datetime achieved_at
    }

    SUBSCRIPTION {
        uuid id PK
        uuid user_id FK
        string tier
        string status
        datetime started_at
        datetime ends_at
        string stripe_subscription_id
    }

    LLM_USAGE {
        uuid id PK
        uuid user_id FK
        string model
        integer prompt_tokens
        integer completion_tokens
        float cost
        datetime created_at
    }
```

---

## Data Flow Diagrams

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant WebApp
    participant Backend
    participant PostgreSQL
    participant JWT

    User->>WebApp: Enter Email/Password
    WebApp->>Backend: POST /api/v1/auth/login
    Backend->>PostgreSQL: Query User
    PostgreSQL-->>Backend: User Record
    Backend->>Backend: Verify Password Hash
    Backend->>Backend: Generate JWT Token
    Backend-->>WebApp: { access_token, user_data }
    WebApp->>WebApp: Store Token in localStorage
    WebApp->>Backend: GET /api/v1/auth/me (with token)
    Backend->>JWT: Validate Token
    JWT-->>Backend: User ID
    Backend-->>WebApp: User Profile
```

### Chapter Content Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant ContentJSON
    participant Database

    User->>Frontend: Navigate to Chapter
    Frontend->>Backend: GET /api/v1/chapters/{id}
    Backend->>ContentJSON: Read Chapter JSON
    ContentJSON-->>Backend: Chapter Content
    Backend->>Database: Update Progress (last_accessed)
    Backend-->>Frontend: { chapter, progress }
    Frontend->>Frontend: Render Chapter Content
    Frontend->>User: Display Chapter with Quiz Link
```

### Quiz Submission Flow

```mermaid
sequenceDiagram
    participant Student
    participant Frontend
    participant Backend
    participant QuizGrader
    participant ProgressTracker
    participant Database

    Student->>Frontend: Submit Quiz Answers
    Frontend->>Backend: POST /api/v1/quizzes/{id}/submit
    Backend->>QuizGrader: Grade Quiz
    QuizGrader->>QuizGrader: Calculate Score
    QuizGrader-->>Backend: { score, feedback }
    Backend->>ProgressTracker: Update Progress
    ProgressTracker->>ProgressTracker: Check Milestones
    ProgressTracker->>Database: Save Progress & Milestones
    Backend-->>Frontend: { score, feedback, new_progress }
    Frontend->>Student: Display Results
```

### ChatGPT Integration Flow

```mermaid
sequenceDiagram
    participant ChatGPT
    participant MCP
    participant Backend
    participant ContentJSON
    participant OpenAI

    ChatGPT->>MCP: tools/call: get_chapters
    MCP->>Backend: GET /api/v1/chapters
    Backend->>ContentJSON: Fetch Chapters
    ContentJSON-->>Backend: Chapters Array
    Backend-->>MCP: JSON Response
    MCP-->>ChatGPT: { structured_content, widget_uri }
    ChatGPT->>ChatGPT: Display Widget
    ChatGPT->>MCP: tools/call: activate_skill(concept-explainer)
    MCP-->>ChatGPT: Skill Activated
    ChatGPT->>ChatGPT: Apply System Prompt
    ChatGPT->>MCP: tools/call: get_chapter(chapter-1)
    MCP->>Backend: GET /api/v1/chapters/chapter-1
    Backend-->>MCP: Chapter Content
    MCP-->>ChatGPT: { content, widget }
    ChatGPT->>ChatGPT: Explain with Concept Explainer
```

### Payment Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Stripe
    participant Webhook
    participant Database

    User->>Frontend: Click "Subscribe"
    Frontend->>Backend: POST /api/v1/payments/create-checkout
    Backend->>Stripe: Create Checkout Session
    Stripe-->>Backend: checkout_url
    Backend-->>Frontend: Redirect to Stripe
    Frontend->>User: Redirect to Stripe Checkout
    User->>Stripe: Complete Payment
    Stripe->>Webhook: Send webhook event
    Webhook->>Backend: POST /api/v1/payments/webhook
    Backend->>Backend: Verify Signature
    Backend->>Database: Update Subscription
    Backend->>Database: Grant Premium Access
    Backend-->>Stripe: 200 OK
    Stripe->>User: Redirect Back to App
    Frontend->>Backend: GET /api/v1/progress
    Backend-->>Frontend: Updated Progress (premium access)
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Fly.io Backend"
            FLY_APP[course-companion-fte.fly.dev<br/>FastAPI Application]
            FLY_DB[PostgreSQL<br/>Fly.io Managed]
            FLY_REDIS[Redis<br/>Optional Cache]
        end

        subgraph "Gadget Platform"
            GADGET_PROD[course-companion-fte-1.gadget.app<br/>ChatGPT App]
            GADGET_MCP[MCP Server<br/>/mcp endpoint]
            GADGET_DEV[--development.gadget.app<br/>Dev Environment]
        end

        subgraph "Web App"
            WEB_APP[course-companion-web.fly.dev<br/>Next.js Application]
        end

        subgraph "Infrastructure"
            CLOUD_Tunnel[Cloudflare Tunnel<br/>Temporary MCP Exposure]
            CF_DNS[Cloudflare DNS<br/>Domain Management]
        end

        subgraph "External Services"
            STRIPE_API[Stripe API<br/>Payment Processing]
            OPENAI_API[OpenAI API<br/>GPT-4o-mini]
            CHATGPT[ChatGPT Platform<br/>App Distribution]
        end
    end

    WEB_APP --> FLY_APP
    GADGET_PROD --> GADGET_MCP
    GADGET_DEV --> GADGET_MCP
    GADGET_MCP --> FLY_APP
    GADGET_MCP --> CLOUD_Tunnel

    FLY_APP --> FLY_DB
    FLY_APP --> FLY_REDIS
    FLY_APP --> STRIPE_API
    FLY_APP --> OPENAI_API

    FLY_APP --> CF_DNS
    GADGET_PROD --> CF_DNS
    WEB_APP --> CF_DNS

    CHATGPT --> GADGET_PROD

    style FLY_APP fill:#6366f1,stroke:#4f46e5,color:#fff
    style GADGET_PROD fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style WEB_APP fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style FLY_DB fill:#10b981,stroke:#059669,color:#fff
```

---

## Security & Authentication

```mermaid
graph LR
    subgraph "Authentication Methods"
        JWT[JWT Tokens<br/>Access & Refresh]
        OAUTH[OAuth 2.0<br/>Google/GitHub]
        API_KEY[API Keys<br/>Stripe/OpenAI]
    end

    subgraph "Authorization Layers"
        RBAC[Role-Based<br/>Access Control]
        ABAC[Attribute-Based<br/>Access Control]
        SUB_TIER[Subscription Tier<br/>Free/Premium]
    end

    subgraph "Security Measures"
        CORS[CORS Policy<br/>Origin Whitelist]
        RATE[Rate Limiting<br/>100 req/min]
        ENCRYPT[Encryption<br/>bcrypt + AES]
        VALIDATE[Input Validation<br/>Pydantic Schemas]
    end

    subgraph "Protected Resources"
        FREE[Free Content<br/>Chapters 1-3]
        PREMIUM[Premium Content<br/>Chapters 4-6]
        TEACHER[Teacher Dashboard<br/>is_teacher=true]
        ADMIN[Admin Panel<br/>Admin Role]
    end

    JWT --> RBAC
    OAUTH --> RBAC
    API_KEY --> ABAC

    RBAC --> SUB_TIER
    SUB_TIER --> FREE
    SUB_TIER --> PREMIUM
    RBAC --> TEACHER
    RBAC --> ADMIN

    CORS --> FREE
    RATE --> FREE
    ENCRYPT --> FREE
    VALIDATE --> FREE

    style JWT fill:#f59e0b,stroke:#d97706,color:#fff
    style RBAC fill:#ef4444,stroke:#dc2626,color:#fff
    style FREE fill:#10b981,stroke:#059669,color:#fff
    style PREMIUM fill:#8b5cf6,stroke:#7c3aed,color:#fff
```

---

## API Endpoints

### v1 Endpoints

```mermaid
graph TB
    subgraph "Authentication (/api/v1/auth)"
        REGISTER[POST /register<br/>Create User]
        LOGIN[POST /login<br/>Get JWT Token]
        LOGOUT[POST /logout<br/>Invalidate Token]
        ME[GET /me<br/>Current User]
        REFRESH[POST /refresh<br/>Refresh Token]
    end

    subgraph "Chapters (/api/v1/chapters)"
        GET_ALL[GET /<br/>List All Chapters]
        GET_ONE[GET /{id}<br/>Get Chapter Content]
        SEARCH[GET /search<br/>Search Content]
        NEXT[GET /{id}/next<br/>Next Chapter]
        PREV[GET /{id}/previous<br/>Previous Chapter]
    end

    subgraph "Quizzes (/api/v1/quizzes)"
        GET_QUIZ[GET /{id}<br/>Get Quiz]
        SUBMIT[POST /{id}/submit<br/>Submit Answers]
        RESULTS[GET /{id}/results<br/>View Results]
    end

    subgraph "Progress (/api/v1/progress)"
        GET_PROG[GET /<br/>User Progress]
        UPDATE[POST /activity<br/>Update Activity]
        STREAK[GET /streak<br/>Streak Info]
        MILESTONES[GET /milestones<br/>Achievements]
    end

    subgraph "Payments (/api/v1/payments)"
        CHECKOUT[POST /create-checkout<br/>Stripe Session]
        WEBHOOK[POST /webhook<br/>Stripe Events]
        HISTORY[GET /history<br/>Payment History]
        CANCEL[POST /cancel<br/>Subscription]
    end

    subgraph "Bookmarks & Notes"
        BOOK_GET[GET /bookmarks<br/>List Bookmarks]
        BOOK_CREATE[POST /bookmarks<br/>Create Bookmark]
        BOOK_DEL[DELETE /bookmarks/{id}<br/>Delete]
        NOTES_GET[GET /notes<br/>List Notes]
        NOTES_CREATE[POST /notes<br/>Create Note]
        NOTES_UPDATE[PUT /notes/{id}<br/>Update Note]
    end

    style REGISTER fill:#10b981,stroke:#059669,color:#fff
    style GET_ALL fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style SUBMIT fill:#f59e0b,stroke:#d97706,color:#fff
    style CHECKOUT fill:#8b5cf6,stroke:#7c3aed,color:#fff
```

### v2 Endpoints (Phase 2)

```mermaid
graph TB
    subgraph "Adaptive Learning (/api/v2)"
        ADAPTIVE[POST /adaptive-path<br/>Generate Learning Path]
        RECOMMEND[GET /recommendations<br/>Content Recommendations]
        DIFFICULTY[GET /difficulty-level<br/>Adjust Difficulty]
    end

    subgraph "Teacher Tools (/api/v2/teacher)"
        CLASS_STATS[GET /class-stats<br/>Class Analytics]
        STUDENT_PROG[GET /student/{id}/progress<br/>Individual Progress]
        COHORT_COMP[GET /cohort-comparison<br/>Cohort Analysis]
        ENGAGEMENT[GET /engagement-metrics<br/>Engagement Data]
    end

    subgraph "Usage Tracking (/api/v2/usage)"
        TOKENS[GET /tokens<br/>Token Usage]
        COSTS[GET /costs<br/>LLM Costs]
        ACTIVITY[GET /activity<br/>User Activity]
        LIMITS[GET /limits<br/>Rate Limits]
    end

    subgraph "Assessments (/api/v2/assessments)"
        AI_GRADE[POST /grade<br/>AI Grading]
        FEEDBACK[GET /feedback<br/>Detailed Feedback]
        ANALYTICS[GET /analytics<br/>Performance Analytics]
    end

    style ADAPTIVE fill:#ec4899,stroke:#db2777,color:#fff
    style CLASS_STATS fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style AI_GRADE fill:#f59e0b,stroke:#d97706,color:#fff
```

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | Latest |
| Runtime | Python | 3.13+ |
| Database | PostgreSQL | 16+ |
| ORM | SQLAlchemy | 2.0+ (async) |
| Migrations | Alembic | Latest |
| Validation | Pydantic | v2 |
| Authentication | JWT | - |
| Payment | Stripe | Latest |
| Deployment | Fly.io | - |
| Caching | Redis | Optional |

### Frontend Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js | 16 |
| UI Library | React | 19 |
| Language | TypeScript | 5.9+ |
| Styling | Tailwind CSS | 4.1+ |
| State | Zustand | Latest |
| Data Fetching | React Query | Latest |
| Icons | Lucide React | Latest |
| Deployment | Vercel/Fly.io | - |

### ChatGPT App Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Platform | Gadget | Latest |
| SDK | OpenAI Apps SDK | Latest |
| MCP SDK | @modelcontextprotocol/sdk | 1.19+ |
| UI | React | 19 |
| Styling | Tailwind CSS | 4.1+ |
| Deployment | Gadget Platform | - |

---

## Phase Architecture

```mermaid
timeline
    title Course Companion FTE - Development Phases
    section Phase 1 (Current)
        Zero-Backend-LLM Architecture : ChatGPT handles all AI<br/>No LLM in backend
        : Web App with static content<br/>Basic progress tracking
        : MCP Server for ChatGPT<br/>14 tools available
        : Freemium model<br/>3 free + 3 premium chapters
    section Phase 2 (Hybrid)
        Hybrid Intelligence : Selective backend LLM calls<br/>Premium-only AI features
        : Adaptive learning paths<br/>AI-graded assessments
        : Teacher analytics dashboard<br/>Cohort tracking
        : Usage-based cost tracking<br/>Token consumption monitoring
    section Phase 3 (Expansion)
        Enhanced Web App : Full standalone web app<br/>Complete feature parity
        : Mobile PWA<br/>Offline support
        : Advanced analytics<br/>Learning recommendations
        : Community features<br/>Discussion forums
```

---

## Monitoring & Observability

```mermaid
graph TB
    subgraph "Monitoring Stack"
        LOGS[Application Logs<br/>Structured JSON]
        METRICS[Metrics Collection<br/>Prometheus]
        TRACES[Distributed Tracing<br/>OpenTelemetry]
        ALERTS[Alerting<br/>PagerDuty/Slack]
    end

    subgraph "Data Sources"
        API_LOGS[API Request Logs]
        DB_LOGS[Database Query Logs]
        ERROR_LOGS[Error Tracking]
        PERF_LOGS[Performance Metrics]
    end

    subgraph "Visualization"
        GRAFANA[Grafana Dashboards<br/>Metrics & Logs]
        SENTRY[Sentry<br/>Error Tracking]
        ANALYTICS[Custom Analytics<br/>User Behavior]
    end

    API_LOGS --> LOGS
    DB_LOGS --> LOGS
    ERROR_LOGS --> SENTRY
    PERF_LOGS --> METRICS

    LOGS --> GRAFANA
    METRICS --> GRAFANA
    TRACES --> GRAFANA
    ERROR_LOGS --> ALERTS

    style LOGS fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style GRAFANA fill:#f59e0b,stroke:#d97706,color:#fff
    style SENTRY fill:#ef4444,stroke:#dc2626,color:#fff
```

---

## Configuration Management

```mermaid
graph TB
    subgraph "Environment Variables"
        PROD[Production<br/>.env.production]
        DEV[Development<br/>.env]
        TEST[Test<br/>.env.test]
    end

    subgraph "Config Categories"
        APP[Application Config<br/>app_name, version, env]
        DB[Database Config<br/>url, pool_size]
        API[API Config<br/>keys, endpoints]
        CORS[CORS Config<br/>allowed origins]
        FEATURE[Feature Flags<br/>enable_v2, enable_ai]
    end

    subgraph "Secrets Management"
        FLY_SECRETS[Fly.io Secrets<br/>Encrypted]
        ENV_FILE[.env File<br/>Local Dev]
        VAULT[HashiCorp Vault<br/>Future]
    end

    PROD --> APP
    PROD --> DB
    PROD --> API
    DEV --> APP
    DEV --> DB
    DEV --> FEATURE

    APP --> FLY_SECRETS
    API --> FLY_SECRETS

    style PROD fill:#ef4444,stroke:#dc2626,color:#fff
    style DEV fill:#f59e0b,stroke:#d97706,color:#fff
    style FLY_SECRETS fill:#8b5cf6,stroke:#7c3aed,color:#fff
```

---

## Summary

The Course Companion FTE is a comprehensive educational platform with:

- **Dual Frontend Architecture**: Web App (Next.js) + ChatGPT App (Gadget)
- **FastAPI Backend**: Scalable Python backend with PostgreSQL
- **MCP Integration**: 14 tools for ChatGPT app
- **AI Skills System**: 4 specialized teaching modes
- **Freemium Model**: 3 free + 3 premium chapters
- **Payment Integration**: Stripe for subscriptions
- **Progress Tracking**: Streaks, milestones, analytics
- **Zero-Backend-LLM**: ChatGPT handles all AI in Phase 1
- **Hybrid Intelligence**: Selective backend AI in Phase 2

**Live URLs:**
- Backend: `https://course-companion-fte.fly.dev`
- ChatGPT App: `https://course-companion-fte-1.gadget.app`
- MCP Endpoint: `https://course-companion-fte-1.gadget.app/mcp`
