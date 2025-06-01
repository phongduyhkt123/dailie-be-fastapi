from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from core.models import BaseModel


class UserAchievementModel(BaseModel):
    __tablename__ = "user_achievements"
    
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, index=True)
    achievement_id = Column(String(100), ForeignKey("achievements.achievement_id"), nullable=False, index=True)
    earned_at = Column(DateTime(timezone=True), nullable=True)  # Nullable if not yet earned
    current_progress = Column(Integer, nullable=True, default=0)
    is_notified = Column(Boolean, nullable=False, default=False)  # Use is_notified to match Flutter
    
    # Relationships
    achievement = relationship("AchievementModel", back_populates="user_achievements")
    user = relationship("UserModel", back_populates="user_achievements")
