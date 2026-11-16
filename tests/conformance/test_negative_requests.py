"""Negative API tests for invalid, missing, and disallowed client requests."""

import pytest
from starlette.testclient import TestClient


def test_create_member_rejects_missing_required_field(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = database_client.post(
        "/members", json={"name": "Incomplete Member"}, headers=admin_headers
    )
    assert_validation_error(response)


@pytest.mark.parametrize(
    ("name", "phone"),
    [
        ("   ", "555-111-2222"),
        ("x" * 121, "555-111-2222"),
        ("Valid Name", "not-a-phone"),
    ],
    ids=["blank-name", "name-over-max", "invalid-phone"],
)
def test_create_member_rejects_invalid_boundary_values(
    database_client: TestClient,
    admin_headers: dict[str, str],
    name: str,
    phone: str,
) -> None:
    response = database_client.post(
        "/members",
        json={
            "name": name,
            "email": "boundary@example.com",
            "membership_id": "LIB-999",
            "phone": phone,
        },
        headers=admin_headers,
    )
    assert_validation_error(response)


@pytest.mark.parametrize(
    "path",
    ["/members/not-an-integer", "/books/not-an-integer"],
    ids=["member-id", "book-id"],
)
def test_typed_path_parameters_reject_wrong_data_type(
    database_client: TestClient,
    admin_headers: dict[str, str],
    path: str,
) -> None:
    response = database_client.get(path, headers=admin_headers)
    assert_validation_error(response)


@pytest.mark.parametrize(
    "path",
    ["/members/999999", "/books/999999"],
    ids=["member", "book"],
)
def test_missing_resources_return_not_found(
    database_client: TestClient,
    admin_headers: dict[str, str],
    path: str,
) -> None:
    response = database_client.get(path, headers=admin_headers)
    assert_problem(response, 404)


def test_create_book_rejects_nonexistent_member(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = database_client.post(
        "/books",
        json={
            "title": "Orphan Book",
            "author": "Unknown Author",
            "isbn": "978-0000000001",
            "published_year": 2020,
            "member_id": 999999,
        },
        headers=admin_headers,
    )
    assert_problem(response, 404)


def assert_validation_error(response) -> None:
    assert_problem(response, 422)
    assert response.json()["errors"]


def assert_problem(response, status_code: int) -> None:
    assert response.status_code == status_code
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert {"type", "title", "status", "detail", "instance"} <= set(body)
    assert body["status"] == status_code
