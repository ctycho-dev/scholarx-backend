# schema.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from app.enums.enums import ImageType, ImageStatus


class ImageCreate(BaseModel):
    type: ImageType
    filename: str
    content_type: str


class ImageUpdate(BaseModel):

    status: ImageStatus | None = None
    article_id: Optional[str] = None


class ImageOut(BaseModel):
    id: int
    r2_key: str | None
    public_url: str | None
    status: str
    type: str
    article_id: Optional[str] = None
    filename: str
    content_type: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        """
        Serialize datetime fields to ISO 8601 string format.
        Applied to both `created_at` and `updated_at`.
        """
        return value.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
