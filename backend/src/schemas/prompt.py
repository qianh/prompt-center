"""
Pydantic schemas for Prompt API.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class PromptBase(BaseModel):
    """Base prompt schema."""
    title: str
    description: Optional[str] = None
    content: str
    tags: Optional[List[str]] = []


class PromptCreate(PromptBase):
    """Schema for creating a prompt."""
    pass


class PromptUpdate(BaseModel):
    """Schema for updating a prompt."""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class PromptResponse(PromptBase):
    """Schema for prompt response."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    """Schema for paginated prompt list response."""
    items: List[PromptResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
