from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import db_members, db_books, member_id_counter
from app.models.member import MemberCreate, MemberUpdate, MemberResponse
from app.models.book import BookResponse

router = APIRouter(prefix="/members", tags=["Members Management"])

@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED, summary="Create a Member")
def create_member(member_in: MemberCreate):
    global member_id_counter
    
    # Enforce uniqueness of email and membership_id
    for m in db_members.values():
        if m["email"] == member_in.email:
            raise HTTPException(status_code=400, detail="A member with this email already exists.")
        if m["membership_id"] == member_in.membership_id:
            raise HTTPException(status_code=400, detail="A member with this membership ID already exists.")
            
    new_id = member_id_counter
    member_data = member_in.model_dump()
    member_data["id"] = new_id
    
    db_members[new_id] = member_data
    member_id_counter += 1
    return member_data

@router.get("", response_model=List[MemberResponse], summary="Retrieve All Members")
def get_all_members():
    return list(db_members.values())

@router.get("/{member_id}", response_model=MemberResponse, summary="Retrieve One Member")
def get_member(member_id: int):
    if member_id not in db_members:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found.")
    return db_members[member_id]

@router.put("/{member_id}", response_model=MemberResponse, summary="Update an Existing Member")
def update_member(member_id: int, member_in: MemberUpdate):
    if member_id not in db_members:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found.")
        
    # Check uniqueness constraints ignoring the current record being updated
    for mid, m in db_members.items():
        if mid != member_id:
            if m["email"] == member_in.email:
                raise HTTPException(status_code=400, detail="A member with this email already exists.")
            if m["membership_id"] == member_in.membership_id:
                raise HTTPException(status_code=400, detail="A member with this membership ID already exists.")

    updated_data = member_in.model_dump()
    updated_data["id"] = member_id
    db_members[member_id] = updated_data
    return updated_data

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an Existing Member")
def delete_member(member_id: int):
    if member_id not in db_members:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found.")
        
    # Block deletion if member still possesses borrowed books
    has_books = any(b["member_id"] == member_id for b in db_books.values())
    if has_books:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete a Member who has borrowed books assigned. Reassign or delete books first."
        )
        
    del db_members[member_id]
    return

@router.get("/{member_id}/books", response_model=List[BookResponse], summary="Retrieve Books Borrowed by a Member")
def get_member_books(member_id: int):
    if member_id not in db_members:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found.")
        
    # Filter books mapping back to this member identifier
    member_books = [b for b in db_books.values() if b["member_id"] == member_id]
    return member_books
