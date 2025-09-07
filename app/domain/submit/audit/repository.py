# app/domain/submit/audit/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists, update
from typing import Optional, List

from app.common.base_repository import BaseRepository
from app.domain.submit.audit.model import AuditSubmit
from app.domain.submit.audit.schema import (
    AuditSubmitSchema,
    AuditSteps,
    AuditOut
)
from app.enums.enums import ReportState
from app.exceptions import DatabaseError, NotFoundError


class AuditRepository(BaseRepository[AuditSubmit, AuditOut, AuditSubmitSchema]):
    """
    PostgreSQL repository for AuditSubmit using SQLAlchemy (async).
    Extends BaseRepository to inherit CRUD, and adds audit-specific methods.
    """

    def __init__(self):
        super().__init__(AuditSubmit, AuditOut, AuditSubmitSchema)

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[AuditOut]:
        """
        Retrieve all audit submissions associated with a given user_id.
        """
        try:
            result = await db.execute(
                select(AuditSubmit).where(AuditSubmit.user_id == user_id)
            )
            audit_list = result.scalars().all()
            
            return [
                AuditOut(
                    id=audit.id,
                    state=audit.state,
                    steps=AuditSteps.model_validate(audit.steps),
                    user_id=audit.user_id,
                    created_at=audit.created_at,
                    updated_at=audit.updated_at
                )
                for audit in audit_list
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch audits for user {user_id}: {str(e)}") from e

    async def get_by_state(
        self,
        db: AsyncSession,
        state: ReportState,
    ) -> List[AuditOut]:
        """
        Retrieve audit submissions filtered by report state, ordered by newest first.
        """
        try:
            result = await db.execute(
                select(AuditSubmit)
                .where(AuditSubmit.state == state)
                .order_by(AuditSubmit.created_at.desc())
            )
            audit_list = result.scalars().all()
            
            return [
                AuditOut(
                    id=audit.id,
                    state=audit.state,
                    steps=AuditSteps.model_validate(audit.steps),
                    user_id=audit.user_id,
                    created_at=audit.created_at,
                    updated_at=audit.updated_at
                )
                for audit in audit_list
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch audits by state {state}: {str(e)}") from e

    async def update_state(
        self,
        db: AsyncSession,
        audit_id: int,
        state: ReportState,
        updated_by: Optional[int] = None
    ) -> AuditOut:
        """
        Update the state of an audit submission by its ID.
        Uses the audit mixin fields for tracking changes.
        """
        try:
            # Check if audit exists
            exists_query = select(exists().where(AuditSubmit.id == audit_id))
            exists_result = await db.execute(exists_query)
            if not exists_result.scalar():
                raise NotFoundError(f"Audit with ID {audit_id} not found")

            # Update the state and audit fields
            update_data = {"state": state}
            if updated_by:
                update_data["updated_by"] = updated_by

            await db.execute(
                update(AuditSubmit)
                .where(AuditSubmit.id == audit_id)
                .values(**update_data)
            )
            await db.commit()

            # Fetch and return the updated audit
            result = await db.execute(
                select(AuditSubmit).where(AuditSubmit.id == audit_id)
            )
            audit = result.scalar_one()
            
            return AuditOut(
                id=audit.id,
                state=audit.state,
                steps=AuditSteps.model_validate(audit.steps),
                user_id=audit.user_id,
                created_at=audit.created_at,
                updated_at=audit.updated_at
            )
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            raise DatabaseError(f"Failed to update audit state: {str(e)}") from e
