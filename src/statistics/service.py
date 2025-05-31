from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from .database_models import UserTaskStreak as UserTaskStreakModel
from ..tasks.database_models import TaskCompletionModel, TaskModel 
from ..tasks.models import TaskCompletionCreate, TaskCompletionUpdate
from .models import UserTaskStreakCreate, UserTaskStreakUpdate


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db

    def create_task_completion(self, completion: TaskCompletionCreate) -> Optional[TaskCompletionModel]:
        """Record a task completion"""
        # Check if task exists
        task = self.db.query(TaskModel).filter(TaskModel.id == completion.task_id).first()
        if not task:
            return None
        
        db_completion = TaskCompletionModel(**completion.dict())
        self.db.add(db_completion)
        self.db.commit()
        self.db.refresh(db_completion)
        
        # Update or create streak
        self._update_user_task_streak(completion.user_id, completion.task_id, completion.completed_at)
        
        return db_completion

    def get_task_completions(
        self,
        user_id: Optional[int] = None,
        task_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskCompletionModel]:
        """Get task completions with optional filters"""
        query = self.db.query(TaskCompletionModel)
        
        if user_id:
            query = query.filter(TaskCompletionModel.user_id == user_id)
        if task_id:
            query = query.filter(TaskCompletionModel.task_id == task_id)
        if start_date:
            query = query.filter(TaskCompletionModel.completed_at >= start_date)
        if end_date:
            query = query.filter(TaskCompletionModel.completed_at <= end_date)
        
        return query.offset(skip).limit(limit).all()

    def get_completion_by_id(self, completion_id: int) -> Optional[TaskCompletionModel]:
        """Get a specific completion by ID"""
        return self.db.query(TaskCompletionModel).filter(
            TaskCompletionModel.id == completion_id
        ).first()

    def update_task_completion(
        self, 
        completion_id: int, 
        completion_update: TaskCompletionUpdate
    ) -> Optional[TaskCompletionModel]:
        """Update a task completion"""
        completion = self.get_completion_by_id(completion_id)
        if not completion:
            return None
        
        update_data = completion_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(completion, field, value)
        
        self.db.commit()
        self.db.refresh(completion)
        return completion

    def delete_task_completion(self, completion_id: int) -> bool:
        """Delete a task completion"""
        completion = self.get_completion_by_id(completion_id)
        if not completion:
            return False
        
        self.db.delete(completion)
        self.db.commit()
        return True

    def get_user_task_streaks(
        self,
        user_id: Optional[int] = None,
        task_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserTaskStreakModel]:
        """Get user task streaks with optional filters"""
        query = self.db.query(UserTaskStreakModel)
        
        if user_id:
            query = query.filter(UserTaskStreakModel.user_id == user_id)
        if task_id:
            query = query.filter(UserTaskStreakModel.task_id == task_id)
        
        return query.offset(skip).limit(limit).all()

    def get_user_task_streak(self, user_id: int, task_id: int) -> Optional[UserTaskStreakModel]:
        """Get a specific user task streak"""
        return self.db.query(UserTaskStreakModel).filter(
            UserTaskStreakModel.user_id == user_id,
            UserTaskStreakModel.task_id == task_id
        ).first()

    def _update_user_task_streak(self, user_id: int, task_id: int, completed_at: datetime):
        """Update or create user task streak"""
        streak = self.get_user_task_streak(user_id, task_id)
        
        if not streak:
            # Create new streak
            streak = UserTaskStreakModel(
                user_id=user_id,
                task_id=task_id,
                current_streak=1,
                longest_streak=1,
                last_completion_date=completed_at.date()
            )
            self.db.add(streak)
        else:
            # Update existing streak
            last_date = streak.last_completion_date
            current_date = completed_at.date()
            
            if last_date and (current_date - last_date).days == 1:
                # Consecutive day - increment streak
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            elif last_date != current_date:
                # Reset streak if not consecutive (but not same day)
                streak.current_streak = 1
            
            streak.last_completion_date = current_date
        
        self.db.commit()
