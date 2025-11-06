"""
LLM Configuration model for storing LLM provider settings.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer

from src.models.base import BaseModel


class LLMConfig(BaseModel):
    """LLM Configuration model for storing LLM provider settings."""
    
    __tablename__ = "llm_configs"
    
    name = Column(String(255), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # openai, anthropic, google
    api_key = Column(Text, nullable=False)  # Encrypted API key
    model = Column(String(100), nullable=False)
    temperature = Column(String(10), nullable=True)
    max_tokens = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<LLMConfig(id={self.id}, name={self.name}, provider={self.provider})>"
