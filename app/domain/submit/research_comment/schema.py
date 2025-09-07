# app/domain/submit/research_comments/schema.py
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from app.enums.enums import UserRole


class CommentCreate(BaseModel):
    """Schema for creating a new research comment."""
    
    research_submit_id: int
    content: str = Field(..., max_length=500, min_length=1)
    role: UserRole = UserRole.USER


class CommentOut(BaseModel):
    """Schema for research comment output."""
    
    id: int
    research_submit_id: int
    role: UserRole
    content: str
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        """Convert `created_at` to ISO 8601 string during serialization."""
        return created_at.isoformat()
    
    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime) -> str:
        """Convert `updated_at` to ISO 8601 string during serialization."""
        return updated_at.isoformat()

    model_config = ConfigDict(from_attributes=True)
