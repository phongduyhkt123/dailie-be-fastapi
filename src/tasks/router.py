from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..core.database import get_db
from .models import (
    Task, TaskCreate, TaskUpdate,
    ScheduledTask, ScheduledTaskCreate, ScheduledTaskUpdate
)
from .service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


@router.post("/", response_model=Task)
def create_task(task: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    """Create a new task definition"""
    return task_service.create_task(task)


@router.get("/", response_model=List[Task])
def get_tasks(
    skip: int = 0, 
    limit: int = 100, 
    task_service: TaskService = Depends(get_task_service)
):
    """Get all tasks with pagination"""
    return task_service.get_tasks(skip=skip, limit=limit)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Get a specific task by ID"""
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    task_service: TaskService = Depends(get_task_service)
):
    """Update a task"""
    task = task_service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Delete a task"""
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# Scheduled Task endpoints
@router.post("/scheduled", response_model=ScheduledTask)
def create_scheduled_task(
    scheduled_task: ScheduledTaskCreate, 
    task_service: TaskService = Depends(get_task_service)
):
    """Create a new scheduled task"""
    result = task_service.create_scheduled_task(scheduled_task)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.get("/scheduled", response_model=List[ScheduledTask])
def get_scheduled_tasks(
    task_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    task_service: TaskService = Depends(get_task_service)
):
    """Get scheduled tasks with optional task filter"""
    return task_service.get_scheduled_tasks(task_id=task_id, skip=skip, limit=limit)


@router.get("/", response_model=List[Task])
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all task definitions"""
    tasks = db.query(TaskModel).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task definition"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.type is not None:
        task.type = task_update.type.value
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task definition"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


# Scheduled Tasks endpoints
@router.post("/scheduled", response_model=ScheduledTask)
def create_scheduled_task(scheduled_task: ScheduledTaskCreate, db: Session = Depends(get_db)):
    """Create a new scheduled task"""
    # Check if task exists
    task = db.query(TaskModel).filter(TaskModel.id == scheduled_task.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_scheduled_task = ScheduledTaskModel(
        task_id=scheduled_task.task_id,
        schedule_id=scheduled_task.schedule_id,
        date=scheduled_task.date,
        status=scheduled_task.status.value,
        priority=scheduled_task.priority,
        note=scheduled_task.note,
        completed_at=scheduled_task.completed_at
    )
    db_scheduled_task.created_at = datetime.utcnow()
    db_scheduled_task.updated_at = datetime.utcnow()
    
    db.add(db_scheduled_task)
    db.commit()
    db.refresh(db_scheduled_task)
    return db_scheduled_task


@router.get("/scheduled", response_model=List[ScheduledTask])
def get_scheduled_tasks(
    date_filter: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get scheduled tasks, optionally filtered by date"""
    query = db.query(ScheduledTaskModel)
    
    if date_filter:
        query = query.filter(ScheduledTaskModel.date >= date_filter)
        query = query.filter(ScheduledTaskModel.date < datetime.combine(date_filter, datetime.min.time().replace(hour=23, minute=59, second=59)))
    
    scheduled_tasks = query.offset(skip).limit(limit).all()
    return scheduled_tasks


@router.get("/scheduled/{scheduled_task_id}", response_model=ScheduledTask)
def get_scheduled_task(scheduled_task_id: int, db: Session = Depends(get_db)):
    """Get a specific scheduled task by ID"""
    scheduled_task = db.query(ScheduledTaskModel).filter(ScheduledTaskModel.id == scheduled_task_id).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    return scheduled_task


@router.put("/scheduled/{scheduled_task_id}", response_model=ScheduledTask)
def update_scheduled_task(
    scheduled_task_id: int, 
    scheduled_task_update: ScheduledTaskUpdate, 
    db: Session = Depends(get_db)
):
    """Update a scheduled task"""
    scheduled_task = db.query(ScheduledTaskModel).filter(ScheduledTaskModel.id == scheduled_task_id).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    
    if scheduled_task_update.status is not None:
        scheduled_task.status = scheduled_task_update.status.value
    if scheduled_task_update.priority is not None:
        scheduled_task.priority = scheduled_task_update.priority
    if scheduled_task_update.note is not None:
        scheduled_task.note = scheduled_task_update.note
    if scheduled_task_update.completed_at is not None:
        scheduled_task.completed_at = scheduled_task_update.completed_at
    
    scheduled_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scheduled_task)
    return scheduled_task


@router.delete("/scheduled/{scheduled_task_id}")
def delete_scheduled_task(scheduled_task_id: int, db: Session = Depends(get_db)):
    """Delete a scheduled task"""
    scheduled_task = db.query(ScheduledTaskModel).filter(ScheduledTaskModel.id == scheduled_task_id).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    
    db.delete(scheduled_task)
    db.commit()
    return {"message": "Scheduled task deleted successfully"}


@router.post("/scheduled/{scheduled_task_id}/complete")
def complete_task(scheduled_task_id: int, note: Optional[str] = None, db: Session = Depends(get_db)):
    """Mark a scheduled task as complete"""
    scheduled_task = db.query(ScheduledTaskModel).filter(ScheduledTaskModel.id == scheduled_task_id).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    
    scheduled_task.status = TaskStatus.COMPLETE.value
    scheduled_task.completed_at = datetime.utcnow()
    if note:
        scheduled_task.note = note
    
    scheduled_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scheduled_task)
    
    return {"message": "Task completed successfully", "task": scheduled_task}
