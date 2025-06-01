from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from schedules.models import ScheduleModel
from tasks.models import ScheduledTaskModel, TaskModel
from schedules.pydantics import SchedulePdtModel, SchedulePdtCreate, SchedulePdtUpdate 
from tasks.pydantics import ScheduledTaskPdtModel, ScheduledTaskPdtCreate, ScheduledTaskPdtUpdate
from auth.router import get_current_authenticated_user
from users.models import UserModel

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


@router.get("/by-date", response_model=SchedulePdtModel)
def get_schedule_by_date(date: str, db: Session = Depends(get_db)):
    """Get schedule by specific date (YYYY-MM-DD format)"""
    schedule = db.query(ScheduleModel).filter(ScheduleModel.date == date).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this date")
    return schedule


@router.get("/by-date-and-user", response_model=SchedulePdtModel)
def get_schedule_by_date_and_user(date: str, user_id: str, db: Session = Depends(get_db)):
    """Get schedule by date and user"""
    schedule = db.query(ScheduleModel).filter(
        ScheduleModel.date == date,
        ScheduleModel.user_id == user_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this date and user")
    return schedule


@router.get("/by-user/{user_id}", response_model=List[SchedulePdtModel])
def get_schedules_by_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all schedules for a specific user"""
    schedules = db.query(ScheduleModel).filter(
        ScheduleModel.user_id == user_id
    ).offset(skip).limit(limit).all()
    return schedules


@router.get("/export")
def export_schedules_to_json(
    current_user: UserModel = Depends(get_current_authenticated_user),
    db: Session = Depends(get_db)
):
    """Export schedules to JSON format for the current authenticated user"""
    query = db.query(ScheduleModel).filter(ScheduleModel.user_id == current_user.id)
    
    schedules = query.all()
    
    export_data = []
    for schedule in schedules:
        # Get scheduled tasks for this schedule
        scheduled_tasks = db.query(ScheduledTaskModel).filter(
            ScheduledTaskModel.schedule_id == schedule.id
        ).all()
        
        schedule_data = {
            "date": schedule.date.isoformat() if schedule.date else None,
            "user_id": schedule.user_id,
            "tasks": [
                {
                    "task_id": st.task_id,
                    "status": st.status,
                    "priority": st.priority,
                    "note": st.note
                }
                for st in scheduled_tasks
            ]
        }
        export_data.append(schedule_data)
    
    return {"schedules": export_data}


@router.post("/import")
def import_schedules_from_json(import_data: dict, db: Session = Depends(get_db)):
    """Import schedules from JSON format"""
    try:
        schedules_data = import_data.get("schedules", [])
        imported_count = 0
        
        for schedule_data in schedules_data:
            # Create or update schedule
            existing_schedule = db.query(ScheduleModel).filter(
                ScheduleModel.date == schedule_data["date"],
                ScheduleModel.user_id == schedule_data["user_id"]
            ).first()
            
            if not existing_schedule:
                new_schedule = ScheduleModel(
                    date=schedule_data["date"],
                    user_id=schedule_data["user_id"]
                )
                db.add(new_schedule)
                db.flush()
                schedule_id = new_schedule.id
            else:
                schedule_id = existing_schedule.id
            
            # Import scheduled tasks
            for task_data in schedule_data.get("tasks", []):
                existing_task = db.query(ScheduledTaskModel).filter(
                    ScheduledTaskModel.schedule_id == schedule_id,
                    ScheduledTaskModel.task_id == task_data["task_id"]
                ).first()
                
                if not existing_task:
                    new_scheduled_task = ScheduledTaskModel(
                        schedule_id=schedule_id,
                        task_id=task_data["task_id"],
                        status=task_data.get("status", "pending"),
                        priority=task_data.get("priority", 0),
                        note=task_data.get("note")
                    )
                    db.add(new_scheduled_task)
            
            imported_count += 1
        
        db.commit()
        return {"message": f"Successfully imported {imported_count} schedules"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


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


@router.get("/tasks/by-date", response_model=List[ScheduledTaskPdtModel])
def get_scheduled_tasks_by_date(date: str, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get scheduled tasks by specific date"""
    # First find the schedule for the given date
    query = db.query(ScheduleModel).filter(ScheduleModel.date == date)
    if user_id:
        query = query.filter(ScheduleModel.user_id == user_id)
    
    schedule = query.first()
    if not schedule:
        return []
    
    # Get scheduled tasks for this schedule
    scheduled_tasks = db.query(ScheduledTaskModel).filter(
        ScheduledTaskModel.schedule_id == schedule.id
    ).all()
    
    return scheduled_tasks


@router.get("/tasks/with-relationships", response_model=List[dict])
def get_scheduled_tasks_with_relationships(
    date: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get scheduled tasks with task and schedule details populated"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(ScheduledTaskModel).options(
        joinedload(ScheduledTaskModel.task),
        joinedload(ScheduledTaskModel.schedule)
    )
    
    if date or user_id:
        # Join with schedule table to filter by date/user
        query = query.join(ScheduleModel)
        if date:
            query = query.filter(ScheduleModel.date == date)
        if user_id:
            query = query.filter(ScheduleModel.user_id == user_id)
    
    scheduled_tasks = query.offset(skip).limit(limit).all()
    
    # Format response with relationships
    result = []
    for st in scheduled_tasks:
        task_data = {
            "id": st.id,
            "task_id": st.task_id,
            "schedule_id": st.schedule_id,
            "status": st.status,
            "priority": st.priority,
            "note": st.note,
            "task": {
                "id": st.task.id,
                "title": st.task.title,
                "description": st.task.description,
                "category": st.task.category
            } if st.task else None,
            "schedule": {
                "id": st.schedule.id,
                "date": st.schedule.date.isoformat() if st.schedule.date else None,
                "user_id": st.schedule.user_id
            } if st.schedule else None
        }
        result.append(task_data)
    
    return result


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
