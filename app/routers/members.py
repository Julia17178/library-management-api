from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.member_service import MemberServiceABC
from app.schemas.schemas import MemberCreate, MemberUpdate, MemberResponse, BookResponse
from app.core.dependencies import get_member_service
from app.core.exceptions import BusinessRuleError, DataConflictError, ResourceNotFoundError

# REMOVED prefix="/members" to prevent double-prefixing conflicts with main.py
router = APIRouter()

@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member_in: MemberCreate, service: MemberServiceABC = Depends(get_member_service)):
    try:
        return service.create(member_in)
    except DataConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

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
        updated = service.update(member_id, member_in)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return updated
    except DataConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    member = service.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    try:
        service.delete(member_id)
    except BusinessRuleError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

@router.get("/{member_id}/books", response_model=List[BookResponse])
def get_member_books(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    member = service.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return service.get_associated_books(member_id)
