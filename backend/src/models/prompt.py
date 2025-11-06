"""
Prompt model for storing prompt templates.
"""

from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Prompt(BaseModel):
    """Prompt model for storing prompt templates."""
    
    __tablename__ = "prompts"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(Text, nullable=True)  # JSON string of tags
    
    # Relationships
    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prompt(id={self.id}, title={self.title})>"
    
    @property
    def tag_list(self):
        """Get tags as list."""
        if self.tags:
            import json
            try:
                return json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @tag_list.setter
    def tag_list(self, value):
        """Set tags from list."""
        if value:
            import json
            self.tags = json.dumps(value)
        else:
            self.tags = None
