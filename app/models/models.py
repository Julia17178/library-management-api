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

    # One-to-many relationship: A member can have many books checked out
    # cascade="all, delete-orphan" is omitted so deleting a member with books fails cleanly via foreign key
    books = relationship("Book", back_populates="member")


class Book(Base):
    __tablename__ = "books"

    # Database-generated primary key ID
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    
    # Enforcing unique and non-null constraint on ISBN
    isbn = Column(String, unique=True, nullable=False, index=True)
    
    # Foreign key constraint pointing to the member table
    # Set to nullable=True if a book can exist without being checked out by a member
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    # Relationship linking back to the Member model
    member = relationship("Member", back_populates="books")
