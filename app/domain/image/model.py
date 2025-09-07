# app/domain/image/model.py
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base
from app.common.audit_mixin import TimestampMixin, UserAuditMixin
from app.enums.enums import ImageType, ImageStatus


class Image(Base, TimestampMixin, UserAuditMixin):
    """
    Tracks images uploaded by users.
    Used for cleanup of orphaned files in R2.
    """
    
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    r2_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    public_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[ImageType] = mapped_column(String(50), nullable=False)
    status: Mapped[ImageStatus] = mapped_column(
        String(50),
        default=ImageStatus.CREATED,
        nullable=False
    )
    # Filename and MIME type (for debugging)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    article_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    def __repr__(self) -> str:
        return f"<Image(id={self.id}, filename='{self.filename}', status='{self.status}')>"
