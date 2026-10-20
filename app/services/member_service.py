from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import sessionmaker

from app import models
from app.core.exceptions import ResourceNotFoundError, DataConflictError, BusinessRuleError
from app.repositories.member_repo import MemberRepository
from app.schemas.schemas import MemberCreate, BookResponse

class MemberServiceABC(ABC):
    """Shared abstract contract describing all allowable Member operations."""
    @abstractmethod
    def get_all_members(self): pass
    @abstractmethod
    def get_member_by_id(self, member_id: int): pass
    @abstractmethod
    def create_member(self, member_data: MemberCreate): pass
    @abstractmethod
    def delete_member(self, member_id: int): pass


class InMemoryMemberService(MemberServiceABC):
    """Temporary process-local state implementation matching Assignment 1 behavior."""
    def __init__(self):
        self._members = {}
        self._id_counter = 1

    def get_all_members(self):
        # Convert dictionary values to match structured outputs
        return list(self._members.values())

    def get_member_by_id(self, member_id: int):
        if member_id not in self._members:
            raise ResourceNotFoundError("Member not found")
        return self._members[member_id]

    def create_member(self, member_data: MemberCreate):
        # Unique constraints check
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
            "books": []
        }
        self._members[self._id_counter] = new_member
        self._id_counter += 1
        return new_member

    def delete_member(self, member_id: int):
        member = self.get_member_by_id(member_id)
        if len(member.get("books", [])) > 0:
            raise BusinessRuleError("Cannot delete a member with associated books")
        del self._members[member_id]


class DatabaseMemberService(MemberServiceABC):
    """Database-backed implementation using transactional repositories."""
    def __init__(self, session_factory: sessionmaker, repo: MemberRepository):
        self.session_factory = session_factory
        self.repo = repo

    def get_all_members(self):
        with self.session_factory() as db:
            return self.repo.get_all(db)

    def get_member_by_id(self, member_id: int):
        with self.session_factory() as db:
            member = self.repo.get_by_id(db, member_id)
            if not member:
                raise ResourceNotFoundError(f"Member with ID {member_id} not found")
            return member

    def create_member(self, member_data: MemberCreate):
        with self.session_factory() as db:
            # Check unique validation criteria before committing transaction records
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

    def delete_member(self, member_id: int):
        with self.session_factory() as db:
            db_member = self.repo.get_by_id(db, member_id)
            if not db_member:
                raise ResourceNotFoundError(f"Member with ID {member_id} not found")
            
            # Preserve Assignment 1 rule: Block deletion if they have books checked out
            if len(db_member.books) > 0:
                raise BusinessRuleError("Cannot delete a member with associated books")
            
            try:
                self.repo.delete(db, db_member)
                db.commit()
            except Exception:
                db.rollback()
                raise
