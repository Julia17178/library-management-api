# Library Management System API

This is a layered FastAPI application for managing library books and members. It supports interchangeable PostgreSQL and temporary process-local in-memory backends through service abstractions, dependency injection, Bearer token authentication with role-based authorization, RFC 9457 Problem Details error responses, and a layered automated test suite.

## Prerequisites
- **Python 3.10+**
- **PostgreSQL Server** (Running locally or via Docker)
- **Docker Desktop** (Required for running `testcontainers` integration and conformance tests)
- **uv** (Modern Python dependency management toolchain)

## Installation & Setup

1. **Clone the repository and switch to the project branch:**
   ```bash
   git clone https://github.com/Julia17178/library-management-api.git
   cd library-management-api
   git checkout assignment-3
   ```

2. **Install project dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Configure Environment Settings:**
   Copy `.env.example` to `.env` in the project root and update the local database credentials if needed:
   ```ini
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/library_db
   STORAGE_BACKEND=DATABASE
   DEMO_MEMBER_TOKEN=member-demo-token
   DEMO_ADMIN_TOKEN=admin-demo-token
   ```
   *(Set `STORAGE_BACKEND` to `IN_MEMORY` if you want to switch back to temporary process-local storage).*

4. **Initialize the PostgreSQL Database:**
   Ensure PostgreSQL is running locally and create an empty database named `library_db` via your terminal or database client:
   ```sql
   CREATE DATABASE library_db;
   ```

## Authentication & Authorization

All `/members` and `/books` endpoints require an HTTP `Authorization: Bearer <token>` header, while `GET /health` remains public:

- **Member Token (`DEMO_MEMBER_TOKEN=member-demo-token`):** Grants read-only (`GET`) access to `/members`, `/members/{member_id}`, `/members/{member_id}/books`, `/books`, and `/books/{book_id}`. Attempting `POST`, `PUT`, or `DELETE` returns `403 Forbidden`.
- **Admin Token (`DEMO_ADMIN_TOKEN=admin-demo-token`):** Grants full read (`GET`) and write (`POST`, `PUT`, `DELETE`) access across all resources.
- **Unauthenticated / Invalid Token:** Returns `401 Unauthorized` with `WWW-Authenticate: Bearer` in RFC 9457 `application/problem+json` format.

## Running the Application

Start the local Uvicorn development server with `uv` (no manual activation step is required):

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If you prefer to activate the environment manually, use `.venv\Scripts\activate` in Windows PowerShell or `source .venv/bin/activate` on macOS/Linux, then run `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.

## Interactive API Documentation

Once the server indicates that startup is complete, you can review, test, and exercise representative success and error payload cases through the interactive dashboards (click **Authorize** in Swagger UI and enter `admin-demo-token` or `member-demo-token`):

- **Swagger UI (Interactive API Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc alternative view:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Core API Endpoint Structure

### System (`/health`)
- `GET /health` - Public health check reporting service status and active storage backend

### Members (`/members`)
- `POST /members` - Create a new member profile *(Admin only)*
- `GET /members` - List all members *(Member or Admin)*
- `GET /members/{member_id}` - Retrieve a member's detail card *(Member or Admin)*
- `PUT /members/{member_id}` - Update a member's attributes *(Admin only)*
- `DELETE /members/{member_id}` - Delete a member *(Admin only; blocked with `409 Conflict` if books are associated)*
- `GET /members/{member_id}/books` - Retrieve all books currently linked to a specific member *(Member or Admin)*

### Books (`/books`)
- `POST /books` - Add a new book *(Admin only; requires a valid `member_id` and mandatory `published_year`)*
- `GET /books` - List all books *(Member or Admin)*
- `GET /books/{book_id}` - Retrieve specific book details by database ID *(Member or Admin)*
- `PUT /books/{book_id}` - Update book properties *(Admin only)*
- `DELETE /books/{book_id}` - Permanently delete a book record *(Admin only)*

## Example Requests

Create a Member (Admin token required):

```bash
curl -X POST http://127.0.0.1:8000/members \
  -H 'Authorization: Bearer admin-demo-token' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Avery Reader","email":"avery@example.com","membership_id":"LIB-1001","phone":"555-123-4567"}'
```

Create a Book for the returned Member ID (replace `1` with the actual ID):

```bash
curl -X POST http://127.0.0.1:8000/books \
  -H 'Authorization: Bearer admin-demo-token' \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example Book","author":"Example Author","isbn":"978-1-4028-9462-6","published_year":2020,"member_id":1}'
```

## Running Automated Tests

Ensure **Docker Desktop** is running before executing integration and conformance tests (which automatically provision and tear down a temporary PostgreSQL container via `testcontainers`).

Run the entire automated test suite:

```bash
uv run pytest
```

Run individual test layers:

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/conformance
```

## Current Project Structure Tree

```text
library-management-api/
├── app/
│   ├── auth/
│   │   ├── dependencies.py    # FastAPI HTTPBearer authentication and admin role dependencies
│   │   └── users.py           # Predefined demo roles, users, and token lookup helpers
│   ├── core/
│   │   ├── config.py          # Typed settings, demo tokens, and database engine/session factory
│   │   ├── dependencies.py    # FastAPI settings and service dependencies
│   │   ├── error_handlers.py  # Centralized RFC 9457 Problem Details exception handlers
│   │   └── exceptions.py      # Application-specific exceptions
│   ├── models/
│   │   └── models.py          # SQLAlchemy Member and Book models
│   ├── repositories/
│   │   ├── book_repo.py       # SQLAlchemy Book queries and writes
│   │   └── member_repo.py     # SQLAlchemy Member queries and writes
│   ├── routers/
│   │   ├── books.py           # Protected Book HTTP endpoints and OpenAPI responses
│   │   └── members.py         # Protected Member HTTP endpoints and OpenAPI responses
│   ├── schemas/
│   │   ├── problem_details.py # RFC 9457 Problem Details schema and OpenAPI response metadata
│   │   └── schemas.py         # Pydantic request and response models
│   ├── services/
│   │   ├── book_service.py    # Book use cases and storage implementations
│   │   └── member_service.py  # Member use cases and storage implementations
│   └── main.py                # Application setup, error handler registration, and routers
├── tests/
│   ├── conformance/
│   │   ├── test_authentication_authorization_contract.py
│   │   ├── test_negative_requests.py
│   │   └── test_openapi_contract.py
│   ├── integration/
│   │   ├── routers/
│   │   │   └── test_library_workflows.py
│   │   └── test_authentication_authorization_api.py
│   ├── unit/
│   │   ├── auth/
│   │   │   └── test_dependencies.py
│   │   └── schemas/
│   │       └── test_schemas.py
│   └── conftest.py            # Shared pytest fixtures (Testcontainers PostgreSQL, clients, auth headers)
├── .env.example               # Local database, backend, and demo token settings example
├── .gitignore                 # Excludes local environment files
├── pyproject.toml             # Project metadata, pytest config, and dependencies
├── uv.lock                    # Locked dependency versions
└── README.md                  # Setup, authentication, testing, and API documentation
```
