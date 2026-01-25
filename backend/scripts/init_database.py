"""
Course Companion FTE - Database Initialization Script

This script initializes the database with both Phase 1 and Phase 2 schemas.
"""

from pathlib import Path
import sqlite3
import sys

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
db_file = backend_dir / 'course_companion.db'

print("="*70)
print("Course Companion FTE - Database Initialization")
print("="*70)
print(f"Database: {db_file}")


def init_database():
    """Initialize the database with all tables"""

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    try:
        # =====================================================
        # Phase 1 Tables (Original Schema)
        # =====================================================

        print("\n[1/6] Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("[2/6] Creating chapters table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_number INTEGER UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                content_file_path TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("[3/6] Creating chapter_progress table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapter_progress (
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
            )
        """)

        print("[4/6] Creating quizzes table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                questions_json TEXT NOT NULL,
                passing_score INTEGER DEFAULT 70,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id)
            )
        """)

        print("[5/6] Creating quiz_submissions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                score INTEGER NOT NULL,
                passed BOOLEAN NOT NULL,
                feedback_json TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """)

        # =====================================================
        # Phase 2 Tables (Premium Features)
        # =====================================================

        print("[6/20] Adding subscription columns to users...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN subscription_type TEXT DEFAULT 'free'")
        except:
            print("    (Column already exists)")

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMP")
        except:
            print("    (Column already exists)")

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN premium_signup_date TIMESTAMP")
        except:
            print("    (Column already exists)")

        print("[7/20] Creating llm_usage_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature_type TEXT NOT NULL,
                tokens_used INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                model_name TEXT NOT NULL,
                request_details TEXT,
                response_details TEXT,
                mock_call BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        print("[8/20] Creating graded_assessments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS graded_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                student_answer TEXT NOT NULL,
                rubric TEXT,
                question_type TEXT DEFAULT 'short_answer',
                score INTEGER NOT NULL,
                feedback_json TEXT NOT NULL,
                llm_usage_log_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)

        print("[9/20] Creating learning_paths table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                current_chapter_id INTEGER NOT NULL,
                focus TEXT NOT NULL,
                path_json TEXT NOT NULL,
                llm_usage_log_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT (datetime('now', '+7 days')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (current_chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)

        print("[10/20] Creating usage_limits table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                assessments_used_this_month INTEGER DEFAULT 0,
                learning_paths_used_this_month INTEGER DEFAULT 0,
                current_month_start DATE DEFAULT (date('now', 'start of month')),
                last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        print("[11/20] Creating monthly_cost_summary table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_cost_summary (
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
            )
        """)

        # =====================================================
        # Indexes
        # =====================================================

        print("[12/20] Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_user_date ON llm_usage_logs(user_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_feature ON llm_usage_logs(feature_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_graded_assessments_user_chapter ON graded_assessments(user_id, chapter_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_graded_assessments_created ON graded_assessments(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_paths_user ON learning_paths(user_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_paths_expires ON learning_paths(expires_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_monthly_cost_user_date ON monthly_cost_summary(user_id, year DESC, month DESC)")

        # =====================================================
        # Views
        # =====================================================

        print("[13/20] Creating user_premium_status view...")
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS user_premium_status AS
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
            LEFT JOIN usage_limits ul ON u.id = ul.user_id
        """)

        # =====================================================
        # Insert Sample Data
        # =====================================================

        print("[14/20] Inserting sample chapters...")
        chapters_data = [
            (1, "Introduction to Generative AI", "Overview of GenAI fundamentals", "content/chapter_01.md", 1),
            (2, "Neural Network Fundamentals", "Deep learning basics", "content/chapter_02.md", 2),
            (3, "Transformer Architecture", "Attention-based models", "content/chapter_03.md", 3),
            (4, "Attention Mechanisms", "Self-attention details", "content/chapter_04.md", 4),
            (5, "Large Language Models", "GPT and beyond", "content/chapter_05.md", 5),
        ]

        for chapter in chapters_data:
            cursor.execute("""
                INSERT OR IGNORE INTO chapters (chapter_number, title, description, content_file_path, order_index)
                VALUES (?, ?, ?, ?, ?)
            """, chapter)

        print("[15/20] Inserting sample quizzes...")
        cursor.execute("""
            INSERT OR IGNORE INTO quizzes (chapter_id, title, questions_json, passing_score)
            VALUES (
                1,
                'Introduction Quiz',
                '[{"question_id": 1, "type": "multiple_choice", "question": "What is Generative AI?", "options": ["AI that creates content", "AI that analyzes data", "AI that classifies images"], "correct_answer": 0, "explanation": "GenAI creates new content"}]',
                70
            )
        """)

        # =====================================================
        # Final Verification
        # =====================================================

        conn.commit()

        print("\n" + "="*70)
        print("SUCCESS: DATABASE INITIALIZED!")
        print("="*70)

        # Show all tables
        print("\n[Verification] All tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")

        # Count records
        print("\n[Verification] Record counts:")
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"  - users: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM chapters")
        print(f"  - chapters: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM quizzes")
        print(f"  - quizzes: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM llm_usage_logs")
        print(f"  - llm_usage_logs: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM graded_assessments")
        print(f"  - graded_assessments: {cursor.fetchone()[0]}")

        print("\n" + "="*70)
        print("Database initialization complete!")
        print("="*70)

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
