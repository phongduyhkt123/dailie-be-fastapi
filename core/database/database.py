from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

# Create SQLAlchemy engine with PostgreSQL
engine = create_engine(
    settings.database_url_complete,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.log_sql,  # Enable SQL logging when log_sql is True
    echo_pool=settings.debug  # Enable connection pool logging when debug is True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    # Import all models to ensure they're registered with Base
    from .base import Base
    from tasks.models import TaskModel, ScheduledTaskModel, TaskCompletionModel
    from users.models import UserModel
    from schedules.models import ScheduleModel
    from statistics.models import UserTaskStreakModel
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
