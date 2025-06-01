from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from core.database import get_db
from users.models import UserModel as UserModel
from .pydantics import UserPdtModel as User, UserPdtCreate as UserCreate, UserPdtUpdate as UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user_id already exists
    existing_user = db.query(UserModel).filter(UserModel.user_id == user.user_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already registered")
    
    # Check if email already exists
    existing_email = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = UserModel(
        user_id=user.user_id,
        name=user.name,
        email=user.email
    )
    db_user.created_at = datetime.now(timezone.utc)
    db_user.updated_at = datetime.now(timezone.utc)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user by user_id"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        # Check if new email already exists
        existing_email = db.query(UserModel).filter(
            UserModel.email == user_update.email,
            UserModel.user_id != user_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = user_update.email
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/by-email/{email}", response_model=User)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Get a user by email address"""
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
