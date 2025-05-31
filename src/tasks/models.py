# Import Pydantic models from the pydantics package
from .pydantics import (
    TaskPdtBase,
    TaskPdtCreate,
    TaskPdtUpdate,
    TaskPdtModel,
    ScheduledTaskPdtBaseModel,
    ScheduledTaskPdtCreate,
    ScheduledTaskPdtUpdate,
    ScheduledTaskPdtModel,
    TaskCompletionPdtBase,
    TaskCompletionPdtCreate,
    TaskCompletionPdtUpdate,
    TaskCompletionPdtModel
)
from .models.enums import TaskTypeEnum as TaskType, TaskStatusEnum as TaskStatus

# Aliases for backward compatibility
TaskModel = TaskPdtModel
TaskCreate = TaskPdtCreate
TaskUpdate = TaskPdtUpdate
ScheduledTaskModel = ScheduledTaskPdtModel
TaskCompletionModel = TaskCompletionPdtModel
