# app/domain/wishlist/service.py
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.wishlist.repository import WishlistRepository
from app.domain.wishlist.schema import (
    WishlistCreate,
    WishlistOut
)


class WishlistService:
    """Simple service layer for Wishlist with CRUD operations."""

    def __init__(self, db: AsyncSession, repo: WishlistRepository):
        self.db = db
        self.repo = repo

    async def get_by_id(self, wishlist_id: int) -> Optional[WishlistOut]:
        """Get wishlist entry by ID."""
        return await self.repo.get_by_id(self.db, wishlist_id)

    async def get_by_email(self, email: str) -> Optional[WishlistOut]:
        """Get wishlist entry by email."""
        return await self.repo.get_by_email(self.db, email)

    async def get_all(self) -> list[WishlistOut]:
        """Get all wishlist entries with pagination."""
        return await self.repo.get_all(self.db)

    async def create_wishlist(
        self,
        data: WishlistCreate,
    ) -> None:
        """Create a new wishlist entry."""
        existing = await self.repo.get_by_email(self.db, data.email)
        if existing:
            return None
        
        await self.repo.create(self.db, data)

    async def delete_wishlist(self, wishlist_id: int) -> None:
        """Delete a wishlist entry (hard delete)."""
        existing = await self.repo.get_by_id(self.db, wishlist_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist entry not found"
            )
        
        await self.repo.delete_by_id(self.db, wishlist_id)
