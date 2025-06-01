from sqlalchemy import Column, String, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from core.models import BaseModel


class AchievementModel(BaseModel):
    __tablename__ = "achievements"
    
    achievement_id = Column(String(100), unique=True, nullable=False, index=True)  # Business logic ID
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)  # Added description field
    icon_code_point = Column(String(20), nullable=False)  # Store icon as code point
    color = Column(String(10), nullable=False)  # Store color as hex string
    type = Column(String(50), nullable=False)  # Achievement type enum as string
    rarity = Column(String(20), nullable=False, default="common")  # Badge rarity enum as string
    target_value = Column(Integer, nullable=False, default=1)
    is_secret = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    user_achievements = relationship("UserAchievementModel", back_populates="achievement")
