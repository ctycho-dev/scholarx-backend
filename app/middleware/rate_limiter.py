# app/middleware/rate_limiter.py
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status

from app.core.config import settings


# Create a custom key function if needed (e.g., user-based limits)
def rate_limit_key(request: Request):

    user = getattr(request.state, "user", None)
    if user:
        return f"user:{user}"
    return get_remote_address(request)


# Initialize limiter with Redis storage
limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=["200/minute", "20/second"],
    # storage_uri=settings.REDIS_URL,
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):

    if isinstance(exc, RateLimitExceeded):
        detail = getattr(exc, 'detail', "Rate limit exceeded. Please try again later.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # More appropriate for backend issues like Redis
            detail="Service temporarily unavailable due to rate limiting backend error.",
        )
