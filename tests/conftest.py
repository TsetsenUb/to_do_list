import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies import get_async_db
from app.core.security import hash_password
from app.core.config import TEST_DATABASE_URL
from app.modules.users.models import User
from app.modules.tasks.models import Task


@pytest_asyncio.fixture
async def test_engine():
    """Создает engine и БД для теста"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Создает сессию для теста"""
    async_session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Создает клиент с существующей сессией"""

    async def _get_async_db_override():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_async_db] = _get_async_db_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user_without_tasks(db_session):
    """Фикстура для создания тестового пользователя в БД (без задач)"""

    hashed_password = hash_password("12345678")
    test_user = User(
        name="User_1",
        email="user_1@example.com",
        hashed_password=hashed_password
    )

    db_session.add(test_user)
    await db_session.flush()
    await db_session.refresh(test_user)

    yield test_user


@pytest_asyncio.fixture
async def test_user_with_tasks(db_session):
    """Фикстура для создания тестового пользователя в БД (с задачами)"""

    hashed_password = hash_password("12345678")
    test_user = User(
        name="User_2",
        email="user_2@example.com",
        hashed_password=hashed_password
    )

    test_tasks = [
        Task(title="Task_1", user=test_user),
        Task(title="Task_2", user=test_user)
    ]

    db_session.add(test_user)
    db_session.add_all(test_tasks)
    await db_session.flush()

    await db_session.refresh(test_user)
    for task in test_tasks:
        await db_session.refresh(task)

    yield test_user
