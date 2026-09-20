from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import db_books, db_members, book_id_counter
from app.models.book import BookCreate, BookUpdate, BookResponse

router = APIRouter(prefix="/books", tags=["Books Management"])

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED, summary="Create a Book")
def create_book(book_in: BookCreate):
    global book_id_counter
    
    # Enforce parent relationship rule: The member must exist
    if book_in.member_id not in db_members:
        raise HTTPException(status_code=400, detail=f"Member parent with ID {book_in.member_id} does not exist.")
        
    # Enforce ISBN uniqueness rule
    if any(b["isbn"] == book_in.isbn for b in db_books.values()):
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists.")
        
    new_id = book_id_counter
    book_data = book_in.model_dump()
    book_data["id"] = new_id
    
    db_books[new_id] = book_data
    book_id_counter += 1
    return book_data

@router.get("", response_model=List[BookResponse], summary="Retrieve All Books")
def get_all_books():
    return list(db_books.values())

@router.get("/{book_id}", response_model=BookResponse, summary="Retrieve One Book")
def get_book(book_id: int):
    if book_id not in db_books:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")
    return db_books[book_id]

@router.put("/{book_id}", response_model=BookResponse, summary="Update an Existing Book")
def update_book(book_id: int, book_in: BookUpdate):
    if book_id not in db_books:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")
        
    # Validate destination member assignment exists
    if book_in.member_id not in db_members:
        raise HTTPException(status_code=400, detail=f"Member parent with ID {book_in.member_id} does not exist.")
        
    # Validate unique ISBN configuration across other books
    for bid, b in db_books.items():
        if bid != book_id and b["isbn"] == book_in.isbn:
            raise HTTPException(status_code=400, detail="A book with this ISBN already exists.")
            
    updated_data = book_in.model_dump()
    updated_data["id"] = book_id
    db_books[book_id] = updated_data
    return updated_data

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an Existing Book")
def delete_book(book_id: int):
    if book_id not in db_books:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found.")
    del db_books[book_id]
    return
