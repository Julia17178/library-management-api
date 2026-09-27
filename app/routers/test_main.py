import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Verify the root route returns a 200 OK status."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_duplicate_member_returns_409():
    """Verify that creating a duplicate member returns a 409 Conflict status."""
    member_payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "membership_id": "M12345",
        "phone": "555-123-4567"
    }
    
    # First creation should succeed (201 Created)
    response1 = client.post("/members", json=member_payload)
    assert response1.status_code == 201
    
    # Second creation with identical payload should trigger a conflict check (409 Conflict)
    response2 = client.post("/members", json=member_payload)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]
