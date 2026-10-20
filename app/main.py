from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings, SessionLocal, engine, StorageBackend
from app.core.exceptions import LibraryException, ResourceNotFoundError, DataConflictError, BusinessRuleError
from app.models.models import Base

# Import repositories and services to build them at startup
from app.repositories.member_repo import MemberRepository
from app.repositories.book_repo import BookRepository
from app.services.member_service import InMemoryMemberService, DatabaseMemberService
from app.services.book_service import InMemoryBookService, DatabaseBookService

# Import routers
from app.routers import books, members

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP EVENT ---
    if settings.STORAGE_BACKEND == StorageBackend.DATABASE:
        # Create database tables automatically if they don't exist yet
        Base.metadata.create_all(bind=engine)
        
        member_repo = MemberRepository()
        book_repo = BookRepository()
        
        app.state.member_service = DatabaseMemberService(SessionLocal, member_repo)
        app.state.book_service = DatabaseBookService(SessionLocal, book_repo)
    else:
        # Instantiate clean memory-isolated services
        in_memory_member = InMemoryMemberService()
        app.state.member_service = in_memory_member
        app.state.book_service = InMemoryBookService(in_memory_member)
        
    yield
    # --- SHUTDOWN EVENT ---
    pass

app = FastAPI(
    title="Library Management System API",
    version="2.0.0",
    lifespan=lifespan
)

# --- GLOBAL EXCEPTION HANDLERS ---
# Converts custom domain exceptions to proper HTTP Status Codes for routers automatically!
@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(DataConflictError)
async def data_conflict_handler(request: Request, exc: DataConflictError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

# Include the API routers
app.include_router(members.router)
app.include_router(books.router)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "backend": settings.STORAGE_BACKEND}
