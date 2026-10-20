# Library Management System API - Assignment 2

## Architecture Layers
This iteration organizes the FastAPI application into distinct structural layers:
* **Core:** Application initialization, global configuration setup, and custom exceptions.
* **Models:** Persistent database data layout structures.
* **Repositories:** Database write operations and SQLAlchemy query handling.
* **Services:** Core business logic workflows.
* **Routers:** Endpoint paths and status codes.

## Setup Instructions
1. Activate your virtual environment.
2. Run the application server: `uvicorn app.main:app --reload`

## Core Execution Flow Examples

### 1. Add Library Member Record (POST /members)
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "membership_id": "LIB-98765",
  "phone": "555-019-2834"
}
```
**Expected Server Status Response:** `201 Created`

### 2. Issue Book Loan Log (POST /books)
```json
{
  "title": "The Clean Coder",
  "author": "Robert C. Martin",
  "isbn": "978-0137081073",
  "published_year": 2011,
  "member_id": 1
}
```
**Expected Server Status Response:** `201 Created`
