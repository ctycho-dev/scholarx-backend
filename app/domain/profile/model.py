# app/domain/profile/model.py
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import List, TYPE_CHECKING
from app.database.connection import Base
from app.common.audit_mixin import FullAuditMixin
from app.domain.user.model import User


class Profile(Base, FullAuditMixin):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Core fields
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_image: Mapped[str | None] = mapped_column(String, nullable=True)
    display_role: Mapped[str | None] = mapped_column(String, nullable=True)
    account_type: Mapped[str] = mapped_column(String, nullable=False)

    # Socials
    github: Mapped[str | None] = mapped_column(String, nullable=True)
    twitter: Mapped[str | None] = mapped_column(String, nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String, nullable=True)
    instagram: Mapped[str | None] = mapped_column(String, nullable=True)
    discord: Mapped[str | None] = mapped_column(String, nullable=True)
    google_scholar: Mapped[str | None] = mapped_column(String, nullable=True)
    orcid: Mapped[str | None] = mapped_column(String, nullable=True)
    researchgate: Mapped[str | None] = mapped_column(String, nullable=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    cmc_cg: Mapped[str | None] = mapped_column(String, nullable=True)

    # Publisher
    organization_name: Mapped[str | None] = mapped_column(String, nullable=True)
    institution_name: Mapped[str | None] = mapped_column(String, nullable=True)
    verification_status: Mapped[bool] = mapped_column(Boolean, default=False)

    # Project
    organization_type: Mapped[str | None] = mapped_column(String, nullable=True)
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    team_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Personal
    current_affiliation: Mapped[str | None] = mapped_column(String, nullable=True)
    interests: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )

    # Relationship back to User
    # user: Mapped["User"] = relationship("User", back_populates="profile")
