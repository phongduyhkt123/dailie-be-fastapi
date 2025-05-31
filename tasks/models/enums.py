import enum


class TaskTypeEnum(enum.Enum):
    HABIT = "habit"
    ONE_TIME = "oneTime"
    PERSONAL = "personal"
    WORK = "work"
    OTHER = "other"


class TaskStatusEnum(enum.Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAIL = "fail"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"
