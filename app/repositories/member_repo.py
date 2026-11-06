from sqlalchemy.orm import Session
from app.models.models import Member, Book
from app.schemas.schemas import MemberCreate, MemberUpdate

class MemberRepository:
    def get_all(self, db: Session):
        return db.query(Member).all()

    def get_by_id(self, db: Session, member_id: int):
        return db.query(Member).filter(Member.id == member_id).first()

    def get_by_membership_id(self, db: Session, membership_id: str):
        return db.query(Member).filter(Member.membership_id == membership_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(Member).filter(Member.email == email).first()

    def create(self, db: Session, member_data: MemberCreate) -> Member:
        db_member = Member(
            membership_id=member_data.membership_id,
            name=member_data.name,
            email=member_data.email,
            phone=member_data.phone
        )
        db.add(db_member)
        return db_member

    def update(self, db: Session, member_id: int, member_data: MemberUpdate) -> Member:
        db_member = db.query(Member).filter(Member.id == member_id).first()
        if db_member:
            for key, value in member_data.model_dump(
                exclude_unset=True, exclude_none=True
            ).items():
                setattr(db_member, key, value)
        return db_member

    def delete(self, db: Session, db_member: Member) -> None:
        db.delete(db_member)

    def has_associated_books(self, db: Session, member_id: int) -> bool:
        return db.query(Book).filter(Book.member_id == member_id).count() > 0

    def get_books(self, db: Session, member_id: int) -> list[Book]:
        return db.query(Book).filter(Book.member_id == member_id).all()
