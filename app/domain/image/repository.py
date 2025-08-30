# repository.py
from datetime import datetime, timedelta
from app.common.base_repository import BaseRepository
from app.domain.image.model import Image
from app.domain.image.schema import ImageOut, ImageCreate
from beanie import PydanticObjectId
from typing import List


class ImageRepository(BaseRepository[Image, ImageOut, ImageCreate]):
    def __init__(self):
        super().__init__(Image, ImageOut, ImageCreate)

    async def get_by_user(self, user_id: str) -> List[ImageOut]:
        data = await self.collection.find({"uploaded_by": user_id}).to_list()
        return [ImageOut(**self._serialize(x.model_dump())) for x in data]

    async def get_pending_by_user(self, user_id: str) -> List[ImageOut]:
        data = await self.collection.find(
            {"uploaded_by": user_id, "status": "pending"}
        ).to_list()
        return [ImageOut(**self._serialize(x.model_dump())) for x in data]

    async def get_pending_older_than(self, hours: int = 24) -> List[ImageOut]:

        cutoff = datetime.now() - timedelta(hours=hours)
        data = await self.collection.find(
            {"status": "pending", "created_at": {"$lt": cutoff}}
        ).to_list()
        return [ImageOut(**self._serialize(x.model_dump())) for x in data]
