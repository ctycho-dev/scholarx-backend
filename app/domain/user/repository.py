# app/domain/user/repository.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import DatabaseError
from app.common.base_repository import BaseRepository
from app.domain.user.model import User
from app.domain.user.schema import UserOut, UserCreate


class UserRepository(BaseRepository[User, UserOut, UserCreate]):
    def __init__(self):
        super().__init__(User, UserOut, UserCreate)

    async def get_by_privy_id(
        self, db: AsyncSession, privy_id: str
    ) -> UserOut | None:
        try:
            result = await db.execute(select(User).where(User.privy_id == privy_id))
            user = result.scalar_one_or_none()
            if not user:
                return None
            return UserOut.model_validate(user)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve user by privy_id: {str(e)}") from e