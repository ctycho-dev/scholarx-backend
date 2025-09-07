from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from fastapi.responses import JSONResponse
from app.domain.article.service import ArticleService
from app.domain.article.schema import ArticleCreate, ArticleOut, ArticleUpdate
from app.middleware.rate_limiter import limiter
from app.core.dependencies import (
    get_article_service_with_auth,
    get_article_service_optional
)
from app.enums.enums import AppMode
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter()


@router.get("/", response_model=List[ArticleOut])
@limiter.limit("100/minute")
async def get_articles(
    request: Request,
    service: ArticleService = Depends(get_article_service_optional),
):
    try:
        return await service.get_all()
    except ValueError as e:
        logger.error('[get_articles] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_articles] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_articles] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e


@router.get("/user/", response_model=List[ArticleOut])
@limiter.limit("100/minute")
async def get_articles_by_user(
    request: Request,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    try:
        return await service.get_by_user()
    except ValueError as e:
        logger.error('[get_articles_by_user] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_articles_by_user] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_articles_by_user] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e
    

@router.get("/user/drafts", response_model=List[ArticleOut])
@limiter.limit("50/minute")
async def get_user_drafts(
    request: Request,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    """
    Get all draft articles for the authenticated user.
    """
    try:
        return await service.get_by_user_and_state("draft")
    except ValueError as e:
        logger.error('[get_user_drafts] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_user_drafts] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_user_drafts] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch drafts"
        ) from e


@router.get("/state/{state}", response_model=List[ArticleOut])
@limiter.limit("100/minute")
async def get_articles_by_state(
    request: Request,
    state: str,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    try:
        return await service.get_by_state(state)
    except ValueError as e:
        logger.error('[get_articles_by_state] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_articles_by_state] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_articles_by_state] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e


@router.get("/{article_id}", response_model=ArticleOut)
@limiter.limit("100/minute")
async def get_article(
    request: Request,
    article_id: str,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    try:
        return await service.get_by_id(article_id)
    except ValueError as e:
        logger.error('[get_article] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_article] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_article] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e


@router.post("/", status_code=200)
@limiter.limit("10/hour")
async def create_article(
    request: Request,
    data: ArticleCreate,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    try:
        if settings.mode == AppMode.TEST:
            return JSONResponse(status_code=200, content={"success": True})
        await service.create(data)
        return JSONResponse(status_code=200, content={"success": True})
    except ValueError as e:
        logger.error('[create_article] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[create_article] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[create_article] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e


@router.put("/{article_id}", response_model=ArticleOut)
@limiter.limit("30/hour")
async def update_article(
    request: Request,
    article_id: str,
    data: ArticleUpdate,  # Use ArticleUpdate schema (all fields optional)
    service: ArticleService = Depends(get_article_service_with_auth),
):
    """
    Update an existing article (supports partial updates).
    """
    try:
        article = await service.update(article_id, data)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except ValueError as e:
        logger.error('[update_article] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[update_article] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[update_article] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article"
        ) from e