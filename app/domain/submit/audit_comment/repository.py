# app/domain/submit/audit_comments/repository.py
from app.common.base_repository import BaseRepository
from app.domain.submit.audit_comment.model import AuditComment
from app.domain.submit.research_comment.schema import CommentCreate, CommentOut


class AuditCommentRepository(BaseRepository[AuditComment, CommentOut, CommentCreate]):
    """
    PostgreSQL repository for AuditComment using SQLAlchemy (async).
    Extends BaseRepository to inherit CRUD operations.
    """

    def __init__(self):
        super().__init__(AuditComment, CommentOut, CommentCreate)
