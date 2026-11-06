from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import sessionmaker

from app import models
from app.core.exceptions import ResourceNotFoundError, DataConflictError, BusinessRuleError
from app.repositories.member_repo import MemberRepository
from app.schemas.schemas import MemberCreate, MemberUpdate

class MemberServiceABC(ABC):
    @abstractmethod
    def get_all(self): pass
    @abstractmethod
    def get_by_id(self, member_id: int): pass
    @abstractmethod
    def create(self, member_data: MemberCreate): pass
    @abstractmethod
    def update(self, member_id: int, member_data: MemberUpdate): pass
    @abstractmethod
    def delete(self, member_id: int): pass
    @abstractmethod
    def get_associated_books(self, member_id: int): pass


class InMemoryMemberService(MemberServiceABC):
    def __init__(self):
        self._members = {}
        self._id_counter = 1
        self.book_service = None

    def get_all(self):
        return list(self._members.values())

    def get_by_id(self, member_id: int):
        if member_id not in self._members:
            return None
        return self._members[member_id]

    def create(self, member_data: MemberCreate):
        for m in self._members.values():
            if m["membership_id"] == member_data.membership_id:
                raise DataConflictError("Membership ID already exists")
            if m["email"] == member_data.email:
                raise DataConflictError("Email already registered")

        new_member = {
            "id": self._id_counter,
            "membership_id": member_data.membership_id,
            "name": member_data.name,
            "email": member_data.email,
            "phone": member_data.phone
        }
        self._members[self._id_counter] = new_member
        self._id_counter += 1
        return new_member

    def update(self, member_id: int, member_data: MemberUpdate):
        existing = self._members.get(member_id)
        if existing is None:
            return None

        update_data = member_data.model_dump(exclude_unset=True, exclude_none=True)
        for m_id, m in self._members.items():
            if m_id != member_id:
                if "membership_id" in update_data and m["membership_id"] == update_data["membership_id"]:
                    raise DataConflictError("Membership ID already exists")
                if "email" in update_data and m["email"] == update_data["email"]:
                    raise DataConflictError("Email already registered")

        existing.update(update_data)
        return existing

    def delete(self, member_id: int):
        if self.book_service and any(
            b["member_id"] == member_id for b in self.book_service.get_all()
        ):
            raise BusinessRuleError("Cannot delete a member with associated books")
        if member_id in self._members:
            del self._members[member_id]

    def get_associated_books(self, member_id: int):
        if not self.book_service:
            return []
        return [book for book in self.book_service.get_all() if book["member_id"] == member_id]


class DatabaseMemberService(MemberServiceABC):
    def __init__(self, session_factory: sessionmaker, repo: MemberRepository):
        self.session_factory = session_factory
        self.repo = repo

    def get_all(self):
        with self.session_factory() as db:
            return self.repo.get_all(db)

    def get_by_id(self, member_id: int):
        with self.session_factory() as db:
            return self.repo.get_by_id(db, member_id)

    def create(self, member_data: MemberCreate):
        with self.session_factory() as db:
            if self.repo.get_by_membership_id(db, member_data.membership_id):
                raise DataConflictError("Membership ID already exists")
            if self.repo.get_by_email(db, member_data.email):
                raise DataConflictError("Email already registered")
            
            try:
                db_member = self.repo.create(db, member_data)
                db.commit()
                db.refresh(db_member)
                return db_member
            except Exception:
                db.rollback()
                raise

    def update(self, member_id: int, member_data: MemberUpdate):
        with self.session_factory() as db:
            existing_member = self.repo.get_by_id(db, member_id)
            if not existing_member:
                return None
            
            conflict_member = self.repo.get_by_email(db, member_data.email)
            if conflict_member and conflict_member.id != member_id:
                raise DataConflictError("Email already registered")
                
            conflict_id = self.repo.get_by_membership_id(db, member_data.membership_id)
            if conflict_id and conflict_id.id != member_id:
                raise DataConflictError("Membership ID already exists")

            try:
                updated = self.repo.update(db, member_id, member_data)
                db.commit()
                db.refresh(updated)
                return updated
            except Exception:
                db.rollback()
                raise

    def delete(self, member_id: int):
        with self.session_factory() as db:
            db_member = self.repo.get_by_id(db, member_id)
            if not db_member:
                raise ResourceNotFoundError(f"Member with ID {member_id} not found")
            
            if self.repo.has_associated_books(db, member_id):
                raise BusinessRuleError("Cannot delete a member with associated books")
            
            try:
                self.repo.delete(db, db_member)
                db.commit()
            except Exception:
                db.rollback()
                raise

    def get_associated_books(self, member_id: int):
        with self.session_factory() as db:
            return self.repo.get_books(db, member_id)
