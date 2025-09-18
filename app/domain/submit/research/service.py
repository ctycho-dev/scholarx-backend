# app/domain/submit/research/service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.domain.submit.research.repository import ResearchRepository
from app.domain.submit.research.schema import (
    ResearchSubmitSchema,
    ResearchOut,
    ResearchSteps
)
from app.domain.user.schema import UserOut
from app.enums.enums import ReportState
from app.exceptions import NotFoundError


class ResearchService:
    """Research Service layer for SQLAlchemy."""

    def __init__(
        self,
        db: AsyncSession,
        repo: ResearchRepository,
        user: UserOut
    ):
        self.db = db
        self.repo = repo
        self.user = user

    async def get_all(self) -> List[ResearchOut]:
        """
        Retrieve all research records from the database.
        """
        return await self.repo.get_all(self.db)

    async def get_by_user(self) -> List[ResearchOut]:
        """
        Retrieve research records submitted by the currently authenticated user.
        """
        if not self.user:
            raise ValueError("User context required")
        return await self.repo.get_by_user(self.db, self.user.id)

    async def get_by_state(self, state: ReportState) -> List[ResearchOut]:
        """
        Retrieve research records filtered by a specific report state.
        """
        return await self.repo.get_by_state(self.db, state)

    async def get_by_id(self, research_id: int) -> ResearchOut:
        """
        Retrieve a specific research record by its ID.
        """
        research = await self.repo.get_by_id(self.db, research_id)
        if not research:
            raise NotFoundError("Research not found")
        return research

    async def create(self, data: ResearchSubmitSchema) -> ResearchOut:
        """
        Create a new research record.
        """
        if not self.user:
            raise ValueError("User context required")
        
        # Set user_id and created_by for audit trail
        data.user_id = self.user.id
        
        research = await self.repo.create(self.db, data)
        if not research:
            raise ValueError('Research creation error.')
        
        return research

    async def update(
        self,
        research_id: int,
        data: ResearchSubmitSchema
    ) -> ResearchOut:
        """
        Update an existing research record.
        """
        # Check if research exists and user owns it
        existing_research = await self.repo.get_by_id(self.db, research_id)
        if not existing_research:
            raise NotFoundError("Research not found")
        
        if existing_research.user_id != self.user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this research"
            )

        updated = await self.repo.update(self.db, research_id, data)
        return updated

    async def update_state(
        self, 
        research_id: int, 
        state: ReportState
    ) -> ResearchOut:
        """
        Update the state of an existing research record.
        """
        research = await self.repo.update_state(
            self.db,
            research_id,
            state=state,
            updated_by=self.user.id
        )
        if not research:
            raise NotFoundError("Research not found")
        return research
