# app/database/connection.py
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Base for models
Base = declarative_base()


class DatabaseManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.async_session: sessionmaker | None = None

    def init_engine(self):
        """
        Initialize the async engine.
        """
        DATABASE_URL = settings.DATABASE_URL
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")

        self.engine = create_async_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL logging
            pool_size=20,
            pool_pre_ping=True,
            connect_args={"server_settings": {"application_name": "scholarx-backend"}}
        )

        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )

    async def create_all_tables(self):
        """
        Create all tables (use only for testing or first run).
        In production, use Alembic migrations instead.
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call init_engine() first.")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self) -> AsyncSession:
        """
        Get a new async session.
        Usage: async with db_manager.get_session() as session:
        """
        if not self.async_session:
            raise RuntimeError("Session not initialized. Call init_engine() first.")
        return self.async_session()

    async def close(self):
        """
        Dispose the engine.
        """
        if self.engine:
            await self.engine.dispose()


db_manager = DatabaseManager()
