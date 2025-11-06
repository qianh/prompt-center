"""
Prompt version model for storing different versions of prompt content.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class PromptVersion(BaseModel):
    """Prompt version model for storing different versions of prompt content."""
    
    __tablename__ = "prompt_versions"
    
    prompt_id = Column(String, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    change_notes = Column(Text, nullable=True)
    
    # Relationships
    prompt = relationship("Prompt", back_populates="versions")
    
    # Comparison relationships
    comparison_executions = relationship("ComparisonPromptVersion", back_populates="prompt_version")
    
    __table_args__ = (
        UniqueConstraint('prompt_id', 'version_number', name='unique_prompt_version'),
    )
    
    def __repr__(self):
        return f"<PromptVersion(id={self.id}, prompt_id={self.prompt_id}, version={self.version_number})>"
    
    @property
    def content_preview(self) -> str:
        """Get a preview of the content (first 100 characters)."""
        if self.content:
            return self.content[:100] + "..." if len(self.content) > 100 else self.content
        return ""
