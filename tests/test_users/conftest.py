import pytest_asyncio
from app.modules.users.models import User
from app.core.security import hash_password


@pytest_asyncio.fixture
async def test_deleted_user(db_session):
    """Фикстура для создания удаленного пользователя в БД"""

    hashed_password = hash_password("12345678")
    test_user = User(
        name="User_1",
        email="user_1@example.com",
        hashed_password=hashed_password,
        is_active=False
    )

    db_session.add(test_user)
    await db_session.flush()
    await db_session.refresh(test_user)
    yield test_user
