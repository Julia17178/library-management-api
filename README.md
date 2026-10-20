# Library Management System API - Assignment 2

This project is a layered REST API built with FastAPI that manages library books and member profiles. It supports dynamic backend switching using environment configurations.

## Architecture Layers
- **API (Routers):** Handles HTTP client validation, status codes, and endpoint routing definitions.
- **Core:** Manages application initialization lifespans, global Pydantic configurations, and custom domain exceptions.
- **Services:** Coordinates business logic workflows and transaction boundaries using abstract contracts (`abc`).
- **Repositories:** Executes raw database queries and write interactions using SQLAlchemy 2.x.
- **Models:** Defines persistent data schema layouts for PostgreSQL tables.

## Setup Instructions

1. **Activate the environment:**
   ```powershell
   . venv/Scripts/Activate.ps1
   ```

2. **Configure environment settings:**
   Create a `.env` file in the root directory to toggle your preferred storage layer:
   ```text
   STORAGE_BACKEND=IN_MEMORY
   ```
   *(To use PostgreSQL, change to `DATABASE` and supply a valid `DATABASE_URL` string).*

3. **Launch the development server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

4. **Access interactive documentation UI:**
   Open your browser and head to: `http://localhost:8000/docs`
