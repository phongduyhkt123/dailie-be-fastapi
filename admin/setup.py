from fastapi import FastAPI, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os

from .config import ADMIN_CONFIG

# Import individual feature routers
from .dashboard.router import router as dashboard_router
from .users.router import router as users_router
from .tasks.router import router as tasks_router
from .schedules.router import router as schedules_router
from .scheduled_tasks.router import router as scheduled_tasks_router
from .completions.router import router as completions_router
from .streaks.router import router as streaks_router

# Create main admin router
admin_router = APIRouter()

# Include all feature routers
admin_router.include_router(dashboard_router)
admin_router.include_router(users_router)
admin_router.include_router(tasks_router)
admin_router.include_router(schedules_router)
admin_router.include_router(scheduled_tasks_router)
admin_router.include_router(completions_router)
admin_router.include_router(streaks_router)

def get_admin_router():
    """Get the admin router"""
    return admin_router


def setup_admin(app: FastAPI, database_url: str = None) -> FastAPI:
    """Setup admin interface for the FastAPI app"""
    # Use environment variables if database_url is not provided
    if database_url is None:
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_sslmode = os.getenv("DB_SSLMODE", "require")
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={db_sslmode}"

    # Create SQLAlchemy engine (if needed for admin)
    engine = create_engine(database_url)
    # You can use 'engine' for admin DB operations if needed

    # Include the admin router in the main app
    app.include_router(admin_router)

    # Add admin static files if needed (can be extended later)
    # from fastapi.staticfiles import StaticFiles
    # app.mount("/admin/static", StaticFiles(directory="src/admin/static"), name="admin-static")

    return app

async def init_admin_db():
    """Initialize admin-specific database setup if needed"""
    # This function can be used for admin-specific database initialization
    # For example: creating admin users, setting up admin tables, etc.
    # Currently, we'll just pass as the main database tables are already created
    pass
