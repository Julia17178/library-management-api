# Library Management System API

A layered FastAPI implementation of a library record system featuring interchangeable data storage backends, input validation, and relation-driven entity protection rules.

## Core Architectural Responsibilities
The project cleanly isolates structural operations into dedicated application slices:
* **Core:** Application lifecycle states, typed environmental parameters, and domain-level exceptions.
* **Models:** Persistent metadata schema layouts mapped to relational target tables.
* **Repositories:** Direct query handling and operational transaction scopes.
* **Services:** Use case workflows, business rule parsing, and structural data mutation isolation.
* **Routers:** Public contract parameters, payload model mappings, and public HTTP exception boundary handling.
* **Schemas:** Structured data enforcement validation engines.

```text
library-management-api/
├── app/
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── models.py
│   ├── repositories/
│   │   ├── book_repo.py
│   │   └── member_repo.py
│   ├── routers/
│   │   ├── books.py
│   │   └── members.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   ├── book_service.py
│   │   └── member_service.py
│   ├── dependencies.py
│   └── main.py
├── .env.example
├── pyproject.toml
└── README.md
```

## Prerequisites & Installation

### 1. Environment and Tools Setup
This application requires Python 3.10+ and the `uv` tool suite or standard virtual environments.

```bash
# Clone the repository structure
git clone https://github.com
cd library-management-api

# Create and lock the virtual workspace environment
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Synchronize declared system dependencies 
uv sync
```

### 2. Configuration Profiles
Copy the distributed baseline setup parameters to create your active environmental configuration variables profile:

```bash
cp .env.example .env
```

Review the configurations inside the produced `.env` file:
* `DATABASE_URL`: Target location mapping for a live PostgreSQL instance.
* `STORAGE_BACKEND`: Controls operational layer execution (`database` or `memory`).

### 3. Server Initialization
Launch the live server framework context under local development reload polling:

```bash
uvicorn app.main:app --reload
```
* **Interactive Open API Contract Interface:** View at [http://127.0.0](http://127.0.0)
* **Alternative Document Portal:** View at [http://127.0.0](http://127.0.0)

---

## Core Execution Flow Examples

### 1. Add Library Member Record (`POST /members`)
* **Payload Structure:**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "membership_id": "LIB-98765",
  "phone": "555-019-2834"
}
```
* **Expected Output Code:** `201 Created`

### 2. Issue Book Loan Log (`POST /books`)
* **Payload Structure:**
```json
{
  "title": "The Clean Coder",
  "author": "Robert C. Martin",
  "isbn": "978-0137081073",
  "published_year": 2011,
  "member_id": 1
}
```
* **Expected Output Code:** `201 Created`

### 3. Retrieve Outstanding Member Allocations (`GET /members/{member_id}/books`)
* **Expected Output Code:** `200 OK`
* **Response Body Array Structure:**
```json
[
  {
    "id": 1,
    "title": "The Clean Coder",
    "author": "Robert C. Martin",
    "isbn": "978-0137081073",
    "published_year": 2011,
    "member_id": 1
  }
]
```

### 4. Remove Profile Instance Under Active Constraint (`DELETE /members/{member_id}`)
* **Scenario:** Attempting to purge a profile instance that still maintains an active book allocation reference.
* **Expected Output Code:** `400 Bad Request`
* **Error Envelope Schema:**
```json
{
  "detail": "Cannot delete Member. Outstanding borrowed books must be returned or reassigned first."
}
```

### 5. Attempt Registry Duplicate Collision (`POST /members`)
* **Scenario:** Attempting to submit an existing recorded email, barcode identifier, or unique book ISBN.
* **Expected Output Code:** `409 Conflict`
