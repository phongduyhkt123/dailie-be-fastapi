from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional
from datetime import datetime, date, timezone

from core.database import get_db
from statistics.models import UserTaskStreakModel
from tasks.models import TaskCompletionModel, TaskModel
from tasks.pydantics import TaskCompletionPdtModel, TaskCompletionPdtCreate, TaskCompletionPdtUpdate
from .pydantics import UserTaskStreakPdtModel, UserTaskStreakPdtCreate, UserTaskStreakPdtUpdate
from logging_config import monitor_endpoint_queries
from n_plus_one_detector import analyze_queries, monitor_n_plus_one

router = APIRouter(prefix="/statistics", tags=["statistics"])


# Task Completions
@router.post("/completions", response_model=TaskCompletionPdtModel)
def create_task_completion(completion: TaskCompletionPdtCreate, db: Session = Depends(get_db)):
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
    db_completion.created_at = datetime.now(timezone.utc)
    db_completion.updated_at = datetime.now(timezone.utc)
    
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    
    # Update streak after completion
    update_streak(completion.task_id, completion.user_id, completion.completion_date, db)
    
    return db_completion


@router.get("/completions", response_model=List[TaskCompletionPdtModel])
@monitor_n_plus_one("GET /completions - Task Completions List")
def get_task_completions(
    user_id: Optional[str] = None,
    task_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get task completions with optional filters - OPTIMIZED to prevent N+1"""
    # Use eager loading to prevent N+1 queries when accessing task details
    query = db.query(TaskCompletionModel).options(
        joinedload(TaskCompletionModel.task)  # Eager load task details
    )
    
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


@router.get("/completions/{completion_id}", response_model=TaskCompletionPdtModel)
def get_task_completion(completion_id: int, db: Session = Depends(get_db)):
    """Get a specific task completion by ID"""
    completion = db.query(TaskCompletionModel).filter(TaskCompletionModel.id == completion_id).first()
    if not completion:
        raise HTTPException(status_code=404, detail="Task completion not found")
    return completion


@router.put("/completions/{completion_id}", response_model=TaskCompletionPdtModel)
def update_task_completion(completion_id: int, completion_update: TaskCompletionPdtUpdate, db: Session = Depends(get_db)):
    """Update a task completion"""
    completion = db.query(TaskCompletionModel).filter(TaskCompletionModel.id == completion_id).first()
    if not completion:
        raise HTTPException(status_code=404, detail="Task completion not found")
    
    update_data = completion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(completion, field, value)
    
    completion.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(completion)
    return completion


@router.delete("/completions/{completion_id}")
def delete_task_completion(completion_id: int, db: Session = Depends(get_db)):
    """Delete a task completion"""
    completion = db.query(TaskCompletionModel).filter(TaskCompletionModel.id == completion_id).first()
    if not completion:
        raise HTTPException(status_code=404, detail="Task completion not found")
    
    db.delete(completion)
    db.commit()
    return {"message": "Task completion deleted successfully"}


@router.get("/completions/date-range", response_model=dict)
def get_completions_by_date_range(
    user_id: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get task completions grouped by date for a specific date range"""
    completions = db.query(TaskCompletionModel).filter(
        TaskCompletionModel.user_id == user_id,
        TaskCompletionModel.completion_date >= start_date,
        TaskCompletionModel.completion_date <= end_date
    ).all()
    
    # Group completions by date
    grouped_completions = {}
    for completion in completions:
        date_key = completion.completion_date.strftime("%Y-%m-%d")
        if date_key not in grouped_completions:
            grouped_completions[date_key] = []
        grouped_completions[date_key].append(completion)
    
    return grouped_completions


# User Task Streaks
@router.get("/streaks", response_model=List[UserTaskStreakPdtModel])
@monitor_n_plus_one("GET /streaks - User Task Streaks List")
def get_user_task_streaks(
    user_id: Optional[str] = None,
    task_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get user task streaks with optional filters - OPTIMIZED to prevent N+1"""
    # Use eager loading to prevent N+1 queries when accessing task/user details
    query = db.query(UserTaskStreakModel).options(
        joinedload(UserTaskStreakModel.task),
        joinedload(UserTaskStreakModel.user)
    )
    
    if user_id:
        query = query.filter(UserTaskStreakModel.user_id == user_id)
    if task_id:
        query = query.filter(UserTaskStreakModel.task_id == task_id)
    
    streaks = query.offset(skip).limit(limit).all()
    return streaks


@router.get("/streaks/{user_id}/{task_id}", response_model=UserTaskStreakPdtModel)
def get_user_task_streak(user_id: str, task_id: int, db: Session = Depends(get_db)):
    """Get streak for a specific user and task"""
    streak = db.query(UserTaskStreakModel).filter(
        UserTaskStreakModel.user_id == user_id,
        UserTaskStreakModel.task_id == task_id
    ).first()
    
    if not streak:
        raise HTTPException(status_code=404, detail="User task streak not found")
    return streak


@router.post("/streaks", response_model=UserTaskStreakPdtModel)
def create_user_task_streak(streak: UserTaskStreakPdtCreate, db: Session = Depends(get_db)):
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
    db_streak.created_at = datetime.now(timezone.utc)
    db_streak.updated_at = datetime.now(timezone.utc)
    
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
        streak.created_at = datetime.now(timezone.utc)
        streak.updated_at = datetime.now(timezone.utc)
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
        streak.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    return streak
