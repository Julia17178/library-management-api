from pydantic import BaseModel, Field, EmailStr, StringConstraints
from typing import Annotated
from datetime import date
from pydantic import field_validator

# Enforce stripped whitespace and character limits for required string inputs
TrimmedTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TrimmedAuthor = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
TrimmedName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]

# --- MEMBER SCHEMAS ---
class MemberBase(BaseModel):
    name: TrimmedName
    email: EmailStr
    membership_id: str = Field(..., min_length=1)
    phone: str = Field(..., pattern=r"^\d{3}-\d{3}-\d{4}$")

class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: TrimmedName | None = None
    email: EmailStr | None = None
    membership_id: str | None = Field(None, min_length=1)
    phone: str | None = Field(None, pattern=r"^\d{3}-\d{3}-\d{4}$")

class MemberResponse(MemberBase):
    id: int

    class Config:
        from_attributes = True


# --- BOOK SCHEMAS ---
class BookBase(BaseModel):
    title: TrimmedTitle
    author: TrimmedAuthor
    isbn: str = Field(..., min_length=1)
    published_year: int = Field(..., ge=1450)
    member_id: int = Field(..., ge=1)

    @field_validator("published_year")
    @classmethod
    def published_year_not_in_future(cls, value: int) -> int:
        if value > date.today().year:
            raise ValueError("published_year cannot be later than the current year")
        return value

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: TrimmedTitle | None = None
    author: TrimmedAuthor | None = None
    isbn: str | None = Field(None, min_length=1)
    published_year: int | None = Field(None, ge=1450)
    member_id: int | None = Field(None, ge=1)

    @field_validator("published_year")
    @classmethod
    def published_year_not_in_future(cls, value: int | None) -> int | None:
        if value is not None and value > date.today().year:
            raise ValueError("published_year cannot be later than the current year")
        return value

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True
