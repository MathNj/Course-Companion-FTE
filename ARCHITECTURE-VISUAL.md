# Course Companion FTE - Visual Architecture Diagrams

Quick reference visual diagrams for Course Companion FTE system architecture.

---

## System Overview (Simplified)

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                               │
│                                                                   │
│   ┌────────────────────┐          ┌────────────────────┐         │
│   │ ChatGPT Custom GPT │          │   Web App (React)  │         │
│   │                    │          │      (Future)       │         │
│   │  • Conversational  │          │  • Native UI        │         │
│   │  • AI Reasoning    │          │  • Dashboard        │         │
│   │  • Actions (API)   │          │  • Direct API       │         │
│   └─────────┬──────────┘          └─────────┬──────────┘         │
│             │                               │                     │
│             └───────────┬───────────────────┘                     │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                          │ HTTPS / REST API
                          │ JWT Bearer Token
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                          │
│                        ┌─────────────┐                            │
│                        │  CORS       │                            │
│                        │  Auth       │                            │
│                        │  Rate Limit │                            │
│                        └─────────────┘                            │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────┴──────────┐        ┌──────────┴─────────┐
│  Business Logic    │        │     Data Layer      │
├────────────────────┤        ├─────────────────────┤
│                    │        │                     │
│  • Auth Service    │        │  • SQLite Database  │
│  • Content Service │        │  • Markdown Files   │
│  • Quiz Service    │        │  • Quiz Definitions │
│  • Progress Svc    │        │                     │
│                    │        │                     │
└────────────────────┘        └─────────────────────┘
```

---

## Detailed Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────┐    ┌──────────────────────────┐     │
│  │   ChatGPT Custom GPT     │    │      Web App (Future)    │     │
│  │                          │    │                          │     │
│  │  URL: chatgpt.com/g/...  │    │  React + TypeScript      │     │
│  │                          │    │                          │     │
│  │  Features:               │    │  Features:               │     │
│  │  • Natural Language UI   │    │  • Native UI/UX          │     │
│  │  • AI Reasoning (GPT-4)  │    │  • Progress Dashboard    │     │
│  │  • Context Memory        │    │  • Interactive Quizzes   │     │
│  │  • Action Execution      │    │  • Visual Analytics      │     │
│  │  • Grounded Q&A          │    │  • Direct API Calls      │     │
│  │                          │    │                          │     │
│  └──────────┬───────────────┘    └──────────┬───────────────┘     │
│             │                                │                    │
│             └────────────┬───────────────────┘                    │
│                          │                                         │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           │ HTTPS (TLS 1.3)
                           │ REST API
                           │ JWT: Bearer <token>
                           │
┌──────────────────────────┼─────────────────────────────────────────┐
│                    API GATEWAY LAYER                               │
│                          │                                         │
│  ┌───────────────────────┴─────────────────────────────────┐      │
│  │             FastAPI Application (backend/app/main.py)    │      │
│  │                                                           │      │
│  │  ┌─────────────────────────────────────────────────┐    │      │
│  │  │  Middleware                                      │    │      │
│  │  │  • CORS (ChatGPT domains only)                  │    │      │
│  │  │  • JWT Authentication                           │    │      │
│  │  │  • Rate Limiting (per endpoint)                 │    │      │
│  │  │  • Error Handling (standardized)                │    │      │
│  │  └─────────────────────────────────────────────────┘    │      │
│  │                                                           │      │
│  │  ┌─────────────────────────────────────────────────┐    │      │
│  │  │  API Documentation                               │    │      │
│  │  │  • Swagger UI: /api/docs                         │    │      │
│  │  │  • ReDoc: /api/redoc                             │    │      │
│  │  │  • OpenAPI: /api/openapi.json                    │    │      │
│  │  └─────────────────────────────────────────────────┘    │      │
│  │                                                           │      │
│  └───────────────────────┬───────────────────────────────────┘      │
│                          │                                         │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
┌─────────┴──────────────┐      ┌──────────┴───────────────┐
│   BUSINESS LOGIC       │      │      DATA LAYER          │
├────────────────────────┤      ├──────────────────────────┤
│                        │      │                          │
│ ┌────────────────────┐ │      │ ┌──────────────────────┐│
│ │  Auth Service      │ │      │ │  SQLite Database     ││
│ │  (auth.py)         │ │      │ │  course_companion.db ││
│ │                    │ │      │ │                      ││
│ │ • Register         │ │      │ │ Tables:              ││
│ │ • Login            │ │      │ │ • users              ││
│ │ • JWT Management   │ │      │ │ • chapters           ││
│ └────────────────────┘ │      │ │ • chapter_progress   ││
│                        │      │ │ • quizzes            ││
│ ┌────────────────────┐ │      │ │ • quiz_submissions   ││
│ │  Content Service   │ │      │ └──────────────────────┘│
│ │  (content.py)      │ │      │                          │
│ │                    │ │      │ ┌──────────────────────┐│
│ │ • List Chapters    │ │      │ │  Course Content      ││
│ │ • Get Chapter      │ │      │ │  backend/content/    ││
│ │ • Search Content   │ │      │ │                      ││
│ │ • Get Definitions  │ │      │ │ • chapter_01.md      ││
│ └────────────────────┘ │      │ │ • chapter_02.md      ││
│                        │      │ │ • ...                ││
│ ┌────────────────────┐ │      │ │ • chapter_15.md      ││
│ │  Quiz Service      │ │      │ └──────────────────────┘│
│ │  (quiz.py)         │ │      │                          │
│ │                    │ │      │ ┌──────────────────────┐│
│ │ • Get Quiz         │ │      │ │  Quiz Definitions    ││
│ │ • Submit Quiz      │ │      │ │  backend/data/       ││
│ │ • Get Submission   │ │      │ │                      ││
│ └────────────────────┘ │      │ │ • quizzes.json       ││
│                        │      │ └──────────────────────┘│
│ ┌────────────────────┐ │      │                          │
│ │  Progress Service  │ │      │                          │
│ │  (progress.py)     │ │      │                          │
│ │                    │ │      │                          │
│ │ • Get Progress     │ │      │                          │
│ │ • Get Chapter      │ │      │                          │
│ │ • Update Progress  │ │      │                          │
│ └────────────────────┘ │      │                          │
└────────────────────────┘      └──────────────────────────┘
```

---

## Data Flow Diagrams

### Registration Flow

```
User          ChatGPT          FastAPI         SQLite
 │              │                │               │
 │──Register───>│                │               │
 │              │                │               │
 │              │──POST /register>│               │
 │              │                │               │
 │              │                │──Check Email──>│
 │              │                │               │
 │              │                │<──Not Found───│
 │              │                │               │
 │              │                │──Insert User──>│
 │              │                │               │
 │              │                │<──Created─────│
 │              │                │               │
 │              │<─201 Created───│               │
 │<─Success─────│                │               │
```

### Content Search Flow

```
User       ChatGPT       FastAPI      Content Files
 │           │             │               │
 │─Search──> │             │               │
 │"transformer"            │               │
 │           │             │               │
 │           │─GET /search>│               │
 │           │             │               │
 │           │             │─Load Files───>│
 │           │             │               │
 │           │             │<─Chapters────│
 │           │             │               │
 │           │             │[Search & Rank]│
 │           │             │               │
 │           │<─200 OK────│               │
 │           │ {results}   │               │
 │<─Answer───│             │               │
```

### Quiz Submission Flow

```
User      ChatGPT       FastAPI         SQLite
 │          │             │               │
 │─Answer──>│             │               │
 │Quiz Q1   │             │               │
 │          │             │               │
 │          │─POST /submit>│               │
 │          │ {answers}   │               │
 │          │             │               │
 │          │             │─Get Quiz─────>│
 │          │             │               │
 │          │             │<─Questions───│
 │          │             │               │
 │          │             │[Grade Answers]│
 │          │             │               │
 │          │             │─Save Result──>│
 │          │             │               │
 │          │             │<─Saved───────│
 │          │             │               │
 │          │<─200 OK────│               │
 │          │ {score,     │               │
 │          │  feedback}  │               │
 │<─Result──│             │               │
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Layer 1: Client Authentication                       │  │
│  │  • JWT Bearer Token in Authorization header          │  │
│  │  • Token expiration: 24 hours                        │  │
│  │  • Token storage: ChatGPT session memory             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Layer 2: API Gateway Protection                     │  │
│  │  • CORS: Only ChatGPT domains allowed                │  │
│  │  • Rate Limiting: Per endpoint limits                │  │
│  │  • Input Validation: Pydantic models                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Layer 3: Authentication Service                     │  │
│  │  • JWT validation on every request                   │  │
│  │  • User identification from token payload            │  │
│  │  • Access control: User-specific data only          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Layer 4: Password Security                          │  │
│  │  • bcrypt hashing (salt rounds: 10)                  │  │
│  │  • Never store plain-text passwords                 │  │
│  │  • Secure password comparison                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Layer 5: Database Security                          │  │
│  │  • Parameterized queries (SQL injection prevention)  │  │
│  │  • User-specific data isolation                     │  │
│  │  • Foreign key constraints                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Deployment                     │
│                    (Fly.io Cloud Platform)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Fly.io App                                           │  │
│  │  URL: course-companion-fte.fly.dev                    │  │
│  │  Region: Newark (ewr)                                 │  │
│  │  Instance: shared-cpu-1x (256 MB RAM)                 │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  FastAPI Application                             │  │  │
│  │  │  • Port: 8000                                   │  │  │
│  │  │  • Auto-start on deploy                         │  │  │
│  │  │  • Health checks                                │  │  │
│  │  │  • Log streaming                                │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  SQLite Database (embedded)                      │  │  │
│  │  │  • File: course_companion.db                    │  │  │
│  │  │  • Local to app instance                        │  │  │
│  │  │  • Persistent across deployments                │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Static Files (course content)                   │  │  │
│  │  │  • backend/content/ (chapters)                   │  │  │
│  │  │  • backend/data/ (quizzes)                       │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Fly.io Infrastructure                                │  │
│  │  • Load Balancer: Automatic                          │  │
│  │  • SSL/TLS: Automatic HTTPS                          │  │
│  │  • Monitoring: Built-in dashboard                    │  │
│  │  • Logs: Real-time streaming                         │  │
│  │  • Deploy: Git push (git push fly main)              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Cost: $0/month (Free Tier)                                 │
│  • App Instance: Free                                      │
│  • Database: Free (SQLite included)                        │
│  • Bandwidth: 3 GB/month free                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Skills Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Claude Code + Agent Skills                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Claude Code Instance                                 │  │
│  │  • General-purpose AI assistant                       │  │
│  │  • Can load Agent Skills as needed                    │  │
│  │  • Skills provide specialized capabilities            │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                 │
│           ┌───────────────┼───────────────┐                 │
│           │               │               │                 │
│  ┌────────┴────┐   ┌──────┴─────┐  ┌────┴─────────┐       │
│  │   concept-  │   │   quiz-    │  │  socratic-   │       │
│  │  explainer  │   │   master   │  │   tutor      │       │
│  │             │   │            │  │              │       │
│  │ • Explain   │   │ • Quizzes  │  │ • Questions  │       │
│  │   at 3      │   │ • Feedback │  │   not        │       │
│  │   levels    │   │ • Encourage│  │   answers    │       │
│  └─────────────┘   └────────────┘  └──────────────┘       │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  progress-motivator                                 │  │
│  │                                                     │  │
│  │  • Celebrate achievements                          │  │
│  │  • Track streaks                                   │  │
│  │  • Unlock milestones                               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│  Skills Location: backend/.skills/{skill-name}/             │
│  • SKILL.md (instructions)                                 │
│  • README.md (documentation)                               │
│  • scripts/validate.py (validation)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoint Structure

```
/api/v1/
├── auth/
│   ├── POST /register          → Create new user
│   └── POST /login             → Get JWT token
│
├── content/
│   ├── GET /chapters           → List all chapters
│   ├── GET /chapters/{id}      → Get chapter content
│   ├── GET /search             → Search all content
│   └── GET /definitions        → Get key term definitions
│
├── quiz/
│   ├── GET /{chapter_id}       → Get quiz for chapter
│   ├── POST /{quiz_id}/submit  → Submit quiz answers
│   └── GET /submissions/{id}   → Get submission result
│
└── progress/
    ├── GET /                   → Get overall progress
    ├── GET /chapters/{id}      → Get chapter progress
    └── PUT /chapters/{id}      → Update chapter progress

Total: 12 endpoints
```

---

## Database Schema Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database Schema                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  users                                                │  │
│  │  ├── id (PK)                                          │  │
│  │  ├── email (UNIQUE)                                   │  │
│  │  ├── hashed_password                                  │  │
│  │  ├── full_name                                        │  │
│  │  ├── created_at                                       │  │
│  │  └── updated_at                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ 1:N                               │
│                          │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  chapter_progress                                    │  │
│  │  ├── id (PK)                                          │  │
│  │  ├── user_id (FK → users.id)                         │  │
│  │  ├── chapter_id (FK → chapters.id)                   │  │
│  │  ├── is_completed                                     │  │
│  │  ├── completion_percentage                            │  │
│  │  ├── last_accessed_at                                 │  │
│  │  └── completed_at                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  chapters                                             │  │
│  │  ├── id (PK)                                          │  │
│  │  ├── chapter_number (UNIQUE)                          │  │
│  │  ├── title                                            │  │
│  │  ├── description                                      │  │
│  │  ├── content_file_path                                │  │
│  │  ├── order_index                                      │  │
│  │  └── created_at                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ 1:N                               │
│                          │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  quizzes                                              │  │
│  │  ├── id (PK)                                          │  │
│  │  ├── chapter_id (FK → chapters.id)                   │  │
│  │  ├── title                                            │  │
│  │  ├── questions_json                                   │  │
│  │  ├── passing_score                                    │  │
│  │  └── created_at                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ 1:N                               │
│                          │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  quiz_submissions                                    │  │
│  │  ├── id (PK)                                          │  │
│  │  ├── user_id (FK → users.id)                         │  │
│  │  ├── quiz_id (FK → quizzes.id)                       │  │
│  │  ├── answers_json                                     │  │
│  │  ├── score                                            │  │
│  │  ├── passed                                           │  │
│  │  ├── feedback_json                                    │  │
│  │  └── submitted_at                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Technology Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Backend:                                                    │
│  ├─ Framework: FastAPI 0.104+                               │
│  ├─ Runtime: Python 3.11+                                   │
│  ├─ Database: SQLite 3                                      │
│  ├─ Auth: JWT (python-jose) + bcrypt                        │
│  ├─ Validation: Pydantic v2                                 │
│  └─ API Docs: Swagger UI + ReDoc                            │
│                                                              │
│  Frontend:                                                   │
│  ├─ ChatGPT: Custom GPT with Actions                        │
│  └─ Web App: React + TypeScript (Future)                    │
│                                                              │
│  Deployment:                                                │
│  ├─ Platform: Fly.io                                        │
│  ├─ CI/CD: Fly.io Git Deploy                               │
│  ├─ Monitoring: Fly.io Dashboard                            │
│  └─ Cost: $0/month (Free Tier)                              │
│                                                              │
│  Development:                                               │
│  ├─ Version Control: Git + GitHub                           │
│  ├─ Package Manager: Poetry                                 │
│  ├─ Code Quality: Black, Ruff, mypy                         │
│  └─ Testing: pytest                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 2 Architecture (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 2 Additions                         │
│              (Hybrid Intelligence Features)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Current (Phase 1)          │  Phase 2 Additions             │
│  ─────────────────────────  │  ───────────────────────────  │
│  • Zero-Backend-LLM         │  • Adaptive Learning Engine   │
│  • Structured Content       │  • LLM Grader Service        │
│  • Multiple Choice Quizzes  │  • Knowledge Graph Service    │
│  • Basic Progress Tracking  │  • AI Mentor Agent           │
│                             │  • Cross-Chapter Synthesis   │
│                             │                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  New Phase 2 Components                             │   │
│  │                                                     │   │
│  │  ┌──────────────────┐    ┌──────────────────┐      │   │
│  │  │ Adaptive Learning│    │ LLM Grader       │      │   │
│  │  │ Engine           │    │ Service          │      │   │
│  │  │                  │    │                  │      │   │
│  │  │ • ML Model       │    │ • LLM API Calls  │      │   │
│  │  │ • Difficulty Adj │    │ • Essay Grading  │      │   │
│  │  │ • Path Optimize  │    │ • Code Review    │      │   │
│  │  └──────────────────┘    └──────────────────┘      │   │
│  │                                                     │   │
│  │  ┌──────────────────┐    ┌──────────────────┐      │   │
│  │  │ Knowledge Graph  │    │ AI Mentor        │      │   │
│  │  │ Service          │    │ Agent            │      │   │
│  │  │                  │    │                  │      │   │
│  │  │ • Concept Links  │    │ • Check-ins      │      │   │
│  │  │ • Synthesis      │    │ • Reminders      │      │   │
│  │  │ • Reviews        │    │ • Scheduling     │      │   │
│  │  └──────────────────┘    └──────────────────┘      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Quick Reference Guide**
- **System Overview**: High-level architecture
- **Component Diagram**: Detailed system components
- **Data Flow**: How requests flow through the system
- **Security**: Security layers and protection mechanisms
- **Deployment**: Production infrastructure on Fly.io
- **Agent Skills**: How the 4 skills integrate
- **API Structure**: All 12 endpoints organized by category
- **Database**: Schema and relationships
- **Tech Stack**: Complete technology overview
- **Phase 2**: Future architecture plans

For detailed documentation, see: ARCHITECTURE-DIAGRAM.md
