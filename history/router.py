from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from .models import HistoryModel
from .pydantics import HistoryPdtModel, HistoryPdtCreate, HistoryPdtUpdate

router = APIRouter(prefix="/history", tags=["history"])


@router.post("/", response_model=HistoryPdtModel)
def create_or_update_history(history: HistoryPdtCreate, db: Session = Depends(get_db)):
    """Create or update history entry"""
    # Check if history entry already exists for this user and date
    existing_history = db.query(HistoryModel).filter(
        HistoryModel.user_id == history.user_id,
        HistoryModel.date == history.date
    ).first()
    
    if existing_history:
        # Update existing history
        update_data = history.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_history, field, value)
        
        db.commit()
        db.refresh(existing_history)
        return existing_history
    else:
        # Create new history entry
        db_history = HistoryModel(**history.model_dump())
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history


@router.get("/", response_model=List[HistoryPdtModel])
def get_all_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all history entries"""
    history_entries = db.query(HistoryModel).offset(skip).limit(limit).all()
    return history_entries


@router.get("/user/{user_id}", response_model=List[HistoryPdtModel])
def get_history_by_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get history entries for a specific user"""
    history_entries = db.query(HistoryModel).filter(
        HistoryModel.user_id == user_id
    ).offset(skip).limit(limit).all()
    return history_entries


@router.get("/{history_id}", response_model=HistoryPdtModel)
def get_history(history_id: int, db: Session = Depends(get_db)):
    """Get a specific history entry by ID"""
    history = db.query(HistoryModel).filter(HistoryModel.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    return history


@router.put("/{history_id}", response_model=HistoryPdtModel)
def update_history(history_id: int, history_update: HistoryPdtUpdate, db: Session = Depends(get_db)):
    """Update a history entry"""
    history = db.query(HistoryModel).filter(HistoryModel.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    update_data = history_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(history, field, value)
    
    db.commit()
    db.refresh(history)
    return history


@router.delete("/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    """Delete a history entry"""
    history = db.query(HistoryModel).filter(HistoryModel.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    db.delete(history)
    db.commit()
    return {"message": "History entry deleted successfully"}
