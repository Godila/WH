from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.stock_movement import StockMovement


class DistributionCenter(Base, UUIDMixin, TimestampMixin):
    """Distribution Center model for marketplace fulfillment centers (РЦ маркетплейсов)."""
    
    __tablename__ = "distribution_centers"
    
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    marketplace: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Relationships
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="distribution_center",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<DistributionCenter {self.code}: {self.name}>"
