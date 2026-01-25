# Course Companion FTE - System Architecture

**Project:** Course Companion FTE (Full-Time Equivalent Educational Tutor)
**Course:** Generative AI Fundamentals
**Architecture:** Zero-Backend-LLM with Dual-Frontend Support
**Last Updated:** 2026-01-26

---

## System Overview

Course Companion FTE is a **digital full-time equivalent educational tutor** that provides personalized learning experiences for the Generative AI Fundamentals course. The system uses a **zero-backend-LLM architecture**, meaning all AI reasoning happens in the client (ChatGPT) while the backend provides structured course content and progress tracking.

### Core Design Principles

1. **Zero-Backend-LLM** - No LLM calls in backend, all AI reasoning in ChatGPT
2. **Grounded Q&A** - All answers grounded in course material (zero hallucination)
3. **Dual Frontend** - Support for both ChatGPT Custom GPT and Web App
4. **Progressive Enhancement** - Phase 1 (essential) → Phase 2 (hybrid intelligence)
5. **API-First Design** - RESTful APIs for all backend functionality

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────┐          ┌──────────────────────┐         │
│  │  ChatGPT Custom GPT  │          │     Web App (React)   │         │
│  │                      │          │      (Future)         │         │
│  │  - AI Reasoning      │          │  - AI Reasoning       │         │
│  │  - Conversational UI │          │  - UI/UX              │         │
│  │  - Actions (API)     │          │  - API Integration    │         │
│  └──────────┬───────────┘          └──────────┬───────────┘         │
│             │                                 │                      │
│             └─────────────┬───────────────────┘                      │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
                            │ HTTPS / REST API
                            │ Bearer Token (JWT)
                            │
┌───────────────────────────┼──────────────────────────────────────────┐
│                    API GATEWAY LAYER                                  │
├───────────────────────────┼──────────────────────────────────────────┤
│                           │                                          │
│  ┌────────────────────────┴──────────────────────────────────┐     │
│  │              FastAPI Application (backend/app/main.py)     │     │
│  │                                                              │     │
│  │  - CORS Middleware (ChatGPT domains)                        │     │
│  │  - Authentication (JWT)                                     │     │
│  │  - Rate Limiting                                            │     │
│  │  - Error Handling                                          │     │
│  │  - OpenAPI Specification                                   │     │
│  └────────────────────────────┬───────────────────────────────┘     │
│                               │                                      │
└───────────────────────────────┼──────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
┌───────────────┴───────────────┐   ┌──────────┴─────────────────────┐
│      BUSINESS LOGIC LAYER      │   │      DATA LAYER                │
├───────────────────────────────┤   ├─────────────────────────────────┤
│                                │   │                                 │
│  ┌─────────────────────────┐   │   │  ┌──────────────────────────┐ │
│  │   Auth Service          │   │   │  │  SQLite Database         │ │
│  │   (auth.py)             │   │   │  │  (course_companion.db)   │ │
│  │                          │   │   │  │                          │ │
│  │  - Register              │   │   │  │  Tables:                 │ │
│  │  - Login                 │   │   │  │  - users                 │ │
│  │  - JWT Management        │   │   │  │  - chapters              │ │
│  └─────────────────────────┘   │   │  │  - chapter_progress      │ │
│                                │   │  │  - quizzes                │ │
│  ┌─────────────────────────┐   │   │  │  - quiz_submissions      │ │
│  │   Content Service       │   │   │  └──────────────────────────┘ │
│  │   (content.py)          │   │   │                                 │
│  │                          │   │   │  ┌──────────────────────────┐ │
│  │  - Get All Chapters      │   │   │  │  Course Content Files     │ │
│  │  - Get Chapter Content   │   │   │  │  (backend/content/)       │ │
│  │  - Search Content        │   │   │  │                          │ │
│  │  - Get Definitions       │   │   │  │  - chapter_01.md          │ │
│  └─────────────────────────┘   │   │  │  - chapter_02.md          │ │
│                                │   │  │  - ...                    │ │
│  ┌─────────────────────────┐   │   │  │  - chapter_15.md          │ │
│  │   Quiz Service          │   │   │  └──────────────────────────┘ │
│  │   (quiz.py)             │   │   │                                 │
│  │                          │   │   │  ┌──────────────────────────┐ │
│  │  - Get Quiz              │   │   │  │  Quiz Definitions         │ │
│  │  - Submit Quiz           │   │   │  │  (backend/data/)          │ │
│  │  - Get Quiz Submission   │   │   │  │                          │ │
│  └─────────────────────────┘   │   │  │  - quizzes.json           │ │
│                                │   │  └──────────────────────────┘ │
│  ┌─────────────────────────┐   │   │                                 │
│  │   Progress Service      │   │   │                                 │
│  │   (progress.py)         │   │   │                                 │
│  │                          │   │   │                                 │
│  │  - Get User Progress     │   │   │                                 │
│  │  - Get Chapter Progress  │   │   │                                 │
│  │  - Update Progress       │   │   │                                 │
│  └─────────────────────────┘   │   │                                 │
│                                │   │                                 │
└────────────────────────────────┘   └─────────────────────────────────┘
```

---

## Component Details

### 1. Client Layer

#### ChatGPT Custom GPT
**URL:** https://chatgpt.com/g/g-6976388081fc8191b24f585910d2b6ce-course-companion-fte-generative-ai

**Responsibilities:**
- Conversational interface for students
- AI reasoning and natural language understanding
- Execute backend Actions (API calls)
- Maintain conversation context
- Guide learning flow

**Key Behaviors:**
- Always calls Actions immediately (no "let me know when you're ready")
- Grounds all responses in course material (zero hallucination)
- Searches before claiming content doesn't exist
- Provides definitions from course content
- Calls quiz APIs for assessments
- Tracks and celebrates student progress

**Actions (5):**
1. `register_user` - Create new user account
2. `get_all_chapters` - List all course chapters
3. `get_chapter_content` - Get full chapter content
4. `search_content` - Search across all chapters
5. `get_definitions` - Get key term definitions
6. `get_quiz` - Get quiz questions for a chapter
7. `submit_quiz` - Submit quiz answers for grading
8. `get_user_progress` - Get overall user progress
9. `get_chapter_progress` - Get progress for specific chapter
10. `update_chapter_progress` - Mark chapter as complete

#### Web App (React) - Future
**Status:** Planned for Phase 2

**Planned Features:**
- Native UI for course navigation
- Interactive quiz interface
- Progress dashboard
- Visual learning analytics
- Direct API integration (same as ChatGPT)

---

### 2. API Gateway Layer

#### FastAPI Application
**File:** `backend/app/main.py`

**Port:** 8000
**Production URL:** https://course-companion-fte.fly.dev

**Middleware:**
- **CORS** - Allows ChatGPT domains (`https://chatgpt.com`, `https://chat.openai.com`)
- **Authentication** - JWT Bearer Token validation
- **Rate Limiting** - Prevents abuse (configured per endpoint)
- **Error Handling** - Standardized error responses

**API Documentation:**
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

**OpenAPI Configuration:**
```python
app = FastAPI(
    title="Course Companion FTE",
    description="Digital FTE Educational Tutor for Generative AI Fundamentals",
    version="1.0.0",
    servers=[
        {
            "url": "https://course-companion-fte.fly.dev",
            "description": "Production server"
        }
    ]
)
```

---

### 3. Business Logic Layer

#### Auth Service
**File:** `backend/app/api/routes/auth.py`

**Endpoints:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

**Features:**
- Password hashing (bcrypt)
- JWT token generation
- Token expiration handling
- User validation

#### Content Service
**File:** `backend/app/api/routes/content.py`

**Endpoints:**
- `GET /api/v1/content/chapters` - List all chapters
- `GET /api/v1/content/chapters/{chapter_id}` - Get chapter content
- `GET /api/v1/content/search` - Search across chapters
- `GET /api/v1/content/definitions` - Get key term definitions

**Features:**
- Markdown content parsing
- Full-text search with ranking
- Definition extraction
- Content filtering by chapter

#### Quiz Service
**File:** `backend/app/api/routes/quiz.py`

**Endpoints:**
- `GET /api/v1/quiz/{chapter_id}` - Get quiz for chapter
- `POST /api/v1/quiz/{quiz_id}/submit` - Submit quiz answers
- `GET /api/v1/quiz/submissions/{submission_id}` - Get submission result

**Features:**
- Multiple question types (multiple choice, true/false, short answer)
- Automated grading
- Immediate feedback generation
- Score calculation
- Answer validation

#### Progress Service
**File:** `backend/app/api/routes/progress.py`

**Endpoints:**
- `GET /api/v1/progress` - Get overall user progress
- `GET /api/v1/progress/chapters/{chapter_id}` - Get chapter progress
- `PUT /api/v1/progress/chapters/{chapter_id}` - Update chapter progress

**Features:**
- Completion percentage calculation
- Streak tracking
- Achievement calculation
- Learning metrics
- Progress history

---

### 4. Data Layer

#### SQLite Database
**File:** `backend/course_companion.db`

**Schema:**

**Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Chapters Table**
```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_number INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    content_file_path TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Chapter Progress Table**
```sql
CREATE TABLE chapter_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chapter_id INTEGER NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completion_percentage INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (chapter_id) REFERENCES chapters(id),
    UNIQUE(user_id, chapter_id)
);
```

**Quizzes Table**
```sql
CREATE TABLE quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    questions_json TEXT NOT NULL,  -- JSON array of questions
    passing_score INTEGER DEFAULT 70,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);
```

**Quiz Submissions Table**
```sql
CREATE TABLE quiz_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    answers_json TEXT NOT NULL,  -- JSON array of answers
    score INTEGER NOT NULL,
    passed BOOLEAN NOT NULL,
    feedback_json TEXT,  -- JSON array of feedback
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);
```

#### Course Content Files
**Directory:** `backend/content/`

**Structure:**
```
backend/content/
├── chapter_01.md  - Introduction to Generative AI
├── chapter_02.md  - Neural Network Fundamentals
├── chapter_03.md  - Transformer Architecture
├── chapter_04.md  - Attention Mechanisms
├── chapter_05.md  - Large Language Models
├── chapter_06.md  - Prompt Engineering
├── chapter_07.md  - Fine-Tuning
├── chapter_08.md  - RAG (Retrieval-Augmented Generation)
├── chapter_09.md  - AI Safety & Alignment
├── chapter_10.md  - Ethical Considerations
├── chapter_11.md  - Practical Applications
├── chapter_12.md  - Building AI Applications
├── chapter_13.md  - Advanced Topics
├── chapter_14.md  - Future Trends
└── chapter_15.md  - Capstone Project
```

**Content Format:**
- Markdown (.md)
- Structured with sections (##, ###)
- Key terms highlighted in **bold**
- Code blocks in ``` fences
- Definitions included inline
- Examples and use cases

#### Quiz Definitions
**File:** `backend/data/quizzes.json`

**Structure:**
```json
{
  "quizzes": [
    {
      "quiz_id": 1,
      "chapter_id": 1,
      "title": "Introduction to Generative AI",
      "passing_score": 70,
      "questions": [
        {
          "question_id": 1,
          "type": "multiple_choice",
          "question": "What is Generative AI?",
          "options": [
            "AI that generates new content",
            "AI that analyzes data",
            "AI that classifies images",
            "AI that predicts stock prices"
          ],
          "correct_answer": 0,
          "explanation": "Generative AI creates new content..."
        }
      ]
    }
  ]
}
```

---

## Data Flow

### User Registration Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   ChatGPT   │         │  FastAPI    │         │   SQLite    │
│   Client    │         │   Backend   │         │  Database   │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ POST /register        │                       │
       │──────────────────────>│                       │
       │ {email, password}     │                       │
       │                       │                       │
       │                       │ Check if user exists  │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ User not found        │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ Hash password         │
       │                       │ Insert user           │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ User created          │
       │                       │<──────────────────────│
       │                       │                       │
       │ 201 Created           │                       │
       │ {user_id, email}      │                       │
       │<──────────────────────│                       │
       │                       │                       │
```

### Content Search Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   ChatGPT   │         │  FastAPI    │         │   Content   │
│   Client    │         │   Backend   │         │    Files    │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ GET /search?query=     │                       │
       │ "transformer"          │                       │
       │──────────────────────>│                       │
       │                       │                       │
       │                       │ Load all chapters     │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ Chapter content       │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ Search & rank         │
       │                       │ [Full-text search]    │
       │                       │                       │
       │ 200 OK                │                       │
       │ {results: [           │                       │
       │   {                  │                       │
       │     chapter: 3,       │                       │
       │     excerpt: "...",   │                       │
       │     relevance: 0.95   │                       │
       │   }                  │                       │
       │ ]}                   │                       │
       │<──────────────────────│                       │
       │                       │                       │
```

### Quiz Submission Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   ChatGPT   │         │  FastAPI    │         │   SQLite    │
│   Client    │         │   Backend   │         │  Database   │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ POST /quiz/1/submit   │                       │
       │ {answers: [0, 1, 2]}  │                       │
       │──────────────────────>│                       │
       │                       │                       │
       │                       │ Get quiz questions    │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ Questions returned    │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ Grade answers         │
       │                       │ [Auto-grading]        │
       │                       │                       │
       │                       │ Save submission       │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ Submission saved      │
       │                       │<──────────────────────│
       │                       │                       │
       │ 200 OK                │                       │
       │ {                     │                       │
       │   score: 85,          │                       │
       │   passed: true,       │                       │
       │   feedback: [...]     │                       │
       │ }                     │                       │
       │<──────────────────────│                       │
       │                       │                       │
```

### Progress Tracking Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   ChatGPT   │         │  FastAPI    │         │   SQLite    │
│   Client    │         │   Backend   │         │  Database   │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ GET /progress         │                       │
       │──────────────────────>│                       │
       │                       │                       │
       │                       │ Get user progress     │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ Progress data         │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ Calculate completion  │
       │                       │ Calculate streak      │
       │                       │                       │
       │ 200 OK                │                       │
       │ {                     │                       │
       │   total_chapters: 8,  │                       │
       │   completion: 53%,    │                       │
       │   streak: 12,         │                       │
       │   achievements: [...] │                       │
       │ }                     │                       │
       │<──────────────────────│                       │
       │                       │                       │
```

---

## Security Architecture

### Authentication Flow

```
┌─────────────┐         ┌─────────────┐
│   ChatGPT   │         │  FastAPI    │
│   Client    │         │   Backend   │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ POST /login           │
       │ {email, password}     │
       │──────────────────────>│
       │                       │
       │                       │ Verify password hash
       │                       │ Generate JWT
       │                       │
       │ 200 OK                │
       │ {access_token}        │
       │<──────────────────────│
       │                       │
       │ Store token           │
       │                       │
       │                       │
       │ GET /chapters         │
       │ Authorization: Bearer │
       │ <jwt_token>           │
       │──────────────────────>│
       │                       │
       │                       │ Validate JWT
       │                       │ Extract user_id
       │                       │ Process request
       │                       │
       │ 200 OK                │
       │ {chapters: [...]}     │
       │<──────────────────────│
       │                       │
```

### Security Features

1. **JWT Authentication**
   - Token-based stateless authentication
   - 24-hour token expiration
   - Bearer token in Authorization header

2. **Password Hashing**
   - bcrypt algorithm
   - Salt rounds: 10
   - Never store plain-text passwords

3. **CORS Protection**
   - Only allows ChatGPT domains
   - Whitelist: `https://chatgpt.com`, `https://chat.openai.com`
   - Blocks unauthorized origins

4. **Rate Limiting**
   - Configured per endpoint
   - Prevents API abuse
   - Distributed attack protection

5. **Input Validation**
   - Pydantic models for all inputs
   - SQL injection prevention (parameterized queries)
   - XSS protection (input sanitization)

---

## Deployment Architecture

### Production Deployment

**Platform:** Fly.io
**URL:** https://course-companion-fte.fly.dev
**Region:** Newark (ewr)
**Instance:** 1x shared-cpu-1x (256 MB RAM)

**Deployment Pipeline:**
```
Local Development
       ↓
Git Push (GitHub)
       ↓
Fly.io Deploy (git push fly main)
       ↓
Production (fly.dev)
```

**Infrastructure:**
- **Load Balancer:** Fly.io automatic
- **SSL/TLS:** Automatic HTTPS
- **Database:** SQLite (local to app)
- **Logs:** Fly.io log streaming
- **Monitoring:** Fly.io metrics dashboard

**Cost Structure:**
- **App Instance:** $0/month (free tier)
- **Database:** $0/month (SQLite included)
- **Bandwidth:** $0/month (3 GB/month free)
- **Total:** $0/month

---

## Agent Skills Architecture

### Skills Integration

The 4 Agent Skills are **not** deployed with the backend. They are **reusable skill packages** that can be loaded by Claude Code instances to provide specialized educational capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Instance                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Agent Skills (Optional)                  │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │   concept-   │  │   quiz-      │                  │  │
│  │  │   explainer  │  │   master     │                  │  │
│  │  └──────────────┘  └──────────────┘                  │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │  socratic-   │  │   progress-  │                  │  │
│  │  │    tutor     │  │  motivator   │                  │  │
│  │  └──────────────┘  └──────────────┘                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Skills can be loaded as needed to provide specialized      │
│  educational guidance and workflows.                        │
└─────────────────────────────────────────────────────────────┘
```

### Skill Structure

Each skill follows the **skill-creator template**:

```
skill-name/
├── SKILL.md              # Core skill instructions
├── README.md             # Documentation
├── scripts/              # Executable code
│   └── validate.py       # Validation script
├── references/           # Reference materials (optional)
└── assets/              # Output files (optional)
```

### Skill Capabilities

**1. concept-explainer**
- Explains at 3 complexity levels
- Uses analogies and examples
- Checks for understanding
- Trigger: "explain", "what is", "how does"

**2. quiz-master**
- Guides through quizzes
- Provides immediate feedback
- Celebrates achievements
- Manages anxiety
- Trigger: "quiz", "test me", "practice"

**3. socratic-tutor**
- Asks guiding questions
- Never gives direct answers
- 3-level hint progression
- Trigger: "help me think", "I'm stuck"

**4. progress-motivator**
- Celebrates achievements
- Tracks learning streaks
- Unlocks milestones
- Encourages during setbacks
- Trigger: "my progress", "streak", "how am I doing"

---

## Phase 2 Architecture (Future)

### Hybrid Intelligence Features

**Planned additions for Phase 2:**

1. **Adaptive Learning**
   - ML-based difficulty adjustment
   - Personalized learning paths
   - Knowledge gap analysis

2. **LLM-Graded Assessments**
   - Open-ended question grading
   - Essay evaluation
   - Code quality assessment

3. **Cross-Chapter Synthesis**
   - Connection mapping
   - Concept relationship graphs
   - Integrated reviews

4. **AI Mentor Agent**
   - Proactive check-ins
   - Personalized reminders
   - Study schedule optimization

### New Components

```
┌─────────────────────────────────────────────────────────┐
│                 Phase 2 Additions                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐    ┌──────────────────┐         │
│  │ Adaptive Learning│    │ LLM Grader       │         │
│  │ Engine           │    │ Service          │         │
│  │                  │    │                  │         │
│  │ - ML Model       │    │ - LLM API        │         │
│  │ - Difficulty Adj │    │ - Essay Grading  │         │
│  │ - Path Optimize  │    │ - Code Review    │         │
│  └──────────────────┘    └──────────────────┘         │
│                                                         │
│  ┌──────────────────┐    ┌──────────────────┐         │
│  │ Knowledge Graph  │    │ AI Mentor        │         │
│  │ Service          │    │ Agent            │         │
│  │                  │    │                  │         │
│  │ - Concept Links  │    │ - Check-ins      │         │
│  │ - Synthesis      │    │ - Reminders      │         │
│  │ - Reviews        │    │ - Scheduling     │         │
│  └──────────────────┘    └──────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **Runtime:** Python 3.11+
- **Database:** SQLite 3
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Validation:** Pydantic v2
- **CORS:** FastAPI CORS Middleware
- **API Docs:** Swagger UI + ReDoc

### Frontend
- **ChatGPT:** Custom GPT with Actions
- **Web App (Future):** React + TypeScript

### Deployment
- **Platform:** Fly.io
- **CI/CD:** Fly.io Git Deploy
- **Monitoring:** Fly.io Dashboard
- **Logs:** Fly.io Log Streaming

### Development
- **Version Control:** Git + GitHub
- **Package Management:** Poetry
- **Code Quality:** Black, Ruff, mypy
- **Testing:** pytest

---

## API Endpoints Summary

### Authentication (2 endpoints)
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user

### Content (4 endpoints)
- `GET /api/v1/content/chapters` - List all chapters
- `GET /api/v1/content/chapters/{chapter_id}` - Get chapter content
- `GET /api/v1/content/search` - Search content
- `GET /api/v1/content/definitions` - Get definitions

### Quiz (3 endpoints)
- `GET /api/v1/quiz/{chapter_id}` - Get quiz
- `POST /api/v1/quiz/{quiz_id}/submit` - Submit quiz
- `GET /api/v1/quiz/submissions/{submission_id}` - Get submission

### Progress (3 endpoints)
- `GET /api/v1/progress` - Get user progress
- `GET /api/v1/progress/chapters/{chapter_id}` - Get chapter progress
- `PUT /api/v1/progress/chapters/{chapter_id}` - Update progress

**Total: 12 endpoints**

---

## Performance Considerations

### Optimization Strategies

1. **Database Indexing**
   - Index on `users.email`
   - Index on `chapter_progress(user_id, chapter_id)`
   - Index on `quiz_submissions(user_id)`

2. **Caching** (Future)
   - Cache frequently accessed chapters
   - Cache quiz definitions
   - Cache user progress data

3. **Pagination** (Future)
   - Paginate search results
   - Paginate quiz submissions
   - Limit response sizes

4. **Async Operations** (Future)
   - Async database queries
   - Async file I/O
   - Concurrent request handling

### Scalability Limits

**Current Architecture (Phase 1):**
- **Concurrent Users:** ~10-50 (single instance)
- **Database Size:** Up to 1 GB (SQLite)
- **Request Rate:** ~100 requests/minute

**Phase 2 Scalability:**
- **Database Migration:** PostgreSQL
- **Horizontal Scaling:** Multiple instances
- **Load Balancing:** Fly.io automatic
- **Caching Layer:** Redis

---

## Monitoring & Observability

### Log Levels
- **INFO:** Normal operations (API calls, user actions)
- **WARNING:** Recoverable issues (failed login, validation errors)
- **ERROR:** Application errors (database failures, exceptions)
- **CRITICAL:** System failures (crashes, data corruption)

### Key Metrics
- **Request Rate:** Requests per second
- **Response Time:** P50, P95, P99 latency
- **Error Rate:** Failed requests percentage
- **User Activity:** Active users, registrations
- **Learning Metrics:** Chapters completed, quizzes passed

### Monitoring Tools
- **Fly.io Dashboard:** Instance metrics, logs
- **Custom Logging:** Structured JSON logs
- **Health Checks:** `/health` endpoint (future)

---

## Compliance & Privacy

### Data Privacy
- **User Data:** Email, hashed password, progress data
- **No PII in Course Content:** Anonymous educational material
- **No Third-Party Tracking:** No analytics cookies
- **Data Retention:** User data stored indefinitely

### Security Standards
- **Authentication:** JWT with expiration
- **Password Security:** bcrypt hashing (salt rounds: 10)
- **CORS:** Restricted to ChatGPT domains
- **Input Validation:** Pydantic models
- **SQL Injection Prevention:** Parameterized queries

### Accessibility (Future)
- **WCAG 2.1 AA:** Compliance target
- **Screen Reader Support:** Semantic HTML
- **Keyboard Navigation:** Full keyboard access
- **Color Contrast:** AA standard

---

## Glossary

- **Zero-Backend-LLM:** Architecture where backend doesn't call LLMs; all AI reasoning happens in client
- **Grounded Q&A:** Question-answering system that only uses provided content (zero hallucination)
- **FTE (Full-Time Equivalent):** Measure equivalent to a full-time educational tutor
- **JWT (JSON Web Token):** Token-based authentication standard
- **CORS (Cross-Origin Resource Sharing):** Security feature for API access control
- **Agent Skills:** Reusable skill packages for Claude Code specialized tasks
- **Hybrid Intelligence:** Combination of structured backend logic with LLM reasoning
- **RAG (Retrieval-Augmented Generation):** AI technique combining retrieval with generation

---

## Conclusion

The Course Companion FTE architecture demonstrates a **clean, modular design** that prioritizes:

- ✅ **Simplicity** - Zero-backend-LLM keeps backend lightweight
- ✅ **Scalability** - API-first design enables multiple frontends
- ✅ **Maintainability** - Clear separation of concerns
- ✅ **Extensibility** - Progressive enhancement to Phase 2
- ✅ **Cost-Efficiency** - $0/month deployment (Fly.io free tier)
- ✅ **Privacy** - No third-party LLM calls in backend
- ✅ **Educational Effectiveness** - Grounded Q&A ensures accuracy

This architecture successfully delivers a **digital FTE educational tutor** for the Generative AI Fundamentals course while maintaining flexibility for future enhancements.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-26
**Author:** Course Companion FTE Development Team
