from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import os

from ...core.database import get_db
from ...core.database.models import UserTaskStreak
from ..config import get_current_admin_user, ADMIN_CONFIG
from ..shared.models import AdminUserTaskStreakResponse

# Create router
router = APIRouter(prefix="/admin/streaks", tags=["admin-streaks"])

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("", response_class=HTMLResponse)
async def admin_streaks(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """List all user task streaks"""
    offset = (page - 1) * limit
    streaks = db.query(UserTaskStreak)\
        .order_by(desc(UserTaskStreak.current_streak))\
        .offset(offset)\
        .limit(limit)\
        .all()
    total_streaks = db.query(UserTaskStreak).count()
    total_pages = (total_streaks + limit - 1) // limit
    
    return templates.TemplateResponse(
        "streaks.html",
        {
            "request": request,
            "streaks": [AdminUserTaskStreakResponse.from_attributes(streak) for streak in streaks],
            "current_page": page,
            "total_pages": total_pages,
            "config": ADMIN_CONFIG
        }
    )


@router.get("/api", response_model=List[AdminUserTaskStreakResponse])
async def get_streaks_api(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """API endpoint to get streaks data"""
    offset = (page - 1) * limit
    streaks = db.query(UserTaskStreak)\
        .order_by(desc(UserTaskStreak.current_streak))\
        .offset(offset)\
        .limit(limit)\
        .all()
    return [AdminUserTaskStreakResponse.from_attributes(streak) for streak in streaks]
