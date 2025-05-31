from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    HABIT = "habit"
    ONE_TIME = "oneTime"
    PERSONAL = "personal"
    WORK = "work"
    OTHER = "other"


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAIL = "fail"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"


class TaskPdtBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: TaskType = TaskType.OTHER


class TaskPdtCreate(TaskPdtBase):
    pass


class TaskPdtUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TaskType] = None


class TaskPdtModel(TaskPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScheduledTaskPdtBaseModel(BaseModel):
    task_id: int
    date: datetime
    status: TaskStatus = TaskStatus.PENDING
    priority: int
    note: Optional[str] = None
    completed_at: Optional[datetime] = None
    schedule_id: int


class ScheduledTaskPdtCreate(ScheduledTaskPdtBaseModel):
    pass


class ScheduledTaskPdtUpdate(BaseModel):
    status: Optional[TaskStatus] = None
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
