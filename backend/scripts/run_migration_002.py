#!/usr/bin/env python3
"""
Run database migration 002 to add Phase 2 premium features
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.config import settings


def run_migration():
    """Run migration 002"""

    migration_file = backend_dir / 'database' / 'migrations' / '002_add_premium_features.sql'

    print(f"Running migration 002...")
    print(f"Migration file: {migration_file}")

    # Read migration SQL
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    # Create synchronous engine for migration
    # Convert async URL to sync URL
    sync_db_url = settings.database_url.replace("+asyncpg", "")
    engine = create_engine(sync_db_url, echo=True)

    # Execute migration
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            # Split by semicolon to handle multiple statements
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

            print(f"\nExecuting {len(statements)} SQL statements...")

            for i, statement in enumerate(statements, 1):
                # Skip comments
                if statement.startswith('--') or not statement.strip():
                    continue

                print(f"\n[{i}/{len(statements)}] Executing:")
                print(f"  {statement[:150]}...")

                conn.execute(text(statement))

            # Commit transaction
            trans.commit()
            print("\n" + "="*70)
            print("✅ MIGRATION 002 COMPLETED SUCCESSFULLY!")
            print("="*70)

            # Verify migration
            print("\n" + "="*70)
            print("VERIFICATION")
            print("="*70)

            # Check users table
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = {row[1]: row[2] for row in result.fetchall()}

            print(f"\n✅ users table - {len(columns)} columns")
            print(f"   - subscription_type: {'✓ ADDED' if 'subscription_type' in columns else '✗ MISSING'}")
            print(f"   - subscription_expires_at: {'✓ ADDED' if 'subscription_expires_at' in columns else '✗ MISSING'}")
            print(f"   - premium_signup_date: {'✓ ADDED' if 'premium_signup_date' in columns else '✗ MISSING'}")

            # Check new tables
            tables_to_check = [
                'llm_usage_logs',
                'graded_assessments',
                'learning_paths',
                'usage_limits',
                'monthly_cost_summary'
            ]

            print(f"\n✅ New tables created:")
            all_tables_exist = True
            for table in tables_to_check:
                result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                exists = result.fetchone() is not None
                status = '✓' if exists else '✗'
                print(f"   {status} {table}")
                if not exists:
                    all_tables_exist = False

            # Check views
            print(f"\n✅ Views created:")
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='view' AND name='user_premium_status'"))
            view_exists = result.fetchone() is not None
            print(f"   {'✓' if view_exists else '✗'} user_premium_status")

            # Count users
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"\n✅ Total users: {user_count}")

            # Count premium users
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE subscription_type='premium'"))
            premium_count = result.scalar()
            print(f"✅ Premium users: {premium_count}")

            print("\n" + "="*70)
            if all_tables_exist:
                print("✅ ALL TABLES CREATED SUCCESSFULLY!")
            else:
                print("⚠️  SOME TABLES MAY BE MISSING - CHECK LOGS ABOVE")
            print("="*70)

        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            print("Rolling back changes...")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            conn.close()


if __name__ == "__main__":
    run_migration()
