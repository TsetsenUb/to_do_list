from sqlalchemy import select

from app.modules.users.models import User
from app.modules.tasks.models import Task


async def test_get_user(client, test_user_without_tasks):
    res = await client.get("/api/users/1")
    assert res.status_code == 200
    user = res.json()
    assert user["id"] == 1
    assert user["name"] == "User_1"
    assert user["email"] == "user_1@example.com"
    assert user["is_active"] is True
    assert user["created_at"] is not None
    assert user["updated_at"] is None


async def test_get_wrong_user(client):
    res = await client.get("/api/users/1")
    assert res.status_code == 404
    assert res.json()["detail"] == "Активный пользователь с ID: 1 не найден"


async def test_create_user(client, db_session):
    res = await client.post(
        "/api/users/",
        json={
            "name": "User_3",
            "email": "user_3@example.com",
            "password": "12345678"
        }
    )
    assert res.status_code == 201
    new_user = res.json()
    assert new_user["name"] == "User_3"
    assert new_user["email"] == "user_3@example.com"
    assert new_user["is_active"] is True
    assert new_user["created_at"] is not None
    assert new_user["updated_at"] is None

    query = (
        select(User)
        .where(User.id == new_user["id"])
    )
    user = await db_session.scalar(query)
    assert user.name == new_user["name"]
    assert user.email == new_user["email"]


async def test_create_user_with_registered_email(client, test_user_without_tasks):
    res = await client.post(
        "/api/users/",
        json={
            "name": "User_1",
            "email": "user_1@example.com",
            "password": "12345678"
        }
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Email user_1@example.com уже зарегистрирован"


async def test_delete_user(client, db_session, test_user_with_tasks):
    assert test_user_with_tasks.is_active is True

    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    user_tasks = (await db_session.scalars(query)).all()
    for task in user_tasks:
        assert task.is_active is True

    res = await client.delete("/api/users/1")
    assert res.status_code == 204
    assert test_user_with_tasks.is_active is False
    for task in user_tasks:
        assert task.is_active is False


async def test_restore_user(client, test_deleted_user):
    assert test_deleted_user.is_active is False

    res = await client.patch("/api/users/restore/1")
    assert res.status_code == 200
    user = res.json()
    assert user["name"] == "User_1"
    assert user["is_active"] is True
    assert user["updated_at"] is not None


async def test_login(client, test_user_without_tasks):
    res = await client.post(
        "/api/users/token",
        data={
            "username": test_user_without_tasks.email,
            "password": "12345678"
        }
    )
    assert res.status_code == 200
    dct = res.json()
    assert dct["access_token"] is not None
    assert dct["token_type"] == "bearer"


async def test_login_with_wrong_password(client, test_user_without_tasks):
    res = await client.post(
        "/api/users/token",
        data={
            "username": test_user_without_tasks.email,
            "password": "0000000000"
        }
    )
    assert res.status_code == 401
    assert res.json()["detail"] == 'Неверный адрес электронной почты или пароль'
