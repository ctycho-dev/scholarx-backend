# app/domain/article/service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domain.article.schema import (
    ArticleCreate, 
    ArticleUpdate, 
    ArticleOut
)
from app.domain.article.repository import ArticleRepository
from app.domain.user.repository import UserRepository
from app.domain.user.schema import UserOut
from app.enums.enums import ArticleState


class ArticleService:
    """Article Service layer - clean business logic without exception handling."""

    def __init__(
        self,
        db: AsyncSession,
        repo: ArticleRepository,
        user: Optional[UserOut] = None
    ):
        self.db = db
        self.repo = repo
        self.user = user

    async def get_all(self) -> List[ArticleOut]:
        """Get all published articles."""
        return await self.repo.get_published(self.db)

    async def get_by_user(self, user_id: Optional[int] = None) -> List[ArticleOut]:
        """Get articles by user."""
        target_user_id = user_id or (self.user.id if self.user else None)
        
        if not target_user_id:
            raise ValueError("User context required")
        
        return await self.repo.get_by_user_id(self.db, target_user_id)

    async def get_by_user_and_state(self, state: str) -> List[ArticleOut]:
        """Get user's articles by state (e.g., drafts)."""
        if not self.user:
            raise ValueError("User context required")
        
        if state == ArticleState.DRAFT:
            return await self.repo.get_drafts_by_user(self.db, self.user.id)
        else:
            # For other states, get all user articles and filter
            all_user_articles = await self.repo.get_by_user_id(self.db, self.user.id)
            return [article for article in all_user_articles if article.state == state]

    async def get_by_state(self, state: str) -> List[ArticleOut]:
        """Get articles by state."""
        article_state = ArticleState(state.upper())
        return await self.repo.get_by_state(self.db, article_state)

    async def get_by_id(self, article_id: int) -> ArticleOut | None:
        """Get article by ID."""
        return await self.repo.get_by_id(self.db, article_id)

    async def create(self, data: ArticleCreate) -> ArticleOut:
        """Create new article."""
        if not self.user:
            raise ValueError("User context required")
        
        # Set user_id and default state
        article_data = data.model_dump()
        article_data['user_id'] = self.user.id
        article_data['state'] = ArticleState.DRAFT
        
        return await self.repo.create(
            self.db, 
            article_data, 
            current_user_id=self.user.id
        )

    async def update(self, article_id: int, data: ArticleUpdate) -> ArticleOut:
        """Update article."""
        if not self.user:
            raise ValueError("User context required")
        
        # Check ownership
        existing_article = await self.repo.get_by_id(self.db, article_id)
        if not existing_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if hasattr(existing_article, 'user_id') and existing_article.user_id != self.user.id:
            raise ValueError("You can only edit your own articles")
        
        return await self.repo.update(
            self.db,
            article_id,
            data,
            current_user_id=self.user.id
        )

    async def publish(self, article_id: int) -> ArticleOut:
        """Publish an article."""
        update_data = ArticleUpdate(state=ArticleState.PUBLISHED)
        return await self.update(article_id, update_data)

    async def unpublish(self, article_id: int) -> ArticleOut:
        """Unpublish an article."""
        update_data = ArticleUpdate(state=ArticleState.DRAFT)
        return await self.update(article_id, update_data)

    async def delete(self, article_id: int) -> None:
        """Delete article."""
        if not self.user:
            raise ValueError("User context required")
        
        # Check ownership
        existing_article = await self.repo.get_by_id(self.db, article_id)
        if not existing_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if hasattr(existing_article, 'user_id') and existing_article.user_id != self.user.id:
            raise ValueError("You can only delete your own articles")
        
        # Use soft delete if available
        if hasattr(self.repo.model, 'deleted_at'):
            await self.repo.soft_delete(self.db, article_id, self.user.id)
        else:
            await self.repo.delete_by_id(self.db, article_id)

    async def search(self, search_term: str) -> List[ArticleOut]:
        """Search articles by title."""
        return await self.repo.search_by_title(self.db, search_term)
