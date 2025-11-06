"""
Comparison model for storing prompt comparison results.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Comparison(BaseModel):
    """Comparison model for storing prompt comparison results."""
    
    __tablename__ = "comparisons"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # version_comparison, llm_comparison
    input_text = Column(Text, nullable=False)
    llm_config_id = Column(String, ForeignKey("llm_configs.id"), nullable=True)
    save_snapshot = Column(Boolean, default=False, nullable=False)
    
    # Results storage
    results = Column(JSON, nullable=True)  # Store comparison results
    successful_executions = Column(Integer, default=0, nullable=False)
    total_executions = Column(Integer, default=0, nullable=False)
    average_execution_time_ms = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    
    # Relationships
    llm_config = relationship("LLMConfig")
    prompt_versions = relationship("ComparisonPromptVersion", back_populates="comparison", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Comparison(id={self.id}, name={self.name}, type={self.type})>"
