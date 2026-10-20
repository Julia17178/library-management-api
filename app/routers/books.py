from fastapi import APIRouter, Depends, status
from typing import List

from app.core.dependencies import get_book_service
from app.schemas.schemas import BookCreate, BookResponse
from app.services.book_service import BookServiceABC

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def list_books(service: BookServiceABC = Depends(get_book_service)):
    """Fetch all cataloged books from storage."""
    return service.get_all_books()

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, service: BookServiceABC = Depends(get_book_service)):
    """Fetch a single book by its sequential ID."""
    return service.get_book_by_id(book_id)

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, service: BookServiceABC = Depends(get_book_service)):
    """Add a new book to the library system catalog."""
    return service.create_book(book_data)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceABC = Depends(get_book_service)):
    """Remove a book from the library system catalog."""
    service.delete_book(book_id)
    return None
