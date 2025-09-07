# app/domain/submit/research/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists, update
from typing import Optional, List

from app.common.base_repository import BaseRepository
from app.domain.submit.research.model import ResearchSubmit
from app.domain.submit.research.schema import (
    ResearchSubmitSchema,
    ResearchOut,
    ResearchSteps
)
from app.enums.enums import ReportState
from app.exceptions import DatabaseError, NotFoundError


class ResearchRepository(BaseRepository[ResearchSubmit, ResearchOut, ResearchSubmitSchema]):
    """
    PostgreSQL repository for ResearchSubmit using SQLAlchemy (async).
    Extends BaseRepository to inherit CRUD, and adds research-specific methods.
    """

    def __init__(self):
        super().__init__(ResearchSubmit, ResearchOut, ResearchSubmitSchema)

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[ResearchOut]:
        """
        Fetch research submissions for a given user_id.
        Returns list for API consistency (typically 0 or 1 item due to unique constraint).
        """
        try:
            result = await db.execute(
                select(ResearchSubmit).where(ResearchSubmit.user_id == user_id)
            )
            research_list = result.scalars().all()
            
            return [
                ResearchOut(
                    id=research.id,
                    steps=ResearchSteps.model_validate(research.steps),
                    state=research.state,
                    user_id=research.user_id,
                    created_at=research.created_at,
                    updated_at=research.updated_at
                )
                for research in research_list
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch research for user {user_id}: {str(e)}") from e

    async def get_by_state(
        self,
        db: AsyncSession,
        state: ReportState,
    ) -> List[ResearchOut]:
        """
        Retrieve research submissions filtered by report state, ordered by newest first.
        """
        try:
            result = await db.execute(
                select(ResearchSubmit)
                .where(ResearchSubmit.state == state)
                .order_by(ResearchSubmit.created_at.desc())
            )
            research_list = result.scalars().all()
            
            return [
                ResearchOut(
                    id=research.id,
                    steps=ResearchSteps.model_validate(research.steps),
                    state=research.state,
                    user_id=research.user_id,
                    created_at=research.created_at,
                    updated_at=research.updated_at
                )
                for research in research_list
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch research by state {state}: {str(e)}") from e

    async def update_state(
        self,
        db: AsyncSession,
        research_id: int,
        state: ReportState,
        updated_by: Optional[int] = None
    ) -> ResearchOut:
        """
        Update the state of a research submission by its ID.
        Uses the audit mixin fields for tracking changes.
        """
        try:
            # Check if research exists
            exists_query = select(exists().where(ResearchSubmit.id == research_id))
            exists_result = await db.execute(exists_query)
            if not exists_result.scalar():
                raise NotFoundError(f"Research with ID {research_id} not found")

            # Update the state and audit fields
            update_data = {"state": state}
            if updated_by:
                update_data["updated_by"] = updated_by

            await db.execute(
                update(ResearchSubmit)
                .where(ResearchSubmit.id == research_id)
                .values(**update_data)
            )
            await db.commit()

            # Fetch and return the updated research
            result = await db.execute(
                select(ResearchSubmit).where(ResearchSubmit.id == research_id)
            )
            research = result.scalar_one()
            
            return ResearchOut(
                id=research.id,
                steps=ResearchSteps.model_validate(research.steps),
                state=research.state,
                user_id=research.user_id,
                created_at=research.created_at,
                updated_at=research.updated_at
            )
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            raise DatabaseError(f"Failed to update research state: {str(e)}") from e
