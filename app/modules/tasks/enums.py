import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
