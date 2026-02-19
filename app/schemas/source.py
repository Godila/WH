from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class SourceBase(BaseModel):
    """Base schema for Source."""
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    """Schema for creating a Source."""
    pass


class SourceUpdate(BaseModel):
    """Schema for updating a Source."""
    name: Optional[str] = None
    description: Optional[str] = None


class SourceResponse(SourceBase):
    """Schema for Source response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
