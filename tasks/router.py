from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from . import pydantics as pydantic_models
from .service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Task definition endpoints
@router.post("/", response_model=pydantic_models.TaskPdtModel)
def create_task(task: pydantic_models.TaskPdtCreate, db: Session = Depends(get_db)):
    """Create a new task definition"""
    service = TaskService(db)
    return service.create_task(task)


@router.get("/", response_model=List[pydantic_models.TaskPdtModel])
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all task definitions"""
    service = TaskService(db)
    return service.get_tasks(skip=skip, limit=limit)


@router.get("/{task_id}", response_model=pydantic_models.TaskPdtModel)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task definition"""
    service = TaskService(db)
    task = service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=pydantic_models.TaskPdtModel)
def update_task(task_id: int, task_update: pydantic_models.TaskPdtUpdate, db: Session = Depends(get_db)):
    """Update a task definition"""
    service = TaskService(db)
    task = service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task definition"""
    service = TaskService(db)
    success = service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# Scheduled task endpoints
@router.post("/scheduled", response_model=pydantic_models.ScheduledTaskPdtModel)
def create_scheduled_task(scheduled_task: pydantic_models.ScheduledTaskPdtCreate, db: Session = Depends(get_db)):
    """Create a new scheduled task"""
    service = TaskService(db)
    result = service.create_scheduled_task(scheduled_task)
    if not result:
        raise HTTPException(status_code=400, detail="Could not create scheduled task")
    return result


@router.get("/scheduled", response_model=List[pydantic_models.ScheduledTaskPdtModel])
def get_scheduled_tasks(
    task_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get scheduled tasks"""
    service = TaskService(db)
    return service.get_scheduled_tasks(task_id=task_id, skip=skip, limit=limit)


@router.get("/scheduled/{scheduled_task_id}", response_model=pydantic_models.ScheduledTaskPdtModel)
def get_scheduled_task(scheduled_task_id: int, db: Session = Depends(get_db)):
    """Get a specific scheduled task"""
    service = TaskService(db)
    scheduled_task = service.get_scheduled_task_by_id(scheduled_task_id)
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    return scheduled_task


@router.put("/scheduled/{scheduled_task_id}", response_model=pydantic_models.ScheduledTaskPdtModel)
def update_scheduled_task(
    scheduled_task_id: int,
    scheduled_task_update: pydantic_models.ScheduledTaskPdtUpdate,
    db: Session = Depends(get_db)
):
    """Update a scheduled task"""
    service = TaskService(db)
    scheduled_task = service.update_scheduled_task(scheduled_task_id, scheduled_task_update)
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    return scheduled_task


@router.delete("/scheduled/{scheduled_task_id}")
def delete_scheduled_task(scheduled_task_id: int, db: Session = Depends(get_db)):
    """Delete a scheduled task"""
    service = TaskService(db)
    success = service.delete_scheduled_task(scheduled_task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    return {"message": "Scheduled task deleted successfully"}