from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..tasks.models import ScheduledTask


class ScheduleBase(BaseModel):
    date: datetime
    user_id: str = Field(..., description="User ID for multi-user support")


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    date: Optional[datetime] = None


class Schedule(ScheduleBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    schedule_tasks: Optional[List[ScheduledTask]] = []
    
    class Config:
        from_attributes = True
