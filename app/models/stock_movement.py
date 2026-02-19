import enum
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.source import Source
    from app.models.distribution_center import DistributionCenter
    from app.models.user import User


class OperationType(str, enum.Enum):
    """Enum for stock movement operation types."""
    RECEIPT = "receipt"              # Приёмка годного товара
    RECEIPT_DEFECT = "receipt_defect"  # Приёмка брака
    SHIPMENT_RC = "shipment_rc"       # Отгрузка в РЦ
    RETURN_PICKUP = "return_pickup"   # Возврат годного с ПВЗ
    RETURN_DEFECT = "return_defect"   # Возврат брака
    SELF_PURCHASE = "self_purchase"   # Самовыкуп
    WRITE_OFF = "write_off"           # Списание в брак
    RESTORATION = "restoration"       # Восстановление из брака
    UTILIZATION = "utilization"       # Утилизация брака


class StockMovement(Base, UUIDMixin, TimestampMixin):
    """StockMovement model for recording all stock operations."""
    
    __tablename__ = "stock_movements"
    
    # Operation details
    operation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(
        nullable=False
    )
    
    # Foreign keys
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    source_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True
    )
    distribution_center_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("distribution_centers.id", ondelete="SET NULL"),
        nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Optional notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="movements",
        lazy="selectin"
    )
    source: Mapped[Optional["Source"]] = relationship(
        "Source",
        back_populates="movements",
        lazy="selectin"
    )
    distribution_center: Mapped[Optional["DistributionCenter"]] = relationship(
        "DistributionCenter",
        back_populates="movements",
        lazy="selectin"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="movements",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<StockMovement {self.operation_type} {self.quantity}x product={self.product_id}>"
