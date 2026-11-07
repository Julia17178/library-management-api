from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker
from app.core.exceptions import ResourceNotFoundError, DataConflictError
from app.repositories.book_repo import BookRepository
from app.repositories.member_repo import MemberRepository
from app.schemas.schemas import BookCreate, BookUpdate

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
        self._books = {}
        self._id_counter = 1

    def get_all(self):
        return list(self._books.values())

    def get_by_id(self, book_id: int):
        return self._books.get(book_id)

    def create(self, book_data: BookCreate):
        if not self.member_service.get_by_id(book_data.member_id):
            raise ResourceNotFoundError("Referenced Member does not exist")

        for b in self._books.values():
            if b["isbn"] == book_data.isbn:
                raise DataConflictError("Book with this ISBN already exists")

        new_book = {
            "id": self._id_counter,
            "title": book_data.title,
            "author": book_data.author,
            "isbn": book_data.isbn,
            "published_year": book_data.published_year,
            "member_id": book_data.member_id
        }
        self._books[self._id_counter] = new_book
        self._id_counter += 1
        return new_book

    def update(self, book_id: int, book_data: BookUpdate):
        existing = self._books.get(book_id)
        if existing is None:
            return None

        update_data = book_data.model_dump(exclude_unset=True, exclude_none=True)
        if "member_id" in update_data and not self.member_service.get_by_id(update_data["member_id"]):
            raise ResourceNotFoundError("Referenced Member does not exist")

        for b_id, b in self._books.items():
            if b_id != book_id and update_data.get("isbn") == b["isbn"]:
                raise DataConflictError("ISBN matches another current entry")

        existing.update(update_data)
        return existing

    def delete(self, book_id: int):
        if book_id in self._books:
            del self._books[book_id]


class DatabaseBookService(BookServiceABC):
    def __init__(
        self,
        session_factory: sessionmaker,
        repo: BookRepository,
        member_repo: MemberRepository,
    ):
        self.session_factory = session_factory
        self.repo = repo
        self.member_repo = member_repo

    def get_all(self):
        with self.session_factory() as db:
            return self.repo.get_all(db)

    def get_by_id(self, book_id: int):
        with self.session_factory() as db:
            return self.repo.get_by_id(db, book_id)

    def create(self, book_data: BookCreate):
        with self.session_factory() as db:
            if not self.member_repo.get_by_id(db, book_data.member_id):
                raise ResourceNotFoundError("Referenced Member does not exist")
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

            update_data = book_data.model_dump(exclude_unset=True, exclude_none=True)
            if "member_id" in update_data and not self.member_repo.get_by_id(db, update_data["member_id"]):
                raise ResourceNotFoundError("Referenced Member does not exist")

            conflict_isbn = (
                self.repo.get_by_isbn(db, update_data["isbn"])
                if "isbn" in update_data
                else None
            )
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
