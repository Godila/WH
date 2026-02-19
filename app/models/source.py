from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.stock_movement import StockMovement


class Source(Base, UUIDMixin, TimestampMixin):
    """Source model for suppliers and pickup points (ПВЗ, поставщики)."""
    
    __tablename__ = "sources"
    
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="source",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Source {self.name}>"
