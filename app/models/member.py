import re
from pydantic import BaseModel, EmailStr, Field, field_validator

class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Name of the library member.")
    email: EmailStr = Field(..., description="Unique email address of the member.")
    membership_id: str = Field(..., description="Unique library membership ID.")
    phone: str = Field(..., description="Contact phone number formatted as XXX-XXX-XXXX.")

    @field_validator("name")
    @classmethod
    def trim_name(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 1:
            raise ValueError("Name cannot be empty after stripping whitespace.")
        return trimmed

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Standardized validation rule: Enforces XXX-XXX-XXXX format
        pattern = r"^\d{3}-\d{3}-\d{4}$"
        if not re.match(pattern, v):
            raise ValueError("Phone number must match the format XXX-XXX-XXXX.")
        return v

class MemberCreate(MemberBase):
    pass

class MemberUpdate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int = Field(..., description="Application-generated identifier.")
