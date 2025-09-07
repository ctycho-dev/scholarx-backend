from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routers import api_router
from app.core.config import settings
from app.database.connection import db_manager
from app.infrastructure.storage.cloudflare.r2_service import CloudflareR2Service
from app.core.logger import get_logger, cleanup_logger
from app.infrastructure.redis.redis_client import redis_client
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastApi lifecycle."""
    try:
        try:
            logger.info("Initializing application resources")
            db_manager.init_engine()
        except ConnectionError as conn_err:
            logger.critical("Connection failed: %s", conn_err, exc_info=True)
            raise

        try:
            app.state.r2_service = CloudflareR2Service()  # ← This calls .connect()
            logger.info("R2 service initialized")
        except Exception as e:
            logger.error("Failed to initialize R2: %s", e, exc_info=True)
            app.state.r2_service = None

        logger.info("App started")
        yield

    finally:
        await db_manager.close()
        await redis_client.close()
        await redis_client.connection_pool.disconnect()
        if app.state.r2_service is not None:
            app.state.r2_service.disconnect()

        cleanup_logger()


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
# app.add_exception_handler(
#     RateLimitExceeded,
#     rate_limit_exceeded_handler
# )

origins = [
    "https://www.athenax.co",
    "http://localhost:5173",
    "https://athenax-git-dev-ilnurs-projects-de603604.vercel.app",
    "https://node23.ru",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

# Include API routers
app.include_router(api_router, prefix=settings.api_version)

logger.info('Start application')


@app.get("/health")
@limiter.limit("5/minute")
async def health_check(request: Request):
    return {"status": "healthy"}
