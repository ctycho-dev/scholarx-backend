from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer, Field
from pydantic.alias_generators import to_camel, to_pascal
from app.enums.enums import ArticleState


class CamelModel(BaseModel):
    """Base model that converts snake_case to camelCase for JSON output"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,     # ✅ NEW: Accept snake_case field names
        validate_by_alias=True,    # ✅ NEW: Accept camelCase aliases  
        from_attributes=True,
    )


class ArticleCreate(CamelModel):
    """
    Schema for creating a new article.
    """
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(max_length=100, default='')
    html_content: str = Field(default="", max_length=50000)
    type: Literal["audit", "research"] = 'research'
    state: ArticleState = ArticleState.DRAFT


class ArticleUpdate(CamelModel):
    """Schema for updating articles."""
    title: Optional[str] = None
    html_content: Optional[str] = None
    slug: str | None = None
    cover_image: str | None = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    
    model_config = ConfigDict(from_attributes=True)


class ArticleOut(CamelModel):
    id: int
    title: str
    slug: str
    summary: str | None
    html_content: str
    cover_image: str | None
    state: ArticleState
    author_profile_id: int | None
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime) -> str:
        return updated_at.isoformat()
