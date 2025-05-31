#!/usr/bin/env python3
"""
N+1 Query Detection and Prevention Utilities
"""
import functools
import logging
import time
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import event

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyzes SQL queries to detect N+1 patterns"""
    
    def __init__(self):
        self.queries: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        
    def add_query(self, statement: str, parameters: Any = None, duration: float = 0):
        """Add a query to the analysis"""
        self.queries.append({
            'statement': str(statement),
            'parameters': parameters,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def detect_n_plus_one(self, threshold: int = 5) -> Dict[str, Any]:
        """Detect potential N+1 query patterns"""
        analysis = {
            'total_queries': len(self.queries),
            'potential_n_plus_one': False,
            'suspicious_patterns': [],
            'recommendations': []
        }
        
        if len(self.queries) <= threshold:
            return analysis
        
        # Group similar queries
        query_patterns = {}
        for query in self.queries:
            # Normalize query by removing parameter values
            normalized = self._normalize_query(query['statement'])
            if normalized not in query_patterns:
                query_patterns[normalized] = []
            query_patterns[normalized].append(query)
        
        # Look for patterns that indicate N+1
        for pattern, occurrences in query_patterns.items():
            if len(occurrences) >= threshold:
                analysis['potential_n_plus_one'] = True
                analysis['suspicious_patterns'].append({
                    'pattern': pattern,
                    'count': len(occurrences),
                    'example_query': occurrences[0]['statement']
                })
                
                # Generate recommendations
                if 'SELECT' in pattern.upper() and 'WHERE' in pattern.upper():
                    analysis['recommendations'].append(
                        f"Consider using eager loading (joinedload/selectinload) for the repeated query pattern: {pattern[:100]}..."
                    )
        
        return analysis
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing specific parameter values"""
        import re
        # Remove specific IDs and values
        normalized = re.sub(r'\b\d+\b', '?', query)
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()


@contextmanager
def analyze_queries(description: str = "", threshold: int = 5):
    """Context manager to analyze queries for N+1 patterns"""
    analyzer = QueryAnalyzer()
    
    # Set up event listener for SQLAlchemy
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        duration = time.time() - getattr(context, '_query_start_time', 0)
        analyzer.add_query(statement, parameters, duration)
    
    # Register event listeners
    from sqlalchemy import event
    from core.database import engine
    
    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    event.listen(engine, "after_cursor_execute", after_cursor_execute)
    
    try:
        yield analyzer
    finally:
        # Remove event listeners
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
        event.remove(engine, "after_cursor_execute", after_cursor_execute)
        
        # Analyze and log results
        analysis = analyzer.detect_n_plus_one(threshold)
        
        logger.info(f"=== Query Analysis for: {description} ===")
        logger.info(f"Total queries: {analysis['total_queries']}")
        
        if analysis['potential_n_plus_one']:
            logger.warning("🚨 POTENTIAL N+1 QUERY DETECTED!")
            for pattern in analysis['suspicious_patterns']:
                logger.warning(f"  - Pattern repeated {pattern['count']} times: {pattern['pattern'][:100]}...")
            
            logger.info("💡 Recommendations:")
            for rec in analysis['recommendations']:
                logger.info(f"  - {rec}")
        else:
            logger.info("✅ No N+1 query patterns detected")
        
        logger.info("=" * 50)


def eager_load_decorator(relationships: List[str]):
    """Decorator to automatically add eager loading to queries"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # This is a placeholder - you would need to modify your service methods
            # to accept and use eager loading options
            logger.info(f"Applying eager loading for: {relationships}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage functions for common N+1 scenarios
def get_tasks_with_completions_optimized(db: Session, user_id: str = None):
    """Example of optimized query to avoid N+1 when fetching tasks with completions"""
    from tasks.models import TaskModel
    
    query = db.query(TaskModel).options(
        selectinload(TaskModel.completions),
        selectinload(TaskModel.streaks)
    )
    
    if user_id:
        # Join with completions to filter by user
        from tasks.models import TaskCompletionModel
        query = query.join(TaskCompletionModel).filter(TaskCompletionModel.user_id == user_id)
    
    return query.all()


def get_completions_with_tasks_optimized(db: Session, user_id: str = None):
    """Example of optimized query to avoid N+1 when fetching completions with task details"""
    from tasks.models import TaskCompletionModel
    
    query = db.query(TaskCompletionModel).options(
        joinedload(TaskCompletionModel.task)
    )
    
    if user_id:
        query = query.filter(TaskCompletionModel.user_id == user_id)
    
    return query.all()


def create_optimized_router_decorator():
    """Create a decorator that can be applied to router functions"""
    def decorator(description: str = ""):
        def route_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with analyze_queries(f"Endpoint: {description or func.__name__}"):
                    return func(*args, **kwargs)
            return wrapper
        return route_decorator
    return decorator


# Create the decorator instance
monitor_n_plus_one = create_optimized_router_decorator()
