from sqlalchemy import Boolean, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.stock import Stock
    from app.models.defect_stock import DefectStock
    from app.models.stock_movement import StockMovement


class Product(Base, UUIDMixin, TimestampMixin):
    """Product model for inventory management."""
    
    __tablename__ = "products"
    
    # Core identifiers
    barcode: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    gtin: Mapped[str] = mapped_column(
        String(14),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Product details
    seller_sku: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    size: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    brand: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    color: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Relationships
    stock: Mapped["Stock"] = relationship(
        "Stock",
        back_populates="product",
        uselist=False,
        lazy="selectin"
    )
    defect_stock: Mapped["DefectStock"] = relationship(
        "DefectStock",
        back_populates="product",
        uselist=False,
        lazy="selectin"
    )
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Product {self.barcode}>"
