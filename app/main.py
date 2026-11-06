from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from app.core.config import Settings, StorageBackend, get_db_engine_and_factory
from app.models.models import Base

from app.repositories.member_repo import MemberRepository
from app.repositories.book_repo import BookRepository
from app.services.member_service import InMemoryMemberService, DatabaseMemberService
from app.services.book_service import InMemoryBookService, DatabaseBookService

from app.routers import books, members

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings

    if settings.STORAGE_BACKEND == StorageBackend.DATABASE:
        # Dynamically generate engine and session factory at application startup
        engine, session_factory = get_db_engine_and_factory(settings.DATABASE_URL)
        app.state.db_engine = engine
        app.state.session_factory = session_factory
        
        # Verify table layout states exist on target backend
        Base.metadata.create_all(bind=engine)
        
        member_repo = MemberRepository()
        book_repo = BookRepository()
        
        app.state.member_service = DatabaseMemberService(session_factory, member_repo)
        app.state.book_service = DatabaseBookService(
            session_factory, book_repo, member_repo
        )
    else:
        in_memory_member = InMemoryMemberService()
        app.state.member_service = in_memory_member
        in_memory_book = InMemoryBookService(in_memory_member)
        in_memory_member.book_service = in_memory_book
        app.state.book_service = in_memory_book
        
    yield
    
    if settings.STORAGE_BACKEND == StorageBackend.DATABASE:
        app.state.db_engine.dispose()

app = FastAPI(
    title="Library Management System API",
    version="2.0.0",
    lifespan=lifespan
)


app.include_router(
    members.router,
    prefix="/members",
    tags=["Members"]
)

app.include_router(
    books.router,
    prefix="/books",
    tags=["Books"]
)

@app.get("/health", tags=["System"])
async def health_check(request: Request):
    return {
        "status": "healthy",
        "backend": request.app.state.settings.STORAGE_BACKEND,
    }
