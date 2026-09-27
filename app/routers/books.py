from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import db_books, db_members, book_id_counter
from app.models.book import BookCreate, BookUpdate, BookResponse

# Adjusted tag to match lowercase "books" defined in your app/main.py metadata
router = APIRouter(prefix="/books", tags=["books"])

@router.post(
    "", 
    response_model=BookResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a Book",
    description="Registers a new book in the library catalog assigned to a specific borrowing member.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "The assigned member_id does not exist."},
        status.HTTP_409_CONFLICT: {"description": "A book with this ISBN already exists."}
    }
)
def create_book(book_in: BookCreate):
    global book_id_counter
    
    # Enforce parent relationship rule: The member must exist
    if book_in.member_id not in db_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Member parent with ID {book_in.member_id} does not exist."
        )
        
    # FIX: Changed from 400 to 409 Conflict to fulfill professor requirement
    if any(b["isbn"] == book_in.isbn for b in db_books.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="A book with this ISBN already exists."
        )
        
    new_id = book_id_counter
    book_data = book_in.model_dump()
    book_data["id"] = new_id
    
    db_books[new_id] = book_data
    book_id_counter += 1
    return book_data

@router.get(
    "", 
    response_model=List[BookResponse], 
    summary="Retrieve All Books",
    description="Fetches a list containing all registered books inside the library database tracking inventory."
)
def get_all_books():
    return list(db_books.values())

@router.get(
    "/{book_id}", 
    response_model=BookResponse, 
    summary="Retrieve One Book",
    description="Retrieves granular database fields matching back to a specific unique book inventory key.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Book with the specified ID could not be located."}
    }
)
def get_book(book_id: int):
    if book_id not in db_books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Book with ID {book_id} not found."
        )
    return db_books[book_id]

@router.put(
    "/{book_id}", 
    response_model=BookResponse, 
    summary="Update an Existing Book",
    description="Alters metadata configuration fields on an explicit library book catalog listing structure.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "The updated member_id does not exist."},
        status.HTTP_404_NOT_FOUND: {"description": "Target book record entries are missing."},
        status.HTTP_409_CONFLICT: {"description": "Altered catalog parameters create unique ISBN data conflicts."}
    }
)
def update_book(book_id: int, book_in: BookUpdate):
    if book_id not in db_books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Book with ID {book_id} not found."
        )
        
    # Validate destination member assignment exists
    if book_in.member_id not in db_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Member parent with ID {book_in.member_id} does not exist."
        )
        
    # FIX: Changed from 400 to 409 Conflict to fulfill professor requirement
    for bid, b in db_books.items():
        if bid != book_id and b["isbn"] == book_in.isbn:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="A book with this ISBN already exists."
            )
            
    updated_data = book_in.model_dump()
    updated_data["id"] = book_id
    db_books[book_id] = updated_data
    return updated_data

@router.delete(
    "/{book_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete an Existing Book",
    description="Removes a book catalog tracking entity safely from global collection data sets.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Target book directory catalog item not discovered."}
    }
)
def delete_book(book_id: int):
    if book_id not in db_books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Book with ID {book_id} not found."
        )
    del db_books[book_id]
    return
