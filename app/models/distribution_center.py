from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


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
    
    def __repr__(self) -> str:
        return f"<DistributionCenter {self.code}: {self.name}>"
