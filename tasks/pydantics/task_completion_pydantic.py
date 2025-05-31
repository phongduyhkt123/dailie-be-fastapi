from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCompletionPdtBase(BaseModel):
    task_id: int
    user_id: str
    completion_date: datetime
    note: Optional[str] = None


class TaskCompletionPdtCreate(TaskCompletionPdtBase):
    pass


class TaskCompletionPdtUpdate(BaseModel):
    note: Optional[str] = None


class TaskCompletionPdtModel(TaskCompletionPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
