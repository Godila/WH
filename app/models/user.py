from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.stock_movement import StockMovement


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Relationships
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="user",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
