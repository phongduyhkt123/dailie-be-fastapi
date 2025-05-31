from pydantic import BaseModel, Field
from typing import Optional, List
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


# Bulk import models
class TaskBulkImportItem(BaseModel):
    id: Optional[int] = None  # Optional ID for existing tasks
    title: str = Field(..., min_length=1, max_length=200)
    type: Optional[TaskTypeEnum] = TaskTypeEnum.OTHER


class TaskBulkImportRequest(BaseModel):
    tasks: List[TaskBulkImportItem] = Field(..., min_items=1)


class TaskBulkImportResponse(BaseModel):
    success: bool
    created_count: int
    updated_count: int
    skipped_count: int
    tasks: List[TaskPdtModel]
    errors: List[str] = []
