from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr

from core.database.base import Base


class BaseModel(Base):
    """
    Abstract base model that provides common fields for all models.
    Contains id, created_at, updated_at, and description fields.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @declared_attr
    def __tablename__(cls):
        # This will be overridden by child classes
        return cls.__name__.lower()
