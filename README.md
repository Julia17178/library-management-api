# Library Management System API

This is a layered, asynchronous FastAPI application providing a robust backend for managing library books and members. The system supports interchangeable storage backends (PostgreSQL database persistence or temporary process-local in-memory storage) using explicit service abstractions and dependency injection.

## Prerequisites
- **Python 3.10+**
- **PostgreSQL Server** (Running locally or via Docker)
- **uv** (Modern Python dependency management toolchain)

## Installation & Setup

1. **Clone the repository and switch to the project branch:**
   ```bash
   git clone https://github.com
   cd library-management-api
   git checkout assignment-2
   ```

2. **Install project dependencies using `uv`:**
   ```bash
   uv sync
   ```

3. **Configure Environment Settings:**
   Create a file named `.env` in the root folder using the layout below as a template:
   ```ini
   DATABASE_URL=postgresql://postgres:password@localhost:5432/library_db
   STORAGE_BACKEND=DATABASE
   ```
   *(Set `STORAGE_BACKEND` to `IN_MEMORY` if you want to switch back to temporary process-local storage).*

4. **Initialize the PostgreSQL Database:**
   Ensure PostgreSQL is running locally and create an empty database named `library_db` via your terminal or database client:
   ```sql
   CREATE DATABASE library_db;
   ```

## Running the Application

Activate your virtual environment and start the local Uvicorn development server:

```bash
# Activate environment
.venv\Scripts\activate

# Launch development web server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

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

## Current Project Structure Tree

```text
library-management-api/
├── app/
│   ├── core/           # App configuration and settings validation
│   ├── models/         # SQLAlchemy ORM database mappings
│   ├── repositories/   # Data-access layers running raw SQL / ORM filters
│   ├── routers/        # FastAPI HTTP endpoints, payload routers, and status maps
│   ├── schemas/        # Pydantic input / output payload validation blueprints
│   ├── services/       # Core business logic processing and transaction boundaries
│   └── main.py         # Application lifecycle and router registration entrypoint
├── .env.example        # Reference configurations file
├── pyproject.toml      # Modern tool dependency metadata manifest
└── README.md           # Documentation guide
```
