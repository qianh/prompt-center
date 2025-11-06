"""
Comparison-Prompt Version junction model.
"""

from sqlalchemy import Column, String, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class ComparisonPromptVersion(BaseModel):
    """Junction model for comparisons and prompt versions."""
    
    __tablename__ = "comparison_prompt_versions"
    
    comparison_id = Column(String, ForeignKey("comparisons.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_version_id = Column(String, ForeignKey("prompt_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Store the execution result for this specific version
    result = Column(Text, nullable=True)  # LLM response
    execution_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    comparison = relationship("Comparison", back_populates="prompt_versions")
    prompt_version = relationship("PromptVersion", back_populates="comparison_executions")
    
    def __repr__(self):
        return f"<ComparisonPromptVersion(comparison_id={self.comparison_id}, version_id={self.prompt_version_id})>"
