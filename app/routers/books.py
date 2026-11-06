from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.book_service import BookServiceABC
from app.schemas.schemas import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import get_book_service
from app.core.exceptions import DataConflictError, ResourceNotFoundError

# Removed the prefix here since it is now handled centrally in app/main.py
router = APIRouter(tags=["Books"])

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, service: BookServiceABC = Depends(get_book_service)):
    try:
        return service.create(book_in)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DataConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

@router.get("", response_model=List[BookResponse])
def get_all_books(service: BookServiceABC = Depends(get_book_service)):
    return service.get_all()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, service: BookServiceABC = Depends(get_book_service)):
    book = service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_in: BookUpdate, service: BookServiceABC = Depends(get_book_service)):
    book = service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    try:
        updated = service.update(book_id, book_in)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return updated
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DataConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, service: BookServiceABC = Depends(get_book_service)):
    book = service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    service.delete(book_id)
