from sqlalchemy import JSON, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum
from app.common.audit_mixin import TimestampMixin, UserAuditMixin
from app.enums.enums import ReportState
from app.database.connection import Base


class ResearchSubmit(Base, TimestampMixin, UserAuditMixin):
    __tablename__ = "research_submits"
    
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
    state: Mapped[ReportState] = mapped_column(
        Enum(ReportState), default=ReportState.SUBMITTED, nullable=False
    )
    
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)
