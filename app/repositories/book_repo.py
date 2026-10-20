from sqlalchemy.orm import Session
from app.models.models import Book
from app.schemas.schemas import BookCreate

class BookRepository:
    def get_all(self, db: Session):
        """Fetch all books currently cataloged in the library."""
        return db.query(Book).all()

    def get_by_id(self, db: Session, book_id: int):
        """Fetch a single book by its database auto-increment ID."""
        return db.query(Book).filter(Book.id == book_id).first()

    def get_by_isbn(self, db: Session, isbn: str):
        """Fetch a single book by its unique ISBN number."""
        return db.query(Book).filter(Book.isbn == isbn).first()

    def create(self, db: Session, book_data: BookCreate) -> Book:
        """Insert a brand new book row into the database."""
        db_book = Book(
            title=book_data.title,
            author=book_data.author,
            isbn=book_data.isbn
        )
        db.add(db_book)
        return db_book

    def delete(self, db: Session, db_book: Book) -> None:
        """Remove an existing book row from the database."""
        db.delete(db_book)
