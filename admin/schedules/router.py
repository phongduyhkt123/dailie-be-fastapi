from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from schedules.models import ScheduleModel
from admin.config import get_current_admin_user, ADMIN_CONFIG
from admin.shared.models import AdminScheduleResponse
from admin.shared.templates_config import admin_templates

# Create router
router = APIRouter(prefix="/admin/schedules", tags=["admin-schedules"])


@router.get("", response_class=HTMLResponse)
async def admin_schedules(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """List all schedules"""
    offset = (page - 1) * limit
    schedules = db.query(ScheduleModel).offset(offset).limit(limit).all()
    total_schedules = db.query(ScheduleModel).count()
    total_pages = (total_schedules + limit - 1) // limit
    
    return admin_templates.TemplateResponse(
        "schedules.html",
        {
            "request": request,
            "schedules": [AdminScheduleResponse.from_attributes(schedule) for schedule in schedules],
            "current_page": page,
            "total_pages": total_pages,
            "config": ADMIN_CONFIG
        }
    )


@router.get("/api", response_model=List[AdminScheduleResponse])
async def get_schedules_api(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """API endpoint to get schedules data"""
    offset = (page - 1) * limit
    schedules = db.query(ScheduleModel).offset(offset).limit(limit).all()
    return [AdminScheduleResponse.from_attributes(schedule) for schedule in schedules]
