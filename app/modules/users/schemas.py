from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    '''Базовая схема пользователя'''
    name: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., max_length=100, description="Email пользователя", examples=["user_1@example.com"])


class UserIn(UserBase):
    '''Схема для создание и обновления пользователя'''
    password: str = Field(..., min_length=8, max_length=255, description="Пароль (минимум 8 символов)")


class UserOut(UserBase):
    '''Схема для возврата пользователя'''
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    is_active: bool = Field(True, description="Активность пользователя")
    created_at: datetime = Field(..., description="Дата создания пользователя")
    updated_at: datetime | None = Field(default=None, description="Дата изменения пользователя")

    model_config = ConfigDict(from_attributes=True)
