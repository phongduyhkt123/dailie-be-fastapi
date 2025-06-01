from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HistoryPdtBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=50)
    date: datetime
    tasks_completed: int = Field(default=0, ge=0)
    tasks_scheduled: int = Field(default=0, ge=0)
    completion_rate: int = Field(default=0, ge=0, le=100)  # Percentage 0-100
    streak_count: int = Field(default=0, ge=0)
    achievements_earned: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=500)


class HistoryPdtCreate(HistoryPdtBase):
    pass


class HistoryPdtUpdate(BaseModel):
    date: Optional[datetime] = None
    tasks_completed: Optional[int] = Field(None, ge=0)
    tasks_scheduled: Optional[int] = Field(None, ge=0)
    completion_rate: Optional[int] = Field(None, ge=0, le=100)
    streak_count: Optional[int] = Field(None, ge=0)
    achievements_earned: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=500)


class HistoryPdtModel(HistoryPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
