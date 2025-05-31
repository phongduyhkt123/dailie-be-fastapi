from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Simple HTTP Basic Auth for admin
security = HTTPBasic()

# Admin credentials (in production, use proper user management)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Admin configuration
ADMIN_CONFIG = {
    "title": "Dailee Admin Dashboard",
    "description": "Administration interface for Dailee Task Management API",
    "version": "1.0.0"
}
