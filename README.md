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
