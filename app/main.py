from fastapi import FastAPI
from app.routers import books, members

app = FastAPI(
    title="Library Management System API",
    description="SDEV 3310 Assignment 1 working version utilizing temporary local application memory state.",
    version="1.0.0"
)

# Mount router resource layers
app.include_router(members.router)
app.include_router(books.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Library Management System API! Navigate to /docs for interactive testing."}
