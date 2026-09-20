# Library Management System API

This application serves as the core foundation for Assignment 1 in SDEV 3310. It establishes a fully functional RESTful backend using FastAPI and Pydantic validation structures to catalog library inventory assets (Books) and tracking records (Members).

## System Directory Architecture
```text
library_api/
├── app/
│   ├── models/
│   │   ├── book.py
│   │   └── member.py
│   ├── routers/
│   │   ├── books.py
│   │   └── members.py
│   ├── database.py
│   └── main.py
└── requirements.txt
```

## Local Installation and Execution Rules
1. **Initialize a python virtual workspace:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
   ```
2. **Synchronize library packages:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Execute engine instance locally:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation Entrypoints
* Swagger Interactive UI Interface: http://127.0.0.1:8000/docs
* Alternative ReDoc Layout: http://127.0.0.1:8000/redoc

## Core Execution Flow Examples

### 1. Add Library Member Record (POST `/members`)
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "membership_id": "LIB-98765",
  "phone": "555-019-2834"
}
```
*Expected Server Status Response:* `201 Created`

### 2. Issue Book Loan Log (POST `/books`)
```json
{
  "title": "The Clean Coder",
  "author": "Robert C. Martin",
  "isbn": "978-0137081073",
  "published_year": 2011,
  "member_id": 1
}
```
*Expected Server Status Response:* `201 Created`
