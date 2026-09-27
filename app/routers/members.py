from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import db_members, db_books, member_id_counter
from app.models.member import MemberCreate, MemberUpdate, MemberResponse
from app.models.book import BookResponse

# Adjusted tag to match lowercase "members" defined in your app/main.py metadata
router = APIRouter(prefix="/members", tags=["members"])

@router.post(
    "", 
    response_model=MemberResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a Member",
    description="Registers a new library member while ensuring unique email and membership ID tracking values.",
    responses={
        status.HTTP_409_CONFLICT: {"description": "A member with this email or membership ID already exists."}
    }
)
def create_member(member_in: MemberCreate):
    global member_id_counter
    
    # FIX: Changed from 400 to 409 Conflict to fulfill professor requirement
    for m in db_members.values():
        if m["email"] == member_in.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A member with this email already exists.")
        if m["membership_id"] == member_in.membership_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A member with this membership ID already exists.")
            
    new_id = member_id_counter
    member_data = member_in.model_dump()
    member_data["id"] = new_id
    
    db_members[new_id] = member_data
    member_id_counter += 1
    return member_data

@router.get(
    "", 
    response_model=List[MemberResponse], 
    summary="Retrieve All Members",
    description="Fetches a list containing all registered profiles within the library directory structure."
)
def get_all_members():
    return list(db_members.values())

@router.get(
    "/{member_id}", 
    response_model=MemberResponse, 
    summary="Retrieve One Member",
    description="Retrieves granular record variables matching back to a specific unique entity parameter key.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Member with the specified ID could not be located."}
    }
)
def get_member(member_id: int):
    if member_id not in db_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
    return db_members[member_id]

@router.put(
    "/{member_id}", 
    response_model=MemberResponse, 
    summary="Update an Existing Member",
    description="Alters fields on an explicit profile records dataset file mapping structure.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Target profile entry file parameter keys are missing."},
        status.HTTP_409_CONFLICT: {"description": "Altered variables create structural conflicts."}
    }
)
def update_member(member_id: int, member_in: MemberUpdate):
    if member_id not in db_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
        
    # FIX: Changed from 400 to 409 Conflict to fulfill professor requirement
    for mid, m in db_members.items():
        if mid != member_id:
            if m["email"] == member_in.email:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A member with this email already exists.")
            if m["membership_id"] == member_in.membership_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A member with this membership ID already exists.")

    updated_data = member_in.model_dump()
    updated_data["id"] = member_id
    db_members[member_id] = updated_data
    return updated_data

@router.delete(
    "/{member_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete an Existing Member",
    description="Removes profile parameters safely tracking validation assets metadata strings.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Profile handles outstanding borrowed tracking sets."},
        status.HTTP_404_NOT_FOUND: {"description": "Target profile directory not discovered."}
    }
)
def delete_member(member_id: int):
    if member_id not in db_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
        
    has_books = any(b["member_id"] == member_id for b in db_books.values())
    if has_books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete a Member who has borrowed books assigned. Reassign or delete books first."
        )
        
    del db_members[member_id]
    return

@router.get(
    "/{member_id}/books", 
    response_model=List[BookResponse], 
    summary="Retrieve Books Borrowed by a Member",
    description="Exposes subcategory data objects tracing borrowed inventories parameters assets directly.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Owner target dataset node cannot be located."}
    }
)
def get_member_books(member_id: int):
    if member_id not in db_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
        
    member_books = [b for b in db_books.values() if b["member_id"] == member_id]
    return member_books
