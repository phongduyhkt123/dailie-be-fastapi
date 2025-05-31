# SQL Query Logging and N+1 Detection Guide

This guide explains how to monitor SQL queries and detect N+1 query issues in your FastAPI application.

## 🔧 Setup

### 1. Environment Configuration

Add these settings to your `.env` file:

```env
LOG_SQL=true        # Enable SQL query logging
LOG_LEVEL=INFO      # Set logging level
DEBUG=true          # Enable debug mode
```

### 2. Logging Configuration

The logging is automatically configured when the application starts. You can see SQL queries in your console output.

## 📊 Query Monitoring Methods

### Method 1: Automatic Endpoint Monitoring

Use the `@monitor_n_plus_one` decorator on your endpoints:

```python
from n_plus_one_detector import monitor_n_plus_one

@router.get("/tasks")
@monitor_n_plus_one("GET /tasks - Task List")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()
```

### Method 2: Manual Query Analysis

Use the `analyze_queries` context manager:

```python
from n_plus_one_detector import analyze_queries

def some_function(db: Session):
    with analyze_queries("Custom operation description"):
        # Your database operations here
        tasks = db.query(TaskModel).all()
        for task in tasks:
            print(len(task.completions))  # This might trigger N+1
```

### Method 3: Query Counter

Use `SQLQueryCounter` for simple query counting:

```python
from logging_config import SQLQueryCounter

with SQLQueryCounter("Operation name"):
    # Your database operations
    results = db.query(Model).all()
```

## 🚨 Detecting N+1 Queries

### What is an N+1 Query?

An N+1 query problem occurs when:
1. You fetch N records with 1 query
2. Then for each record, you execute 1 additional query
3. Total: 1 + N queries (should be just 1 or 2)

### Example of N+1 Problem:

```python
# BAD: This creates N+1 queries
tasks = db.query(TaskModel).all()  # 1 query
for task in tasks:
    print(len(task.completions))   # N additional queries!
```

### How to Fix N+1 Queries:

```python
# GOOD: Use eager loading
from sqlalchemy.orm import selectinload, joinedload

# Option 1: selectinload (separate query, but efficient)
tasks = db.query(TaskModel).options(
    selectinload(TaskModel.completions)
).all()

# Option 2: joinedload (single query with JOIN)
tasks = db.query(TaskModel).options(
    joinedload(TaskModel.completions)
).all()

# Now accessing completions won't trigger additional queries
for task in tasks:
    print(len(task.completions))  # No additional queries!
```

## 🔍 Understanding the Output

### Normal Logging Output:
```
INFO - sqlalchemy.engine - SELECT tasks.id, tasks.title FROM tasks
INFO - [Query Counter] Query #1: SELECT tasks.id, tasks.title...
```

### N+1 Detection Output:
```
WARNING - 🚨 POTENTIAL N+1 QUERY DETECTED!
WARNING -   - Pattern repeated 10 times: SELECT completions.* FROM completions WHERE completions.task_id = ?
INFO - 💡 Recommendations:
INFO -   - Consider using eager loading (joinedload/selectinload)
```

## 🛠️ Testing Your Setup

Run the test script to see the logging in action:

```bash
cd /home/duy/projects/dailie-be-fastapi
python test_n_plus_one.py
```

This will demonstrate:
- N+1 query problems
- Optimized queries with eager loading
- Query counting and analysis

## 📈 Best Practices

### 1. Use Eager Loading

Always use eager loading when you know you'll access related data:

```python
# For one-to-many relationships
query.options(selectinload(Model.related_items))

# For many-to-one relationships  
query.options(joinedload(Model.parent))

# For multiple relationships
query.options(
    selectinload(Model.items),
    joinedload(Model.parent)
)
```

### 2. Monitor Your Endpoints

Add monitoring to endpoints that return lists:

```python
@router.get("/items")
@monitor_n_plus_one("GET /items")
def get_items(db: Session = Depends(get_db)):
    return db.query(ItemModel).options(
        selectinload(ItemModel.related_data)
    ).all()
```

### 3. Regular Performance Checks

- Run your test suite with logging enabled
- Check endpoints that return lists of items
- Look for query counts > 5-10 as potential issues

## 🔧 Configuration Options

### Disable Logging in Production

In production, you might want to disable detailed SQL logging:

```env
LOG_SQL=false
LOG_LEVEL=WARNING
DEBUG=false
```

### Custom Thresholds

Adjust the N+1 detection threshold in your code:

```python
with analyze_queries("Custom operation", threshold=3):
    # Will warn if more than 3 similar queries
    pass
```

## 🚀 Running Your Application

Start your FastAPI application and watch the console for SQL queries:

```bash
cd /home/duy/projects/dailie-be-fastapi
python run_server.py
```

When you make API calls, you'll see:
- All SQL queries being executed
- Query counts per endpoint
- Warnings about potential N+1 issues
- Recommendations for optimization

## 📚 Additional Resources

- [SQLAlchemy Eager Loading](https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [N+1 Query Problem Explained](https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem-in-orm-object-relational-mapping)
