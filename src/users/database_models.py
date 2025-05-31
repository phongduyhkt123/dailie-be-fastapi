# Import all models from the models directory for backward compatibility
from .models.user_model import User

# Export all models
__all__ = [
    "User"
]
