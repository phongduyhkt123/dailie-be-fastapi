from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.config import settings
from .pydantics import TokenPdt, UserRegisterPdt
from .service import AuthService
from users.models import UserModel

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_authenticated_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserModel:
    """Dependency to get the current authenticated user"""
    email = auth_service.verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/register", response_model=dict)
def register(user_data: UserRegisterPdt, auth_service: AuthService = Depends(get_auth_service)):
    """Register a new user"""
    user = auth_service.register_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return {"message": "User registered successfully", "user_id": user.id}


@router.post("/token", response_model=TokenPdt)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return access token"""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_current_user(
    current_user: UserModel = Depends(get_current_authenticated_user)
):
    """Get current authenticated user"""
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email}
