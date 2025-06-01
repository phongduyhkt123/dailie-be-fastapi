from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.database import get_db
from .models import AchievementModel, UserAchievementModel
from .pydantics import (
    AchievementPdtModel, AchievementPdtCreate, AchievementPdtUpdate,
    UserAchievementPdtModel, UserAchievementPdtCreate, UserAchievementPdtUpdate
)
from .service import AchievementService
from .default_achievements import DEFAULT_ACHIEVEMENTS

router = APIRouter(prefix="/achievements", tags=["achievements"])


def get_achievement_service(db: Session = Depends(get_db)) -> AchievementService:
    """Dependency to get achievement service"""
    return AchievementService(db)


# Achievement endpoints
@router.post("/", response_model=AchievementPdtModel)
def create_achievement(achievement: AchievementPdtCreate, db: Session = Depends(get_db)):
    """Create a new achievement"""
    db_achievement = AchievementModel(**achievement.model_dump())
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement


@router.get("/", response_model=List[AchievementPdtModel])
def get_achievements(
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None,
    rarity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all achievements with optional filtering"""
    query = db.query(AchievementModel)
    
    if type:
        query = query.filter(AchievementModel.type == type)
    if rarity:
        query = query.filter(AchievementModel.rarity == rarity)
    
    achievements = query.offset(skip).limit(limit).all()
    return achievements


@router.get("/{achievement_id}", response_model=AchievementPdtModel)
def get_achievement(achievement_id: str, db: Session = Depends(get_db)):
    """Get a specific achievement by ID"""
    achievement = db.query(AchievementModel).filter(AchievementModel.id == achievement_id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return achievement


@router.put("/{achievement_id}", response_model=AchievementPdtModel)
def update_achievement(achievement_id: str, achievement_update: AchievementPdtUpdate, db: Session = Depends(get_db)):
    """Update an achievement"""
    achievement = db.query(AchievementModel).filter(AchievementModel.id == achievement_id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    update_data = achievement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(achievement, field, value)
    
    db.commit()
    db.refresh(achievement)
    return achievement


@router.delete("/{achievement_id}")
def delete_achievement(achievement_id: str, db: Session = Depends(get_db)):
    """Delete an achievement"""
    achievement = db.query(AchievementModel).filter(AchievementModel.id == achievement_id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    db.delete(achievement)
    db.commit()
    return {"message": "Achievement deleted successfully"}


@router.post("/initialize-defaults")
def initialize_default_achievements(db: Session = Depends(get_db)):
    """Initialize default achievements from the predefined list"""
    created_count = 0
    updated_count = 0
    
    for achievement_data in DEFAULT_ACHIEVEMENTS:
        existing = db.query(AchievementModel).filter(
            AchievementModel.achievement_id == achievement_data["achievement_id"]
        ).first()
        
        if existing:
            # Update existing achievement with new data
            for field, value in achievement_data.items():
                setattr(existing, field, value)
            updated_count += 1
        else:
            # Create new achievement
            achievement = AchievementModel(**achievement_data)
            db.add(achievement)
            created_count += 1
    
    db.commit()
    return {
        "message": f"Initialized achievements: {created_count} created, {updated_count} updated",
        "total_achievements": len(DEFAULT_ACHIEVEMENTS)
    }


# User Achievement endpoints
@router.post("/user", response_model=UserAchievementPdtModel)
def create_user_achievement(user_achievement: UserAchievementPdtCreate, db: Session = Depends(get_db)):
    """Grant an achievement to a user"""
    # Check if achievement exists
    achievement = db.query(AchievementModel).filter(
        AchievementModel.achievement_id == user_achievement.achievement_id
    ).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Check if user already has this achievement
    existing = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == user_achievement.user_id,
        UserAchievementModel.achievement_id == user_achievement.achievement_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has this achievement")
    
    db_user_achievement = UserAchievementModel(**user_achievement.model_dump())
    db.add(db_user_achievement)
    db.commit()
    db.refresh(db_user_achievement)
    return db_user_achievement


@router.get("/user/{user_id}", response_model=List[UserAchievementPdtModel])
def get_user_achievements(user_id: str, earned_only: bool = False, db: Session = Depends(get_db)):
    """Get all achievements for a specific user"""
    query = db.query(UserAchievementModel).filter(UserAchievementModel.user_id == user_id)
    
    if earned_only:
        query = query.filter(UserAchievementModel.earned_at.isnot(None))
    
    user_achievements = query.all()
    return user_achievements


@router.get("/user/{user_id}/by-type/{achievement_type}", response_model=List[UserAchievementPdtModel])
def get_user_achievements_by_type(user_id: str, achievement_type: str, db: Session = Depends(get_db)):
    """Get user achievements filtered by achievement type"""
    user_achievements = db.query(UserAchievementModel).join(AchievementModel).filter(
        UserAchievementModel.user_id == user_id,
        AchievementModel.type == achievement_type
    ).all()
    return user_achievements


@router.get("/user/{user_id}/{achievement_id}", response_model=UserAchievementPdtModel)
def get_user_achievement(user_id: str, achievement_id: str, db: Session = Depends(get_db)):
    """Get a specific user achievement"""
    user_achievement = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == user_id,
        UserAchievementModel.achievement_id == achievement_id
    ).first()
    if not user_achievement:
        raise HTTPException(status_code=404, detail="User achievement not found")
    return user_achievement


@router.put("/user/{user_id}/{achievement_id}", response_model=UserAchievementPdtModel)
def update_user_achievement(
    user_id: str, 
    achievement_id: str, 
    user_achievement_update: UserAchievementPdtUpdate, 
    db: Session = Depends(get_db)
):
    """Update a user achievement"""
    user_achievement = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == user_id,
        UserAchievementModel.achievement_id == achievement_id
    ).first()
    if not user_achievement:
        raise HTTPException(status_code=404, detail="User achievement not found")
    
    update_data = user_achievement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_achievement, field, value)
    
    db.commit()
    db.refresh(user_achievement)
    return user_achievement


@router.delete("/user/{user_id}/{achievement_id}")
def delete_user_achievement(user_id: str, achievement_id: str, db: Session = Depends(get_db)):
    """Remove an achievement from a user"""
    user_achievement = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == user_id,
        UserAchievementModel.achievement_id == achievement_id
    ).first()
    if not user_achievement:
        raise HTTPException(status_code=404, detail="User achievement not found")
    
    db.delete(user_achievement)
    db.commit()
    return {"message": "User achievement deleted successfully"}


# Achievement checking and awarding endpoints
@router.post("/user/{user_id}/award/{achievement_id}", response_model=UserAchievementPdtModel)
def award_achievement_to_user(
    user_id: str, 
    achievement_id: str, 
    service: AchievementService = Depends(get_achievement_service)
):
    """Award a specific achievement to a user"""
    user_achievement = service.award_achievement(user_id, achievement_id)
    if not user_achievement:
        raise HTTPException(status_code=400, detail="Achievement already earned or doesn't exist")
    return user_achievement


@router.post("/user/{user_id}/update-progress/{achievement_id}", response_model=UserAchievementPdtModel)
def update_achievement_progress(
    user_id: str, 
    achievement_id: str, 
    progress: int,
    service: AchievementService = Depends(get_achievement_service)
):
    """Update progress for a specific achievement"""
    user_achievement = service.update_progress(user_id, achievement_id, progress)
    return user_achievement


@router.post("/user/{user_id}/check-task-completion", response_model=List[UserAchievementPdtModel])
def check_task_completion_achievements(
    user_id: str,
    total_tasks: int,
    tasks_today: int,
    service: AchievementService = Depends(get_achievement_service)
):
    """Check and award task completion achievements"""
    return service.check_task_completion_achievements(user_id, total_tasks, tasks_today)


@router.post("/user/{user_id}/check-streak", response_model=List[UserAchievementPdtModel])
def check_streak_achievements(
    user_id: str,
    current_streak: int,
    service: AchievementService = Depends(get_achievement_service)
):
    """Check and award streak achievements"""
    return service.check_streak_achievements(user_id, current_streak)


@router.post("/user/{user_id}/check-consistency", response_model=List[UserAchievementPdtModel])
def check_consistency_achievements(
    user_id: str,
    active_days: int,
    consistency_percentage: float,
    service: AchievementService = Depends(get_achievement_service)
):
    """Check and award consistency achievements"""
    return service.check_consistency_achievements(user_id, active_days, consistency_percentage)


@router.post("/user/{user_id}/check-health", response_model=List[UserAchievementPdtModel])
def check_health_achievements(
    user_id: str,
    health_connected: bool,
    health_tasks: int,
    service: AchievementService = Depends(get_achievement_service)
):
    """Check and award health integration achievements"""
    return service.check_health_achievements(user_id, health_connected, health_tasks)


@router.post("/user/{user_id}/check-multitasking", response_model=List[UserAchievementPdtModel])
def check_multitasking_achievements(
    user_id: str,
    concurrent_tasks: int,
    service: AchievementService = Depends(get_achievement_service)
):
    """Check and award multitasking achievements"""
    return service.check_multitasking_achievements(user_id, concurrent_tasks)


@router.post("/user/{user_id}/check-special", response_model=List[UserAchievementPdtModel])
def check_special_achievements(
    user_id: str,
    completion_time: datetime,
    service: AchievementService = Depends(get_achievement_service)
):
    """Check and award special time-based achievements"""
    return service.check_special_achievements(user_id, completion_time)


# Statistics and utility endpoints
@router.get("/user/{user_id}/stats")
def get_user_achievement_stats(
    user_id: str,
    service: AchievementService = Depends(get_achievement_service)
):
    """Get comprehensive achievement statistics for a user"""
    return service.get_user_achievement_stats(user_id)


@router.get("/user/{user_id}/unnotified", response_model=List[UserAchievementPdtModel])
def get_unnotified_achievements(
    user_id: str, 
    service: AchievementService = Depends(get_achievement_service)
):
    """Get unnotified achievements for a user"""
    return service.get_unnotified_achievements(user_id)


@router.put("/user/{user_id}/mark-notified")
def mark_achievements_as_notified(
    user_id: str,
    achievement_ids: List[str],
    service: AchievementService = Depends(get_achievement_service)
):
    """Mark multiple achievements as notified"""
    service.mark_achievements_as_notified(user_id, achievement_ids)
    return {"message": f"Marked {len(achievement_ids)} achievements as notified"}


@router.put("/user/{user_id}/{achievement_id}/mark-notified")
def mark_achievement_as_notified(
    user_id: str, 
    achievement_id: str, 
    db: Session = Depends(get_db)
):
    """Mark a single achievement as notified"""
    user_achievement = db.query(UserAchievementModel).filter(
        UserAchievementModel.user_id == user_id,
        UserAchievementModel.achievement_id == achievement_id
    ).first()
    if not user_achievement:
        raise HTTPException(status_code=404, detail="User achievement not found")
    
    user_achievement.is_notified = True
    db.commit()
    return {"message": "Achievement marked as notified"}


# Admin endpoints
@router.get("/types")
def get_achievement_types():
    """Get all available achievement types"""
    return {
        "types": [
            "firstTask",
            "taskMilestone", 
            "streakMilestone",
            "consistency",
            "healthIntegration",
            "multiTasking",
            "special"
        ]
    }


@router.get("/rarities")  
def get_achievement_rarities():
    """Get all available achievement rarities"""
    return {
        "rarities": [
            "common",
            "uncommon", 
            "rare",
            "epic",
            "legendary"
        ]
    }
