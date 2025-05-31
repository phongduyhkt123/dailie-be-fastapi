from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ...tasks.models.enums import TaskTypeEnum, TaskStatusEnum


# Pydantic models for admin responses
class AdminUserResponse(BaseModel):
    id: int
    user_id: str
    name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminTaskResponse(BaseModel):
    id: int
    title: str
    type: TaskTypeEnum
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminScheduleResponse(BaseModel):
    id: int
    date: datetime
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminScheduledTaskResponse(BaseModel):
    id: int
    task_id: int
    schedule_id: int
    date: datetime
    status: TaskStatusEnum
    priority: int
    note: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminTaskCompletionResponse(BaseModel):
    id: int
    task_id: int
    user_id: str
    completion_date: datetime
    note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminUserTaskStreakResponse(BaseModel):
    id: int
    task_id: int
    user_id: str
    current_streak: int
    longest_streak: int
    last_completed_date: Optional[datetime]
    streak_start_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Dashboard statistics model
class AdminDashboardStats(BaseModel):
    total_users: int
    total_tasks: int
    total_completions: int
    active_streaks: int
    recent_completions: List[AdminTaskCompletionResponse]
