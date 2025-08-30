# schema.py
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel


class ImageCreate(BaseModel):
    uploaded_by: str
    filename: str
    content_type: str


class ImageUpdate(BaseModel):

    status: Optional[Literal["pending", "published"]] = None
    article_id: Optional[str] = None


class ImageOut(BaseModel):
    id: str
    r2_key: str | None
    public_url: str | None
    uploaded_by: str
    status: str
    article_id: Optional[str] = None
    filename: str
    content_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }