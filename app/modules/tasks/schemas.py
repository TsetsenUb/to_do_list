from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone

from .enums import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    '''Базовая схема задачи'''
    description: str | None = Field(None, description="Описание задачи")
    due_date: datetime | None = Field(None, description="Срок выполнения задачи")

    @field_validator("due_date", mode="after")
    def validate_due_date(cls, v: datetime):
        if v:
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v < datetime.now(timezone.utc):
                raise ValueError("due_date не может быть в прошлом")
        return v


class TaskIn(TaskBase):
    '''Схема для создания или обновления задачи'''
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок задачи")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Статус задачи")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Приоритет выполнения задачи")


class TaskOut(TaskBase):
    '''Схема для возврата задачи'''
    id: int = Field(..., description="Уникальный идентификатор задачи")
    title: str = Field(..., description="Заголовок задачи")
    status: TaskStatus = Field(..., description="Статус задачи")
    priority: TaskPriority = Field(..., description="Приоритет выполнения задачи")
    user_id: int = Field(..., description="Уникальный идентификатор пользователя")
    is_active: bool = Field(..., description="Активность задачи")
    created_at: datetime = Field(..., description="Дата создания задачи")
    updated_at: datetime | None = Field(..., description="Дата обновления задачи")

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(TaskBase):
    '''Схема для обновления задачи'''

    title: str | None = Field(None, description="Заголовок задачи")
    status: TaskStatus | None = Field(None, description="Статус задачи")
    priority: TaskPriority | None = Field(None, description="Приоритет выполнения задачи")
