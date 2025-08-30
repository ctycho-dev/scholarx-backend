# image_service.py
import mimetypes
from fastapi import UploadFile
from urllib.parse import quote
from typing import List, Optional
from datetime import datetime

from app.domain.image.schema import ImageOut, ImageCreate
from app.domain.image.repository import ImageRepository
from app.infrastructure.storage.cloudflare.r2_service import CloudflareR2Service
from app.domain.user.schema import UserOut
from app.core.config import settings


class ImageService:
    def __init__(
        self,
        repo: ImageRepository,
        r2_service: CloudflareR2Service,
        user: UserOut
    ):
        self.repo = repo
        self.r2_service = r2_service
        self.user = user

    async def upload_file(
        self,
        file: UploadFile,
        bucket: str = "scholarx-article"
    ) -> ImageOut:
        """
        Upload file directly via server.
        Used for form submissions, admin uploads, etc.
        """
        original_name = file.filename or "file.unknown"
        original_ct = file.content_type or mimetypes.guess_type(original_name)[0]

        new_doc = await self.repo.create(ImageCreate(
            uploaded_by=self.user.id,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream"
        ))

        key = f"{new_doc.id}-{original_name.replace(' ', '-')}"
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
            raise Exception(f"Upload to R2 failed: {str(e)}")

        updated_doc = await self.repo.update(new_doc.id, {
            'r2_key': key,
            'public_url': public_url,
            'status': 'stored'
        })

        return updated_doc

    async def delete(self, image_id: str):
        image = await self.repo.get_by_id(image_id)
        if not image or image.uploaded_by != self.user.privy_id:
            raise ValueError("Image not found or access denied")
        if image.status == "published":
            raise ValueError("Cannot delete published image")

        await self.r2_service.delete_file(
            bucket=self._extract_bucket_from_key(image.r2_key),
            key=image.r2_key,
        )
        await self.repo.delete_by_id(image_id)

    def _extract_bucket_from_key(self, key: str) -> str:
        parts = key.split("/")
        if not parts or not parts[0]:
            raise ValueError(f"Invalid key: '{key}' — could not extract bucket")
        return parts[0]