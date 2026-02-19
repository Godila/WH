from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Stock(Base, UUIDMixin, TimestampMixin):
    """Stock model for good quality inventory."""
    
    __tablename__ = "stocks"
    
    # Foreign key to product (one-to-one)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    
    # Quantity of good items
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Relationship back to product
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="stock"
    )
    
    def __repr__(self) -> str:
        return f"<Stock product_id={self.product_id} quantity={self.quantity}>"
