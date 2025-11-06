"""
CRUD operations for LLM Config.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.llm_config import LLMConfig
from src.schemas.llm_config import LLMConfigCreate, LLMConfigUpdate


class LLMConfigCRUD:
    """CRUD operations for LLM Config model."""
    
    def get(self, db: Session, *, config_id: str) -> Optional[LLMConfig]:
        """Get LLM config by ID."""
        return db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        provider: Optional[str] = None,
        active: Optional[bool] = None
    ) -> Tuple[List[LLMConfig], int]:
        """Get multiple LLM configs with filtering."""
        query = db.query(LLMConfig)
        
        # Apply filters
        if provider:
            query = query.filter(LLMConfig.provider == provider)
        if active is not None:
            query = query.filter(LLMConfig.is_active == active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        configs = query.offset(skip).limit(limit).all()
        
        return configs, total
    
    def get_active_configs(self, db: Session) -> List[LLMConfig]:
        """Get all active LLM configs."""
        return db.query(LLMConfig).filter(LLMConfig.is_active == True).all()
    
    def get_by_provider(
        self,
        db: Session,
        *,
        provider: str
    ) -> List[LLMConfig]:
        """Get LLM configs by provider."""
        return db.query(LLMConfig).filter(LLMConfig.provider == provider).all()
    
    def create(self, db: Session, *, obj_in: LLMConfigCreate) -> LLMConfig:
        """Create a new LLM config."""
        db_obj = LLMConfig(
            name=f"{obj_in.provider}-{obj_in.model}",
            provider=obj_in.provider,
            api_key=obj_in.api_key,
            model=obj_in.model,
            temperature=str(obj_in.temperature),
            max_tokens=obj_in.max_tokens,
            is_active=obj_in.active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: LLMConfig,
        obj_in: LLMConfigUpdate
    ) -> LLMConfig:
        """Update an LLM config."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Map schema fields to model fields
        for field, value in update_data.items():
            if field == 'active':
                db_obj.is_active = value
            elif field == 'temperature':
                db_obj.temperature = str(value)
            else:
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, config_id: str) -> bool:
        """Delete an LLM config."""
        obj = self.get(db=db, config_id=config_id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def activate(self, db: Session, *, config_id: str) -> Optional[LLMConfig]:
        """Activate an LLM config."""
        obj = self.get(db=db, config_id=config_id)
        if obj:
            obj.is_active = True
            db.commit()
            db.refresh(obj)
            return obj
        return None
    
    def deactivate(self, db: Session, *, config_id: str) -> Optional[LLMConfig]:
        """Deactivate an LLM config."""
        obj = self.get(db=db, config_id=config_id)
        if obj:
            obj.is_active = False
            db.commit()
            db.refresh(obj)
            return obj
        return None


# Create a singleton instance
llm_config_crud = LLMConfigCRUD()
