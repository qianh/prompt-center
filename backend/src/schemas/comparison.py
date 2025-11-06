"""
Pydantic schemas for Comparison API.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ComparisonBase(BaseModel):
    """Base comparison schema."""
    name: str
    description: Optional[str] = None
    type: str
    input_text: str
    llm_config_id: Optional[str] = None
    save_snapshot: bool = False


class ComparisonCreate(ComparisonBase):
    """Schema for creating a comparison."""
    pass


class ComparisonResponse(ComparisonBase):
    """Schema for comparison response."""
    id: str
    results: Optional[List[Dict[str, Any]]] = None
    successful_executions: int
    total_executions: int
    average_execution_time_ms: int
    total_tokens_used: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComparisonListResponse(BaseModel):
    """Schema for paginated comparison list response."""
    items: List[ComparisonResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
