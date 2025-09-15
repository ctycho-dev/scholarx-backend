from fastapi import (
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.repository import UserRepository
from app.domain.profile.repository import ProfileRepository
from app.domain.user.schema import (
    UserCreate,
    UserOut,
    UserUpdate
)
from app.enums.enums import UserRole
from app.utils.serialize import serialize


class UserService:
    """User Service layer."""

    def __init__(
        self,
        db: AsyncSession,
        repo: UserRepository,
        profile_repo: ProfileRepository
    ):
        self.db = db
        self.repo = repo
        self.profile_repo = profile_repo

    async def get_user_by_privy_id(self, privy_id: str) -> UserOut:
        """
        Get user
        """
        user = await self.repo.get_by_privy_id(self.db, privy_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user_dict = serialize(user.model_dump())
        return UserOut(**user_dict)

    async def create_user(
        self,
        data: UserCreate,
        # current_user_id: int,
    ) -> UserOut:
        """Create user."""
        # Set email if not set but found in linked accounts
        if not getattr(data, "email", None):
            email_from_linked = None
            for account in data.linked_accounts:
                # Prefer a non-null email in the linked_account (OAuth or otherwise)
                if getattr(account, "email", None):
                    email_from_linked = account.email
                    break
                # Fallback: for "email" provider, check 'address'
                if account.type == "email" and getattr(account, "address", None):
                    email_from_linked = account.address
                    break
            if email_from_linked:
                data.email = email_from_linked
        
        # Business logic for role
        has_bd_account = any(
            account.type == "google_oauth"
            and account.email
            and account.email.endswith('@athenax.co')
            for account in data.linked_accounts
        )

        # Set role to BD if criteria met and current role is USER
        if has_bd_account and data.role == UserRole.USER:
            data.role = UserRole.BD

        new_user = await self.repo.create(
            self.db, data,
        )
        if not new_user:
            raise ValueError('User creation error.')
        return new_user
    
    async def update(
        self,
        current_user_id: int,
        data: UserUpdate
    ) -> UserOut:
        """
        Delete a message by its ID.
        """
        updated = await self.repo.update(
            self.db,
            current_user_id,
            data,
            current_user_id=current_user_id
        )
        return updated

    async def has_profile(self, user_id: int) -> bool:

        profile = await self.profile_repo.user_has_profile(self.db, user_id)

        return profile if profile is not None else False
