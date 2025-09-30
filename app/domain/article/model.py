# app/domain/article/model.py
from typing import List, Literal, Optional, TYPE_CHECKING
from pydantic import Field
from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.audit_mixin import FullAuditMixin
from app.enums.enums import ArticleState
from app.database.connection import Base


if TYPE_CHECKING:
    from app.domain.profile.model import Profile


class Article(Base, FullAuditMixin):
    """Article model with draft/publish lifecycle."""
    
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    html_content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    cover_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[ArticleState] = mapped_column(
        String(20), default=ArticleState.DRAFT, nullable=False, index=True
    )

    author_profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    author_profile: Mapped["Profile"] = relationship("Profile")

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title}', state='{self.state}')>"
