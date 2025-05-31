from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database.models import (
    Schedule as ScheduleModel,
    ScheduledTask as ScheduledTaskModel,
    Task as TaskModel
)
from .models import ScheduleCreate, ScheduleUpdate
from ..tasks.models import ScheduledTaskCreate, ScheduledTaskUpdate


class ScheduleService:
    def __init__(self, db: Session):
        self.db = db

    def create_schedule(self, schedule: ScheduleCreate) -> ScheduleModel:
        """Create a new schedule"""
        db_schedule = ScheduleModel(**schedule.dict())
        self.db.add(db_schedule)
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def get_schedules(self, skip: int = 0, limit: int = 100) -> List[ScheduleModel]:
        """Get all schedules with pagination"""
        return self.db.query(ScheduleModel).offset(skip).limit(limit).all()

    def get_schedule_by_id(self, schedule_id: int) -> Optional[ScheduleModel]:
        """Get a specific schedule by ID"""
        return self.db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()

    def update_schedule(self, schedule_id: int, schedule_update: ScheduleUpdate) -> Optional[ScheduleModel]:
        """Update a schedule"""
        schedule = self.get_schedule_by_id(schedule_id)
        if not schedule:
            return None
        
        update_data = schedule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule"""
        schedule = self.get_schedule_by_id(schedule_id)
        if not schedule:
            return False
        
        self.db.delete(schedule)
        self.db.commit()
        return True

    def create_scheduled_task(self, scheduled_task: ScheduledTaskCreate) -> Optional[ScheduledTaskModel]:
        """Create a new scheduled task"""
        # Check if task exists
        task = self.db.query(TaskModel).filter(TaskModel.id == scheduled_task.task_id).first()
        if not task:
            return None
        
        # Check if schedule exists
        schedule = self.get_schedule_by_id(scheduled_task.schedule_id)
        if not schedule:
            return None
        
        db_scheduled_task = ScheduledTaskModel(**scheduled_task.dict())
        self.db.add(db_scheduled_task)
        self.db.commit()
        self.db.refresh(db_scheduled_task)
        return db_scheduled_task

    def get_scheduled_tasks(
        self,
        task_id: Optional[int] = None,
        schedule_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ScheduledTaskModel]:
        """Get scheduled tasks with optional filters"""
        query = self.db.query(ScheduledTaskModel)
        
        if task_id:
            query = query.filter(ScheduledTaskModel.task_id == task_id)
        if schedule_id:
            query = query.filter(ScheduledTaskModel.schedule_id == schedule_id)
        
        return query.offset(skip).limit(limit).all()

    def get_scheduled_task_by_id(self, scheduled_task_id: int) -> Optional[ScheduledTaskModel]:
        """Get a specific scheduled task by ID"""
        return self.db.query(ScheduledTaskModel).filter(
            ScheduledTaskModel.id == scheduled_task_id
        ).first()

    def update_scheduled_task(
        self, 
        scheduled_task_id: int, 
        scheduled_task_update: ScheduledTaskUpdate
    ) -> Optional[ScheduledTaskModel]:
        """Update a scheduled task"""
        scheduled_task = self.get_scheduled_task_by_id(scheduled_task_id)
        if not scheduled_task:
            return None
        
        update_data = scheduled_task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scheduled_task, field, value)
        
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
