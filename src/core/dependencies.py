from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db  # Assuming you have a database module for session management

def get_current_user(db: Session = Depends(get_db)):
    # Logic to retrieve the current user from the database
    user = db.query(User).filter(User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_query_params(param: str = None):
    return param