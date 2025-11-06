"""
Base model classes for SQLAlchemy.
"""

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid

from src.core.database import Base


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key."""
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model for all entities."""
    
    __abstract__ = True
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
