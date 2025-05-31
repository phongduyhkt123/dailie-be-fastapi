from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBasePdtModel(BaseModel):
    user_id: str = Field(..., description="Business logic user ID (like auth ID)")
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')


class UserPdtCreate(UserBasePdtModel):
    pass


class UserPdtUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')


class UserPdtModel(UserBasePdtModel):
    id: Optional[int] = None  # Database ID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
