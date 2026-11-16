"""Conformance tests for the public OpenAPI contract."""

from typing import Any

import pytest
import schemathesis
from openapi_spec_validator import validate
from schemathesis.checks import (
    content_type_conformance,
    not_a_server_error,
    response_schema_conformance,
    status_code_conformance,
)
from starlette.testclient import TestClient


def test_generated_openapi_document_is_valid(database_client: TestClient) -> None:
    """The API publishes a structurally valid OpenAPI document."""
    response = database_client.get("/openapi.json")
    assert response.status_code == 200
    validate(response.json())


def test_openapi_document_declares_approved_public_operations(
    database_client: TestClient,
) -> None:
    """Required paths, methods, and status codes stay published."""
    paths = database_client.get("/openapi.json").json()["paths"]

    expected_statuses = {
        "/health": {"get": {"200"}},
        "/members": {"get": {"200", "401"}, "post": {"201", "401", "403", "422"}},
        "/members/{member_id}": {
            "get": {"200", "401", "422"},
            "put": {"200", "401", "403", "422"},
            "delete": {"204", "401", "403", "422"},
        },
        "/members/{member_id}/books": {"get": {"200", "401", "422"}},
        "/books": {"get": {"200", "401"}, "post": {"201", "401", "403", "422"}},
        "/books/{book_id}": {
            "get": {"200", "401", "422"},
            "put": {"200", "401", "403", "422"},
            "delete": {"204", "401", "403", "422"},
        },
    }

    for path, operations in expected_statuses.items():
        assert path in paths
        for method, statuses in operations.items():
            assert method in paths[path]
            documented_statuses = set(paths[path][method]["responses"])
            assert statuses <= documented_statuses


@pytest.fixture
def openapi_schema(database_client: TestClient) -> Any:
    """Load the OpenAPI contract after the isolated database is ready."""
    from app.main import app

    return schemathesis.openapi.from_asgi("/openapi.json", app)


schema = schemathesis.pytest.from_fixture("openapi_schema").include(
    method="GET",
    path_regex=r"^/(health|members|books)$",
)


@schema.parametrize()
def test_generated_read_only_responses_conform_to_openapi(
    case: Any,
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Generated safe requests receive responses valid for their OpenAPI schema."""
    case.call_and_validate(
        session=database_client,
        headers=admin_headers,
        checks=[
            not_a_server_error,
            status_code_conformance,
            content_type_conformance,
            response_schema_conformance,
        ],
    )
