from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from core.models import BaseModel


class ScheduleModel(BaseModel):
    __tablename__ = "schedules"
    
    date = Column(DateTime, nullable=False)
    user_id = Column(String(50), nullable=False)
    
    # Relationships
    scheduled_tasks = relationship("ScheduledTaskModel", back_populates="schedule")
