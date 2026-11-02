from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker
from app.core.exceptions import ResourceNotFoundError, DataConflictError
from app.repositories.book_repo import BookRepository
from app.schemas.schemas import BookCreate, BookUpdate

# Central application-memory collection for books matching Assignment 1 behavior
_memory_books = {}
_memory_id_counter = 1

class BookServiceABC(ABC):
    @abstractmethod
    def get_all(self): pass
    @abstractmethod
    def get_by_id(self, book_id: int): pass
    @abstractmethod
    def create(self, book_data: BookCreate): pass
    @abstractmethod
    def update(self, book_id: int, book_data: BookUpdate): pass
    @abstractmethod
    def delete(self, book_id: int): pass


class InMemoryBookService(BookServiceABC):
    def __init__(self, member_service):
        self.member_service = member_service

    def get_all(self):
        return list(_memory_books.values())

    def get_by_id(self, book_id: int):
        if book_id not in _memory_books:
            return None
        return _memory_books[book_id]

    def create(self, book_data: BookCreate):
        global _memory_id_counter
        for b in _memory_books.values():
            if b["isbn"] == book_data.isbn:
                raise DataConflictError("Book with this ISBN already exists")

        new_book = {
            "id": _memory_id_counter,
            "title": book_data.title,
            "author": book_data.author,
            "isbn": book_data.isbn,
            "published_year": book_data.published_year,
            "member_id": book_data.member_id
        }
        _memory_books[_memory_id_counter] = new_book
        _memory_id_counter += 1
        return new_book

    def update(self, book_id: int, book_data: BookUpdate):
        for b_id, b in _memory_books.items():
            if b_id != book_id and b["isbn"] == book_data.isbn:
                raise DataConflictError("ISBN matches another current entry")

        updated_book = {
            "id": book_id,
            "title": book_data.title,
            "author": book_data.author,
            "isbn": book_data.isbn,
            "published_year": book_data.published_year,
            "member_id": book_data.member_id
        }
        _memory_books[book_id] = updated_book
        return updated_book

    def delete(self, book_id: int):
        if book_id in _memory_books:
            del _memory_books[book_id]


class DatabaseBookService(BookServiceABC):
    def __init__(self, session_factory: sessionmaker, repo: BookRepository):
        self.session_factory = session_factory
        self.repo = repo

    def get_all(self):
        with self.session_factory() as db:
            return self.repo.get_all(db)

    def get_by_id(self, book_id: int):
        with self.session_factory() as db:
            return self.repo.get_by_id(db, book_id)

    def create(self, book_data: BookCreate):
        with self.session_factory() as db:
            if self.repo.get_by_isbn(db, book_data.isbn):
                raise DataConflictError("Book with this ISBN already exists")
            
            try:
                db_book = self.repo.create(db, book_data)
                db.commit()
                db.refresh(db_book)
                return db_book
            except Exception:
                db.rollback()
                raise

    def update(self, book_id: int, book_data: BookUpdate):
        with self.session_factory() as db:
            existing_book = self.repo.get_by_id(db, book_id)
            if not existing_book:
                return None

            conflict_isbn = self.repo.get_by_isbn(db, book_data.isbn)
            if conflict_isbn and conflict_isbn.id != book_id:
                raise DataConflictError("ISBN matches another current entry")

            try:
                updated = self.repo.update(db, book_id, book_data)
                db.commit()
                db.refresh(updated)
                return updated
            except Exception:
                db.rollback()
                raise

    def delete(self, book_id: int):
        with self.session_factory() as db:
            db_book = self.repo.get_by_id(db, book_id)
            if not db_book:
                raise ResourceNotFoundError(f"Book with ID {book_id} not found")
            
            try:
                self.repo.delete(db, db_book)
                db.commit()
            except Exception:
                db.rollback()
                raise
