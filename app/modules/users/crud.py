from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from .models import User
from .schemas import UserIn
from app.modules.tasks.crud import Task
from app.core.security import hash_password


class UserCrud:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int, active: bool = True) -> User | None:
        '''
        Возвращает пользователя с указанным ID, если такого пользователя нет, вернется None
        '''
        db_user = await self.db.scalar(
            select(User)
            .where(User.id == user_id, User.is_active.is_(active))
        )
        return db_user

    async def create_user(self, user: UserIn) -> User:
        '''
        Создает нового пользователя и хеширует его пароль для хранения в базе данных
        '''
        new_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hash_password(user.password)
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def check_user_email(self, email: str) -> User | None:
        '''
        Возвращает пользователя с указанной почтой, если такого пользователя нет, вернется None
        '''
        user_email = await self.db.scalar(
            select(User)
            .where(User.email == email)
        )
        return user_email

    async def delete_user(self, user_id: int) -> None:
        '''
        Выполняет мягкое удаление пользователя с указанным ID и всех его задач(is_active = False)
        '''
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.execute(
            update(Task)
            .where(Task.user_id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()

    async def restore_user(self, user_id: int) -> User:
        '''
        Восстановление удаленного пользователя (is_active = True)
        '''
        restored_user = await self.db.get(User, user_id)
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=True)
        )
        await self.db.commit()
        await self.db.refresh(restored_user)
        return restored_user
