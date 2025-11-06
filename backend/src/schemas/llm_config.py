"""
Pydantic schemas for LLM Config API.
"""

from typing import Optional
from pydantic import BaseModel, Field


class LLMConfigBase(BaseModel):
    """Base LLM Config schema."""
    provider: str = Field(..., description="LLM provider (openai, anthropic, mock)")
    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(..., description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(1000, ge=1, le=8000, description="Maximum tokens to generate")
    active: bool = Field(True, description="Whether this config is active")


class LLMConfigCreate(LLMConfigBase):
    """Schema for creating LLM config."""
    pass


class LLMConfigUpdate(BaseModel):
    """Schema for updating LLM config."""
    provider: Optional[str] = Field(None, description="LLM provider")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    model: Optional[str] = Field(None, description="Model name")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, ge=1, le=8000, description="Maximum tokens to generate")
    active: Optional[bool] = Field(None, description="Whether this config is active")


class LLMConfigResponse(LLMConfigBase):
    """Schema for LLM config response."""
    id: str = Field(..., description="LLM config ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class LLMConfigListResponse(BaseModel):
    """Schema for LLM config list response."""
    items: list[LLMConfigResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
