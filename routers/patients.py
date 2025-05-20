from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
import crud
import schemas
from auth import get_current_active_user, check_admin_access
from models import User

# Create router for patient operations
router = APIRouter(
    prefix="/patients",
    tags=["patient_operations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", 
    response_model=schemas.Patient,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
    description="Create a new patient record. Requires user authentication."
)
def create_patient(
    patient: schemas.PatientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new patient record"""
    return crud.create_patient(db=db, patient=patient, user_id=current_user.id)

@router.get("/me", 
    response_model=List[schemas.Patient],
    summary="Get current user's patients",
    description="Retrieve all patients associated with the currently logged-in user."
)
def read_my_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all patients for the current user"""
    return crud.get_user_patients(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{patient_id}", 
    response_model=schemas.Patient,
    summary="Get patient by ID",
    description="Retrieve a specific patient's information by ID. Users can only access their own patients, admins can access any patient."
)
def read_patient(
    patient_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific patient by ID"""
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if user has permission to access this patient
    if current_user.role != "admin" and db_patient.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this patient"
        )
    
    return db_patient

@router.put("/{patient_id}", 
    response_model=schemas.Patient,
    summary="Update patient information",
    description="Update a specific patient's information. Users can only update their own patients, admins can update any patient."
)
def update_patient(
    patient_id: int,
    patient: schemas.PatientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a patient's information"""
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if user has permission to update this patient
    if current_user.role != "admin" and db_patient.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this patient"
        )
    
    return crud.update_patient(db=db, patient_id=patient_id, patient=patient)

# Admin-only endpoints
@router.get("/", 
    response_model=List[schemas.Patient],
    summary="Get all patients (Admin only)",
    description="Retrieve a list of all patients in the system. Admin access required."
)
def read_all_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get all patients (admin only)"""
    return crud.get_patients(db, skip=skip, limit=limit)

@router.delete("/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete patient (Admin only)",
    description="Delete a specific patient. Only administrators can delete patients."
)
def delete_patient(
    patient_id: int,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Delete a patient (admin only)"""
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    crud.delete_patient(db=db, patient_id=patient_id) 