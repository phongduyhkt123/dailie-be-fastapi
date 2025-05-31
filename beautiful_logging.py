#!/usr/bin/env python3
"""
Beautiful logging configuration for SQL query monitoring and N+1 detection using Rich
"""
import logging
import sys
import re
import time
from typing import Any, Dict, List
from datetime import datetime

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.text import Text
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.theme import Theme
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import sqlparse
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("❌ Rich not available. Install with: pip install rich sqlparse")

from core.config import settings


# Custom theme for better SQL visibility
custom_theme = Theme({
    "sql.keyword": "bold blue",
    "sql.table": "bold green",
    "sql.column": "bold yellow",
    "sql.value": "magenta",
    "warning": "bold red",
    "info": "bold cyan",
    "success": "bold green",
    "query_count": "bold white on blue",
})

# Initialize Rich console
console = Console(theme=custom_theme, width=120) if RICH_AVAILABLE else None


class BeautifulSQLFormatter:
    """Format SQL queries beautifully"""
    
    @staticmethod
    def format_sql(sql_query: str) -> str:
        """Format SQL query with proper indentation and highlighting"""
        if not sql_query or not sqlparse:
            return sql_query
        
        try:
            # Remove extra whitespace and format
            formatted = sqlparse.format(
                sql_query,
                reindent=True,
                keyword_case='upper',
                identifier_case='lower',
                indent_width=2,
                wrap_after=80,
                strip_comments=False
            )
            return formatted
        except Exception:
            return sql_query
    
    @staticmethod
    def highlight_sql(sql_query: str) -> Syntax:
        """Create syntax-highlighted SQL"""
        if not RICH_AVAILABLE:
            return sql_query
            
        formatted_sql = BeautifulSQLFormatter.format_sql(sql_query)
        return Syntax(
            formatted_sql, 
            "sql", 
            theme="monokai", 
            line_numbers=True, 
            word_wrap=True,
            background_color="default"
        )


class RichSQLHandler(logging.Handler):
    """Custom logging handler with Rich formatting for SQL queries"""
    
    def __init__(self):
        super().__init__()
        self.query_count = 0
        
    def emit(self, record):
        if not RICH_AVAILABLE:
            return
            
        try:
            msg = record.getMessage()
            
            if 'sqlalchemy.engine' in record.name:
                if any(keyword in msg.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                    self._log_sql_query(msg, record)
                elif any(keyword in msg.upper() for keyword in ['BEGIN', 'COMMIT', 'ROLLBACK']):
                    self._log_transaction(msg, record)
                else:
                    console.print(f"[dim blue]🔗 DB Connection:[/dim blue] {msg}")
                    
            elif 'sqlalchemy.query_counter' in record.name:
                self._log_query_counter(msg, record)
            else:
                # Regular log message with Rich formatting
                level_colors = {
                    'DEBUG': 'dim white',
                    'INFO': 'cyan',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold red'
                }
                color = level_colors.get(record.levelname, 'white')
                console.print(f"[{color}]{record.levelname}[/{color}] {msg}")
                
        except Exception as e:
            # Fallback to standard logging
            print(f"Rich logging error: {e}")
            print(record.getMessage())
    
    def _log_sql_query(self, msg: str, record):
        """Log SQL query with beautiful formatting"""
        self.query_count += 1
        
        # Extract SQL from the message
        sql_match = re.search(r'(SELECT|INSERT|UPDATE|DELETE).*', msg, re.IGNORECASE | re.DOTALL)
        if sql_match:
            sql_query = sql_match.group(0)
            
            # Determine query type for icon and color
            query_type = sql_query.strip().upper().split()[0]
            type_config = {
                'SELECT': {'icon': '📖', 'color': 'blue', 'label': 'QUERY'},
                'INSERT': {'icon': '➕', 'color': 'green', 'label': 'INSERT'},
                'UPDATE': {'icon': '✏️', 'color': 'yellow', 'label': 'UPDATE'},
                'DELETE': {'icon': '🗑️', 'color': 'red', 'label': 'DELETE'},
            }
            
            config = type_config.get(query_type, {'icon': '🔍', 'color': 'cyan', 'label': 'SQL'})
            
            # Create syntax highlighted SQL
            syntax = BeautifulSQLFormatter.highlight_sql(sql_query)
            
            # Create panel with query
            panel = Panel(
                syntax,
                title=f"[bold {config['color']}]{config['icon']} {config['label']} #{self.query_count}[/bold {config['color']}]",
                title_align="left",
                border_style=config['color'],
                padding=(0, 1),
                expand=False
            )
            
            console.print(panel)
            
            # Add execution time if available
            if hasattr(record, 'duration'):
                console.print(f"[dim]⏱️  Execution time: {record.duration:.3f}s[/dim]")
            
            console.print()  # Add spacing
            
        else:
            # Fallback for non-SQL messages
            console.print(f"[blue]🗃️  Database:[/blue] {msg}")
    
    def _log_transaction(self, msg: str, record):
        """Log database transactions"""
        if 'BEGIN' in msg.upper():
            console.print("[dim green]🟢 Transaction started[/dim green]")
        elif 'COMMIT' in msg.upper():
            console.print("[dim green]✅ Transaction committed[/dim green]")
        elif 'ROLLBACK' in msg.upper():
            console.print("[dim red]↩️  Transaction rolled back[/dim red]")
    
    def _log_query_counter(self, msg: str, record):
        """Log query counter messages with special formatting"""
        if "Total queries executed" in msg:
            # Extract count and description
            count_match = re.search(r'Total queries executed: (\d+)', msg)
            desc_match = re.search(r'\[(.*?)\]', msg)
            
            if count_match:
                count = int(count_match.group(1))
                description = desc_match.group(1) if desc_match else "Unknown endpoint"
                
                if count > 10:
                    # N+1 warning
                    warning_panel = Panel(
                        f"[bold red]⚠️  POTENTIAL N+1 QUERY ISSUE![/bold red]\n\n"
                        f"[yellow]Endpoint:[/yellow] {description}\n"
                        f"[yellow]Query count:[/yellow] [bold white]{count}[/bold white]\n\n"
                        f"[dim]💡 Consider using eager loading:[/dim]\n"
                        f"[dim]   • joinedload() for one-to-one/many-to-one[/dim]\n"
                        f"[dim]   • selectinload() for one-to-many/many-to-many[/dim]",
                        title="[bold red]🚨 Performance Warning[/bold red]",
                        border_style="red",
                        padding=(1, 2)
                    )
                    console.print(warning_panel)
                elif count > 5:
                    console.print(f"[yellow]⚠️  {description}: {count} queries (moderate)[/yellow]")
                else:
                    console.print(f"[green]✅ {description}: {count} queries (good)[/green]")
        
        elif "Query #" in msg:
            # Individual query counter
            console.print(f"[dim cyan]📊 {msg}[/dim cyan]")
        else:
            console.print(f"[cyan]📈 {msg}[/cyan]")


def setup_logging():
    """Setup beautiful logging configuration for SQL monitoring"""
    
    if RICH_AVAILABLE:
        # Show welcome message
        console.print(Panel(
            "[bold green]🎨 Beautiful SQL Logging Initialized![/bold green]\n\n"
            f"[cyan]• SQL Query Logging:[/cyan] {'[bold green]✅ ENABLED[/bold green]' if settings.log_sql else '[bold red]❌ DISABLED[/bold red]'}\n"
            f"[cyan]• Debug Mode:[/cyan] {'[bold green]✅ ON[/bold green]' if settings.debug else '[bold yellow]❌ OFF[/bold yellow]'}\n"
            f"[cyan]• Log Level:[/cyan] [bold]{settings.log_level.upper()}[/bold]\n"
            f"[cyan]• Rich Formatting:[/cyan] [bold green]✅ ACTIVE[/bold green]",
            title="[bold blue]🗄️  Database Monitoring[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))
        
        # Setup Rich logging for general logs
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=settings.debug,
            omit_repeated_times=False
        )
        
        # Custom SQL handler
        sql_handler = RichSQLHandler()
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format="%(message)s",
            handlers=[rich_handler],
            force=True  # Override any existing configuration
        )
        
        # Configure SQLAlchemy loggers
        if settings.log_sql:
            # SQL query logger
            sql_logger = logging.getLogger('sqlalchemy.engine')
            sql_logger.handlers.clear()
            sql_logger.addHandler(sql_handler)
            sql_logger.setLevel(logging.INFO)
            sql_logger.propagate = False
            
            # Query counter logger
            counter_logger = logging.getLogger('sqlalchemy.query_counter')
            counter_logger.handlers.clear()
            counter_logger.addHandler(sql_handler)
            counter_logger.setLevel(logging.INFO)
            counter_logger.propagate = False
            
            if settings.debug:
                sql_logger.setLevel(logging.DEBUG)
        
        # Suppress noisy loggers
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    else:
        # Fallback to colored console logging
        print("🎨 Setting up colored console logging (Rich not available)")
        from logging_config_fallback import setup_fallback_logging
        setup_fallback_logging()


class SQLQueryCounter:
    """Enhanced context manager to count SQL queries for N+1 detection"""
    
    def __init__(self, description: str = ""):
        self.description = description
        self.query_count = 0
        self.queries = []
        self.original_execute = None
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        
        # Store original execute method
        import sqlalchemy.engine.base
        self.original_execute = sqlalchemy.engine.base.Connection._execute_context
        
        # Create wrapper to count queries
        def counting_execute(connection_self, dialect, constructor, statement, parameters, *args, **kwargs):
            query_start = time.time()
            
            self.query_count += 1
            query_info = {
                'query_num': self.query_count,
                'statement': str(statement),
                'parameters': parameters,
                'timestamp': query_start
            }
            self.queries.append(query_info)
            
            # Execute query and measure time
            result = self.original_execute(connection_self, dialect, constructor, statement, parameters, *args, **kwargs)
            
            query_duration = time.time() - query_start
            query_info['duration'] = query_duration
            
            # Log query with timing
            logger = logging.getLogger('sqlalchemy.query_counter')
            if query_duration > 0.1:  # Slow query warning
                logger.warning(f"[{self.description}] 🐌 Slow Query #{self.query_count} ({query_duration:.3f}s): {str(statement)[:100]}...")
            else:
                logger.info(f"[{self.description}] Query #{self.query_count} ({query_duration:.3f}s): {str(statement)[:100]}...")
            
            return result
        
        # Replace execute method
        sqlalchemy.engine.base.Connection._execute_context = counting_execute
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original execute method
        import sqlalchemy.engine.base
        sqlalchemy.engine.base.Connection._execute_context = self.original_execute
        
        total_time = time.time() - self.start_time
        
        # Log summary
        logger = logging.getLogger('sqlalchemy.query_counter')
        logger.warning(f"[{self.description}] Total queries executed: {self.query_count} in {total_time:.3f}s")
        
        # Performance analysis
        if self.query_count > 10:
            logger.warning(f"[{self.description}] ⚠️  POTENTIAL N+1 QUERY ISSUE: {self.query_count} queries!")
            
            # Show slowest queries
            slow_queries = [q for q in self.queries if q.get('duration', 0) > 0.05]
            if slow_queries:
                logger.warning(f"[{self.description}] Found {len(slow_queries)} slow queries (>50ms)")


def monitor_endpoint_queries(description: str):
    """Decorator to monitor SQL queries for an endpoint with beautiful output"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with SQLQueryCounter(f"🔄 {description}"):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with SQLQueryCounter(f"⚡ {description}"):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Quick test function
def test_beautiful_logging():
    """Test the beautiful logging setup"""
    setup_logging()
    
    if RICH_AVAILABLE:
        console.print(Panel(
            "[bold green]🧪 Testing Beautiful SQL Logging[/bold green]\n\n"
            "[cyan]This is what your SQL queries will look like![/cyan]",
            title="[bold blue]Test Mode[/bold blue]",
            border_style="green"
        ))
        
        # Simulate some SQL logs
        test_logger = logging.getLogger('sqlalchemy.engine')
        test_logger.info("SELECT users.id, users.name, users.email FROM users WHERE users.active = true ORDER BY users.created_at DESC LIMIT 10")
        
        counter_logger = logging.getLogger('sqlalchemy.query_counter')
        counter_logger.warning("[Test Endpoint] Total queries executed: 15")
    else:
        print("❌ Rich not available - falling back to basic logging")
