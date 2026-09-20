from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the book.")
    author: str = Field(..., min_length=1, max_length=120, description="Author of the book.")
    isbn: str = Field(..., description="Unique International Standard Book Number.")
    published_year: int = Field(..., description="Year published between 1450 and the current year.")
    member_id: int = Field(..., description="The ID of the existing Member who borrowed this Book.")

    @field_validator("title", "author")
    @classmethod
    def trim_whitespace(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 1:
            raise ValueError("String field cannot be empty after stripping whitespace.")
        return trimmed

    @field_validator("published_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if not (1450 <= v <= current_year):
            raise ValueError(f"Published year must be between 1450 and {current_year}.")
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookResponse(BookBase):
    id: int = Field(..., description="Application-generated identifier.")
