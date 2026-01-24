# Data Model: Phase 1 - Zero-Backend-LLM Course Companion

**Date**: 2026-01-24
**Feature**: Phase 1 - Zero-Backend-LLM Course Companion
**Purpose**: Define database schemas, entity relationships, and data flows

## Entity-Relationship Overview

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────┐
│   Student   │───────│ Subscription │       │ ChapterProgress │
│             │ 1:1   │              │       │                 │
│ - email     │       │ - tier       │       │ - completion    │
│ - password  │       │ - expires_at │       │ - quiz_score    │
│ - timezone  │       │              │       │                 │
└─────────────┘       └──────────────┘       └─────────────────┘
       │                                              │
       │ 1:1                                          │ 1:N
       │                                              │
┌─────────────┐                              ┌─────────────────┐
│   Streak    │                              │  QuizAttempt    │
│             │                              │                 │
│ - current   │                              │ - answers       │
│ - longest   │                              │ - score         │
│ - last_date │                              │ - passed        │
└─────────────┘                              └─────────────────┘

Note: Chapter and Quiz content stored in Cloudflare R2, not in database.
Database only stores user-generated data (progress, attempts, streaks).
```

## Core Entities

### 1. Student (User)

Represents a learner using the course. Stores authentication credentials, subscription information, and profile data.

**SQL Schema**:
```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT check_tier CHECK (subscription_tier IN ('free', 'premium')),
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_subscription ON students(subscription_tier, subscription_expires_at);
```

**Fields**:
- `id`: UUID primary key
- `email`: Unique email address (used for login)
- `password_hash`: Bcrypt hashed password
- `full_name`: Optional display name
- `timezone`: IANA timezone (e.g., "America/New_York") for streak calculations
- `subscription_tier`: 'free' or 'premium'
- `subscription_expires_at`: NULL for free tier, expiration date for premium
- `created_at`: Registration timestamp
- `last_active_at`: Last interaction timestamp (updated on any API call)

**Validation Rules**:
- Email: Valid email format, unique
- Password: Minimum 8 characters (enforced at API level before hashing)
- Timezone: Valid IANA timezone string
- Subscription tier: Enum ('free', 'premium')

**Relationships**:
- 1:N with ChapterProgress (one student, many chapter progresses)
- 1:N with QuizAttempt (one student, many quiz attempts)
- 1:1 with Streak (one student, one streak record)

---

### 2. ChapterProgress

Represents a student's progress on a specific chapter. Tracks completion status, quiz performance, and time spent.

**SQL Schema**:
```sql
CREATE TABLE chapter_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    chapter_id VARCHAR(50) NOT NULL,
    completion_status VARCHAR(20) DEFAULT 'not_started',
    quiz_score DECIMAL(5,2),
    time_spent_minutes INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    CONSTRAINT check_status CHECK (completion_status IN ('not_started', 'in_progress', 'completed')),
    CONSTRAINT check_score_range CHECK (quiz_score IS NULL OR (quiz_score >= 0 AND quiz_score <= 100)),
    CONSTRAINT unique_student_chapter UNIQUE (student_id, chapter_id)
);

CREATE INDEX idx_progress_student ON chapter_progress(student_id);
CREATE INDEX idx_progress_chapter ON chapter_progress(chapter_id);
CREATE INDEX idx_progress_completion ON chapter_progress(completion_status, completed_at);
```

**Fields**:
- `id`: UUID primary key
- `student_id`: Foreign key to students
- `chapter_id`: Chapter identifier (e.g., "01-intro-genai", matches R2 filename)
- `completion_status`: 'not_started', 'in_progress', 'completed'
- `quiz_score`: Highest quiz score achieved (0-100), NULL if quiz not attempted
- `time_spent_minutes`: Accumulated reading time
- `last_accessed_at`: Last time student viewed this chapter
- `completed_at`: Timestamp when chapter marked complete (quiz passed with ≥70%)

**Validation Rules**:
- chapter_id: Must match one of 6 chapter IDs (validated at API level)
- quiz_score: 0-100 or NULL
- completion_status: Enum ('not_started', 'in_progress', 'completed')

**Business Logic**:
- Chapter marked 'completed' when quiz_score ≥ 70%
- Progress percentage calculated as: (completed chapters / 6) * 100

---

### 3. QuizAttempt

Represents a single quiz submission by a student. Stores answers, score, and grading details.

**SQL Schema**:
```sql
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    quiz_id VARCHAR(50) NOT NULL,
    chapter_id VARCHAR(50) NOT NULL,
    answers_json JSONB NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    passed BOOLEAN NOT NULL,
    grading_details_json JSONB,
    submitted_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT check_score_range CHECK (score >= 0 AND score <= 100)
);

CREATE INDEX idx_attempts_student ON quiz_attempts(student_id, submitted_at DESC);
CREATE INDEX idx_attempts_quiz ON quiz_attempts(quiz_id);
CREATE INDEX idx_attempts_chapter ON quiz_attempts(chapter_id);
```

**Fields**:
- `id`: UUID primary key
- `student_id`: Foreign key to students
- `quiz_id`: Quiz identifier (e.g., "01-quiz")
- `chapter_id`: Associated chapter (e.g., "01-intro-genai")
- `answers_json`: JSONB of submitted answers: `{"q1": "a", "q2": true, "q3": "RAG uses..."}`
- `score`: Calculated score (0-100)
- `passed`: Boolean (true if score ≥ 70%)
- `grading_details_json`: JSONB of per-question feedback: `{"q1": {"correct": true, "explanation": "..."}}`
- `submitted_at`: Submission timestamp

**JSONB Structure**:
```json
// answers_json
{
  "q1": "a",                    // Multiple-choice answer
  "q2": false,                  // True/false answer
  "q3": "RAG retrieves relevant documents..." // Short-answer text
}

// grading_details_json
{
  "q1": {
    "correct": true,
    "explanation": "Correct! LLMs are generative models."
  },
  "q2": {
    "correct": false,
    "explanation": "Incorrect. Most LLMs are text-only, not multimodal."
  },
  "q3": {
    "correct": true,
    "score": 8.5,
    "feedback": "Good explanation. Could elaborate on cost tradeoffs."
  }
}
```

**Business Logic**:
- Unlimited retakes allowed (each attempt stored separately)
- Highest score per student per chapter used for progress tracking
- Short-answer grading: Keyword matching with partial credit (0-10 scale per question)

---

### 4. Streak

Represents a student's learning streak. Tracks current streak, longest streak, and last activity date.

**SQL Schema**:
```sql
CREATE TABLE streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID UNIQUE NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    timezone VARCHAR(50) DEFAULT 'UTC',

    CONSTRAINT check_streaks_positive CHECK (current_streak >= 0 AND longest_streak >= 0)
);

CREATE INDEX idx_streaks_student ON streaks(student_id);
CREATE INDEX idx_streaks_last_activity ON streaks(last_activity_date DESC);
```

**Fields**:
- `id`: UUID primary key
- `student_id`: Foreign key to students (unique - one streak per student)
- `current_streak`: Current consecutive days of activity
- `longest_streak`: All-time record streak
- `last_activity_date`: Date of last activity (in user's timezone)
- `timezone`: IANA timezone for accurate date calculations

**Validation Rules**:
- current_streak: ≥ 0
- longest_streak: ≥ 0, ≥ current_streak

**Business Logic (Timezone-Aware)**:
```python
def update_streak(student_id: UUID):
    """Update streak based on activity in user's local timezone."""
    streak = get_streak(student_id)
    user_tz = get_user_timezone(student_id)
    today_local = datetime.now(tz=ZoneInfo(user_tz)).date()

    if streak.last_activity_date is None:
        # First activity
        streak.current_streak = 1
        streak.longest_streak = 1
    elif (today_local - streak.last_activity_date).days == 1:
        # Consecutive day
        streak.current_streak += 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    elif (today_local - streak.last_activity_date).days == 0:
        # Same day (already counted)
        pass
    else:
        # Streak broken
        streak.current_streak = 1

    streak.last_activity_date = today_local
    save_streak(streak)
```

**Milestone Celebrations** (per FR-024):
- 3-day streak: "Great start! 3 days in a row!"
- 7-day streak: "One week streak! You're building a habit."
- 14-day streak: "Two weeks of consistent learning! Impressive dedication."
- 30-day streak: "30-day streak! You're unstoppable!"

---

## Content Entities (Stored in Cloudflare R2, Not Database)

### 5. Chapter (R2 JSON File)

Stored as JSON files in R2: `content/chapters/01-intro-genai.json`

**Structure**:
```json
{
  "chapter_id": "01-intro-genai",
  "chapter_number": 1,
  "title": "Introduction to Generative AI",
  "subtitle": "Understanding the GenAI landscape",
  "access_tier": "free",
  "estimated_time_minutes": 45,
  "difficulty_level": "beginner",
  "learning_objectives": [
    "Define Generative AI and distinguish from other AI types",
    "Identify key GenAI model categories (LLMs, image, multimodal)"
  ],
  "sections": [
    {
      "section_id": "01-what-is-genai",
      "title": "What is Generative AI?",
      "order": 1,
      "estimated_time_minutes": 10,
      "content_markdown": "# What is Generative AI?\n\nGenerative AI is..."
    }
  ]
}
```

---

### 6. Quiz (R2 JSON File)

Stored as JSON files in R2: `content/quizzes/01-quiz.json`

**Structure**:
```json
{
  "quiz_id": "01-quiz",
  "chapter_id": "01-intro-genai",
  "passing_score": 70,
  "questions": [
    {
      "question_id": "q1",
      "question_text": "Which of the following is a generative model?",
      "type": "multiple-choice",
      "options": ["GPT-4", "Logistic Regression", "Decision Tree", "K-Means"],
      "correct_answer": "GPT-4",
      "explanation_correct": "Correct! GPT-4 is a large language model that generates text.",
      "explanation_incorrect": "Incorrect. {selected} is not a generative model. GPT-4 generates new content."
    },
    {
      "question_id": "q2",
      "question_text": "Most LLMs are multimodal (text + image).",
      "type": "true-false",
      "correct_answer": false,
      "explanation_correct": "Correct! Most LLMs are text-only (GPT-3, Claude, etc.).",
      "explanation_incorrect": "Incorrect. Most LLMs are text-only. Multimodal models are less common."
    },
    {
      "question_id": "q3",
      "question_text": "Explain the difference between RAG and fine-tuning.",
      "type": "short-answer",
      "keywords": ["retrieval", "documents", "parameters", "training"],
      "explanation": "RAG retrieves relevant documents at inference time, while fine-tuning updates model parameters during training."
    }
  ]
}
```

---

## Data Flow Diagrams

### Authentication Flow

```
┌────────┐                ┌────────────┐              ┌──────────┐
│ Client │                │ FastAPI    │              │ Database │
└───┬────┘                └─────┬──────┘              └────┬─────┘
    │                           │                          │
    │ POST /auth/register       │                          │
    │ {email, password}         │                          │
    ├──────────────────────────>│                          │
    │                           │                          │
    │                           │ Hash password (bcrypt)   │
    │                           │                          │
    │                           │ INSERT INTO students     │
    │                           ├─────────────────────────>│
    │                           │                          │
    │                           │<─────────────────────────┤
    │                           │ (student_id)             │
    │                           │                          │
    │ 201 Created               │                          │
    │ {user_id, email}          │                          │
    │<──────────────────────────┤                          │
    │                           │                          │
    │ POST /auth/login          │                          │
    │ {email, password}         │                          │
    ├──────────────────────────>│                          │
    │                           │                          │
    │                           │ SELECT FROM students     │
    │                           │ WHERE email = ?          │
    │                           ├─────────────────────────>│
    │                           │                          │
    │                           │<─────────────────────────┤
    │                           │ (user, password_hash)    │
    │                           │                          │
    │                           │ Verify password (bcrypt) │
    │                           │                          │
    │                           │ Generate JWT token       │
    │                           │ (user_id, tier, exp)     │
    │                           │                          │
    │ 200 OK                    │                          │
    │ {access_token, exp}       │                          │
    │<──────────────────────────┤                          │
```

### Content Delivery Flow

```
┌────────┐     ┌────────────┐     ┌───────┐     ┌──────┐
│ Client │     │ FastAPI    │     │ Redis │     │  R2  │
└───┬────┘     └─────┬──────┘     └───┬───┘     └──┬───┘
    │                │                 │            │
    │ GET /v1/chapters/01-intro-genai  │            │
    │ Authorization: Bearer {token}    │            │
    ├─────────────────>│                 │            │
    │                │                 │            │
    │                │ Verify JWT      │            │
    │                │ Verify access   │            │
    │                │ (tier vs chapter)│           │
    │                │                 │            │
    │                │ Check cache     │            │
    │                ├────────────────>│            │
    │                │                 │            │
    │                │<────────────────┤            │
    │                │ (MISS)          │            │
    │                │                 │            │
    │                │ Fetch from R2   │            │
    │                │ (01-intro-genai.json)        │
    │                ├────────────────────────────>│
    │                │                 │            │
    │                │<────────────────────────────┤
    │                │ (chapter JSON)  │            │
    │                │                 │            │
    │                │ Cache (TTL: 24h)│            │
    │                ├────────────────>│            │
    │                │                 │            │
    │ 200 OK         │                 │            │
    │ {chapter data} │                 │            │
    │<───────────────┤                 │            │
```

### Quiz Submission Flow

```
┌────────┐     ┌────────────┐     ┌──────────┐     ┌──────┐
│ Client │     │ FastAPI    │     │ Database │     │  R2  │
└───┬────┘     └─────┬──────┘     └────┬─────┘     └──┬───┘
    │                │                  │              │
    │ POST /v1/quizzes/01-quiz/submit  │              │
    │ {answers: {q1: "a", q2: false}}  │              │
    ├─────────────────>│                  │              │
    │                │                  │              │
    │                │ Fetch quiz from R2              │
    │                ├─────────────────────────────────>│
    │                │                  │              │
    │                │<─────────────────────────────────┤
    │                │ (quiz JSON with answer keys)    │
    │                │                  │              │
    │                │ Grade answers    │              │
    │                │ (deterministic)  │              │
    │                │ - MC: exact match│              │
    │                │ - T/F: boolean   │              │
    │                │ - SA: keywords   │              │
    │                │                  │              │
    │                │ Calculate score  │              │
    │                │ (80% = 8/10)     │              │
    │                │                  │              │
    │                │ INSERT quiz_attempt             │
    │                ├─────────────────>│              │
    │                │                  │              │
    │                │ UPDATE chapter_progress         │
    │                │ (highest score)  │              │
    │                ├─────────────────>│              │
    │                │                  │              │
    │                │ UPDATE streak    │              │
    │                ├─────────────────>│              │
    │                │                  │              │
    │ 200 OK         │                  │              │
    │ {score, passed,│                  │              │
    │  grading_details}                 │              │
    │<───────────────┤                  │              │
```

---

## Caching Strategy

### Redis Cache Keys

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `chapter:{chapter_id}` | 24 hours | Full chapter JSON from R2 |
| `quiz:{quiz_id}` | 24 hours | Quiz JSON with answer keys |
| `user_progress:{user_id}` | 5 minutes | User progress summary |
| `streak:{user_id}` | 1 hour | Current streak data |

### Cache Invalidation

- Chapter content: Invalidated manually when content updated in R2
- Quiz data: Invalidated manually when quiz updated in R2
- User progress: Invalidated on any progress update (chapter completion, quiz submission)
- Streak: Invalidated on any user activity

---

## Migration Strategy

### Alembic Migrations

**Initial Migration (v001)**:
```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Create students table
    op.create_table('students', ...)

    # Create chapter_progress table
    op.create_table('chapter_progress', ...)

    # Create quiz_attempts table
    op.create_table('quiz_attempts', ...)

    # Create streaks table
    op.create_table('streaks', ...)

    # Create indexes
    op.create_index('idx_students_email', 'students', ['email'])
    ...

def downgrade():
    op.drop_table('streaks')
    op.drop_table('quiz_attempts')
    op.drop_table('chapter_progress')
    op.drop_table('students')
```

### Rollback Plan

If migration fails:
1. Run `alembic downgrade -1` to revert to previous version
2. Fix migration script
3. Re-run `alembic upgrade head`

For production:
1. Backup database before migration
2. Test migration on staging environment first
3. Run migration during low-traffic window
4. Monitor for errors
5. Rollback if issues detected

---

## Performance Optimization

### Query Optimization

**Frequent Queries** (must be <100ms):
```sql
-- Get user progress (with index on student_id)
SELECT * FROM chapter_progress WHERE student_id = ? ORDER BY last_accessed_at DESC;

-- Get highest quiz score (with index on student_id, chapter_id)
SELECT MAX(score) FROM quiz_attempts WHERE student_id = ? AND chapter_id = ?;

-- Check subscription (with index on email)
SELECT subscription_tier, subscription_expires_at FROM students WHERE email = ?;
```

**Index Coverage**:
- All foreign keys indexed
- All frequently filtered columns indexed (email, student_id, chapter_id, submission timestamp)
- Composite indexes for common query patterns (student_id + chapter_id)

### Connection Pooling

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Max 20 connections
    max_overflow=10,       # Allow 10 overflow connections
    pool_pre_ping=True,    # Verify connection health before use
    echo=False             # Disable SQL logging in production
)
```

---

## Data Retention & Privacy

### Retention Policy

| Data Type | Retention Period | Rationale |
|-----------|------------------|-----------|
| User accounts | Indefinite (until user deletes) | Required for service |
| Progress data | Indefinite | Historical learning data valuable |
| Quiz attempts | 90 days | Sufficient for analysis, then archived |
| Streaks | Indefinite | Motivational data |
| Session logs | 30 days | Debugging, then deleted |

### GDPR Compliance (if applicable)

- Right to access: API endpoint to export all user data as JSON
- Right to delete: Cascade delete on `students` table removes all related data
- Right to rectify: Update endpoints for profile data
- Data portability: Export endpoint provides machine-readable JSON

---

**Data Model Complete. Ready for API contract definition.**
