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


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: TaskType = TaskType.OTHER


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TaskType] = None


class Task(TaskBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScheduledTaskBase(BaseModel):
    task_id: int
    date: datetime
    status: TaskStatus = TaskStatus.PENDING
    priority: int
    note: Optional[str] = None
    completed_at: Optional[datetime] = None
    schedule_id: int


class ScheduledTaskCreate(ScheduledTaskBase):
    pass


class ScheduledTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    note: Optional[str] = None
    completed_at: Optional[datetime] = None


class ScheduledTask(ScheduledTaskBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    task: Optional[Task] = None
    
    class Config:
        from_attributes = True


class TaskCompletionBase(BaseModel):
    task_id: int
    user_id: str
    completion_date: datetime
    note: Optional[str] = None


class TaskCompletionCreate(TaskCompletionBase):
    pass


class TaskCompletionUpdate(BaseModel):
    note: Optional[str] = None


class TaskCompletion(TaskCompletionBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
