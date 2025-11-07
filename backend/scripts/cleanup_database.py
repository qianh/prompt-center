"""
Clean up orphaned comparison_prompt_version records.

This script removes comparison_prompt_version records that have invalid foreign keys.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from src.core.config import settings


def cleanup_orphaned_records():
    """Remove orphaned comparison_prompt_version records."""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            # Find orphaned records (where referenced prompt_version doesn't exist)
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM comparison_prompt_versions cpv
                LEFT JOIN prompt_versions pv ON cpv.prompt_version_id = pv.id
                WHERE pv.id IS NULL
            """))
            orphaned_count = result.fetchone()[0]

            if orphaned_count > 0:
                print(f"Found {orphaned_count} orphaned comparison_prompt_version records")

                # Delete orphaned records
                conn.execute(text("""
                    DELETE FROM comparison_prompt_versions
                    WHERE id IN (
                        SELECT cpv.id
                        FROM comparison_prompt_versions cpv
                        LEFT JOIN prompt_versions pv ON cpv.prompt_version_id = pv.id
                        WHERE pv.id IS NULL
                    )
                """))

                print(f"Deleted {orphaned_count} orphaned records")
            else:
                print("No orphaned records found")

            # Also check for NULL prompt_version_id (shouldn't exist but let's be safe)
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM comparison_prompt_versions
                WHERE prompt_version_id IS NULL
            """))
            null_count = result.fetchone()[0]

            if null_count > 0:
                print(f"Found {null_count} records with NULL prompt_version_id")
                conn.execute(text("""
                    DELETE FROM comparison_prompt_versions
                    WHERE prompt_version_id IS NULL
                """))
                print(f"Deleted {null_count} records with NULL prompt_version_id")

            # Commit transaction
            trans.commit()
            print("Database cleanup completed successfully!")

        except Exception as e:
            trans.rollback()
            print(f"Error during cleanup: {e}")
            raise


if __name__ == "__main__":
    cleanup_orphaned_records()
