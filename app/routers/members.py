from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.member_service import MemberServiceABC
from app.schemas.schemas import MemberCreate, MemberUpdate, MemberResponse, BookResponse
# Clean Developer Comment: Import from the core module layer location
from app.core.dependencies import get_member_service

router = APIRouter(prefix="/members", tags=["Members"])

@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member_in: MemberCreate, service: MemberServiceABC = Depends(get_member_service)):
    try:
        return service.create(member_in)
    except Exception as e:
        if "conflict" in str(e).lower() or "already registered" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[MemberResponse])
def get_all_members(service: MemberServiceABC = Depends(get_member_service)):
    return service.get_all()

@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    member = service.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member

@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member_in: MemberUpdate, service: MemberServiceABC = Depends(get_member_service)):
    member = service.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    try:
        return service.update(member_id, member_in)
    except Exception as e:
        if "conflict" in str(e).lower() or "already registered" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    member = service.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    try:
        service.delete(member_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{member_id}/books", response_model=List[BookResponse])
def get_member_books(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    member = service.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return service.get_associated_books(member_id)
