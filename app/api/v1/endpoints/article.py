from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    Query
)
from fastapi.responses import JSONResponse
from app.domain.article.service import ArticleService
from app.domain.article.schema import ArticleCreate, ArticleOut, ArticleUpdate
# from app.middleware.rate_limiter import limiter
from app.core.dependencies import (
    get_article_service_with_auth,
    get_article_service_optional,
    get_user_with_profile
)
from app.enums.enums import AppMode, ArticleState
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger('api.v1.article')
router = APIRouter()


@router.get("/", response_model=List[ArticleOut])
# @limiter.limit("100/minute")
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


@router.get("/search", response_model=List[ArticleOut])
# @limiter.limit("50/minute")
async def search_articles(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    service: ArticleService = Depends(get_article_service_optional),
):
    """
    Search articles by title.
    """
    try:
        return await service.search(q)
    except ValueError as e:
        logger.error('[search_articles] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[search_articles] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[search_articles] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e


@router.get("/user/", response_model=List[ArticleOut])
# @limiter.limit("100/minute")
async def get_articles_by_user(
    request: Request,
    state: ArticleState | None = Query(None, description="Filter by state: draft, published"),
    service: ArticleService = Depends(get_article_service_with_auth),
):
    """
    Get all articles by the authenticated user.
    """
    try:
        if state:
            return await service.get_by_user_and_state(state)
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


@router.get("/{article_id}", response_model=ArticleOut)
# @limiter.limit("100/minute")
async def get_article(
    request: Request,
    article_id: int,
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
# @limiter.limit("10/hour")
async def create_article(
    request: Request,
    data: ArticleCreate,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    try:
        if settings.mode == AppMode.TEST:
            return JSONResponse(status_code=200, content={"success": True})
        article = await service.create(data)
        return article
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
# @limiter.limit("30/hour")
async def update_article(
    request: Request,
    article_id: int,
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


@router.patch("/{article_id}/publish", response_model=ArticleOut)
# @limiter.limit("20/hour")
async def publish_article(
    request: Request,
    article_id: int,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    """
    Publish an article (change state from draft to published).
    """
    try:
        return await service.publish(article_id)
    except ValueError as e:
        logger.error('[publish_article] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[publish_article] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[publish_article] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article"
        ) from e


@router.patch("/{article_id}/unpublish", response_model=ArticleOut)
# @limiter.limit("20/hour")
async def unpublish_article(
    request: Request,
    article_id: int,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    """
    Unpublish an article (change state from published to draft).
    """
    try:
        return await service.unpublish(article_id)
    except ValueError as e:
        logger.error('[unpublish_article] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[unpublish_article] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[unpublish_article] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article"
        ) from e


@router.delete("/{article_id}", status_code=204)
# @limiter.limit("10/hour")
async def delete_article(
    request: Request,
    article_id: int,
    service: ArticleService = Depends(get_article_service_with_auth),
):
    """
    Delete an article. Only the article owner can delete their articles.
    """
    try:
        await service.delete(article_id)
        return None  # 204 No Content
    except ValueError as e:
        logger.error('[delete_article] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[delete_article] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[delete_article] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article"
        ) from e
