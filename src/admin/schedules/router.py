from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import os

from ...core.database import get_db
from ...core.database.models import Schedule
from ..config import get_current_admin_user, ADMIN_CONFIG
from ..shared.models import AdminScheduleResponse

# Create router
router = APIRouter(prefix="/admin/schedules", tags=["admin-schedules"])

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


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
    schedules = db.query(Schedule).offset(offset).limit(limit).all()
    total_schedules = db.query(Schedule).count()
    total_pages = (total_schedules + limit - 1) // limit
    
    return templates.TemplateResponse(
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
    schedules = db.query(Schedule).offset(offset).limit(limit).all()
    return [AdminScheduleResponse.from_attributes(schedule) for schedule in schedules]
