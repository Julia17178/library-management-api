from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# --- BOOK SCHEMAS ---
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the book")
    author: str = Field(..., min_length=1, description="The author of the book")
    isbn: str = Field(..., min_length=10, max_length=13, description="Unique ISBN code")

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    member_id: Optional[int] = None

    model_config = {"from_attributes": True}


# --- MEMBER SCHEMAS ---
class MemberBase(BaseModel):
    membership_id: str = Field(..., min_length=3, description="Unique library membership ID")
    name: str = Field(..., min_length=1, description="Full name of the library member")
    email: EmailStr = Field(..., description="Unique personal email address")

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int
    # Includes their books automatically when viewing a member response payload
    books: List[BookResponse] = []

    model_config = {"from_attributes": True}
