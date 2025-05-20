from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from database import get_db
import crud
import schemas
from auth import (
    create_access_token,
    get_current_active_user,
    check_admin_access,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password
)
from models import UserRole

# Create separate routers for user and admin operations
user_router = APIRouter(
    prefix="/users",
    tags=["user_operations"],
    responses={404: {"description": "Not found"}},
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin_operations"],
    responses={404: {"description": "Not found"}},
)

# Public endpoints (no authentication required)
@user_router.post("/register", 
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Returns the created user information."
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)

@admin_router.post("/register", 
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new admin user",
    description="Create a new admin account with email and password. Returns the created admin information. Only works if no admin exists yet."
)
def register_admin(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """Register a new admin user"""
    # Check if any admin exists
    existing_admin = crud.get_admin_user(db)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin already exists. Only the first admin can be created without authentication."
        )
    
    # Check if email is already registered
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create the first admin
    return crud.create_user(db=db, user=user, role=UserRole.ADMIN)

@user_router.post("/login", 
    response_model=schemas.Token,
    summary="Login user",
    description="""
    Authenticate user with email and password.
    
    Returns:
    - access_token: JWT token to be used in Authorization header
    - token_type: Always "bearer"
    - expires_in: Token expiration time in seconds
    """
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# User operations (requires user authentication)
@user_router.get("/me", 
    response_model=schemas.User,
    summary="Get current user information",
    description="Retrieve the current authenticated user's information."
)
def read_users_me(current_user = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@user_router.put("/me", 
    response_model=schemas.User,
    summary="Update current user information",
    description="Update the current authenticated user's information."
)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    db_user = crud.update_user(db, user_id=current_user.id, user=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@user_router.delete("/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
    description="Delete the current authenticated user's account."
)
def delete_user_me(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account"""
    if not crud.delete_user(db, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

# Admin operations (requires admin authentication)
@admin_router.get("/users", 
    response_model=List[schemas.User],
    summary="Get all users",
    description="Retrieve a list of all users in the system. Admin access required."
)
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@admin_router.get("/user/{user_id}", 
    response_model=schemas.User,
    summary="Get user by ID",
    description="Retrieve a specific user's information by ID. Admin access required."
)
def get_user_by_id(
    user_id: int,
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@admin_router.put("/user/{user_id}", 
    response_model=schemas.User,
    summary="Update user information",
    description="Update a specific user's information. Admin access required."
)
def update_user_by_id(
    user_id: int,
    user: schemas.UserUpdate,
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)"""
    try:
        db_user = crud.update_user(db, user_id=user_id, user=user)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return db_user
    except ValueError as e:
        if "Email already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@admin_router.delete("/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a specific user's account. Admin access required."
)
def delete_user_by_id(
    user_id: int,
    current_user = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    if not crud.delete_user(db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

# Create the main router and include the sub-routers
router = APIRouter()
router.include_router(user_router)
router.include_router(admin_router) 