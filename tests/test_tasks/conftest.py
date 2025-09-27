import pytest_asyncio
import jwt
from datetime import datetime, timedelta

from app.core.config import SECRET_KEY, ALGORITHM


@pytest_asyncio.fixture
async def authenticated_client_without_tasks(client, test_user_without_tasks):
    """Клиент с аутентификацией тестового пользователя у которого нет задач"""

    dct = {
        "sub": test_user_without_tasks.email,
        "id": test_user_without_tasks.id,
        "exp": datetime.now() + timedelta(hours=1)
    }
    token = jwt.encode(dct, SECRET_KEY, algorithm=ALGORITHM)

    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client

    client.headers.pop("Authorization", None)


@pytest_asyncio.fixture
async def authenticated_client_with_tasks(client, test_user_with_tasks):
    """Клиент с аутентификацией тестового пользователя у которого есть задачи"""

    dct = {
        "sub": test_user_with_tasks.email,
        "id": test_user_with_tasks.id,
        "exp": datetime.now() + timedelta(hours=1)
    }
    token = jwt.encode(dct, SECRET_KEY, algorithm=ALGORITHM)

    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client

    client.headers.pop("Authorization", None)
