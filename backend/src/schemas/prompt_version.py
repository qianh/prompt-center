"""
Pydantic schemas for Prompt Version API.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PromptVersionBase(BaseModel):
    """Base prompt version schema."""
    content: str
    change_notes: Optional[str] = None


class PromptVersionCreate(PromptVersionBase):
    """Schema for creating a prompt version."""
    pass


class PromptVersionUpdate(BaseModel):
    """Schema for updating a prompt version."""
    content: Optional[str] = None
    change_notes: Optional[str] = None


class PromptVersionResponse(PromptVersionBase):
    """Schema for prompt version response."""
    id: str
    prompt_id: str
    version_number: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
