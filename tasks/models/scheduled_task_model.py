from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship

from core.models import BaseModel
from .enums import TaskStatusEnum


class ScheduledTaskModel(BaseModel):
    __tablename__ = "scheduled_tasks"
    
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    priority = Column(Integer, default=0)
    note = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    task = relationship("TaskModel", back_populates="scheduled_tasks")
    schedule = relationship("ScheduleModel", back_populates="scheduled_tasks")
