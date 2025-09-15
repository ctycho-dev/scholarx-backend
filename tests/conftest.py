import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock
from app.database.connection import Base
from app.core.dependencies import get_current_user, get_user_service, get_db
from app.api.v1.endpoints.user import router as user_router
from app.domain.user.schema import UserOut
from app.domain.user.service import UserService
from app.domain.user.repository import UserRepository
from app.domain.profile.repository import ProfileRepository

# SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_engine():
    """Create test database engine with SQLite."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def mock_current_user():
    """Mock authenticated user for testing."""
    return UserOut(
        id=1,
        privy_id="test_privy_id",
        email="test@example.com",
        username="testuser",
        has_profile=True
    )

@pytest.fixture
def mock_user_service():
    """Mock UserService for endpoint testing."""
    service = AsyncMock(spec=UserService)
    
    # Configure common return values
    service.has_profile.return_value = True
    service.create_user.return_value = UserOut(
        id=1,
        privy_id="new_privy_id",
        email="new@example.com",
        username="newuser",
        has_profile=True
    )
    service.update.return_value = UserOut(
        id=1,
        privy_id="test_privy_id",
        email="test@example.com",
        username="testuser",
        has_profile=True
    )
    
    return service

@pytest.fixture
def test_app(mock_current_user, mock_user_service):
    """Create FastAPI test application with mocked dependencies."""
    app = FastAPI()
    
    # Include routers
    app.include_router(user_router, prefix="/users", tags=["users"])
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    return app

@pytest.fixture
async def client(test_app):
    """Create async test client."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac
