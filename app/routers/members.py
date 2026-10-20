from fastapi import APIRouter, Depends, status
from typing import List

from app.core.dependencies import get_member_service
from app.schemas.schemas import MemberCreate, MemberResponse
from app.services.member_service import MemberServiceABC

router = APIRouter(prefix="/members", tags=["Members"])

@router.get("", response_model=List[MemberResponse], status_code=status.HTTP_200_OK)
async def list_members(service: MemberServiceABC = Depends(get_member_service)):
    """Fetch all registered library members along with their book lists."""
    return service.get_all_members()

@router.get("/{member_id}", response_model=MemberResponse, status_code=status.HTTP_200_OK)
async def get_member(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    """Fetch a single library member profile by their ID."""
    return service.get_member_by_id(member_id)

@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(member_data: MemberCreate, service: MemberServiceABC = Depends(get_member_service)):
    """Register a new library member profile."""
    return service.create_member(member_data)

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(member_id: int, service: MemberServiceABC = Depends(get_member_service)):
    """Remove an existing library member profile."""
    service.delete_member(member_id)
    return None
