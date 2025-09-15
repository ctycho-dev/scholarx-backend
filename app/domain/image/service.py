# image_service.py
import os
import re
from datetime import datetime
import mimetypes
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status
from typing import List
from datetime import datetime

from app.domain.image.schema import ImageOut, ImageCreate
from app.domain.image.repository import ImageRepository
from app.infrastructure.storage.cloudflare.r2_service import CloudflareR2Service
from app.domain.user.schema import UserOut
from app.enums.enums import ImageType
from app.core.config import settings


class ImageService:
    def __init__(
        self,
        db: AsyncSession,
        repo: ImageRepository,
        r2_service: CloudflareR2Service,
        user: UserOut
    ):
        self.db = db
        self.repo = repo
        self.r2_service = r2_service
        self.user = user

    async def upload_file(
        self,
        file: UploadFile,
        image_type: ImageType,
        bucket: str = "scholarx-article"
    ) -> ImageOut:
        """
        Upload file directly via server.
        Used for form submissions, admin uploads, etc.
        """
        original_name = file.filename or "file.unknown"
        original_ct = file.content_type or mimetypes.guess_type(original_name)[0]

        new_doc = await self.repo.create(
            self.db,
            ImageCreate(
                type=image_type,
                filename=file.filename or "upload",
                content_type=file.content_type or "application/octet-stream"
            ),
            current_user_id=self.user.id
        )

        key = self._generate_storage_key(new_doc.id, image_type, original_name)
        public_url = self.r2_service.make_public_url(bucket, key)

        # Upload to R2
        try:
            await file.seek(0)  # Ensure we're at start
            self.r2_service.upload_fileobj(
                file.file,
                bucket=bucket,
                key=key,
                content_type=original_ct
            )
        except Exception as e:
            await self.repo.delete_by_id(self.db, new_doc.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload to R2 failed: {str(e)}"
            ) from e

        updated_doc = await self.repo.update(
            self.db,
            new_doc.id,
            {
                'r2_key': key,
                'public_url': public_url,
                'status': 'stored'
            },
            current_user_id=self.user.id
        )

        return updated_doc
    
    async def get_user_images(self) -> List[ImageOut]:
        """Get all images for the current user."""
        return await self.repo.get_by_user(self.db, self.user.id)

    async def get_user_pending_images(self) -> List[ImageOut]:
        """Get pending images for the current user."""
        return await self.repo.get_pending_by_user(self.db, self.user.id)

    async def delete(self, image_id: int):
        image = await self.repo.get_by_id(self.db, image_id)
        # if not image or image.uploaded_by != self.user.privy_id:
        if not image:
            raise ValueError("Image not found or access denied")
        if image.status == "published":
            raise ValueError("Cannot delete published image")

        if image.r2_key:
            await self.r2_service.delete_file(
                bucket=self._extract_bucket_from_key(image.r2_key),
                key=image.r2_key,
            )
        await self.repo.delete_by_id(self.db, image_id)

    def _extract_bucket_from_key(self, key: str) -> str:
        parts = key.split("/")
        if not parts or not parts[0]:
            raise ValueError(f"Invalid key: '{key}' — could not extract bucket")
        return parts[0]

    def _generate_storage_key(self, doc_id: int, image_type: ImageType, filename: str) -> str:
        """
        Generate optimized S3/R2 key with best practices.
        Structure: {user_id}/{image_type}/{doc_id}-{timestamp}-{safe_filename}
        """
        # Create timestamp for uniqueness and ordering
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        
        # Sanitize filename - keep only safe characters
        safe_filename = self._sanitize_filename(filename)
        
        # Build hierarchical key for better performance and organization
        key = f"{doc_id}-{timestamp}-{safe_filename}"
        
        return key

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to be S3-safe and avoid issues.
        """
        if not filename:
            return "unknown"
        
        # Extract extension
        name, ext = os.path.splitext(filename)
        
        # Remove unsafe characters, keep only alphanumeric, hyphens, underscores, dots
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '-', name)
        
        # Remove multiple consecutive hyphens/dots
        safe_name = re.sub(r'[-\.]+', '-', safe_name)
        
        # Trim and ensure reasonable length
        safe_name = safe_name.strip('-.')[:50]  # Max 50 chars
        
        # Ensure we have something
        if not safe_name:
            safe_name = "file"
        
        return f"{safe_name}{ext.lower()}"