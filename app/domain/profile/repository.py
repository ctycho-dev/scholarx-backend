# app/domain/profile/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists

from app.common.base_repository import BaseRepository
from app.domain.profile.model import Profile
from app.domain.profile.schema import ProfileCreate, ProfileOut
from app.exceptions import DatabaseError


class ProfileRepository(BaseRepository[Profile, ProfileOut, ProfileCreate]):
    """
    Postgres repository for Profile using SQLAlchemy (async).
    Extends BaseRepository to inherit CRUD, and adds get_by_user_id.
    """

    def __init__(self):
        super().__init__(Profile, ProfileOut, ProfileCreate)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> ProfileOut | None:
        """
        Fetch the profile for a given user_id.
        """
        try:
            result = await db.execute(
                select(Profile).where(Profile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            if not profile:
                return None
            # Pydantic v2: validate directly from ORM object
            return ProfileOut.model_validate(profile)
        except Exception as e:
            raise DatabaseError(f"Failed to fetch profile for user {user_id}: {str(e)}") from e

    async def user_has_profile(
        self, db: AsyncSession, user_id: int
    ) -> bool | None:
        """
        Check if user has a profile using EXISTS query.
        Returns True if profile exists, False otherwise.
        """
        try:
            query = select(exists().where(Profile.user_id == user_id))
            result = await db.execute(query)
            return result.scalar()
        except Exception as e:
            raise DatabaseError(f"Failed to check if user has profile: {str(e)}") from e