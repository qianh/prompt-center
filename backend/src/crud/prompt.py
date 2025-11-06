"""
CRUD operations for Prompt model.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.models.prompt import Prompt
from src.schemas.prompt import PromptCreate, PromptUpdate


class PromptCRUD:
    """CRUD operations for Prompt model."""

    def get(self, db: Session, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by ID."""
        return db.query(Prompt).filter(Prompt.id == prompt_id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[Prompt], int]:
        """Get multiple prompts with filtering and pagination."""
        query = db.query(Prompt)

        # Apply search filter
        if search:
            search_filter = or_(
                Prompt.title.ilike(f"%{search}%"),
                Prompt.description.ilike(f"%{search}%"),
                Prompt.content.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Apply tags filter
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(Prompt.tags.ilike(f"%{tag}%"))
            if tag_filters:
                query = query.filter(and_(*tag_filters))

        # Get total count
        total = query.count()

        # Apply sorting
        if sort_by == "created_at":
            order_column = Prompt.created_at
        elif sort_by == "updated_at":
            order_column = Prompt.updated_at
        elif sort_by == "title":
            order_column = Prompt.title
        else:
            order_column = Prompt.created_at

        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Apply pagination
        prompts = query.offset(skip).limit(limit).all()

        return prompts, total

    def create(self, db: Session, *, obj_in: PromptCreate) -> Prompt:
        """Create a new prompt."""
        import json
        
        db_obj = Prompt(
            title=obj_in.title,
            description=obj_in.description,
            content=obj_in.content,
            tags=json.dumps(obj_in.tags) if obj_in.tags else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Prompt,
        obj_in: PromptUpdate
    ) -> Prompt:
        """Update a prompt."""
        import json
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "tags" in update_data:
            update_data["tags"] = json.dumps(update_data["tags"]) if update_data["tags"] else None
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, prompt_id: str) -> bool:
        """Delete a prompt."""
        obj = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False


# Create a singleton instance
prompt_crud = PromptCRUD()
