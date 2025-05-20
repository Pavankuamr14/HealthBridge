from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date
from models import UserRole

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# Patient schemas
class PatientBase(BaseModel):
    name: str
    age: int = Field(..., gt=0, lt=150)
    disease: str
    admission_date: date
    discharge_date: Optional[date] = None
    is_admitted: bool = True

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, gt=0, lt=150)
    disease: Optional[str] = None
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    is_admitted: Optional[bool] = None

class Patient(PatientBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True 