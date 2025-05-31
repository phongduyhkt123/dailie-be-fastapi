from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from tasks.models.enums import TaskTypeEnum


class TaskPdtBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: TaskTypeEnum = TaskTypeEnum.OTHER


class TaskPdtCreate(TaskPdtBase):
    pass


class TaskPdtUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TaskTypeEnum] = None


class TaskPdtModel(TaskPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
