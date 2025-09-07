# app/domain/user/model.py
from sqlalchemy import String, Boolean, Integer, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Dict, Any, Optional

from app.database.connection import Base
from app.domain.user.schema import LinkedAccount
from app.common.audit_mixin import FullAuditMixin
from app.enums.enums import UserRole


class User(Base, FullAuditMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    privy_id: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(
        String, unique=True, index=True, nullable=True
    )

    last_login_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime, nullable=True
    )
    login_count: Mapped[int] = mapped_column(Integer, default=0)

    linked_accounts: Mapped[LinkedAccount] = mapped_column(
        ARRAY(JSON), default=list, nullable=False
    )
    wallets: Mapped[List[Dict[str, Any]]] = mapped_column(
        ARRAY(JSON), default=list, nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    has_accepted_terms: Mapped[bool] = mapped_column(Boolean, default=False)
    is_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    account_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
