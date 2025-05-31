from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import os

from core.database import get_db
from tasks.models import TaskCompletionModel
from admin.config import get_current_admin_user, ADMIN_CONFIG
from admin.shared.models import AdminTaskCompletionResponse

# Create router
router = APIRouter(prefix="/admin/completions", tags=["admin-completions"])

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("", response_class=HTMLResponse)
async def admin_completions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """List all task completions"""
    offset = (page - 1) * limit
    completions = db.query(TaskCompletionModel)\
        .order_by(desc(TaskCompletionModel.completion_date))\
        .offset(offset)\
        .limit(limit)\
        .all()
    total_completions = db.query(TaskCompletionModel).count()
    total_pages = (total_completions + limit - 1) // limit
    
    return templates.TemplateResponse(
        "completions.html",
        {
            "request": request,
            "completions": [AdminTaskCompletionResponse.from_attributes(comp) for comp in completions],
            "current_page": page,
            "total_pages": total_pages,
            "config": ADMIN_CONFIG
        }
    )


@router.get("/api", response_model=List[AdminTaskCompletionResponse])
async def get_completions_api(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """API endpoint to get completions data"""
    offset = (page - 1) * limit
    completions = db.query(TaskCompletionModel)\
        .order_by(desc(TaskCompletionModel.completion_date))\
        .offset(offset)\
        .limit(limit)\
        .all()
    return [AdminTaskCompletionResponse.from_attributes(comp) for comp in completions]
