from sqlalchemy.orm import Session
from app.models.models import Member
from app.schemas.schemas import MemberCreate

class MemberRepository:
    def get_all(self, db: Session):
        """Fetch all library members along with their books."""
        return db.query(Member).all()

    def get_by_id(self, db: Session, member_id: int):
        """Fetch a single member by their database auto-increment ID."""
        return db.query(Member).filter(Member.id == member_id).first()

    def get_by_membership_id(self, db: Session, membership_id: str):
        """Fetch a single member by their unique library card membership ID."""
        return db.query(Member).filter(Member.membership_id == membership_id).first()

    def get_by_email(self, db: Session, email: str):
        """Fetch a single member by their unique email address."""
        return db.query(Member).filter(Member.email == email).first()

    def create(self, db: Session, member_data: MemberCreate) -> Member:
        """Insert a brand new member row into the database."""
        db_member = Member(
            membership_id=member_data.membership_id,
            name=member_data.name,
            email=member_data.email
        )
        db.add(db_member)
        return db_member

    def delete(self, db: Session, db_member: Member) -> None:
        """Remove an existing member row from the database."""
        db.delete(db_member)
