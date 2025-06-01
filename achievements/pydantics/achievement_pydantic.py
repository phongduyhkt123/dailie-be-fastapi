from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AchievementPdtBase(BaseModel):
    achievement_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    icon_code_point: str = Field(..., min_length=1, max_length=20)
    color: str = Field(..., min_length=7, max_length=10)  # Hex color format #RRGGBB
    type: str = Field(..., min_length=1, max_length=50)
    rarity: str = Field(default="common", min_length=1, max_length=20)
    target_value: int = Field(default=1, ge=1)
    is_secret: bool = Field(default=False)


class AchievementPdtCreate(AchievementPdtBase):
    pass


class AchievementPdtUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    icon_code_point: Optional[str] = Field(None, min_length=1, max_length=20)
    color: Optional[str] = Field(None, min_length=7, max_length=10)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    rarity: Optional[str] = Field(None, min_length=1, max_length=20)
    target_value: Optional[int] = Field(None, ge=1)
    is_secret: Optional[bool] = None


class AchievementPdtModel(AchievementPdtBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
