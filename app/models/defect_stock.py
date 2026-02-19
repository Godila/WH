from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class DefectStock(Base, UUIDMixin, TimestampMixin):
    """DefectStock model for defective/damaged inventory."""
    
    __tablename__ = "defect_stocks"
    
    # Foreign key to product (one-to-one)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    
    # Quantity of defective items
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Relationship back to product
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="defect_stock"
    )
    
    def __repr__(self) -> str:
        return f"<DefectStock product_id={self.product_id} quantity={self.quantity}>"
