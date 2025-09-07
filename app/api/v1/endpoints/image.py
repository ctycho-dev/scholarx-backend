from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    UploadFile
)
from fastapi.responses import JSONResponse
from app.domain.image.service import ImageService
from app.domain.image.schema import (
    ImageCreate,
    ImageOut,
    ImageUpdate
)
from app.enums.enums import ImageType
from app.middleware.rate_limiter import limiter
from app.core.dependencies import (
    get_image_service,
)
from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger()
router = APIRouter()


@router.post("/{image_type}/{bucket}", response_model=ImageOut, status_code=201)
@limiter.limit("5/minute")
async def upload_image_file(
    request: Request,
    image_type: ImageType,
    bucket: str,
    file: UploadFile,
    service: ImageService = Depends(get_image_service),
):
    """
    Server-side upload: file is sent directly to backend.
    Useful for admin panels or non-JS clients.
    """
    try:
        image_out = await service.upload_file(file, image_type, bucket)
        return image_out
    except ValueError as e:
        logger.error('[upload_image_file] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        logger.error('[upload_image_file] HTTPException: %s', e)
        raise
    except Exception as e:
        logger.error('[upload_image_file] Exception: %s', e)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}") from e

@router.get("/", response_model=List[ImageOut])
@limiter.limit("100/minute")
async def get_all_images(
    request: Request,
    bucket: str = None,
    status: str = None,
    service: ImageService = Depends(get_image_service),
):
    """
    Get all images uploaded by user.
    Optionally filter by status or bucket/folder.
    """
    try:
        images = await service.get_all(bucket=bucket, status=status)
        return images
    except Exception as e:
        logger.error('[get_all_images] %s', e)
        raise HTTPException(status_code=500, detail="Failed to fetch images") from e


@router.get("/{image_id}", response_model=ImageOut)
@limiter.limit("100/minute")
async def get_image_by_id(
    request: Request,
    image_id: str,
    service: ImageService = Depends(get_image_service),
):
    """
    Get a single image by ID.
    """
    try:
        image = await service.get_by_id(image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return image
    except HTTPException:
        raise
    except Exception as e:
        logger.error('[get_image_by_id] %s', e)
        raise HTTPException(status_code=500, detail="Internal error") from e


@router.delete("/{image_id}", status_code=200)
@limiter.limit("10/hour")
async def delete_image(
    request: Request,
    image_id: str,
    service: ImageService = Depends(get_image_service),
):
    """
    Delete image from R2 and DB.
    Only allowed for pending images (not linked to article).
    """
    try:
        await service.delete(image_id)
        return JSONResponse(status_code=200, content={"success": True})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error('[delete_image] %s', e)
        raise HTTPException(status_code=500, detail="Delete failed") from e