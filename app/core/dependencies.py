from fastapi import Request
from app.core.config import Settings
from app.services.book_service import BookServiceABC
from app.services.member_service import MemberServiceABC

def get_settings(request: Request) -> Settings:
    """Injects the active application settings loaded at startup."""
    return request.app.state.settings

def get_member_service(request: Request) -> MemberServiceABC:
    """
    Injects the active Member service implementation configured at app startup.
    Routers use this to avoid caring if data lives in memory or PostgreSQL.
    """
    return request.app.state.member_service

def get_book_service(request: Request) -> BookServiceABC:
    """
    Injects the active Book service implementation configured at app startup.
    Routers use this to avoid caring if data lives in memory or PostgreSQL.
    """
    return request.app.state.book_service
