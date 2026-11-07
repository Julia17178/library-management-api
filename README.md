# Library Management System API

This is a layered FastAPI application for managing library books and members. It supports interchangeable PostgreSQL and temporary process-local in-memory backends through service abstractions and dependency injection.

## Prerequisites
- **Python 3.10+**
- **PostgreSQL Server** (Running locally or via Docker)
- **uv** (Modern Python dependency management toolchain)

## Installation & Setup

1. **Clone the repository and switch to the project branch:**
   ```bash
   git clone https://github.com/Julia17178/library-management-api.git
   cd library-management-api
   git checkout assignment-2
   ```

2. **Install project dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Configure Environment Settings:**
   Copy `.env.example` to `.env` in the project root and update the local database credentials if needed:
   ```ini
   DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/library_db
   STORAGE_BACKEND=DATABASE
   ```
   *(Set `STORAGE_BACKEND` to `IN_MEMORY` if you want to switch back to temporary process-local storage).*

4. **Initialize the PostgreSQL Database:**
   Ensure PostgreSQL is running locally and create an empty database named `library_db` via your terminal or database client:
   ```sql
   CREATE DATABASE library_db;
   ```

## Running the Application

Start the local Uvicorn development server with `uv` (no manual activation step is required):

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If you prefer to activate the environment manually, use `.venv\\Scripts\\activate` in Windows PowerShell or `source .venv/bin/activate` on macOS/Linux, then run `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.

## Interactive API Documentation

Once the server indicates that startup is complete, you can review, test, and exercise representative success and error payload cases through the interactive dashboards:

- **Swagger UI (Interactive API Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc alternative view:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Core API Endpoint Structure

### Members (`/members`)
- `POST /members/` - Create a new member profile
- `GET /members/` - List all members
- `GET /members/{member_id}` - Retrieve a member's detail card
- `PUT /members/{member_id}` - Update a member's attributes
- `DELETE /members/{member_id}` - Delete a member (Blocked if books are associated)
- `GET /members/{member_id}/books` - Retrieve all books currently linked to a specific member

### Books (`/books`)
- `POST /books/` - Add a new book (Requires a valid `member_id` and a mandatory `published_year`)
- `GET /books/` - List all books 
- `GET /books/{book_id}` - Retrieve specific book details by database ID
- `PUT /books/{book_id}` - Update book properties
- `DELETE /books/{book_id}` - Permanently delete a book record

## Example Requests

Create a Member:

```bash
curl -X POST http://127.0.0.1:8000/members \
  -H 'Content-Type: application/json' \
  -d '{"name":"Avery Reader","email":"avery@example.com","membership_id":"LIB-1001","phone":"555-123-4567"}'
```

Create a Book for the returned Member ID (replace `1` with the actual ID):

```bash
curl -X POST http://127.0.0.1:8000/books \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example Book","author":"Example Author","isbn":"978-1-4028-9462-6","published_year":2020,"member_id":1}'
```

## Current Project Structure Tree

```text
library-management-api/
├── app/
│   ├── core/
│   │   ├── config.py          # Typed settings and database engine/session factory
│   │   ├── dependencies.py    # FastAPI service dependencies
│   │   └── exceptions.py      # Application-specific exceptions
│   ├── models/
│   │   └── models.py          # SQLAlchemy Member and Book models
│   ├── repositories/
│   │   ├── book_repo.py       # SQLAlchemy Book queries and writes
│   │   └── member_repo.py     # SQLAlchemy Member queries and writes
│   ├── routers/
│   │   ├── books.py           # Book HTTP endpoints and error translation
│   │   └── members.py         # Member HTTP endpoints and error translation
│   ├── schemas/
│   │   └── schemas.py         # Pydantic request and response models
│   ├── services/
│   │   ├── book_service.py    # Book use cases and storage implementations
│   │   └── member_service.py  # Member use cases and storage implementations
│   └── main.py                # Application setup and router registration
├── .env.example               # Local database and backend settings example
├── .gitignore                 # Excludes local environment files
├── pyproject.toml             # Project metadata and dependencies
├── uv.lock                    # Locked dependency versions
└── README.md                  # Setup and API documentation
```
