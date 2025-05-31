from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.enums import TaskStatusEnum
from .task_pydantic import TaskPdtModel


class ScheduledTaskPdtBaseModel(BaseModel):
    task_id: int
    date: datetime
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority: int
    note: Optional[str] = None
    completed_at: Optional[datetime] = None
    schedule_id: int


class ScheduledTaskPdtCreate(ScheduledTaskPdtBaseModel):
    pass


class ScheduledTaskPdtUpdate(BaseModel):
    status: Optional[TaskStatusEnum] = None
    priority: Optional[int] = None
    note: Optional[str] = None
    completed_at: Optional[datetime] = None


class ScheduledTaskPdtModel(ScheduledTaskPdtBaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    task: Optional[TaskPdtModel] = None
    
    class Config:
        from_attributes = True
