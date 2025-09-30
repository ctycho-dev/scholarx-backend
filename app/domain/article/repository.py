# app/domain/article/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc

from app.common.base_repository import BaseRepository
from app.domain.article.model import Article
from app.domain.article.schema import ArticleOut, ArticleCreate
from app.enums.enums import ArticleState
from app.exceptions import DatabaseError


class ArticleRepository(BaseRepository[Article, ArticleOut, ArticleCreate]):
    def __init__(self):
        super().__init__(Article, ArticleOut, ArticleCreate)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> list[ArticleOut]:
        """Get all articles by user ID using SQLAlchemy."""
        try:
            query = select(self.model).where(
                self.model.author_profile_id == user_id
            ).order_by(desc(self.model.created_at))
            
            result = await db.execute(query)
            articles = result.scalars().all()
            return [ArticleOut.model_validate(article) for article in articles]
        except Exception as e:
            raise DatabaseError(f"Failed to get articles for user {user_id}: {str(e)}") from e
    
    async def get_by_state(
        self, 
        db: AsyncSession, 
        state: ArticleState
    ) -> list[ArticleOut]:
        """Get all articles by state."""
        try:
            query = select(self.model).where(
                self.model.state == state
            ).order_by(desc(self.model.created_at))
            
            result = await db.execute(query)
            articles = result.scalars().all()
            return [ArticleOut.model_validate(article) for article in articles]
        except Exception as e:
            raise DatabaseError(f"Failed to get articles by state {state}: {str(e)}") from e

    async def get_published(self, db: AsyncSession) -> list[ArticleOut]:
        """Get all published articles."""
        return await self.get_by_state(db, ArticleState.PUBLISHED)

    async def get_by_user_and_state(
        self,
        db: AsyncSession,
        profile_id: int,
        state: ArticleState
    ) -> list[ArticleOut]:
        """Get articles by user and state."""
        try:
            query_conditions = [
                self.model.author_profile_id == profile_id,
                self.model.state == state
            ]
            
            query = select(self.model).where(
                and_(*query_conditions)
            ).order_by(desc(self.model.updated_at))
            
            result = await db.execute(query)
            articles = result.scalars().all()
            return [ArticleOut.model_validate(article) for article in articles]
        except Exception as e:
            raise DatabaseError(f"Failed to get articles for profile {profile_id} with state {state}: {str(e)}") from e

    async def search_by_title(
        self, 
        db: AsyncSession, 
        search_term: str
    ) -> list[ArticleOut]:
        """Search articles by title."""
        try:
            query_conditions = [self.model.title.ilike(f"%{search_term}%")]
            
            if hasattr(self.model, 'deleted_at'):
                query_conditions.append(self.model.deleted_at.is_(None))
            
            query = select(self.model).where(
                and_(*query_conditions)
            ).order_by(desc(self.model.created_at))
            
            result = await db.execute(query)
            articles = result.scalars().all()
            return [ArticleOut.model_validate(article) for article in articles]
        except Exception as e:
            raise DatabaseError(f"Failed to search articles: {str(e)}") from e
