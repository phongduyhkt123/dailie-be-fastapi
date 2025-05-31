# Import Pydantic models from the pydantics package
from .pydantics.schedule_pydantic import (
    ScheduleBasePdtModel,
    SchedulePdtCreate,
    SchedulePdtUpdate,
    SchedulePdtModel
)
from ..tasks.pydantics import ScheduledTaskPdtModel

# Aliases for backward compatibility
ScheduleModel = SchedulePdtModel
ScheduleCreate = SchedulePdtCreate
ScheduleUpdate = SchedulePdtUpdate
ScheduledTaskModel = ScheduledTaskPdtModel
