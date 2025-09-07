# app/common/user_relationships.py
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import declarative_mixin, declared_attr, relationship
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from app.domain.user.model import User


@declarative_mixin
class UserRelationshipsMixin:
    """Add user relationship properties for easy access."""
    
    @declared_attr
    def created_by(cls) -> Mapped[Optional["User"]]:
        return relationship("User", foreign_keys=[cls.created_by_id], lazy="select")
    
    @declared_attr  
    def updated_by(cls) -> Mapped[Optional["User"]]:
        return relationship("User", foreign_keys=[cls.updated_by_id], lazy="select")
