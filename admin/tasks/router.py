from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from tasks.models import TaskModel
from admin.config import get_current_admin_user, ADMIN_CONFIG
from admin.shared.models import AdminTaskResponse
from admin.shared.templates_config import admin_templates

# Create router
router = APIRouter(prefix="/admin/tasks", tags=["admin-tasks"])


@router.get("", response_class=HTMLResponse)
async def admin_tasks(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """List all tasks"""
    offset = (page - 1) * limit
    tasks = db.query(TaskModel).offset(offset).limit(limit).all()
    total_tasks = db.query(TaskModel).count()
    total_pages = (total_tasks + limit - 1) // limit
    
    return admin_templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": [AdminTaskResponse.from_attributes(task) for task in tasks],
            "current_page": page,
            "total_pages": total_pages,
            "config": ADMIN_CONFIG
        }
    )


@router.get("/api", response_model=List[AdminTaskResponse])
async def get_tasks_api(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """API endpoint to get tasks data"""
    offset = (page - 1) * limit
    tasks = db.query(TaskModel).offset(offset).limit(limit).all()
    return [AdminTaskResponse.from_attributes(task) for task in tasks]
