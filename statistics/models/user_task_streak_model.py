from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from core.models import BaseModel


class UserTaskStreakModel(BaseModel):
    __tablename__ = "user_task_streaks"
    
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_completed_date = Column(DateTime, nullable=True)
    streak_start_date = Column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("TaskModel", back_populates="streaks")
    user = relationship("UserModel", back_populates="streaks")
