"""Database-backed integration tests for Library CRUD and business rules."""

from starlette.testclient import TestClient


def test_database_crud_and_member_deletion_protection(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    m_res = database_client.post(
        "/members",
        json={
            "name": "Bob Jones",
            "email": "bob@example.com",
            "membership_id": "LIB-002",
            "phone": "555-444-5555",
        },
        headers=admin_headers,
    )
    assert m_res.status_code == 201
    member_id = m_res.json()["id"]

    b_res = database_client.post(
        "/books",
        json={
            "title": "Designing Data-Intensive Applications",
            "author": "Martin Kleppmann",
            "isbn": "978-1449373320",
            "published_year": 2017,
            "member_id": member_id,
        },
        headers=admin_headers,
    )
    assert b_res.status_code == 201
    book_id = b_res.json()["id"]

    upd_res = database_client.put(
        f"/members/{member_id}",
        json={"name": "Robert Jones"},
        headers=admin_headers,
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Robert Jones"

    del_member_res = database_client.delete(
        f"/members/{member_id}", headers=admin_headers
    )
    assert del_member_res.status_code == 409
    assert del_member_res.headers["content-type"].startswith("application/problem+json")

    assert (
        database_client.delete(f"/books/{book_id}", headers=admin_headers).status_code
        == 204
    )
    assert (
        database_client.delete(
            f"/members/{member_id}", headers=admin_headers
        ).status_code
        == 204
    )
