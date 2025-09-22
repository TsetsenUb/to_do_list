from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated
from fastapi import Depends

from .database import async_session_maker
from app.modules.users.crud import UserCrud
from app.modules.tasks.crud import Task_Crud


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as async_session:
        yield async_session


def get_user_crud(db: Annotated[UserCrud, Depends(get_async_db)]) -> UserCrud:
    '''
    Возвращает экземпляр UserCrud-класса для работы с пользователями.
    '''
    return UserCrud(db)


def get_task_crud(db: Annotated[Task_Crud, Depends(get_async_db)]) -> Task_Crud:
    '''
    Возвращает экземпляр Task_Crud-класса для работы с задачами.
    '''
    return Task_Crud(db)
