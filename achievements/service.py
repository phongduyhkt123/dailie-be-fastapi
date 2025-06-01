from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import AchievementModel, UserAchievementModel
from .pydantics import UserAchievementPdtCreate


class AchievementService:
    """Service for managing achievements and user achievements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def award_achievement(self, user_id: str, achievement_id: str) -> Optional[UserAchievementModel]:
        """Award an achievement to a user if they don't already have it"""
        # Check if user already has this achievement
        existing = self.db.query(UserAchievementModel).filter(
            UserAchievementModel.user_id == user_id,
            UserAchievementModel.achievement_id == achievement_id
        ).first()
        
        if existing:
            return None
        
        # Check if achievement exists
        achievement = self.db.query(AchievementModel).filter(
            AchievementModel.achievement_id == achievement_id
        ).first()
        
        if not achievement:
            return None
        
        # Create new user achievement
        user_achievement = UserAchievementModel(
            user_id=user_id,
            achievement_id=achievement_id,
            earned_at=datetime.utcnow(),
            current_progress=achievement.target_value,
            is_notified=False
        )
        
        self.db.add(user_achievement)
        self.db.commit()
        self.db.refresh(user_achievement)
        
        return user_achievement
    
    def update_progress(self, user_id: str, achievement_id: str, progress: int) -> Optional[UserAchievementModel]:
        """Update progress for an achievement, awarding it if target is reached"""
        # Get or create user achievement
        user_achievement = self.db.query(UserAchievementModel).filter(
            UserAchievementModel.user_id == user_id,
            UserAchievementModel.achievement_id == achievement_id
        ).first()
        
        if not user_achievement:
            # Create new user achievement with progress
            user_achievement = UserAchievementModel(
                user_id=user_id,
                achievement_id=achievement_id,
                current_progress=progress,
                is_notified=False
            )
            self.db.add(user_achievement)
        else:
            # Update existing progress
            user_achievement.current_progress = progress
        
        # Check if achievement should be awarded
        achievement = self.db.query(AchievementModel).filter(
            AchievementModel.achievement_id == achievement_id
        ).first()
        
        if achievement and progress >= achievement.target_value and not user_achievement.earned_at:
            user_achievement.earned_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user_achievement)
        
        return user_achievement
    
    def check_task_completion_achievements(self, user_id: str, total_tasks: int, tasks_today: int) -> List[UserAchievementModel]:
        """Check and award task completion achievements"""
        newly_awarded = []
        
        # First task achievement
        if total_tasks >= 1:
            achievement = self.award_achievement(user_id, "first_task")
            if achievement:
                newly_awarded.append(achievement)
        
        # Task milestone achievements
        milestones = [
            (10, "task_master_10"),
            (50, "productivity_pro_50"),
            (100, "task_legend_100"),
            (500, "task_god_500")
        ]
        
        for milestone, achievement_id in milestones:
            if total_tasks >= milestone:
                achievement = self.award_achievement(user_id, achievement_id)
                if achievement:
                    newly_awarded.append(achievement)
        
        return newly_awarded
    
    def check_streak_achievements(self, user_id: str, current_streak: int) -> List[UserAchievementModel]:
        """Check and award streak achievements"""
        newly_awarded = []
        
        milestones = [
            (7, "week_warrior"),
            (30, "month_champion"),
            (100, "streak_master_100"),
            (365, "unstoppable_365")
        ]
        
        for milestone, achievement_id in milestones:
            if current_streak >= milestone:
                achievement = self.award_achievement(user_id, achievement_id)
                if achievement:
                    newly_awarded.append(achievement)
        
        return newly_awarded
    
    def check_consistency_achievements(self, user_id: str, active_days: int, consistency_percentage: float) -> List[UserAchievementModel]:
        """Check and award consistency achievements"""
        newly_awarded = []
        
        if active_days >= 7:
            achievement = self.award_achievement(user_id, "consistent_performer")
            if achievement:
                newly_awarded.append(achievement)
        
        if active_days >= 30:
            achievement = self.award_achievement(user_id, "monthly_regular")
            if achievement:
                newly_awarded.append(achievement)
        
        if active_days >= 100 and consistency_percentage >= 80.0:
            achievement = self.award_achievement(user_id, "habit_champion")
            if achievement:
                newly_awarded.append(achievement)
        
        return newly_awarded
    
    def check_health_achievements(self, user_id: str, health_connected: bool, health_tasks: int) -> List[UserAchievementModel]:
        """Check and award health integration achievements"""
        newly_awarded = []
        
        if health_connected and health_tasks >= 1:
            achievement = self.award_achievement(user_id, "fitness_friend")
            if achievement:
                newly_awarded.append(achievement)
        
        if health_tasks >= 10:
            achievement = self.award_achievement(user_id, "health_hero")
            if achievement:
                newly_awarded.append(achievement)
        
        if health_tasks >= 50:
            achievement = self.award_achievement(user_id, "wellness_warrior")
            if achievement:
                newly_awarded.append(achievement)
        
        return newly_awarded
    
    def check_multitasking_achievements(self, user_id: str, concurrent_tasks: int) -> List[UserAchievementModel]:
        """Check and award multitasking achievements"""
        newly_awarded = []
        
        if concurrent_tasks >= 3:
            achievement = self.award_achievement(user_id, "multi_tasker")
            if achievement:
                newly_awarded.append(achievement)
        
        if concurrent_tasks >= 5:
            achievement = self.award_achievement(user_id, "juggler")
            if achievement:
                newly_awarded.append(achievement)
        
        return newly_awarded
    
    def check_special_achievements(self, user_id: str, completion_time: datetime) -> List[UserAchievementModel]:
        """Check and award special time-based achievements"""
        newly_awarded = []
        
        # Early bird (before 6 AM)
        if completion_time.hour < 6:
            achievement = self.award_achievement(user_id, "early_bird")
            if achievement:
                newly_awarded.append(achievement)
        
        # Night owl (after 11 PM)
        if completion_time.hour >= 23:
            achievement = self.award_achievement(user_id, "night_owl")
            if achievement:
                newly_awarded.append(achievement)
        
        # Weekend warrior (Saturday or Sunday)
        if completion_time.weekday() in [5, 6]:  # Saturday=5, Sunday=6
            achievement = self.award_achievement(user_id, "weekend_warrior")
            if achievement:
                newly_awarded.append(achievement)
        
        return newly_awarded
    
    def get_user_achievement_stats(self, user_id: str) -> Dict[str, Any]:
        """Get achievement statistics for a user"""
        user_achievements = self.db.query(UserAchievementModel).filter(
            UserAchievementModel.user_id == user_id
        ).all()
        
        total_achievements = self.db.query(AchievementModel).count()
        earned_achievements = [ua for ua in user_achievements if ua.earned_at is not None]
        
        # Group by type
        achievements_by_type = {}
        all_achievements = self.db.query(AchievementModel).all()
        
        for achievement in all_achievements:
            if achievement.type not in achievements_by_type:
                achievements_by_type[achievement.type] = {"total": 0, "earned": 0}
            achievements_by_type[achievement.type]["total"] += 1
            
            # Check if user has earned this achievement
            user_achievement = next(
                (ua for ua in earned_achievements if ua.achievement_id == achievement.achievement_id),
                None
            )
            if user_achievement:
                achievements_by_type[achievement.type]["earned"] += 1
        
        return {
            "total_earned": len(earned_achievements),
            "total_available": total_achievements,
            "completion_percentage": int((len(earned_achievements) / total_achievements * 100)) if total_achievements > 0 else 0,
            "by_type": achievements_by_type,
            "recent_achievements": [
                {
                    "achievement_id": ua.achievement_id,
                    "earned_at": ua.earned_at.isoformat() if ua.earned_at else None
                }
                for ua in sorted(earned_achievements, key=lambda x: x.earned_at or datetime.min, reverse=True)[:5]
            ]
        }
    
    def get_unnotified_achievements(self, user_id: str) -> List[UserAchievementModel]:
        """Get achievements that haven't been shown to the user yet"""
        return self.db.query(UserAchievementModel).filter(
            UserAchievementModel.user_id == user_id,
            UserAchievementModel.is_notified == False,
            UserAchievementModel.earned_at.isnot(None)
        ).all()
    
    def mark_achievements_as_notified(self, user_id: str, achievement_ids: List[str]):
        """Mark multiple achievements as notified"""
        self.db.query(UserAchievementModel).filter(
            UserAchievementModel.user_id == user_id,
            UserAchievementModel.achievement_id.in_(achievement_ids)
        ).update({"is_notified": True}, synchronize_session=False)
        
        self.db.commit()
