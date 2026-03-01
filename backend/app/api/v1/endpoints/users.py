from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.models.database import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

router = APIRouter()

# Pydantic Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: str

# Endpoints

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    In a real app, this should be restricted to admins.
    """
    # Check if user exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return _format_user_response(db_user)

@router.get("/me", response_model=UserResponse)
def read_user_me(db: Session = Depends(get_db)):
    """
    Get current user.
    For now, this returns a mock user or the first user in DB for testing.
    """
    # Mock behavior: return the first user found or a dummy
    user = db.query(User).first()
    if not user:
        # Create a default admin if none exists
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return _format_user_response(user)

def _format_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=str(user.created_at)
    )
