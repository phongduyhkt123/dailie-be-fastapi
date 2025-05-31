from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
import os

from ...core.database import get_db
from ...core.database.models import User, Task, TaskCompletion, UserTaskStreak
from ..config import get_current_admin_user, ADMIN_CONFIG
from ..shared.models import AdminDashboardStats, AdminTaskCompletionResponse

# Create router
router = APIRouter(prefix="/admin", tags=["admin-dashboard"])

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """Admin dashboard with statistics"""
    
    # Get statistics
    total_users = db.query(User).count()
    total_tasks = db.query(Task).count()
    total_completions = db.query(TaskCompletion).count()
    active_streaks = db.query(UserTaskStreak).filter(UserTaskStreak.current_streak > 0).count()
    
    # Get recent completions
    recent_completions = db.query(TaskCompletion)\
        .order_by(desc(TaskCompletion.completion_date))\
        .limit(5)\
        .all()
    
    stats = AdminDashboardStats(
        total_users=total_users,
        total_tasks=total_tasks,
        total_completions=total_completions,
        active_streaks=active_streaks,
        recent_completions=[AdminTaskCompletionResponse.from_attributes(comp) for comp in recent_completions]
    )
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": stats,
            "config": ADMIN_CONFIG
        }
    )
