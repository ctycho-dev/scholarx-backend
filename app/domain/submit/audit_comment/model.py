from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum
from app.common.audit_mixin import TimestampMixin, UserAuditMixin
from app.enums.enums import UserRole
from app.database.connection import Base


class AuditComment(Base, TimestampMixin, UserAuditMixin):
    __tablename__ = "audit_comments"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    audit_submit_id: Mapped[int] = mapped_column(
        ForeignKey("audit_submits.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
