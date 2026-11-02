from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Base class for our SQLAlchemy ORM models
Base = declarative_base()

class Member(Base):
    __tablename__ = "members"

    # Database-generated primary key ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Enforcing database-level unique and non-null constraints as required
    membership_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)

    # One-to-many relationship: A member can have many books checked out
    books = relationship("Book", back_populates="member")


class Book(Base):
    __tablename__ = "books"

    # Database-generated primary key ID
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    
    # Enforcing unique and non-null constraint on ISBN
    isbn = Column(String, unique=True, nullable=False, index=True)
    published_year = Column(Integer, nullable=False)
    
    # Foreign key constraint linking back to the associated member
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    # Relationship linking back to the Member model
    member = relationship("Member", back_populates="books")
