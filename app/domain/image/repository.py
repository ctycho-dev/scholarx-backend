# repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from datetime import datetime, timedelta
from app.common.base_repository import BaseRepository
from app.domain.image.model import Image
from app.domain.image.schema import ImageOut, ImageCreate
from typing import List
from app.exceptions import DatabaseError


class ImageRepository(BaseRepository[Image, ImageOut, ImageCreate]):
    def __init__(self):
        super().__init__(Image, ImageOut, ImageCreate)

    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[ImageOut]:
        """Get all images uploaded by a specific user."""
        try:
            stmt = select(self.model).where(self.model.uploaded_by == user_id)
            result = await db.execute(stmt)
            instances = result.scalars().all()
            return [ImageOut.model_validate(instance) for instance in instances]
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve images by user: {str(e)}") from e

    async def get_pending_by_user(
        self, db: AsyncSession, user_id: int
    ) -> List[ImageOut]:
        """Get all pending images uploaded by a specific user."""
        try:
            stmt = select(self.model).where(
                and_(
                    self.model.uploaded_by == user_id,
                    self.model.status == "pending",
                )
            )
            result = await db.execute(stmt)
            instances = result.scalars().all()
            return [ImageOut.model_validate(instance, from_attributes=True) for instance in instances]
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve pending images by user: {str(e)}") from e

    async def get_pending_older_than(self, db: AsyncSession, hours: int = 24) -> List[ImageOut]:
        """Get all pending images older than specified hours."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            stmt = select(self.model).where(
                and_(
                    self.model.status == "pending",
                    self.model.created_at < cutoff
                )
            )
            result = await db.execute(stmt)
            instances = result.scalars().all()
            return [ImageOut.model_validate(instance, from_attributes=True) for instance in instances]
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve old pending images: {str(e)}") from e

    async def get_by_status(self, db: AsyncSession, status: str) -> List[ImageOut]:
        """Get all images by status."""
        try:
            stmt = select(self.model).where(
                and_(
                    self.model.status == status,
                    self.model.deleted_at.is_(None)
                )
            )
            result = await db.execute(stmt)
            instances = result.scalars().all()
            return [ImageOut.model_validate(instance, from_attributes=True) for instance in instances]
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve images by status: {str(e)}")
