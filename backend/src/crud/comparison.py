"""
CRUD operations for Comparison model.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.comparison import Comparison
from src.models.comparison_prompt_version import ComparisonPromptVersion
from src.schemas.comparison import ComparisonCreate


class ComparisonCRUD:
    """CRUD operations for Comparison model."""

    def get(self, db: Session, comparison_id: str) -> Optional[Comparison]:
        """Get a comparison by ID."""
        return db.query(Comparison).filter(Comparison.id == comparison_id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        type: Optional[str] = None
    ) -> tuple[List[Comparison], int]:
        """Get multiple comparisons with filtering and pagination."""
        query = db.query(Comparison)

        # Apply type filter
        if type:
            query = query.filter(Comparison.type == type)

        # Get total count
        total = query.count()

        # Apply pagination
        comparisons = query.order_by(Comparison.created_at.desc()).offset(skip).limit(limit).all()

        return comparisons, total

    def create(self, db: Session, *, obj_in: ComparisonCreate) -> Comparison:
        """Create a new comparison."""
        db_obj = Comparison(
            name=obj_in.name,
            description=obj_in.description,
            type=obj_in.type,
            input_text=obj_in.input_text,
            llm_config_id=obj_in.llm_config_id,
            save_snapshot=obj_in.save_snapshot
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, comparison_id: str) -> bool:
        """Delete a comparison."""
        obj = db.query(Comparison).filter(Comparison.id == comparison_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def add_prompt_version(
        self,
        db: Session,
        *,
        comparison_id: str,
        prompt_version_id: str
    ) -> ComparisonPromptVersion:
        """Add a prompt version to a comparison."""
        db_obj = ComparisonPromptVersion(
            comparison_id=comparison_id,
            prompt_version_id=prompt_version_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def export_comparison(self, db: Session, *, comparison_id: str) -> Optional[Dict[str, Any]]:
        """Export a comparison with all results."""
        comparison = self.get(db, comparison_id)
        if not comparison:
            return None
        
        # Get all prompt versions and their results
        results = (
            db.query(ComparisonPromptVersion)
            .filter(ComparisonPromptVersion.comparison_id == comparison_id)
            .all()
        )
        
        return {
            "id": comparison.id,
            "name": comparison.name,
            "description": comparison.description,
            "type": comparison.type,
            "input_text": comparison.input_text,
            "results": [
                {
                    "prompt_version_id": result.prompt_version_id,
                    "result": result.result,
                    "execution_time_ms": result.execution_time_ms,
                    "tokens_used": result.tokens_used,
                    "error_message": result.error_message
                }
                for result in results
            ],
            "successful_executions": comparison.successful_executions,
            "total_executions": comparison.total_executions,
            "average_execution_time_ms": comparison.average_execution_time_ms,
            "total_tokens_used": comparison.total_tokens_used,
            "created_at": comparison.created_at,
            "updated_at": comparison.updated_at
        }


# Create a singleton instance
comparison_crud = ComparisonCRUD()
