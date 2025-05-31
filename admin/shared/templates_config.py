"""
Centralized template configuration for admin modules
"""
from fastapi.templating import Jinja2Templates
from pathlib import Path

def get_admin_templates():
    """Get Jinja2Templates instance with all admin template directories"""
    admin_dir = Path(__file__).parent.parent  # /admin/
    
    template_dirs = [
        str(admin_dir / "shared" / "templates"),
        str(admin_dir / "dashboard" / "templates"),
        str(admin_dir / "users" / "templates"),
        str(admin_dir / "tasks" / "templates"),
        str(admin_dir / "schedules" / "templates"),
        str(admin_dir / "scheduled_tasks" / "templates"),
        str(admin_dir / "completions" / "templates"),
        str(admin_dir / "streaks" / "templates")
    ]
    
    return Jinja2Templates(directory=template_dirs)

# Create a singleton instance
admin_templates = get_admin_templates()
