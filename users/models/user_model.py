from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from core.models import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"
    
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Relationships
    streaks = relationship("UserTaskStreakModel", back_populates="user")
    user_achievements = relationship("UserAchievementModel", back_populates="user")
    history = relationship("HistoryModel", back_populates="user")
