from fastapi import (
    APIRouter, Depends, HTTPException,
    Response, Request, status
)
from app.middleware.rate_limiter import limiter
from app.domain.wishlist.service import WishlistService
from app.core.dependencies import get_wishlist_service
from app.domain.wishlist.schema import WishlistCreate
from app.core.config import settings
from app.enums.enums import AppMode
from app.core.logger import get_logger


logger = get_logger()
router = APIRouter()


@router.get("/")
@limiter.limit("100/minute")
async def get_wishlish(
    request: Request,
    repo: WishlistService = Depends(get_wishlist_service)
):
    try:
        data = await repo.get_all()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/")
@limiter.limit("5/minute")
async def create_wishlish(
    request: Request,
    data: WishlistCreate,
    repo: WishlistService = Depends(get_wishlist_service)
):

    if not data.email or "@" not in data.email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    try:
        if settings.mode == AppMode.TEST:
            return Response(status_code=status.HTTP_200_OK)
        await repo.create_wishlist(data)
        return Response(status_code=200)
    except ValueError as e:
        logger.error('[create_user] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[create_user] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[create_user] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user details"
        ) from e
