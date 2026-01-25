#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run database migration 002 to add Phase 2 premium features (SQLite version)
"""

import sys
import os
from pathlib import Path
import sqlite3

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
db_file = backend_dir / 'course_companion.db'

print(f"Running migration 002 for SQLite database...")
print(f"Database file: {db_file}")


def run_migration():
    """Run migration 002"""

    # Check if database exists
    if not db_file.exists():
        print(f"\nDatabase file not found: {db_file}")
        print("Creating new database...")

    # Connect to database
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Read migration SQL
    migration_file = backend_dir / 'database' / 'migrations' / '002_add_premium_features.sql'

    if not migration_file.exists():
        print(f"\nERROR: Migration file not found: {migration_file}")
        sys.exit(1)

    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    # Start transaction
    try:
        # Split by semicolon to handle multiple statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        print(f"\nExecuting {len(statements)} SQL statements...")

        executed = 0
        skipped = 0

        for i, statement in enumerate(statements, 1):
            # Skip comments and empty lines
            if statement.startswith('--') or not statement.strip():
                continue

            print(f"\n[{i}/{len(statements)}] Executing...")
            # Print first 80 chars
            print(f"  {statement[:80]}...")

            try:
                cursor.execute(statement)
                executed += 1
            except Exception as e:
                # Check if it's a "already exists" error
                error_str = str(e).lower()
                if "already exists" in error_str or "duplicate column" in error_str:
                    print(f"  INFO: Object already exists, skipping...")
                    skipped += 1
                    continue
                else:
                    print(f"\nERROR executing statement:")
                    print(f"  {statement}")
                    print(f"  Error: {e}")
                    raise e

        # Commit transaction
        conn.commit()
        print("\n" + "="*70)
        print("SUCCESS: MIGRATION 002 COMPLETED!")
        print("="*70)
        print(f"Executed: {executed} statements")
        print(f"Skipped: {skipped} statements (already existed)")

        # Verify migration
        print("\n" + "="*70)
        print("VERIFICATION")
        print("="*70)

        # Check users table
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        print(f"\nOK: users table - {len(columns)} columns")
        has_subscription = 'subscription_type' in columns
        has_expires = 'subscription_expires_at' in columns
        has_signup = 'premium_signup_date' in columns

        print(f"   subscription_type: {'ADDED' if has_subscription else 'MISSING'}")
        print(f"   subscription_expires_at: {'ADDED' if has_expires else 'MISSING'}")
        print(f"   premium_signup_date: {'ADDED' if has_signup else 'MISSING'}")

        # Check new tables
        tables_to_check = [
            'llm_usage_logs',
            'graded_assessments',
            'learning_paths',
            'usage_limits',
            'monthly_cost_summary'
        ]

        print(f"\nOK: Checking new tables:")
        all_tables_exist = True
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            status = 'OK' if exists else 'MISSING'
            print(f"   [{status}] {table}")
            if not exists:
                all_tables_exist = False

        # Check views
        print(f"\nOK: Checking views:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='user_premium_status'")
        view_exists = cursor.fetchone() is not None
        print(f"   [{'OK' if view_exists else 'MISSING'}] user_premium_status")

        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\nOK: Total users: {user_count}")

        # Count premium users
        cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_type='premium'")
        premium_count = cursor.fetchone()[0]
        print(f"OK: Premium users: {premium_count}")

        # Show all tables
        print(f"\nOK: All tables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")

        print("\n" + "="*70)
        if all_tables_exist:
            print("SUCCESS: ALL TABLES CREATED!")
        else:
            print("WARNING: SOME TABLES MAY BE MISSING")
        print("="*70)

    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"\nERROR: Migration failed: {e}")
        print("Rolling back changes...")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
