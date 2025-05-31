from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserTaskStreakPdtBase(BaseModel):
    task_id: int
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_completed_date: Optional[datetime] = None
    streak_start_date: Optional[datetime] = None


class UserTaskStreakPdtCreate(UserTaskStreakPdtBase):
    pass


class UserTaskStreakPdtUpdate(BaseModel):
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    last_completed_date: Optional[datetime] = None
    streak_start_date: Optional[datetime] = None


class UserTaskStreakPdtModel(UserTaskStreakPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
