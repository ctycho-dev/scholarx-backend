# app/core/dependencies.py
import os
import certifi
import urllib
import jwt
from jwt import PyJWKClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.exceptions import NotFoundError
from app.core.config import settings
from app.core.logger import get_logger
from app.domain.user.model import User
from app.domain.user.schema import UserOut
from app.domain.user.repository import UserRepository
from app.domain.profile.repository import ProfileRepository
from app.domain.article.repository import ArticleRepository
from app.domain.image.repository import ImageRepository
from app.domain.submit.audit.repository import AuditRepository
from app.domain.submit.research.repository import ResearchRepository
from app.domain.wishlist.repository import WishlistRepository
from app.domain.user.service import UserService
from app.domain.profile.service import ProfileService
from app.domain.article.service import ArticleService
from app.domain.image.service import ImageService
from app.domain.submit.audit.service import AuditService
from app.domain.submit.research.service import ResearchService
from app.domain.wishlist.service import WishlistService
from app.infrastructure.storage.cloudflare.r2_service import CloudflareR2Service
from app.utils.serialize import serialize
from app.database.connection import db_manager

# SSL Cert setup
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

security = HTTPBearer(auto_error=False)

logger = get_logger()

# JWKS client for Privy
jwks_client = PyJWKClient(settings.PRIVY_JWSK_URL, timeout=10, max_cached_keys=5, cache_keys=True)


# -------------------------
# Database Connection
# -------------------------
# Dependency to get DB session
async def get_db():
    """
    FastAPI dependency to get a database session.
    """
    async with db_manager.get_session() as session:
        yield session


# -------------------------
# Repository Factories
# -------------------------
def get_wislist_repo() -> WishlistRepository:
    return WishlistRepository()


def get_user_repo() -> UserRepository:
    return UserRepository()


def get_profile_repo() -> ProfileRepository:
    return ProfileRepository()


def get_article_repo() -> ArticleRepository:
    return ArticleRepository()


def get_image_repo() -> ImageRepository:
    return ImageRepository()


def get_audit_repo() -> AuditRepository:
    return AuditRepository()


def get_research_repo() -> ResearchRepository:
    return ResearchRepository()


def get_wishlist_repo() -> WishlistRepository:
    return WishlistRepository()


# -------------------------
# External Service Injection
# -------------------------
def get_r2_service(request: Request) -> CloudflareR2Service:
    return request.app.state.r2_service


# -------------------------
# User Authentication
# -------------------------
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserOut:
    """
    Returns authenticated User from Privy JWT.
    In dev mode, returns a mock dev user if no token provided.
    """
    # Dev mode: return mock user if no auth
    if settings.mode == "dev" and not creds:
        mock_user = await user_repo.get_by_id(db, settings.DEV_USER_ID)
        if mock_user:
            logger.info("Using dev mode mock user: %s", mock_user.privy_id)
            request.state.user = mock_user.privy_id
            return mock_user
        else:
            logger.warning("Dev user not found in DB. Create one with id=%s", settings.DEV_USER_ID)

    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(creds.credentials)
        decoded = jwt.decode(
            creds.credentials,
            signing_key.key,
            issuer="privy.io",
            audience=settings.PRIVY_APP_ID,
            algorithms=["ES256"],
            leeway=10
        )
        user_id = decoded['sub']
        request.state.user = user_id

        user = await user_repo.get_by_privy_id(db, user_id)  # Pass db session
        if not user:
            raise NotFoundError('User not found')

        return user
    except urllib.error.URLError as e:
        logger.error("Network error accessing JWKS URL: %s", e)
        raise HTTPException(status_code=502, detail="Authentication service unavailable") from e
    except jwt.PyJWKClientError as e:
        logger.error("JWKS client error: %s", e)
        raise HTTPException(status_code=502, detail="Failed to retrieve signing keys") from e
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWKClientError as e:
        logger.error('Invalid authentication credentials: %s', e)
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") from e
    except NotFoundError as e:
        logger.error('User not found: %s', e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error('Get Current User failed: %s', e)
        raise HTTPException(status_code=500, detail="Token verification failed") from e


async def get_optional_user(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserOut | None:
    try:
        return await get_current_user(request, creds, user_repo)
    except HTTPException as e:
        if e.status_code in {401, 404}:
            return None
        raise
    except Exception:
        return None


# -------------------------
# Service Factories
# -------------------------
def get_wishlist_service(
    db: AsyncSession = Depends(get_db),
    repo: WishlistRepository = Depends(get_wishlist_repo),
) -> WishlistService:
    return WishlistService(db=db, repo=repo)


def get_user_service(
    db: AsyncSession = Depends(get_db),
    repo: UserRepository = Depends(get_user_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo)
) -> UserService:
    return UserService(db=db, repo=repo, profile_repo=profile_repo)


def get_profile_service(
    db: AsyncSession = Depends(get_db),
    repo: ProfileRepository = Depends(get_profile_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    user: UserOut = Depends(get_current_user)
) -> ProfileService:
    return ProfileService(db=db, repo=repo, user_repo=user_repo, user=user)


def get_article_service_with_auth(
    repo: ArticleRepository = Depends(get_article_repo),
    user: User = Depends(get_current_user)
) -> ArticleService:
    return ArticleService(repo=repo, user=user)


def get_article_service_optional(
    repo: ArticleRepository = Depends(get_article_repo),
    user: User | None = Depends(get_optional_user)
) -> ArticleService:
    return ArticleService(repo=repo, user=user)


def get_audit_service(
    db: AsyncSession = Depends(get_db),
    repo: AuditRepository = Depends(get_audit_repo),
    user: User = Depends(get_current_user)
) -> AuditService:
    return AuditService(db=db, repo=repo, user=user)


def get_research_service(
    db: AsyncSession = Depends(get_db),
    repo: ResearchRepository = Depends(get_research_repo),
    user: User = Depends(get_current_user)
) -> ResearchService:
    return ResearchService(db=db, repo=repo, user=user)


def get_image_service(
    db: AsyncSession = Depends(get_db),
    repo: ImageRepository = Depends(get_image_repo),
    r2_service: CloudflareR2Service = Depends(get_r2_service),
    user: UserOut = Depends(get_current_user)
) -> ImageService:
    return ImageService(db=db, repo=repo, r2_service=r2_service, user=user)
