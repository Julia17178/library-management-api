from sqlalchemy.orm import Session
from app.models.models import Book
from app.schemas.schemas import BookCreate, BookUpdate

class BookRepository:

    def get_all(self, db: Session):
        return db.query(Book).all()

    def get_by_id(self, db: Session, book_id: int):
        return db.query(Book).filter(Book.id == book_id).first()

    def get_by_isbn(self, db: Session, isbn: str):
        return db.query(Book).filter(Book.isbn == isbn).first()

    def create(self, db: Session, book_data: BookCreate) -> Book:
       
        
        db_book = Book(**book_data.model_dump())
        db.add(db_book)
        return db_book

    def update(self, db: Session, book_id: int, book_data: BookUpdate) -> Book | None:
        db_book = self.get_by_id(db, book_id)
        if not db_book:
            return None
        
        
        update_data = book_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(db_book, key, value)
            
        return db_book

    def delete(self, db: Session, db_book: Book) -> None:
        
        db.delete(db_book)
