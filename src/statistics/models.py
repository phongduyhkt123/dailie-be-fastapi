# Import Pydantic models from the pydantics package
from .pydantics.statistics_pydantic import (
    UserTaskStreakPdtBase,
    UserTaskStreakPdtCreate,
    UserTaskStreakPdtUpdate,
    UserTaskStreakPdtModel
)

# Aliases for backward compatibility
UserTaskStreak = UserTaskStreakPdtModel
UserTaskStreakCreate = UserTaskStreakPdtCreate
UserTaskStreakUpdate = UserTaskStreakPdtUpdate
