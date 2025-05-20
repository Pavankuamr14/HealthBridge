from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import date

import models
import schemas
from auth import get_password_hash, verify_password

# User CRUD operations
def get_user(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users with pagination"""
    return db.query(models.User).order_by(desc(models.User.id)).offset(skip).limit(limit).all()

def get_admin_user(db: Session):
    """Get first admin user if exists"""
    return db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()

def create_user(db: Session, user: schemas.UserCreate, role: str = models.UserRole.USER):
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    """Update user information"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    
    # Check if email is being updated and if it's already in use
    if "email" in update_data:
        existing_user = get_user_by_email(db, email=update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise ValueError("Email already registered")
    
    # Handle password update
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Update user fields
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise ValueError(str(e))

def delete_user(db: Session, user_id: int):
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Patient CRUD operations
def get_patient(db: Session, patient_id: int):
    """Get a patient by ID"""
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None
):
    """Get all patients with optional user filter"""
    query = db.query(models.Patient)
    if user_id:
        query = query.filter(models.Patient.owner_id == user_id)
    return query.order_by(desc(models.Patient.admission_date)).offset(skip).limit(limit).all()

def get_user_patients(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all patients for a specific user"""
    return db.query(models.Patient).filter(models.Patient.owner_id == user_id).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate, user_id: int):
    """Create a new patient"""
    db_patient = models.Patient(**patient.dict(), owner_id=user_id)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    """Update a patient's information"""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    """Delete a patient (admin only)"""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return False
    db.delete(db_patient)
    db.commit()
    return True 