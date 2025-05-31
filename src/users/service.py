from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database.models import User as UserModel
from .models import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserModel:
        """Create a new user"""
        db_user = UserModel(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get all users with pagination"""
        return self.db.query(UserModel).offset(skip).limit(limit).all()

    def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get a specific user by ID"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserModel]:
        """Update a user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
