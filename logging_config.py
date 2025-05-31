#!/usr/bin/env python3
"""
Logging configuration for SQL query monitoring and N+1 detection
"""
import logging
import sys
import re
import time
from typing import Any, Dict
from datetime import datetime

from core.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and better SQL formatting"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',      # Reset
        'BOLD': '\033[1m',       # Bold
        'DIM': '\033[2m',        # Dim
    }
    
    def format(self, record):
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        bold = self.COLORS['BOLD']
        dim = self.COLORS['DIM']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # Handle SQL query formatting
        if 'sqlalchemy.engine' in record.name and record.levelname == 'INFO':
            return self._format_sql_query(record, timestamp, color, reset, bold, dim)
        
        # Handle query counter messages
        if 'sqlalchemy.query_counter' in record.name:
            return self._format_query_counter(record, timestamp, color, reset, bold, dim)
        
        # Regular log formatting
        return f"{dim}[{timestamp}]{reset} {color}{bold}{record.levelname:8}{reset} {dim}{record.name:25}{reset} {record.getMessage()}"
    
    def _format_sql_query(self, record, timestamp, color, reset, bold, dim):
        """Format SQL query logs with syntax highlighting and formatting"""
        message = record.getMessage()
        
        # Extract SQL from the message
        if message.startswith('BEGIN') or message.startswith('COMMIT') or message.startswith('ROLLBACK'):
            return f"{dim}[{timestamp}]{reset} {color}💾 TRANSACTION{reset} {bold}{message}{reset}"
        
        # Format SELECT queries
        if 'SELECT' in message.upper():
            formatted_sql = self._prettify_sql(message)
            return f"{dim}[{timestamp}]{reset} {color}📖 QUERY{reset}\n{formatted_sql}\n"
        
        # Format INSERT/UPDATE/DELETE queries  
        if any(op in message.upper() for op in ['INSERT', 'UPDATE', 'DELETE']):
            formatted_sql = self._prettify_sql(message)
            return f"{dim}[{timestamp}]{reset} {color}✏️  MODIFY{reset}\n{formatted_sql}\n"
        
        return f"{dim}[{timestamp}]{reset} {color}🔍 SQL{reset} {message}"
    
    def _format_query_counter(self, record, timestamp, color, reset, bold, dim):
        """Format query counter messages"""
        message = record.getMessage()
        
        if "Total queries executed" in message:
            query_count = re.search(r'(\d+)', message)
            count = query_count.group(1) if query_count else "?"
            
            if int(count) > 10:
                return f"{dim}[{timestamp}]{reset} {self.COLORS['ERROR']}⚠️  N+1 WARNING{reset} {bold}{message}{reset}"
            else:
                return f"{dim}[{timestamp}]{reset} {self.COLORS['INFO']}📊 SUMMARY{reset} {message}"
        
        if "Query #" in message:
            return f"{dim}[{timestamp}]{reset} {color}#{reset} {message}"
        
        return f"{dim}[{timestamp}]{reset} {color}{record.levelname}{reset} {message}"
    
    def _prettify_sql(self, sql):
        """Make SQL more readable with formatting and colors"""
        
        # Keywords to highlight
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN',
            'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', 'OFFSET', 'INSERT', 'UPDATE', 
            'DELETE', 'SET', 'VALUES', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'UNION',
            'CREATE', 'ALTER', 'DROP', 'INDEX', 'TABLE', 'DATABASE'
        ]
        
        # Add line breaks and indentation
        formatted = sql
        formatted = re.sub(r'\bSELECT\b', '\n  SELECT', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bFROM\b', '\n  FROM', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bWHERE\b', '\n  WHERE', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bJOIN\b', '\n  JOIN', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bLEFT JOIN\b', '\n  LEFT JOIN', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bINNER JOIN\b', '\n  INNER JOIN', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bORDER BY\b', '\n  ORDER BY', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bGROUP BY\b', '\n  GROUP BY', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bLIMIT\b', '\n  LIMIT', formatted, flags=re.IGNORECASE)
        
        # Highlight keywords with colors
        for keyword in keywords:
            pattern = rf'\b{keyword}\b'
            replacement = f"{self.COLORS['BOLD']}{self.COLORS['INFO']}{keyword}{self.COLORS['RESET']}"
            formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
        
        # Indent the SQL
        lines = formatted.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append(f"    {line}")
        
        return '\n'.join(indented_lines)


def setup_logging():
    """Setup logging configuration for SQL monitoring"""
    
    # Create custom handler with colored formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.handlers = [handler]  # Replace all handlers
    
    # Configure SQLAlchemy loggers for query monitoring
    if settings.log_sql:
        # Log all SQL statements with our custom formatter
        sql_logger = logging.getLogger('sqlalchemy.engine')
        sql_logger.setLevel(logging.INFO)
        sql_logger.propagate = True
        
        # Log SQL statement parameters (be careful in production)
        if settings.debug:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
            logging.getLogger('sqlalchemy.dialects').setLevel(logging.DEBUG)
            logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
        
        # Query counter logger
        counter_logger = logging.getLogger('sqlalchemy.query_counter')
        counter_logger.setLevel(logging.INFO)
        counter_logger.propagate = True
        
        # Disable other verbose loggers
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)


class SQLQueryCounter:
    """Context manager to count SQL queries for N+1 detection"""
    
    def __init__(self, description: str = ""):
        self.description = description
        self.query_count = 0
        self.queries = []
        self.original_execute = None
        
    def __enter__(self):
        # Store original execute method
        import sqlalchemy.engine.base
        self.original_execute = sqlalchemy.engine.base.Connection._execute_context
        
        # Create wrapper to count queries
        def counting_execute(connection_self, dialect, constructor, statement, parameters, *args, **kwargs):
            self.query_count += 1
            query_info = {
                'query_num': self.query_count,
                'statement': str(statement),
                'parameters': parameters
            }
            self.queries.append(query_info)
            
            # Log each query with count
            logger = logging.getLogger('sqlalchemy.query_counter')
            logger.info(f"[{self.description}] Query #{self.query_count}: {str(statement)[:100]}...")
            
            return self.original_execute(connection_self, dialect, constructor, statement, parameters, *args, **kwargs)
        
        # Replace execute method
        sqlalchemy.engine.base.Connection._execute_context = counting_execute
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original execute method
        import sqlalchemy.engine.base
        sqlalchemy.engine.base.Connection._execute_context = self.original_execute
        
        # Log summary
        logger = logging.getLogger('sqlalchemy.query_counter')
        logger.warning(f"[{self.description}] Total queries executed: {self.query_count}")
        
        # Warn about potential N+1 if many queries
        if self.query_count > 10:
            logger.warning(f"[{self.description}] ⚠️  POTENTIAL N+1 QUERY ISSUE: {self.query_count} queries executed!")
            logger.warning("Consider using eager loading with joinedload() or selectinload()")


def monitor_endpoint_queries(description: str):
    """Decorator to monitor SQL queries for an endpoint"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with SQLQueryCounter(f"ASYNC {description}"):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with SQLQueryCounter(f"SYNC {description}"):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
