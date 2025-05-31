from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

from core.config import settings
from users.models import UserModel
from .pydantics import UserLoginPdt, UserRegisterPdt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        """Authenticate a user by email and password"""
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
        return encoded_jwt

    def register_user(self, user_data: UserRegisterPdt) -> Optional[UserModel]:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.db.query(UserModel).filter(UserModel.email == user_data.email).first()
        if existing_user:
            return None
        
        # Create new user
        hashed_password = self.get_password_hash(user_data.password)
        db_user = UserModel(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return email"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None
