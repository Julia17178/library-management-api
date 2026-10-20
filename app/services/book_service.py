from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import sessionmaker

from app import models
from app.core.exceptions import ResourceNotFoundError, DataConflictError, BusinessRuleError
from app.repositories.book_repo import BookRepository
from app.repositories.member_repo import MemberRepository
from app.schemas.schemas import BookCreate

class BookServiceABC(ABC):
    """Shared abstract contract describing all allowable Book operations."""
    @abstractmethod
    def get_all_books(self): pass
    @abstractmethod
    def get_book_by_id(self, book_id: int): pass
    @abstractmethod
    def create_book(self, book_data: BookCreate): pass
    @abstractmethod
    def delete_book(self, book_id: int): pass


class InMemoryBookService(BookServiceABC):
    """Temporary process-local state implementation matching Assignment 1 behavior."""
    def __init__(self, member_service: InMemoryMemberService):
        self._books = {}
        self._id_counter = 1
        self.member_service = member_service

    def get_all_books(self):
        return list(self._books.values())

    def get_book_by_id(self, book_id: int):
        if book_id not in self._books:
            raise ResourceNotFoundError("Book not found")
        return self._books[book_id]

    def create_book(self, book_data: BookCreate):
        for b in self._books.values():
            if b["isbn"] == book_data.isbn:
                raise DataConflictError("ISBN already exists")

        new_book = {
            "id": self._id_counter,
            "title": book_data.title,
            "author": book_data.author,
            "isbn": book_data.isbn,
            "member_id": None
        }
        self._books[self._id_counter] = new_book
        self._id_counter += 1
        return new_book

    def delete_book(self, book_id: int):
        self.get_book_by_id(book_id)
        del self._books[book_id]


class DatabaseBookService(BookServiceABC):
    """Database-backed implementation using transactional repositories."""
    def __init__(self, session_factory: sessionmaker, repo: BookRepository):
        self.session_factory = session_factory
        self.repo = repo

    def get_all_books(self):
        with self.session_factory() as db:
            return self.repo.get_all(db)

    def get_book_by_id(self, book_id: int):
        with self.session_factory() as db:
            book = self.repo.get_by_id(db, book_id)
            if not book:
                raise ResourceNotFoundError(f"Book with ID {book_id} not found")
            return book

    def create_book(self, book_data: BookCreate):
        with self.session_factory() as db:
            if self.repo.get_by_isbn(db, book_data.isbn):
                raise DataConflictError("ISBN already exists")
            
            try:
                db_book = self.repo.create(db, book_data)
                db.commit()
                db.refresh(db_book)
                return db_book
            except Exception:
                db.rollback()
                raise

    def delete_book(self, book_id: int):
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
