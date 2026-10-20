from fastapi import Request
from app.services.book_service import BookServiceABC
from app.services.member_service import MemberServiceABC

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
