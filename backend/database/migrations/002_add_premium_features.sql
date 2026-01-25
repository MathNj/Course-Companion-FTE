-- Migration 002: Add Premium Features Support
-- Course Companion FTE - Phase 2 Hybrid Intelligence

-- =====================================================
-- 1. Update users table for subscription tracking
-- =====================================================

ALTER TABLE users ADD COLUMN subscription_type TEXT DEFAULT 'free' CHECK(subscription_type IN ('free', 'premium'));
ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMP;
ALTER TABLE users ADD COLUMN premium_signup_date TIMESTAMP;

-- Add index for subscription queries
CREATE INDEX idx_users_subscription ON users(subscription_type);

-- =====================================================
-- 2. Create LLM usage tracking table
-- =====================================================

CREATE TABLE llm_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type TEXT NOT NULL,  -- 'graded_assessment', 'learning_path'
    tokens_used INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    model_name TEXT NOT NULL,
    request_details TEXT,  -- JSON metadata about the request
    response_details TEXT,  -- JSON metadata about the response
    mock_call BOOLEAN DEFAULT TRUE,  -- TRUE for mock, FALSE for real LLM
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX idx_llm_usage_user_date ON llm_usage_logs(user_id, created_at DESC);
CREATE INDEX idx_llm_usage_feature ON llm_usage_logs(feature_type);
CREATE INDEX idx_llm_usage_mock ON llm_usage_logs(mock_call);

-- =====================================================
-- 3. Create graded assessments table
-- =====================================================

CREATE TABLE graded_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chapter_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    student_answer TEXT NOT NULL,
    rubric TEXT,
    question_type TEXT DEFAULT 'short_answer',  -- 'short_answer', 'essay', 'code_explanation'
    score INTEGER CHECK(score >= 0 AND score <= 100),
    feedback_json TEXT NOT NULL,  -- JSON with strengths, weaknesses, suggestions
    llm_usage_log_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    FOREIGN KEY (llm_usage_log_id) REFERENCES llm_usage_logs(id)
);

-- Create indexes
CREATE INDEX idx_graded_assessments_user_chapter ON graded_assessments(user_id, chapter_id);
CREATE INDEX idx_graded_assessments_created ON graded_assessments(created_at DESC);

-- =====================================================
-- 4. Create learning paths table
-- =====================================================

CREATE TABLE learning_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    current_chapter_id INTEGER NOT NULL,
    focus TEXT NOT NULL,  -- 'reinforce_weaknesses', 'fastest_completion', 'deepest_understanding'
    path_json TEXT NOT NULL,  -- JSON with recommendations, study plan, gaps
    llm_usage_log_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (datetime('now', '+7 days')),  -- Paths expire in 7 days
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (current_chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    FOREIGN KEY (llm_usage_log_id) REFERENCES llm_usage_logs(id)
);

-- Create indexes
CREATE INDEX idx_learning_paths_user ON learning_paths(user_id, created_at DESC);
CREATE INDEX idx_learning_paths_expires ON learning_paths(expires_at);

-- =====================================================
-- 5. Add usage limits tracking
-- =====================================================

CREATE TABLE usage_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    assessments_used_this_month INTEGER DEFAULT 0,
    learning_paths_used_this_month INTEGER DEFAULT 0,
    current_month_start DATE DEFAULT (date('now', 'start of month')),
    last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- 6. Create monthly cost summary table
-- =====================================================

CREATE TABLE monthly_cost_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK(month >= 1 AND month <= 12),
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0.0,
    assessments_count INTEGER DEFAULT 0,
    learning_paths_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, year, month)
);

-- Create index
CREATE INDEX idx_monthly_cost_user_date ON monthly_cost_summary(user_id, year DESC, month DESC);

-- =====================================================
-- 7. Insert default usage limits for existing users
-- =====================================================

INSERT INTO usage_limits (user_id)
SELECT id FROM users
WHERE NOT EXISTS (SELECT 1 FROM usage_limits WHERE usage_limits.user_id = users.id);

-- =====================================================
-- 8. Create view for user premium status
-- =====================================================

CREATE VIEW user_premium_status AS
SELECT
    u.id as user_id,
    u.email,
    u.subscription_type,
    u.subscription_expires_at,
    CASE
        WHEN u.subscription_type = 'premium' AND (u.subscription_expires_at IS NULL OR u.subscription_expires_at > datetime('now'))
        THEN 1
        ELSE 0
    END as is_premium_active,
    COALESCE(ul.assessments_used_this_month, 0) as assessments_used,
    COALESCE(ul.learning_paths_used_this_month, 0) as learning_paths_used
FROM users u
LEFT JOIN usage_limits ul ON u.id = ul.user_id;

-- =====================================================
-- Migration complete
-- =====================================================

-- Verify migration
SELECT 'Migration 002 completed successfully' as status;
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as premium_users FROM users WHERE subscription_type = 'premium';
