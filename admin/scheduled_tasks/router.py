from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from tasks.models import ScheduledTaskModel
from admin.config import get_current_admin_user, ADMIN_CONFIG
from admin.shared.models import AdminScheduledTaskResponse
from admin.shared.templates_config import admin_templates

# Create router
router = APIRouter(prefix="/admin/scheduled-tasks", tags=["admin-scheduled-tasks"])


@router.get("", response_class=HTMLResponse)
async def admin_scheduled_tasks(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """List all scheduled tasks"""
    offset = (page - 1) * limit
    scheduled_tasks = db.query(ScheduledTaskModel).offset(offset).limit(limit).all()
    total_scheduled_tasks = db.query(ScheduledTaskModel).count()
    total_pages = (total_scheduled_tasks + limit - 1) // limit
    
    return admin_templates.TemplateResponse(
        "scheduled_tasks.html",
        {
            "request": request,
            "scheduled_tasks": [AdminScheduledTaskResponse.from_attributes(st) for st in scheduled_tasks],
            "current_page": page,
            "total_pages": total_pages,
            "config": ADMIN_CONFIG
        }
    )


@router.get("/api", response_model=List[AdminScheduledTaskResponse])
async def get_scheduled_tasks_api(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """API endpoint to get scheduled tasks data"""
    offset = (page - 1) * limit
    scheduled_tasks = db.query(ScheduledTaskModel).offset(offset).limit(limit).all()
    return [AdminScheduledTaskResponse.from_attributes(st) for st in scheduled_tasks]
