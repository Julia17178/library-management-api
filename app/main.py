from fastapi import FastAPI
from app.routers import books, members

tags_metadata = [
    {
        "name": "Root",
        "description": "Root entry point for API health check.",
    },
    {
        "name": "members",
        "description": "Operations with library members, including registration and profile tracking.",
    },
    {
        "name": "books",
        "description": "Operations with library books, including cataloging and searching.",
    },
]

app = FastAPI(
    title="Library Management API",
    description="SDEV 3310 Assignment 1",
    version="1.0.0",
    openapi_tags=tags_metadata
)


# Mount router resource layers
app.include_router(members.router)
app.include_router(books.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Library Management System API! Navigate to /docs for interactive testing."}
