from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import datetime, timezone

from .pydantics import (
    TaskPdtCreate, 
    TaskPdtUpdate, 
    ScheduledTaskPdtCreate, 
    ScheduledTaskPdtUpdate,
    TaskBulkImportItem,
)
from .models.enums import TaskStatusEnum as TaskStatus
from tasks.models import TaskModel, ScheduledTaskModel


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task: TaskPdtCreate) -> TaskModel:
        """Create a new task definition"""
        db_task = TaskModel(
            title=task.title,
            type=task.type.value
        )
        db_task.created_at = datetime.now(timezone.utc)
        db_task.updated_at = datetime.now(timezone.utc)
        
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def bulk_import_tasks(self, tasks: List[TaskBulkImportItem]) -> Tuple[List[TaskModel], List[str], int, int, int]:
        """
        Bulk import tasks from a list
        Returns: (created_tasks, errors, created_count, updated_count, skipped_count)
        """
        created_tasks = []
        errors = []
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for task_item in tasks:
            try:
                # If ID is provided, try to update existing task
                if task_item.id is not None:
                    existing_task = self.get_task_by_id(task_item.id)
                    if existing_task:
                        # Update existing task
                        existing_task.title = task_item.title
                        if task_item.type:
                            existing_task.type = task_item.type.value
                        existing_task.updated_at = datetime.now(timezone.utc)
                        self.db.commit()
                        self.db.refresh(existing_task)
                        created_tasks.append(existing_task)
                        updated_count += 1
                        continue
                    else:
                        # ID provided but task doesn't exist, create with specific ID
                        db_task = TaskModel(
                            id=task_item.id,
                            title=task_item.title,
                            type=task_item.type.value if task_item.type else 'other'
                        )
                else:
                    # No ID provided, create new task with auto-increment
                    db_task = TaskModel(
                        title=task_item.title,
                        type=task_item.type.value if task_item.type else 'other'
                    )
                
                db_task.created_at = datetime.now(timezone.utc)
                db_task.updated_at = datetime.now(timezone.utc)
                
                self.db.add(db_task)
                self.db.commit()
                self.db.refresh(db_task)
                created_tasks.append(db_task)
                created_count += 1
                
            except Exception as e:
                # Skip this task and log error
                errors.append(f"Error processing task '{task_item.title}': {str(e)}")
                skipped_count += 1
                self.db.rollback()
        
        return created_tasks, errors, created_count, updated_count, skipped_count

    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskModel]:
        """Get all tasks with pagination"""
        return self.db.query(TaskModel).offset(skip).limit(limit).all()

    def get_task_by_id(self, task_id: int) -> Optional[TaskModel]:
        """Get a specific task by ID"""
        return self.db.query(TaskModel).filter(TaskModel.id == task_id).first()

    def update_task(self, task_id: int, task_update: TaskPdtUpdate) -> Optional[TaskModel]:
        """Update a task"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'type' and value:
                setattr(task, field, value.value)
            else:
                setattr(task, field, value)
        
        task.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        return True

    def create_scheduled_task(self, scheduled_task: ScheduledTaskPdtCreate) -> Optional[ScheduledTaskModel]:
        """Create a new scheduled task"""
        # Check if task exists
        task = self.get_task_by_id(scheduled_task.task_id)
        if not task:
            return None
        
        db_scheduled_task = ScheduledTaskModel(**scheduled_task.model_dump())
        self.db.add(db_scheduled_task)
        self.db.commit()
        self.db.refresh(db_scheduled_task)
        return db_scheduled_task

    def get_scheduled_tasks(
        self, 
        task_id: Optional[int] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ScheduledTaskModel]:
        """Get scheduled tasks with optional task filter"""
        query = self.db.query(ScheduledTaskModel)
        
        if task_id:
            query = query.filter(ScheduledTaskModel.task_id == task_id)
        
        return query.offset(skip).limit(limit).all()

    def get_scheduled_task_by_id(self, scheduled_task_id: int) -> Optional[ScheduledTaskModel]:
        """Get a specific scheduled task by ID"""
        return self.db.query(ScheduledTaskModel).filter(
            ScheduledTaskModel.id == scheduled_task_id
        ).first()

    def update_scheduled_task(
        self, 
        scheduled_task_id: int, 
        scheduled_task_update: ScheduledTaskPdtUpdate
    ) -> Optional[ScheduledTaskModel]:
        """Update a scheduled task"""
        scheduled_task = self.get_scheduled_task_by_id(scheduled_task_id)
        if not scheduled_task:
            return None
        
        update_data = scheduled_task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'status' and value:
                setattr(scheduled_task, field, value.value)
            else:
                setattr(scheduled_task, field, value)
        
        scheduled_task.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(scheduled_task)
        return scheduled_task

    def delete_scheduled_task(self, scheduled_task_id: int) -> bool:
        """Delete a scheduled task"""
        scheduled_task = self.get_scheduled_task_by_id(scheduled_task_id)
        if not scheduled_task:
            return False
        
        self.db.delete(scheduled_task)
        self.db.commit()
        return True

    def complete_scheduled_task(self, scheduled_task_id: int, note: Optional[str] = None) -> Optional[ScheduledTaskModel]:
        """Mark a scheduled task as complete"""
        scheduled_task = self.get_scheduled_task_by_id(scheduled_task_id)
        if not scheduled_task:
            return None
        
        scheduled_task.status = TaskStatus.COMPLETE.value
        scheduled_task.completed_at = datetime.now(timezone.utc)
        if note:
            scheduled_task.note = note
        
        scheduled_task.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(scheduled_task)
        return scheduled_task
