# tests/domain/image/test_schema.py
from datetime import datetime
from app.domain.image.schema import ImageOut
from app.enums.enums import ImageType, ImageStatus


def test_imageout_serializes_to_camelcase():
    data = {
        "id": "667a123b4c5d6e7f8g9h",
        "r2_key": "articles/cover.jpg",
        "public_url": "https://scholarx-article.mypinx.store/articles/cover.jpg",
        "uploaded_by": "user_abc123",
        "status": ImageStatus.CREATED,
        "type": ImageType.PROFILE,
        "filename": "cover.jpg",
        "content_type": "image/jpeg",
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 1, 12, 1, 0),
    }

    out = ImageOut(**data)
    json_data = out.model_dump(mode="json", by_alias=True)

    # Assert camelCase keys
    assert "uploadedBy" in json_data
    assert "createdAt" in json_data
    assert "updatedAt" in json_data

    # # Assert values
    assert json_data["uploadedBy"] == "user_abc123"
    assert json_data["createdAt"] == "2024-01-01T12:00:00"
    assert json_data["status"] == "created"
