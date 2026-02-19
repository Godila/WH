from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class DCBase(BaseModel):
    """Base schema for Distribution Center."""
    code: str
    name: str
    marketplace: str


class DCCreate(DCBase):
    """Schema for creating a Distribution Center."""
    pass


class DCUpdate(BaseModel):
    """Schema for updating a Distribution Center."""
    code: Optional[str] = None
    name: Optional[str] = None
    marketplace: Optional[str] = None


class DCResponse(DCBase):
    """Schema for Distribution Center response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
