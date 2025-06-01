#!/usr/bin/env python3
"""
Database migration and setup script
"""
import asyncio
from sqlalchemy import text
from database.database import engine
from database.models import Base
from config import settings


def create_database():
    """Create the database if it doesn't exist"""
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    
    # Connect to postgres database to create our target database
    postgres_url = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/postgres"
    temp_engine = create_engine(postgres_url)
    
    try:
        with temp_engine.connect() as conn:
            conn.execute(text("COMMIT"))  # End any existing transaction
            conn.execute(text(f"CREATE DATABASE {settings.db_name}"))
            print(f"Database '{settings.db_name}' created successfully")
    except OperationalError as e:
        if "already exists" in str(e):
            print(f"Database '{settings.db_name}' already exists")
        else:
            print(f"Error creating database: {e}")
            raise
    finally:
        temp_engine.dispose()


def create_tables():
    """Create all tables"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")


def main():
    """Main migration function"""
    print("Starting database setup...")
    print(f"Database URL: {settings.database_url_complete}")
    
    # Create database
    create_database()
    
    # Create tables
    create_tables()
    
    print("Database setup completed!")


if __name__ == "__main__":
    main()
