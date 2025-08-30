# model.py
from typing import Literal
from pydantic import Field
from app.common.metadata_document import BaseDocument


class Image(BaseDocument):
    """
    Tracks images uploaded by users.
    Used for cleanup of orphaned files in R2.
    """

    # R2 object key (e.g. 'articles/171234567890-cover.jpg')
    r2_key: str | None = None

    # Public URL (e.g. https://scholarx-article.mypinx.store/articles/171234567890-cover.jpg)
    public_url: str | None = None

    uploaded_by: str = Field(..., description="User ID (from JWT or Privy)")

    # Status: pending (not published) or published (used in article)
    status: Literal['created', "stored", 'published'] = Field(
        default="created",
        description="Whether image is in draft or published article"
    )

    # Optional: link to article if used
    article_id: str | None = None

    # Filename and MIME type (for debugging)
    filename: str
    content_type: str

    class Settings:
        name = "images"
        indexes = ["status", "article_id", "created_at"]

    class Config:
        json_schema_extra = {
            "example": {
                "r2_key": "articles/171234567890-cover.jpg",
                "public_url": "https://scholarx-article.mypinx.store/articles/171234567890-cover.jpg",
                "uploaded_by": "user_abc123",
                "status": "pending",
                "filename": "cover.jpg",
                "content_type": "image/jpeg"
            }
        }
