from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.book_service import BookServiceABC
from app.services.member_service import MemberServiceABC
from app.schemas.schemas import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import get_book_service, get_member_service

# Removed the prefix here since it is now handled centrally in app/main.py
router = APIRouter(tags=["Books"])

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, service: BookServiceABC = Depends(get_book_service), member_service: MemberServiceABC = Depends(get_member_service)):
    if not member_service.get_by_id(book_in.member_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Referenced Member does not exist")
    try:
        return service.create(book_in)
    except Exception as e:
        if "conflict" in str(e).lower() or "isbn" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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
def update_book(book_id: int, book_in: BookUpdate, service: BookServiceABC = Depends(get_book_service), member_service: MemberServiceABC = Depends(get_member_service)):
    book = service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    # FIXED: Only check if member exists if member_id is actually provided in the partial update
    if book_in.member_id is not None:
        if not member_service.get_by_id(book_in.member_id):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Referenced Member does not exist")
            
    try:
        return service.update(book_id, book_in)
    except Exception as e:
        if "conflict" in str(e).lower() or "isbn" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, service: BookServiceABC = Depends(get_book_service)):
    book = service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    service.delete(book_id)
