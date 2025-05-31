from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database.base import Base
from .enums import TaskTypeEnum


class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    type = Column(Enum(TaskTypeEnum), default=TaskTypeEnum.OTHER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scheduled_tasks = relationship("ScheduledTaskModel", back_populates="task")
    completions = relationship("TaskCompletionModel", back_populates="task")
    streaks = relationship("UserTaskStreakModel", back_populates="task")
