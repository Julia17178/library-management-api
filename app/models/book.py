from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

class BookBase(BaseModel):
    model_config = ConfigDict(extra="forbid") 
    
    title: str = Field(..., min_length=1, max_length=200, description="Title of the book.", examples=["The Great Gatsby"])
    author: str = Field(..., min_length=1, max_length=120, description="Author of the book.", examples=["F. Scott Fitzgerald"])
    isbn: str = Field(..., description="Unique International Standard Book Number.", examples=["978-0743273565"])
    published_year: int = Field(..., description="Year published between 1450 and the current year.", examples=[1925])
    member_id: int = Field(..., description="The ID of the existing Member who borrowed this Book.", examples=[1])

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
