from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db
from auth import get_current_active_user, check_admin_access

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

@router.get("/patients", 
    response_model=List[schemas.Patient],
    summary="Get all patients (Admin only)",
    description="Retrieve all patients in the system. This endpoint is only accessible to admin users."
)
def read_all_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all patients (admin only)"""
    if not check_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access all patients"
        )
    return crud.get_patients(db, skip=skip, limit=limit)

@router.delete("/patients/{patient_id}", 
    summary="Delete a patient (Admin only)",
    description="Delete a patient record. This endpoint is only accessible to admin users."
)
def delete_patient(
    patient_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a patient (admin only)"""
    if not check_admin_access(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete patients"
        )
    success = crud.delete_patient(db, patient_id=patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"} 