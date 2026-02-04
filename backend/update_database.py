"""
Update database schema to add missing columns
"""
import sqlite3

def update_schema():
    conn = sqlite3.connect('course_companion.db')
    cursor = conn.cursor()

    try:
        # Rename hashed_password to password_hash if it exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'hashed_password' in columns and 'password_hash' not in columns:
            print("Renaming hashed_password to password_hash...")
            cursor.execute("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash")

        # Add missing columns
        if 'timezone' not in columns:
            print("Adding timezone column...")
            cursor.execute("ALTER TABLE users ADD COLUMN timezone TEXT DEFAULT 'UTC'")

        if 'preferences' not in columns:
            print("Adding preferences column...")
            cursor.execute("ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}'")

        if 'last_active_at' not in columns:
            print("Adding last_active_at column...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_active_at TIMESTAMP")

        if 'is_active' not in columns:
            print("Adding is_active column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")

        if 'is_teacher' not in columns:
            print("Adding is_teacher column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_teacher BOOLEAN DEFAULT 0")

        if 'subscription_tier' not in columns:
            # Rename subscription_type to subscription_tier if needed
            if 'subscription_type' in columns:
                print("Renaming subscription_type to subscription_tier...")
                cursor.execute("ALTER TABLE users RENAME COLUMN subscription_type TO subscription_tier")
            else:
                print("Adding subscription_tier column...")
                cursor.execute("ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'free'")

        conn.commit()
        print("\n[OK] Database schema updated successfully!")

        # Create teacher account
        print("\nCreating teacher account...")
        from app.utils.auth import hash_password
        password_hash = hash_password("teacher123")

        cursor.execute("""
            INSERT OR REPLACE INTO users
            (email, password_hash, full_name, timezone, subscription_tier, is_active, is_teacher)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("mathnj120@gmail.com", password_hash, "Teacher Account", "UTC", "premium", 1, 1))

        conn.commit()
        print("[OK] Teacher account created!")
        print("\nLogin credentials:")
        print("   Email: mathnj120@gmail.com")
        print("   Password: teacher123")
        print("\nLogin at: http://localhost:3003/login")
        print("Dashboard: http://localhost:3003/teacher")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
