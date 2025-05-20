from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
import enum
from database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    
    # Relationship with patients
    patients = relationship("Patient", back_populates="owner", cascade="all, delete-orphan")

class Patient(Base):
    """Patient model with user relationship"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    disease = Column(String)
    admission_date = Column(Date)
    discharge_date = Column(Date, nullable=True)
    is_admitted = Column(Boolean, default=True)
    
    # Foreign key to link patient with user
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Relationship with user
    owner = relationship("User", back_populates="patients") 