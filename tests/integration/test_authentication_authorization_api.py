"""Integration tests for authentication and role-based authorization."""

from starlette.testclient import TestClient


def test_health_endpoint_is_public(memory_client: TestClient) -> None:
    response = memory_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_unauthenticated_requests_return_401_problem_details(
    memory_client: TestClient,
) -> None:
    get_res = memory_client.get("/members")
    assert get_res.status_code == 401
    assert get_res.headers["content-type"].startswith("application/problem+json")
    assert get_res.headers["www-authenticate"] == "Bearer"

    post_res = memory_client.post(
        "/members",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "membership_id": "LIB-001",
            "phone": "555-222-3333",
        },
    )
    assert post_res.status_code == 401


def test_member_token_can_read_but_cannot_write(
    memory_client: TestClient,
    member_headers: dict[str, str],
) -> None:
    assert memory_client.get("/members", headers=member_headers).status_code == 200
    assert memory_client.get("/books", headers=member_headers).status_code == 200

    post_res = memory_client.post(
        "/members",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "membership_id": "LIB-001",
            "phone": "555-222-3333",
        },
        headers=member_headers,
    )
    assert post_res.status_code == 403
    assert post_res.headers["content-type"].startswith("application/problem+json")


def test_admin_token_can_create_update_and_delete_resources(
    memory_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    member_res = memory_client.post(
        "/members",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "membership_id": "LIB-001",
            "phone": "555-222-3333",
        },
        headers=admin_headers,
    )
    assert member_res.status_code == 201
    member_id = member_res.json()["id"]

    book_res = memory_client.post(
        "/books",
        json={
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
            "isbn": "978-0134494166",
            "published_year": 2017,
            "member_id": member_id,
        },
        headers=admin_headers,
    )
    assert book_res.status_code == 201
    book_id = book_res.json()["id"]

    nested_res = memory_client.get(
        f"/members/{member_id}/books", headers=member_headers
    )
    assert nested_res.status_code == 200
    assert len(nested_res.json()) == 1

    assert (
        memory_client.delete(f"/books/{book_id}", headers=admin_headers).status_code
        == 204
    )
    assert (
        memory_client.delete(
            f"/members/{member_id}", headers=admin_headers
        ).status_code
        == 204
    )
