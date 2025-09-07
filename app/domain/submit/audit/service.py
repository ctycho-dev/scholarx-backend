# app/domain/submit/audit/service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.domain.submit.audit.repository import AuditRepository
from app.domain.submit.audit.schema import (
    AuditSubmitSchema,
    AuditOut
)
from app.domain.user.schema import UserOut
from app.enums.enums import ReportState
from app.exceptions import NotFoundError


class AuditService:
    """
    Service layer for handling business logic related to audit operations.
    """

    def __init__(
        self,
        db: AsyncSession,
        repo: AuditRepository,
        user: UserOut
    ):
        self.db = db
        self.repo = repo
        self.user = user

    async def get_all(self) -> List[AuditOut]:
        """
        Retrieve all audit records from the database.
        """
        return await self.repo.get_all(self.db)

    async def get_by_user(self) -> List[AuditOut]:
        """
        Retrieve audit records submitted by the currently authenticated user.
        """
        if not self.user:
            raise ValueError("User context required")
        return await self.repo.get_by_user(self.db, self.user.id)

    async def get_by_state(self, state: ReportState) -> List[AuditOut]:
        """
        Retrieve audits filtered by a specific report state.
        """
        return await self.repo.get_by_state(self.db, state)

    async def get_by_id(self, audit_id: int) -> AuditOut:
        """
        Retrieve a single audit by its unique ID.
        """
        audit = await self.repo.get_by_id(self.db, audit_id)
        if not audit:
            raise NotFoundError(f"Audit with ID {audit_id} not found")
        return audit

    async def create(self, data: AuditSubmitSchema) -> AuditOut:
        """
        Create a new audit entry for the current user.
        """
        if not self.user:
            raise ValueError("User context required")
        
        # Set user_id and created_by for audit trail
        data.user_id = self.user.id
        
        audit = await self.repo.create(self.db, data)
        if not audit:
            raise ValueError('Audit creation error.')
        
        return audit

    async def update(
        self, 
        audit_id: int, 
        data: AuditSubmitSchema
    ) -> AuditOut:
        """
        Update an existing audit if the current user is the owner.
        """
        # Check if audit exists and user owns it
        existing_audit = await self.repo.get_by_id(self.db, audit_id)
        if not existing_audit:
            raise NotFoundError("Audit not found")
        
        if existing_audit.user_id != self.user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this audit"
            )

        # Set state to CHECKING when updated by user
        data.state = ReportState.CHECKING
        
        updated = await self.repo.update(self.db, audit_id, data)
        return updated

    async def update_state(
        self, 
        audit_id: int, 
        state: ReportState
    ) -> AuditOut:
        """
        Update the state of an existing audit.
        """
        audit = await self.repo.update_state(
            self.db,
            audit_id,
            state=state,
            updated_by=self.user.id
        )
        if not audit:
            raise NotFoundError("Audit not found")
        return audit
