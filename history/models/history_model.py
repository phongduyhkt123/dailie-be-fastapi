from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from core.models import BaseModel


class HistoryModel(BaseModel):
    __tablename__ = "history"
    
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, nullable=False)
    tasks_completed = Column(Integer, nullable=False, default=0)
    tasks_scheduled = Column(Integer, nullable=False, default=0)
    completion_rate = Column(Integer, nullable=False, default=0)  # Percentage as integer
    streak_count = Column(Integer, nullable=False, default=0)
    achievements_earned = Column(JSON, nullable=True)  # Store list of achievement IDs
    notes = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="history")
