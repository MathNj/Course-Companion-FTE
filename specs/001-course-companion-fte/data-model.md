# Data Model: Course Companion FTE

**Phase**: 1 (Design)
**Date**: 2026-01-24
**Purpose**: Define entity relationships, database schemas, and data flow

## Entity Relationship Diagram

```
┌──────────┐         ┌──────────────┐         ┌─────────────┐
│  User    │────────>│ Subscription │         │   Session   │
│          │1      1 │              │         │             │
└────┬─────┘         └──────────────┘         └──────┬──────┘
     │                                                │
     │ 1                                              │ N
     │                                                │
     │ N                                              │
     V                                                V
┌────────────────┐                           ┌──────────────┐
│ChapterProgress │                           │  Interaction │
│                │                           │   (metadata) │
└────────────────┘                           └──────────────┘
     │ N
     │
     │
     V
┌────────────────┐         ┌──────────┐
│  QuizAttempt   │────────>│   Quiz   │
│                │N      1 │ (content)│
└────────────────┘         └────┬─────┘
                                │
                                │ 1
                                │
                                │ N
                                V
                           ┌──────────┐
                           │ Question │
                           │ (content)│
                           └──────────┘

┌──────────┐         ┌──────────┐
│  Streak  │         │ Chapter  │
│          │         │(content) │
└──────────┘         └────┬─────┘
     │ 1                  │
     │                    │ 1
     │                    │
     V                    │ N
┌──────────┐              V
│  User    │         ┌──────────┐
│          │         │ Section  │
└──────────┘         │(content) │
                     └──────────┘
```

## Core Entities

### 1. User

**Purpose**: Represents a student using the Course Companion

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email (for authentication) |
| password_hash | VARCHAR(255) | NULL | Hashed password (NULL if OAuth only) |
| full_name | VARCHAR(255) | NULL | Student's name |
| subscription_tier | VARCHAR(20) | DEFAULT 'free' | 'free', 'premium', or 'pro' |
| subscription_expires_at | TIMESTAMP | NULL | Expiration date (NULL = no expiration) |
| timezone | VARCHAR(50) | DEFAULT 'UTC' | User's timezone (for streak calculation) |
| preferences | JSONB | DEFAULT '{}' | {explanation_level: 'beginner', notifications: true} |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| last_active_at | TIMESTAMP | NULL | Last interaction timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |

**Relationships**:
- One-to-Many with ChapterProgress
- One-to-Many with QuizAttempt
- One-to-Many with Session
- One-to-One with Streak
- One-to-One with Subscription

**Validation Rules**:
- Email must be valid format and unique
- Password must be hashed (bcrypt/argon2)
- Subscription tier must be one of: 'free', 'premium', 'pro'
- Timezone must be valid IANA timezone string

**Indexes**:
- PRIMARY KEY on id
- UNIQUE INDEX on email
- INDEX on subscription_tier (for freemium queries)
- INDEX on last_active_at (for churn analysis)

---

### 2. Subscription

**Purpose**: Tracks user's subscription tier and payment status

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | FOREIGN KEY, UNIQUE | References users(id) |
| tier | VARCHAR(20) | NOT NULL | 'free', 'premium', 'pro' |
| status | VARCHAR(20) | DEFAULT 'active' | 'active', 'expired', 'canceled' |
| started_at | TIMESTAMP | DEFAULT NOW() | Subscription start date |
| expires_at | TIMESTAMP | NULL | Expiration date (NULL = lifetime) |
| payment_provider | VARCHAR(50) | NULL | 'stripe', 'paypal', etc. |
| payment_id | VARCHAR(255) | NULL | External payment reference |
| auto_renew | BOOLEAN | DEFAULT FALSE | Auto-renewal enabled |
| canceled_at | TIMESTAMP | NULL | Cancellation timestamp |

**Relationships**:
- One-to-One with User

**Validation Rules**:
- Tier must match user.subscription_tier (consistency check)
- Expires_at must be in the future if status='active'
- Cannot downgrade from pro to free (business rule)

**Indexes**:
- PRIMARY KEY on id
- UNIQUE INDEX on user_id
- INDEX on expires_at (for expiration checks)

---

### 3. ChapterProgress

**Purpose**: Tracks student progress through course chapters

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | References users(id) |
| chapter_id | VARCHAR(50) | NOT NULL | '01-intro-genai', '02-llms', etc. |
| completed | BOOLEAN | DEFAULT FALSE | Chapter completion status |
| last_section_id | VARCHAR(50) | NULL | Most recent section accessed |
| time_spent_seconds | INTEGER | DEFAULT 0 | Total time in chapter |
| started_at | TIMESTAMP | DEFAULT NOW() | First access timestamp |
| completed_at | TIMESTAMP | NULL | Completion timestamp |
| completion_percentage | DECIMAL(5,2) | DEFAULT 0.00 | % of sections read |

**Relationships**:
- Many-to-One with User

**Validation Rules**:
- chapter_id must be one of: '01-intro-genai', '02-llms', '03-prompting', '04-rag', '05-fine-tuning', '06-ai-applications'
- completion_percentage must be between 0 and 100
- completed_at must be NULL if completed=FALSE

**Indexes**:
- PRIMARY KEY on id
- UNIQUE INDEX on (user_id, chapter_id) - prevents duplicates
- INDEX on user_id (for progress queries)
- INDEX on completed (for analytics)

---

### 4. Quiz (Content - stored in JSON files, not database)

**Purpose**: Quiz questions and answer keys (static content)

**File Location**: `backend/content/quizzes/01-quiz.json`

**JSON Schema**:
```json
{
  "quiz_id": "01-quiz",
  "chapter_id": "01-intro-genai",
  "title": "Introduction to Generative AI Quiz",
  "description": "Test your understanding of GenAI basics",
  "time_limit_minutes": 30,
  "passing_score": 70,
  "questions": [
    {
      "question_id": "q1",
      "type": "multiple_choice",
      "question_text": "Which of the following is a type of Generative AI?",
      "options": [
        {"id": "a", "text": "Large Language Models"},
        {"id": "b", "text": "Image Generation Models"},
        {"id": "c", "text": "Rule-Based Systems"},
        {"id": "d", "text": "All of the above"}
      ],
      "correct_answer": "a",
      "explanation": "LLMs like GPT are generative models. Rule-based systems are not."
    },
    {
      "question_id": "q2",
      "type": "true_false",
      "question_text": "All LLMs are multimodal.",
      "correct_answer": false,
      "explanation": "Most LLMs are text-only. GPT-4V is multimodal (text + images)."
    },
    {
      "question_id": "q3",
      "type": "open_ended",
      "question_text": "Explain the difference between RAG and fine-tuning.",
      "rubric": {
        "accuracy": "Correctly distinguishes retrieval vs parameter updates",
        "completeness": "Mentions use cases for each approach",
        "depth": "Explains tradeoffs (cost, latency, accuracy)"
      },
      "sample_answer": "RAG retrieves relevant documents at inference time..."
    }
  ]
}
```

---

### 5. QuizAttempt

**Purpose**: Records student quiz submissions and scores

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | References users(id) |
| quiz_id | VARCHAR(50) | NOT NULL | References quiz content file |
| attempt_number | INTEGER | DEFAULT 1 | Nth attempt for this quiz |
| score | DECIMAL(5,2) | NULL | Percentage score (0-100) |
| total_questions | INTEGER | NOT NULL | Number of questions |
| correct_answers | INTEGER | DEFAULT 0 | Number correct |
| answers | JSONB | NOT NULL | {q1: "a", q2: false, q3: "text..."} |
| grading_details | JSONB | NULL | {q1: {correct: true, explanation: "..."}} |
| submitted_at | TIMESTAMP | DEFAULT NOW() | Submission timestamp |
| time_taken_seconds | INTEGER | NULL | Time spent on quiz |
| passed | BOOLEAN | NULL | score >= passing_score |

**Relationships**:
- Many-to-One with User

**Validation Rules**:
- score must be between 0 and 100
- correct_answers must be <= total_questions
- answers JSONB must contain keys for all question IDs

**Indexes**:
- PRIMARY KEY on id
- INDEX on (user_id, quiz_id) - for attempt history
- INDEX on user_id (for progress queries)
- INDEX on submitted_at (for analytics)

---

### 6. Session

**Purpose**: Tracks individual learning interactions

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | FOREIGN KEY, NOT NULL | References users(id) |
| interface | VARCHAR(20) | NOT NULL | 'chatgpt' or 'web' |
| started_at | TIMESTAMP | DEFAULT NOW() | Session start |
| ended_at | TIMESTAMP | NULL | Session end (NULL = active) |
| interaction_count | INTEGER | DEFAULT 0 | Number of API calls |
| chapters_accessed | TEXT[] | DEFAULT '{}' | Array of chapter IDs |
| quizzes_taken | TEXT[] | DEFAULT '{}' | Array of quiz IDs |
| metadata | JSONB | DEFAULT '{}' | {device: 'mobile', ip: '...', user_agent: '...'} |

**Relationships**:
- Many-to-One with User

**Validation Rules**:
- interface must be 'chatgpt' or 'web'
- ended_at must be >= started_at if not NULL

**Indexes**:
- PRIMARY KEY on id
- INDEX on user_id (for session history)
- INDEX on started_at (for time-series analysis)

---

### 7. Streak

**Purpose**: Tracks daily learning streaks for motivation

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | FOREIGN KEY, UNIQUE | References users(id) |
| current_streak | INTEGER | DEFAULT 0 | Current consecutive days |
| longest_streak | INTEGER | DEFAULT 0 | All-time longest streak |
| last_activity_date | DATE | NULL | Last day with activity (in user timezone) |
| last_activity_at | TIMESTAMP | NULL | Last activity timestamp (UTC) |
| total_active_days | INTEGER | DEFAULT 0 | Total days with activity |
| streak_frozen | BOOLEAN | DEFAULT FALSE | Streak freeze enabled (premium feature) |

**Relationships**:
- One-to-One with User

**Validation Rules**:
- current_streak <= longest_streak
- last_activity_date derived from last_activity_at + user.timezone

**Indexes**:
- PRIMARY KEY on id
- UNIQUE INDEX on user_id
- INDEX on current_streak (for leaderboards)

---

### 8. Chapter (Content - stored in JSON files, not database)

**Purpose**: Course chapter content (static)

**File Location**: `backend/content/chapters/01-intro-genai.json`

**JSON Schema**:
```json
{
  "chapter_id": "01-intro-genai",
  "chapter_number": 1,
  "title": "Introduction to Generative AI",
  "subtitle": "Understanding the GenAI landscape",
  "learning_objectives": [
    "Define Generative AI and distinguish from other AI types",
    "Identify key GenAI model categories (LLMs, image, multimodal)",
    "Explain historical evolution from GPT-1 to GPT-4"
  ],
  "estimated_time_minutes": 45,
  "prerequisites": [],
  "access_tier": "free",
  "sections": [
    {
      "section_id": "01-what-is-genai",
      "title": "What is Generative AI?",
      "order": 1,
      "content_markdown": "# What is Generative AI?\n\nGenerative AI refers to...",
      "examples": [
        {"name": "ChatGPT", "type": "LLM", "description": "Conversational AI"},
        {"name": "DALL-E", "type": "Image", "description": "Text-to-image generation"}
      ],
      "key_concepts": ["generative models", "neural networks", "transformers"],
      "estimated_time_minutes": 10
    },
    {
      "section_id": "02-brief-history",
      "title": "Brief History of GenAI",
      "order": 2,
      "content_markdown": "# Brief History\n\nFrom GPT-1 (2018) to...",
      "timeline": [
        {"year": 2018, "event": "GPT-1 released"},
        {"year": 2019, "event": "GPT-2 released"},
        {"year": 2020, "event": "GPT-3 released"},
        {"year": 2023, "event": "GPT-4 + ChatGPT widespread adoption"}
      ],
      "estimated_time_minutes": 15
    }
  ],
  "summary": "This chapter introduced the fundamentals of Generative AI...",
  "next_chapter_id": "02-llms"
}
```

---

## Data Flow Diagrams

### User Registration & Authentication Flow
```
┌──────┐         ┌─────────┐         ┌──────────┐         ┌──────┐
│Client│────────>│ FastAPI │────────>│PostgreSQL│────────>│Client│
│      │ POST    │  /auth  │  INSERT │  users   │  JWT    │      │
│      │ email   │ /register│  user   │  table   │  token  │      │
│      │ password│         │         │          │         │      │
└──────┘         └─────────┘         └──────────┘         └──────┘
```

### Content Delivery Flow (Zero-Backend-LLM)
```
┌──────┐         ┌─────────┐         ┌──────────┐         ┌──────┐
│Client│────────>│ FastAPI │────────>│   R2     │────────>│Client│
│      │  GET    │  /v1/   │  FETCH  │ Content  │  JSON   │      │
│      │ chapter │chapters │  file   │  Storage │  data   │      │
└──────┘         └─────────┘         └──────────┘         └──────┘
                      │
                      │ UPDATE
                      V
                 ┌──────────┐
                 │PostgreSQL│
                 │ progress │
                 │  table   │
                 └──────────┘
```

### Quiz Submission Flow (Deterministic Grading)
```
┌──────┐         ┌─────────┐         ┌──────────┐         ┌──────────┐
│Client│────────>│ FastAPI │────────>│   R2     │         │PostgreSQL│
│      │  POST   │  /v1/   │  FETCH  │Quiz JSON │         │ quiz_    │
│      │ answers │ quizzes │  quiz   │  file    │         │ attempts │
│      │         │ /submit │         │          │         │          │
└──────┘         └─────────┘         └──────────┘         └──────────┘
                      │                     │                     │
                      │<────────────────────┘                     │
                      │  Answer key                                │
                      │                                            │
                      │  Grade answers (deterministic)             │
                      │  Calculate score                           │
                      │                                            │
                      │────────────────────────────────────────────>│
                      │                INSERT quiz_attempt         │
                      │<────────────────────────────────────────────│
                      │                                            │
                      V
                 ┌──────┐
                 │Client│
                 │ Score│
                 │Result│
                 └──────┘
```

### Adaptive Learning Flow (Phase 2 - Hybrid)
```
┌──────┐         ┌─────────┐         ┌──────────┐         ┌────────┐
│Client│────────>│ FastAPI │────────>│PostgreSQL│────────>│Claude  │
│      │  POST   │  /v2/   │  QUERY  │ Progress,│  Analyze│Sonnet  │
│      │ request │adaptive │  user   │  Quizzes │ patterns│        │
│      │         │  /path  │  data   │          │         │        │
└──────┘         └─────────┘         └──────────┘         └────────┘
                      │                     │                     │
                      │<────────────────────┘                     │
                      │  User performance data                    │
                      │                                            │
                      │────────────────────────────────────────────>│
                      │  Generate recommendations prompt          │
                      │<────────────────────────────────────────────│
                      │  Personalized learning path               │
                      │                                            │
                      │  Log cost (tokens * price)                 │
                      V
                 ┌──────┐
                 │Client│
                 │Recommendations│
                 └──────┘
```

---

## State Transitions

### User Subscription State Machine
```
┌──────┐
│ free │
└───┬──┘
    │ Upgrade
    V
┌─────────┐
│ premium │
└────┬────┘
    │ Upgrade
    V
┌──────┐         ┌─────────┐
│ pro  │────────>│ expired │
└──────┘  Expires│         │
    │            └─────────┘
    │ Downgrade       │
    V                 │ Renew
┌─────────┐           │
│ premium │<──────────┘
└─────────┘
    │ Cancel
    V
┌──────┐
│ free │
└──────┘
```

### Chapter Progress State Machine
```
┌──────────┐
│not_started│
└─────┬────┘
      │ Access chapter
      V
┌────────────┐
│ in_progress│
└─────┬──────┘
      │ Complete all sections
      V
┌──────────┐
│ completed│
└──────────┘
```

### Quiz Attempt State Machine
```
┌─────────┐
│ started │
└────┬────┘
     │ Submit answers
     V
┌─────────┐         ┌────────┐
│ grading │────────>│ passed │
└────┬────┘  >=70%  └────────┘
     │
     │ <70%
     V
┌────────┐
│ failed │
└────┬───┘
     │ Retry (new attempt)
     V
┌─────────┐
│ started │
└─────────┘
```

---

## Data Integrity Constraints

### Referential Integrity
```sql
-- Cascade deletes for user data
ALTER TABLE chapter_progress ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE quiz_attempts ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE sessions ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- One-to-one relationship enforcement
ALTER TABLE subscriptions ADD CONSTRAINT fk_user_unique
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    UNIQUE(user_id);

ALTER TABLE streaks ADD CONSTRAINT fk_user_unique
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    UNIQUE(user_id);
```

### Business Logic Constraints
```sql
-- Subscription must be active if not expired
ALTER TABLE subscriptions ADD CONSTRAINT chk_active_not_expired
    CHECK (
        (status = 'expired' AND expires_at < NOW()) OR
        (status = 'active' AND (expires_at IS NULL OR expires_at > NOW()))
    );

-- Quiz score must be between 0 and 100
ALTER TABLE quiz_attempts ADD CONSTRAINT chk_score_range
    CHECK (score >= 0 AND score <= 100);

-- Current streak must not exceed longest streak
ALTER TABLE streaks ADD CONSTRAINT chk_streak_consistency
    CHECK (current_streak <= longest_streak);

-- Chapter progress percentage must be 0-100
ALTER TABLE chapter_progress ADD CONSTRAINT chk_progress_range
    CHECK (completion_percentage >= 0 AND completion_percentage <= 100);
```

---

## Caching Strategy

### Redis Cache Keys

| Key Pattern | Value Type | TTL | Purpose |
|-------------|------------|-----|---------|
| `user:{user_id}` | JSON (User object) | 1 hour | User session data |
| `subscription:{user_id}` | JSON (Subscription object) | 1 hour | Access control checks |
| `chapter:{chapter_id}` | JSON (Chapter content) | 24 hours | Content delivery |
| `quiz:{quiz_id}` | JSON (Quiz content) | 24 hours | Quiz delivery |
| `progress:{user_id}` | JSON (Progress summary) | 5 minutes | Dashboard data |
| `streak:{user_id}` | JSON (Streak data) | 5 minutes | Streak display |

### Cache Invalidation

- **User update**: Invalidate `user:{user_id}`
- **Subscription change**: Invalidate `subscription:{user_id}`
- **Chapter completion**: Invalidate `progress:{user_id}`
- **Quiz submission**: Invalidate `progress:{user_id}`
- **Content update**: Invalidate `chapter:{chapter_id}` or `quiz:{quiz_id}`

---

## Migration Strategy

### Initial Schema (Alembic Migration v001)
```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Create users table
    op.create_table('users', ...)

    # Create subscriptions table
    op.create_table('subscriptions', ...)

    # Create chapter_progress table
    op.create_table('chapter_progress', ...)

    # Create quiz_attempts table
    op.create_table('quiz_attempts', ...)

    # Create sessions table
    op.create_table('sessions', ...)

    # Create streaks table
    op.create_table('streaks', ...)

    # Create indexes
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_progress_user_chapter', 'chapter_progress', ['user_id', 'chapter_id'])
    ...

def downgrade():
    # Drop tables in reverse order
    op.drop_table('streaks')
    op.drop_table('sessions')
    op.drop_table('quiz_attempts')
    op.drop_table('chapter_progress')
    op.drop_table('subscriptions')
    op.drop_table('users')
```

### Rollback Plan
- Alembic `downgrade` command
- Database backup before each migration (automated)
- Blue-green deployment for zero-downtime schema changes

---

## Performance Optimization

### Query Optimization
- **Avoid N+1 queries**: Use SQLAlchemy eager loading (`.options(joinedload(...))`)
- **Pagination**: Limit + offset for large result sets
- **Indexes**: Cover all foreign keys and frequently queried columns

### Connection Pooling
```python
# backend/app/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Max connections
    max_overflow=10,  # Additional connections if pool full
    pool_timeout=30,  # Wait time before error
    pool_recycle=3600  # Recycle connections every hour
)
```

### Estimated Query Times (p95)
| Query | Estimated Latency | Optimization |
|-------|-------------------|--------------|
| Get user by ID | <5ms | Primary key index |
| Get chapter progress | <10ms | Composite index on (user_id, chapter_id) |
| Get quiz attempts | <15ms | Index on user_id |
| Check subscription tier | <5ms | Redis cache (1 hour TTL) |
| Get streak | <5ms | Unique index on user_id |

---

## Next Steps

1. Create `contracts/` directory with OpenAPI specs
2. Create `quickstart.md` with local development setup
3. Generate database migration scripts (Alembic)
4. Update agent context with data model decisions
