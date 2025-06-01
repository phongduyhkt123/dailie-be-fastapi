from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from core.models import BaseModel
from .enums import TaskTypeEnum


class TaskModel(BaseModel):
    __tablename__ = "tasks"
    
    title = Column(String(200), nullable=False)
    type = Column(Enum(TaskTypeEnum), default=TaskTypeEnum.OTHER)
    
    # Relationships
    scheduled_tasks = relationship("ScheduledTaskModel", back_populates="task")
    completions = relationship("TaskCompletionModel", back_populates="task")
    streaks = relationship("UserTaskStreakModel", back_populates="task")
