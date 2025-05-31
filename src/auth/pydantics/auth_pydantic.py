from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenPdt(BaseModel):
    access_token: str
    token_type: str


class TokenDataPdt(BaseModel):
    username: Optional[str] = None


class UserLoginPdt(BaseModel):
    email: EmailStr
    password: str


class UserRegisterPdt(BaseModel):
    name: str
    email: EmailStr
    password: str


class PasswordResetPdt(BaseModel):
    email: EmailStr


class PasswordUpdatePdt(BaseModel):
    current_password: str
    new_password: str
