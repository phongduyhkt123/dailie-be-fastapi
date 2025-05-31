#!/usr/bin/env python3
"""
Script to create an admin user for the Dailee Task Management API.
This script adds a password_hash field to the users table and creates an admin user.
"""

import sys
import os
import getpass
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from core.database import SessionLocal
from users.models import UserModel

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def add_password_field_to_users():
    """Add password_hash field to users table if it doesn't exist."""
    try:
        engine = create_engine(settings.database_url_complete)
        with engine.connect() as connection:
            # Check if password_hash column exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='password_hash'
            """))
            
            if not result.fetchone():
                print("Adding password_hash field to users table...")
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN password_hash VARCHAR(255)
                """))
                connection.commit()
                print("✓ password_hash field added successfully")
            else:
                print("✓ password_hash field already exists")
                
    except Exception as e:
        print(f"Error adding password_hash field: {e}")
        return False
    return True


def create_admin_user(name: str, email: str, password: str, user_id: str = None):
    """Create an admin user in the database."""
    if not user_id:
        user_id = f"admin_{email.split('@')[0]}"
    
    try:
        db = SessionLocal()
        
        # Check if user already exists
        existing_user = db.query(UserModel).filter(UserModel.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return False
        
        # Create new admin user
        hashed_password = hash_password(password)
        admin_user = UserModel(
            user_id=user_id,
            name=name,
            email=email
        )
        
        # Set password_hash using setattr since it might not be in the model definition yet
        setattr(admin_user, 'password_hash', hashed_password)
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✓ Admin user created successfully!")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  User ID: {user_id}")
        print(f"  ID: {admin_user.id}")
        
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function to create admin user."""
    print("=== Dailee Admin User Creation ===\n")
    
    # Add password field to users table
    if not add_password_field_to_users():
        print("Failed to add password field. Exiting.")
        sys.exit(1)
    
    print("\nCreating admin user...")
    
    # Get admin user details
    name = input("Enter admin name: ").strip()
    if not name:
        print("Name cannot be empty!")
        sys.exit(1)
    
    email = input("Enter admin email: ").strip()
    if not email or "@" not in email:
        print("Please enter a valid email!")
        sys.exit(1)
    
    password = getpass.getpass("Enter admin password: ").strip()
    if len(password) < 6:
        print("Password must be at least 6 characters!")
        sys.exit(1)
    
    confirm_password = getpass.getpass("Confirm admin password: ").strip()
    if password != confirm_password:
        print("Passwords do not match!")
        sys.exit(1)
    
    # Create admin user
    if create_admin_user(name, email, password):
        print(f"\n✓ Admin user created successfully!")
        print(f"\nYou can now update the admin configuration to use database authentication")
        print(f"or use this user for API authentication at /api/v1/auth/token")
    else:
        print("\n✗ Failed to create admin user")
        sys.exit(1)


if __name__ == "__main__":
    main()
