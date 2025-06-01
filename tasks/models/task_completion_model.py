from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from core.models import BaseModel


class TaskCompletionModel(BaseModel):
    __tablename__ = "task_completions"
    
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String(50), nullable=False)
    completion_date = Column(DateTime, nullable=False)
    note = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("TaskModel", back_populates="completions")
