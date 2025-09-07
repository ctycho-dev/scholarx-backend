# app/domain/wishlist/repository.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.base_repository import BaseRepository
from app.domain.wishlist.model import Wishlist
from app.domain.wishlist.schema import WishlistCreate, WishlistOut
from app.exceptions import DatabaseError


class WishlistRepository(BaseRepository[Wishlist, WishlistOut, WishlistCreate]):
    """
    SQLAlchemy repository implementation for managing wishlist entries.
    
    This class extends the BaseRepository and provides CRUD operations
    and additional methods specific to wishlist functionality.
    """

    def __init__(self):
        """
        Initializes the WishlistRepository with the Wishlist model and schemas.
        """
        super().__init__(Wishlist, WishlistOut, WishlistCreate)

    async def get_by_email(self, db: AsyncSession, email: str) -> WishlistOut | None:
        """
        Get wishlist entry by email address.
        
        Args:
            db: Database session
            email: Email address to search for
            
        Returns:
            WishlistOut object if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            result = await db.execute(
                select(self.model).where(self.model.email == email)
            )
            instance = result.scalar_one_or_none()
            if not instance:
                return None
            return WishlistOut.model_validate(instance)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve wishlist by email: {str(e)}") from e
