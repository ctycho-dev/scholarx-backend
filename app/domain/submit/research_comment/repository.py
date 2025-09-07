# app/domain/submit/research_comments/repository.py
from app.common.base_repository import BaseRepository
from app.domain.submit.research_comment.model import ResearchComment
from app.domain.submit.research_comment.schema import CommentCreate, CommentOut


class ResearchCommentRepository(BaseRepository[ResearchComment, CommentOut, CommentCreate]):
    """
    PostgreSQL repository for ResearchComment using SQLAlchemy (async).
    Extends BaseRepository to inherit CRUD operations.
    """

    def __init__(self):
        super().__init__(ResearchComment, CommentOut, CommentCreate)
