from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..core.database import get_db
from ..core.database.models import (
    TaskCompletion as TaskCompletionModel,
    UserTaskStreak as UserTaskStreakModel,
    Task as TaskModel
)
from ..tasks.models import TaskCompletion, TaskCompletionCreate, TaskCompletionUpdate
from .models import UserTaskStreak, UserTaskStreakCreate, UserTaskStreakUpdate

router = APIRouter(prefix="/statistics", tags=["statistics"])


# Task Completions
@router.post("/completions", response_model=TaskCompletion)
def create_task_completion(completion: TaskCompletionCreate, db: Session = Depends(get_db)):
    """Create a new task completion"""
    # Check if task exists
    task = db.query(TaskModel).filter(TaskModel.id == completion.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_completion = TaskCompletionModel(
        task_id=completion.task_id,
        user_id=completion.user_id,
        completion_date=completion.completion_date,
        note=completion.note
    )
    db_completion.created_at = datetime.utcnow()
    db_completion.updated_at = datetime.utcnow()
    
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    
    # Update streak after completion
    update_streak(completion.task_id, completion.user_id, completion.completion_date, db)
    
    return db_completion


@router.get("/completions", response_model=List[TaskCompletion])
def get_task_completions(
    user_id: Optional[str] = None,
    task_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get task completions with optional filters"""
    query = db.query(TaskCompletionModel)
    
    if user_id:
        query = query.filter(TaskCompletionModel.user_id == user_id)
    if task_id:
        query = query.filter(TaskCompletionModel.task_id == task_id)
    if start_date:
        query = query.filter(TaskCompletionModel.completion_date >= start_date)
    if end_date:
        query = query.filter(TaskCompletionModel.completion_date <= end_date)
    
    completions = query.offset(skip).limit(limit).all()
    return completions


@router.get("/completions/{completion_id}", response_model=TaskCompletion)
def get_task_completion(completion_id: int, db: Session = Depends(get_db)):
    """Get a specific task completion by ID"""
    completion = db.query(TaskCompletionModel).filter(TaskCompletionModel.id == completion_id).first()
    if not completion:
        raise HTTPException(status_code=404, detail="Task completion not found")
    return completion


# User Task Streaks
@router.get("/streaks", response_model=List[UserTaskStreak])
def get_user_task_streaks(
    user_id: Optional[str] = None,
    task_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user task streaks with optional filters"""
    query = db.query(UserTaskStreakModel)
    
    if user_id:
        query = query.filter(UserTaskStreakModel.user_id == user_id)
    if task_id:
        query = query.filter(UserTaskStreakModel.task_id == task_id)
    
    streaks = query.offset(skip).limit(limit).all()
    return streaks


@router.get("/streaks/{user_id}/{task_id}", response_model=UserTaskStreak)
def get_user_task_streak(user_id: str, task_id: int, db: Session = Depends(get_db)):
    """Get streak for a specific user and task"""
    streak = db.query(UserTaskStreakModel).filter(
        UserTaskStreakModel.user_id == user_id,
        UserTaskStreakModel.task_id == task_id
    ).first()
    
    if not streak:
        raise HTTPException(status_code=404, detail="User task streak not found")
    return streak


@router.post("/streaks", response_model=UserTaskStreak)
def create_user_task_streak(streak: UserTaskStreakCreate, db: Session = Depends(get_db)):
    """Create a new user task streak"""
    # Check if streak already exists
    existing_streak = db.query(UserTaskStreakModel).filter(
        UserTaskStreakModel.user_id == streak.user_id,
        UserTaskStreakModel.task_id == streak.task_id
    ).first()
    
    if existing_streak:
        raise HTTPException(status_code=400, detail="Streak already exists for this user and task")
    
    db_streak = UserTaskStreakModel(
        task_id=streak.task_id,
        user_id=streak.user_id,
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        last_completed_date=streak.last_completed_date,
        streak_start_date=streak.streak_start_date
    )
    db_streak.created_at = datetime.utcnow()
    db_streak.updated_at = datetime.utcnow()
    
    db.add(db_streak)
    db.commit()
    db.refresh(db_streak)
    return db_streak


def update_streak(task_id: int, user_id: str, completion_date: datetime, db: Session):
    """Update user task streak after completion"""
    streak = db.query(UserTaskStreakModel).filter(
        UserTaskStreakModel.user_id == user_id,
        UserTaskStreakModel.task_id == task_id
    ).first()
    
    if not streak:
        # Create new streak
        streak = UserTaskStreakModel(
            task_id=task_id,
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_completed_date=completion_date,
            streak_start_date=completion_date
        )
        streak.created_at = datetime.utcnow()
        streak.updated_at = datetime.utcnow()
        db.add(streak)
    else:
        # Update existing streak
        if streak.last_completed_date:
            # Check if completion is consecutive
            days_diff = (completion_date.date() - streak.last_completed_date.date()).days
            if days_diff == 1:
                # Consecutive day - increment streak
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            elif days_diff > 1:
                # Gap in streak - reset
                streak.current_streak = 1
                streak.streak_start_date = completion_date
        else:
            # First completion
            streak.current_streak = 1
            streak.longest_streak = 1
            streak.streak_start_date = completion_date
        
        streak.last_completed_date = completion_date
        streak.updated_at = datetime.utcnow()
    
    db.commit()
    return streak
