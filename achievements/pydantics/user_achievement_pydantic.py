from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserAchievementPdtBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=50)
    achievement_id: str = Field(..., min_length=1, max_length=100)
    earned_at: Optional[datetime] = None
    current_progress: Optional[int] = Field(default=0, ge=0)
    is_notified: bool = Field(default=False)  # Changed from notified to is_notified to match Flutter


class UserAchievementPdtCreate(UserAchievementPdtBase):
    pass


class UserAchievementPdtUpdate(BaseModel):
    earned_at: Optional[datetime] = None
    current_progress: Optional[int] = Field(None, ge=0)
    is_notified: Optional[bool] = None


class UserAchievementPdtModel(UserAchievementPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
