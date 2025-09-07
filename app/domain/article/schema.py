from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer, Field
from pydantic.alias_generators import to_camel, to_pascal
from app.enums.enums import ArticleState


class ArticleCreate(BaseModel):
    """
    Schema for creating a new article.
    """
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., max_length=100)
    html_content: str = Field(default="", max_length=50000)
    cover_image: Optional[str] = None
    type: Literal["audit", "research"]
    state: ArticleState = ArticleState.DRAFT
    related_audit_ids: List[str] = []
    related_research_ids: List[str] = []

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_pascal
    )


class ArticleUpdate(BaseModel):
    """
    Schema for updating an existing article (all fields optional).
    Only provided fields will be updated.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, max_length=100)
    html_content: Optional[str] = Field(None, max_length=50000)
    cover_image: Optional[str] = None
    type: Optional[Literal["audit", "research"]] = None
    state: Optional[ArticleState] = None
    related_audit_ids: Optional[List[str]] = None
    related_research_ids: Optional[List[str]] = None

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated Title",
                    "cover_image": "https://cdn.example.com/image.jpg",
                    "html_content": "<p>Partially updated content...</p>"
                }
            ]
        }
    }


class ArticleOut(BaseModel):
    id: str
    title: str
    slug: str
    html_content: str
    cover_image: Optional[str] = None
    type: Literal["audit", "research"]
    state: ArticleState
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime) -> str:
        return updated_at.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
