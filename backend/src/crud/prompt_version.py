"""
CRUD operations for Prompt Version model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.prompt_version import PromptVersion
from src.schemas.prompt_version import PromptVersionCreate, PromptVersionUpdate


class PromptVersionCRUD:
    """CRUD operations for Prompt Version model."""

    def get(self, db: Session, version_id: str) -> Optional[PromptVersion]:
        """Get a prompt version by ID."""
        return db.query(PromptVersion).filter(PromptVersion.id == version_id).first()

    def get_versions(self, db: Session, prompt_id: str) -> List[PromptVersion]:
        """Get all versions for a specific prompt."""
        return (
            db.query(PromptVersion)
            .filter(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
            .all()
        )

    def get_by_prompt(
        self,
        db: Session,
        *,
        prompt_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[PromptVersion]:
        """Get versions for a specific prompt."""
        return (
            db.query(PromptVersion)
            .filter(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_next_version_number(self, db: Session, prompt_id: str) -> str:
        """Get the next version number for a prompt.
        Handles both integer (old DB schema) and string (new DB schema) version numbers.
        """
        versions = (
            db.query(PromptVersion.version_number)
            .filter(PromptVersion.prompt_id == prompt_id)
            .all()
        )

        if not versions:
            return "1.0"

        # Parse all version numbers and find the maximum
        max_num = 0.0
        for (version_value,) in versions:
            try:
                # Handle both integer (old) and string (new) version numbers
                if isinstance(version_value, int):
                    num = float(version_value)
                else:
                    num = float(version_value)

                if num > max_num:
                    max_num = num
            except (ValueError, TypeError):
                # If not a valid number, skip it
                continue

        # Increment by 1.0
        next_version = max_num + 1.0
        # Format: if it's a whole number, return "X.0", otherwise keep decimal
        if next_version.is_integer():
            return f"{int(next_version)}.0"
        else:
            return str(next_version)

    def create(self, db: Session, *, obj_in: PromptVersionCreate, prompt_id: str) -> PromptVersion:
        """Create a new prompt version."""
        # Use provided version number or auto-generate
        version_number = obj_in.version_number if obj_in.version_number is not None else self.get_next_version_number(db, prompt_id)

        # Check if version number already exists
        existing = db.query(PromptVersion).filter(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number == version_number
        ).first()

        if existing:
            raise ValueError(f"Version {version_number} already exists for this prompt")

        db_obj = PromptVersion(
            prompt_id=prompt_id,
            version_number=version_number,
            content=obj_in.content,
            change_notes=obj_in.change_notes
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: PromptVersion,
        obj_in: PromptVersionUpdate
    ) -> PromptVersion:
        """Update a prompt version."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, version_id: str) -> bool:
        """Delete a prompt version."""
        obj = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def compare_versions(
        self,
        db: Session,
        *,
        prompt_id: str,
        version_a: str,
        version_b: str
    ) -> Optional[dict]:
        """Compare two versions of a prompt."""
        version_a_obj = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_a
            )
            .first()
        )
        
        version_b_obj = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_b
            )
            .first()
        )
        
        if not version_a_obj or not version_b_obj:
            return None
        
        # Simple diff implementation
        import difflib
        
        diff = list(difflib.unified_diff(
            version_a_obj.content.splitlines(keepends=True),
            version_b_obj.content.splitlines(keepends=True),
            fromfile=f"version_{version_a}",
            tofile=f"version_{version_b}",
            lineterm=""
        ))
        
        return {
            "version_a": {
                "version_number": version_a_obj.version_number,
                "content": version_a_obj.content
            },
            "version_b": {
                "version_number": version_b_obj.version_number,
                "content": version_b_obj.content
            },
            "diff": "".join(diff)
        }


# Create a singleton instance
prompt_version_crud = PromptVersionCRUD()
