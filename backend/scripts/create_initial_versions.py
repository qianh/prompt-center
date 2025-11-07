"""
Script to create initial version 1.0 for all prompts that don't have any versions yet.

This is needed for prompts created before the auto-version feature was added.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import SessionLocal
from src.models.prompt import Prompt
from src.models.prompt_version import PromptVersion
from src.crud import prompt_crud, prompt_version_crud
from src.schemas.prompt_version import PromptVersionCreate


def create_initial_versions():
    """Create version 1.0 for all prompts that don't have any versions."""
    db = SessionLocal()

    try:
        # Get all prompts
        prompts = db.query(Prompt).all()
        print(f"Found {len(prompts)} prompts")

        created_count = 0
        skipped_count = 0

        for prompt in prompts:
            # Check if prompt has any versions
            existing_versions = prompt_version_crud.get_versions(db, prompt.id)

            if existing_versions:
                print(f"  ✓ Prompt '{prompt.title}' already has {len(existing_versions)} version(s)")
                skipped_count += 1
                continue

            # Create initial version 1.0
            print(f"  + Creating version 1.0 for prompt '{prompt.title}'")
            initial_version = PromptVersionCreate(
                content=prompt.content,
                change_notes="Initial version (auto-created)",
                version_number="1.0"
            )

            try:
                prompt_version_crud.create(db=db, obj_in=initial_version, prompt_id=prompt.id)
                created_count += 1
                print(f"    ✓ Created version 1.0")
            except Exception as e:
                print(f"    ✗ Failed to create version: {e}")

        print(f"\nSummary:")
        print(f"  Created: {created_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Total: {len(prompts)}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating initial versions for prompts without versions...\n")
    create_initial_versions()
    print("\nDone!")
