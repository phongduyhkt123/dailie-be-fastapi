from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from schedules.models import ScheduleModel
from tasks.models import ScheduledTaskModel, TaskModel
from schedules.pydantics import SchedulePdtModel, SchedulePdtCreate, SchedulePdtUpdate 
from tasks.pydantics import ScheduledTaskPdtModel, ScheduledTaskPdtCreate, ScheduledTaskPdtUpdate

router = APIRouter(prefix="/schedules", tags=["schedules"])


# Schedule endpoints
@router.post("/", response_model=SchedulePdtModel)
def create_schedule(schedule: SchedulePdtCreate, db: Session = Depends(get_db)):
    """Create a new schedule"""
    db_schedule = ScheduleModel(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/", response_model=List[SchedulePdtModel])
def get_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all schedules"""
    schedules = db.query(ScheduleModel).offset(skip).limit(limit).all()
    return schedules


@router.get("/{schedule_id}", response_model=SchedulePdtModel)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Get a specific schedule by ID"""
    schedule = db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/{schedule_id}", response_model=SchedulePdtModel)
def update_schedule(
    schedule_id: int, 
    schedule_update: SchedulePdtUpdate, 
    db: Session = Depends(get_db)
):
    """Update a schedule"""
    schedule = db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Delete a schedule"""
    schedule = db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}


# Scheduled Task endpoints
@router.post("/tasks", response_model=ScheduledTaskPdtModel)
def create_scheduled_task(scheduled_task: ScheduledTaskPdtCreate, db: Session = Depends(get_db)):
    """Create a new scheduled task"""
    # Check if task exists
    task = db.query(TaskModel).filter(TaskModel.id == scheduled_task.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if schedule exists
    schedule = db.query(ScheduleModel).filter(ScheduleModel.id == scheduled_task.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db_scheduled_task = ScheduledTaskModel(**scheduled_task.model_dump())
    db.add(db_scheduled_task)
    db.commit()
    db.refresh(db_scheduled_task)
    return db_scheduled_task


@router.get("/tasks", response_model=List[ScheduledTaskPdtModel])
def get_scheduled_tasks(
    task_id: Optional[int] = None,
    schedule_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get scheduled tasks with optional filters"""
    query = db.query(ScheduledTaskModel)
    
    if task_id:
        query = query.filter(ScheduledTaskModel.task_id == task_id)
    if schedule_id:
        query = query.filter(ScheduledTaskModel.schedule_id == schedule_id)
    
    scheduled_tasks = query.offset(skip).limit(limit).all()
    return scheduled_tasks


@router.get("/tasks/{scheduled_task_id}", response_model=ScheduledTaskPdtModel)
def get_scheduled_task(scheduled_task_id: int, db: Session = Depends(get_db)):
    """Get a specific scheduled task by ID"""
    scheduled_task = db.query(ScheduledTaskModel).filter(
        ScheduledTaskModel.id == scheduled_task_id
    ).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    return scheduled_task


@router.put("/tasks/{scheduled_task_id}", response_model=ScheduledTaskPdtModel)
def update_scheduled_task(
    scheduled_task_id: int,
    scheduled_task_update: ScheduledTaskPdtUpdate,
    db: Session = Depends(get_db)
):
    """Update a scheduled task"""
    scheduled_task = db.query(ScheduledTaskModel).filter(
        ScheduledTaskModel.id == scheduled_task_id
    ).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    
    update_data = scheduled_task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scheduled_task, field, value)
    
    db.commit()
    db.refresh(scheduled_task)
    return scheduled_task


@router.delete("/tasks/{scheduled_task_id}")
def delete_scheduled_task(scheduled_task_id: int, db: Session = Depends(get_db)):
    """Delete a scheduled task"""
    scheduled_task = db.query(ScheduledTaskModel).filter(
        ScheduledTaskModel.id == scheduled_task_id
    ).first()
    if not scheduled_task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    
    db.delete(scheduled_task)
    db.commit()
    return {"message": "Scheduled task deleted successfully"}
