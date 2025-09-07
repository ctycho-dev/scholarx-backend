# app/domain/wishlist/model.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base
from app.common.audit_mixin import TimestampMixin


class Wishlist(Base, TimestampMixin):
    """Wishlist model for storing user email wishlist entries."""
    
    __tablename__ = "wishlist"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Wishlist(id={self.id}, email='{self.email}')>"
