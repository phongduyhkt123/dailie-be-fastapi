from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import os

from ...core.database import get_db
from ...core.database.models import User
from ..config import get_current_admin_user, ADMIN_CONFIG
from ..shared.models import AdminUserResponse

# Create router
router = APIRouter(prefix="/admin/users", tags=["admin-users"])

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """List all users"""
    offset = (page - 1) * limit
    users = db.query(User).offset(offset).limit(limit).all()
    total_users = db.query(User).count()
    total_pages = (total_users + limit - 1) // limit
    
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": [AdminUserResponse.from_attributes(user) for user in users],
            "current_page": page,
            "total_pages": total_pages,
            "config": ADMIN_CONFIG
        }
    )


@router.get("/api", response_model=List[AdminUserResponse])
async def get_users_api(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_admin_user)
):
    """API endpoint to get users data"""
    offset = (page - 1) * limit
    users = db.query(User).offset(offset).limit(limit).all()
    return [AdminUserResponse.from_attributes(user) for user in users]
