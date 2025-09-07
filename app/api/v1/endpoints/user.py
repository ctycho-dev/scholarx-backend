from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request
)
from app.middleware.rate_limiter import limiter
from app.core.dependencies import (
    get_current_user
)
from app.domain.user.schema import (
    UserCreate,
    UserOut,
    UserUpdate
)
from app.core.logger import get_logger
from app.core.dependencies import get_user_service
from app.domain.user.service import UserService

logger = get_logger()

router = APIRouter()


@router.get("/me/", response_model=UserOut)
@limiter.limit("30/minute")
async def get_user(
    request: Request,
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserOut:
    """
    Get user details for the currently authenticated user.
    """
    try:
        has_profile = await service.has_profile(current_user.id)

        current_user.has_profile = has_profile

        return current_user
    except ValueError as e:
        logger.error('[get_user] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_user] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_user] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user details"
        ) from e


@router.post("/", response_model=UserOut)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    data: UserCreate,
    service: UserService = Depends(get_user_service)
) -> UserOut | None:
    """
    Create a new user after validating authorization.

    Args:
        data: User creation data validated by UserCreate schema
        privy_id: The authenticated user's Privy ID obtained from the dependency
        db_repo: User repository instance for database operations

    Returns:
        UserOut: The newly created user details

    Raises:
        HTTPException: 
            - 403 if authorization fails
            - 409 if user already exists
            - 500 if there's an unexpected database error
    """
    try:
        return await service.create_user(data)
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


@router.patch("/")
@limiter.limit("15/minute")
async def update_user(
    request: Request,
    data: UserUpdate,
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Update profile, bio, or social links for the current user.
    Only provided fields will be updated.

    Args:
        data: Fields to update, validated by UserUpdate schema.

    Returns:
        UserOut: The updated user object.

    Raises:
        HTTPException:
            - 400 for validation errors
            - 404 if user not found
            - 500 for unexpected errors
    """
    try:
        updated_user = await service.update(current_user.id, data)
        has_profile = await service.has_profile(current_user.id)

        updated_user.has_profile = has_profile
        return updated_user
    except ValueError as e:
        logger.error('[update_user] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[update_user] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[update_user] Exception: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user details"
        ) from e
