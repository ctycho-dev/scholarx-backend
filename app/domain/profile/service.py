from fastapi import (
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.repository import UserRepository
from app.domain.profile.repository import ProfileRepository
from app.domain.profile.schema import (
    ProfileCreate,
    ProfileUpdate,
    ProfileOut
)
from app.infrastructure.storage.cloudflare.r2_service import CloudflareR2Service
from app.domain.user.schema import (
    LinkedAccount,
    AuthProvider
)
from app.domain.user.schema import UserOut


class ProfileService:
    """User Service layer."""

    def __init__(
        self,
        db: AsyncSession,
        repo: ProfileRepository,
        r2_service: CloudflareR2Service,
        user: UserOut
    ):
        self.db = db
        self.repo = repo
        self.r2_service = r2_service
        self.user = user

    async def get_by_user_id(self, user_id: int) -> ProfileOut | None:
        """
        Get user
        """
        profile = await self.repo.get_by_user_id(self.db, user_id)
        return profile

    async def create_profile(
        self,
        data: ProfileCreate,
        # current_user: UserOut
    ) -> ProfileOut:
        """Create user."""

        existing_profile = await self.repo.get_by_user_id(self.db, self.user.id)
        if existing_profile:
            await self.repo.delete_by_id(self.db, existing_profile.id)

        data.user_id = self.user.id

        if self.user.linked_accounts:
            data = self._populate_socials_from_linked_accounts(
                data,
                self.user.linked_accounts
            )

        profile = await self.repo.create(self.db, data)
        if not profile:
            raise ValueError('Profile creation error.')

        return profile

    async def update(
        self,
        profile_id: int,
        data: ProfileUpdate
    ) -> ProfileOut:
        """
        Delete a message by its ID.
        """
        # Get current profile
        profile = await self.repo.get_by_id(self.db, profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail='Profile with provided id not found.')
        
        # Store old image URL for cleanup
        old_image_url = profile.profile_image
        
        # Update the profile
        updated = await self.repo.update(self.db, profile_id, data)
        if (
            old_image_url and
            data.profile_image and
            old_image_url != data.profile_image
        ):
            key = self.r2_service.extract_key_if_url(old_image_url)
            self.r2_service.delete_file(
                'scholarx-profile', key
            )
        return updated

    async def get_profile_by_user(
        self,
    ) -> ProfileOut | None:
        """Create user."""
        
        profile = await self.repo.get_by_user_id(self.db, self.user.id)
        return profile

    def _populate_socials_from_linked_accounts(
        self, 
        profile_data: ProfileCreate, 
        linked_accounts: list[LinkedAccount]
    ) -> ProfileCreate:
        """Extract social information from linked accounts and populate profile data."""
        
        for account in linked_accounts:
            if account.type == AuthProvider.GITHUB and account.username:
                profile_data.github = account.username
            elif account.type == AuthProvider.TWITTER and account.username:
                profile_data.twitter = account.username
            elif account.type == AuthProvider.DISCORD and account.username:
                profile_data.discord = account.username
        
        return profile_data

