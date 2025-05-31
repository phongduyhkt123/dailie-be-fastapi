# Import Pydantic models from the pydantics package
from .pydantics.user_pydantic import (
    UserBasePdtModel,
    UserPdtCreate,
    UserPdtUpdate,
    UserPdtModel
)

# Aliases for backward compatibility
User = UserPdtModel
UserCreate = UserPdtCreate
UserUpdate = UserPdtUpdate
