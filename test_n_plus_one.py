#!/usr/bin/env python3
"""
Test script to demonstrate N+1 query detection
Run this to see how the logging works
"""
import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from logging_config import setup_logging, SQLQueryCounter
from n_plus_one_detector import analyze_queries
from tasks.models import TaskModel, TaskCompletionModel
from users.models import UserModel


def test_n_plus_one_detection():
    """Test function to demonstrate N+1 query detection"""
    
    # Setup logging
    setup_logging()
    
    print("🔍 Testing N+1 Query Detection...")
    print("=" * 60)
    
    # Create a database session
    db: Session = SessionLocal()
    
    try:
        # Example 1: Demonstrate N+1 query problem
        print("\n📊 Example 1: PROBLEMATIC CODE (N+1 queries)")
        with analyze_queries("BAD: Fetching tasks and accessing completions individually"):
            # This will trigger N+1 queries
            tasks = db.query(TaskModel).limit(5).all()
            for task in tasks:
                # Each of these will trigger a separate query - N+1 problem!
                completions_count = len(task.completions)
                print(f"Task '{task.title}' has {completions_count} completions")
        
        print("\n" + "=" * 60)
        
        # Example 2: Demonstrate optimized approach
        print("\n✅ Example 2: OPTIMIZED CODE (eager loading)")
        with analyze_queries("GOOD: Fetching tasks with eager loading"):
            from sqlalchemy.orm import selectinload
            # This will use eager loading - no N+1 problem!
            tasks = db.query(TaskModel).options(
                selectinload(TaskModel.completions)
            ).limit(5).all()
            for task in tasks:
                # No additional queries - data is already loaded!
                completions_count = len(task.completions)
                print(f"Task '{task.title}' has {completions_count} completions")
        
        print("\n" + "=" * 60)
        
        # Example 3: Using the query counter context manager
        print("\n📈 Example 3: Using SQLQueryCounter")
        with SQLQueryCounter("Manual query counting example"):
            # Simulate some database operations
            user_count = db.query(UserModel).count()
            task_count = db.query(TaskModel).count()
            completion_count = db.query(TaskCompletionModel).count()
            
            print(f"Database stats: {user_count} users, {task_count} tasks, {completion_count} completions")
    
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("🎉 N+1 Query Detection Test Complete!")
    print("\nTo enable logging in your application:")
    print("1. Set LOG_SQL=True in your .env file")
    print("2. Add @monitor_n_plus_one decorator to your endpoints")
    print("3. Use analyze_queries() context manager in your code")
    print("4. Use eager loading (joinedload/selectinload) to prevent N+1")


def test_with_api_call():
    """Test with actual API endpoint"""
    print("\n🌐 Testing with API endpoint simulation...")
    
    # This simulates what happens when you call your API endpoint
    from statistics.router import get_task_completions
    from core.database import get_db
    
    db = next(get_db())
    
    try:
        # This will use the optimized version with eager loading
        completions = get_task_completions(limit=5, db=db)
        print(f"Retrieved {len(completions)} task completions")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting N+1 Query Detection Demo")
    test_n_plus_one_detection()
    test_with_api_call()
