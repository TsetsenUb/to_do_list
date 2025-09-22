from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from .models import Task
from .schemas import TaskIn


class Task_Crud:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task(self, task_id: int, active: bool = True) -> Task | None:
        '''
        Получает из базы данных задачу с указанным ID
        '''
        db_task = await self.db.scalar(
            select(Task)
            .where(Task.id == task_id, Task.is_active.is_(active))
        )
        return db_task

    async def get_user_tasks(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
        '''
        Получает из базы данных активные задачи конкретного пользователя
        '''
        user_tasks = await self.db.scalars(
            select(Task)
            .where(Task.user_id == user_id, Task.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return user_tasks.all()

    async def create_task(self, task: TaskIn, user_id: int) -> Task:
        '''
        Создает новую задачу в базе данных.
        '''
        dct_values = task.model_dump()
        dct_values.update({"user_id": user_id})
        new_task = Task(**dct_values)

        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)
        return new_task

    async def update_task(self, task_id: int, task_dict: dict) -> Task:
        '''
        Обновляет задачу с указанным ID
        '''
        updated_task = await self.db.get(Task, task_id)

        await self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(**task_dict)
        )
        await self.db.commit()
        await self.db.refresh(updated_task)
        return updated_task

    async def delete_task(self, task_id: int) -> None:
        '''
        Выполняет мягкое удаление задачи (значение is_active меняется на False)
        '''
        await self.db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(is_active=False)
        )
        await self.db.commit()
