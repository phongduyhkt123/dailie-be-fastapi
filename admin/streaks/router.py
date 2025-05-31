from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from core.database import get_db
from statistics.models import UserTaskStreakModel
from admin.config import get_current_admin_user, ADMIN_CONFIG
from admin.shared.models import AdminUserTaskStreakResponse
from admin.shared.templates_config import admin_templates

# Create router
router = APIRouter(prefix="/admin/streaks", tags=["admin-streaks"])


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
    streaks = db.query(UserTaskStreakModel)\
        .order_by(desc(UserTaskStreakModel.current_streak))\
        .offset(offset)\
        .limit(limit)\
        .all()
    total_streaks = db.query(UserTaskStreakModel).count()
    total_pages = (total_streaks + limit - 1) // limit
    
    return admin_templates.TemplateResponse(
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
    streaks = db.query(UserTaskStreakModel)\
        .order_by(desc(UserTaskStreakModel.current_streak))\
        .offset(offset)\
        .limit(limit)\
        .all()
    return [AdminUserTaskStreakResponse.from_attributes(streak) for streak in streaks]
