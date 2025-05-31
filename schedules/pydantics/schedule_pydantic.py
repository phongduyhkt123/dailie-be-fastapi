from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ScheduleBasePdtModel(BaseModel):
    date: datetime
    user_id: str = Field(..., description="User ID for multi-user support")


class SchedulePdtCreate(ScheduleBasePdtModel):
    pass


class SchedulePdtUpdate(BaseModel):
    date: Optional[datetime] = None


class SchedulePdtModel(ScheduleBasePdtModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    schedule_tasks: Optional[List] = []  # Will use forward reference for ScheduledTaskModel
    
    class Config:
        from_attributes = True
