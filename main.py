from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import create_tables
from tasks.router import router as tasks_router
from users.router import router as users_router
from statistics.router import router as statistics_router
from schedules.router import router as schedules_router
from auth.router import router as auth_router
from achievements.router import router as achievements_router
from history.router import router as history_router
from admin.setup import setup_admin, init_admin_db
from beautiful_logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()  # Setup SQL logging
    create_tables()
    await init_admin_db()
    yield
    # Shutdown


app = FastAPI(
    title="Dailee Task Management API",
    description="A FastAPI backend for the Dailee task management app",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(achievements_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")

# Setup admin interface
admin_app = setup_admin(app, settings.database_url_complete)


@app.get("/")
async def root():
    return {
        "message": "Dailee Task Management API", 
        "version": "1.0.0",
        "admin_url": "/admin",
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}