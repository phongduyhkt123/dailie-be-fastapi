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


@router.post("/bulk", response_model=pydantic_models.TaskBulkImportResponse)
def bulk_import_tasks(
    bulk_request: pydantic_models.TaskBulkImportRequest, 
    db: Session = Depends(get_db)
):
    """Bulk import tasks from JSON data"""
    service = TaskService(db)
    
    try:
        tasks, errors, created_count, updated_count, skipped_count = service.bulk_import_tasks(
            bulk_request.tasks
        )
        
        return pydantic_models.TaskBulkImportResponse(
            success=len(errors) == 0,
            created_count=created_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            tasks=[pydantic_models.TaskPdtModel.model_validate(task) for task in tasks],
            errors=errors
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bulk import failed: {str(e)}")


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


@router.post("/export")
def export_tasks_to_json(db: Session = Depends(get_db)):
    """Export all tasks to JSON format"""
    service = TaskService(db)
    tasks = service.get_tasks()
    
    export_data = []
    for task in tasks:
        task_data = {
            "title": task.title,
            "description": task.description,
            "category": task.category,
            "difficulty": task.difficulty,
            "estimated_duration": task.estimated_duration,
            "tags": task.tags,
            "is_template": task.is_template
        }
        export_data.append(task_data)
    
    return {"tasks": export_data}


@router.post("/import")
def import_tasks_from_json(import_data: dict, db: Session = Depends(get_db)):
    """Import tasks from JSON format"""
    try:
        tasks_data = import_data.get("tasks", [])
        service = TaskService(db)
        imported_count = 0
        
        for task_data in tasks_data:
            # Check if task already exists by title
            from .models import TaskModel
            existing_task = db.query(TaskModel).filter(
                TaskModel.title == task_data["title"]
            ).first()
            
            if not existing_task:
                from tasks.pydantics import TaskPdtCreate
                task_create = TaskPdtCreate(**task_data)
                service.create_task(task_create)
                imported_count += 1
        
        return {"message": f"Successfully imported {imported_count} tasks"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


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