"""Unit tests for Pydantic Member and Book validation schemas."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.schemas import BookCreate, MemberCreate


def test_member_create_trims_name_and_validates_phone() -> None:
    member = MemberCreate(
        name="  Julia Haines  ",
        email="julia@example.com",
        membership_id="MEM-1001",
        phone="555-123-4567",
    )
    assert member.name == "Julia Haines"


def test_member_create_rejects_invalid_phone_format() -> None:
    with pytest.raises(ValidationError):
        MemberCreate(
            name="Julia Haines",
            email="julia@example.com",
            membership_id="MEM-1001",
            phone="5551234567",
        )


def test_book_create_rejects_future_published_year() -> None:
    with pytest.raises(ValidationError):
        BookCreate(
            title="Future Book",
            author="Jane Doe",
            isbn="978-0134685991",
            published_year=date.today().year + 1,
            member_id=1,
        )
