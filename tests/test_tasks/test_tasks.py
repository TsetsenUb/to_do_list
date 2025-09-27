from sqlalchemy import select
from datetime import datetime, timedelta

from app.modules.tasks.models import Task


async def test_get_user_tasks_with_tasks(
        authenticated_client_with_tasks,
        test_user_with_tasks
):
    res = await authenticated_client_with_tasks.get("/api/tasks/")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 2
    assert tasks[0]["user_id"] == test_user_with_tasks.id
    assert tasks[0]["title"] == "Task_1"
    assert tasks[1]["user_id"] == test_user_with_tasks.id
    assert tasks[1]["title"] == "Task_2"


async def test_get_user_tasks_without_tasks(
        authenticated_client_without_tasks
):
    res = await authenticated_client_without_tasks.get("/api/tasks/")
    assert res.status_code == 200
    assert len(res.json()) == 0


async def test_get_task(
        authenticated_client_with_tasks,
        test_user_with_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    task = (await db_session.scalars(query)).first()
    assert task is not None

    res = await authenticated_client_with_tasks.get(
        f"/api/tasks/{task.id}"
    )
    assert res.status_code == 200
    task_check = res.json()
    assert task_check["id"] == task.id
    assert task_check["title"] == task.title


async def test_get_wrong_task(authenticated_client_with_tasks):
    res = await authenticated_client_with_tasks.get(
        "/api/tasks/1000"
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Активная задача с ID: 1000 не найдена"


async def test_get_task_not_owner(
        authenticated_client_without_tasks,
        test_user_with_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.id == test_user_with_tasks.id)
    )
    task = (await db_session.scalars(query)).first()

    res = await authenticated_client_without_tasks.get(
        f"/api/tasks/{task.id}"
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Только владелец имеет доступ к задаче"


async def test_create_task(
        authenticated_client_without_tasks,
        test_user_without_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_without_tasks.id)
    )
    user_tasks = (await db_session.scalars(query)).all()
    assert len(user_tasks) == 0

    res = await authenticated_client_without_tasks.post(
        "/api/tasks/",
        json={
            "title": "New Task"
        }
    )
    assert res.status_code == 201
    new_task = res.json()
    assert new_task["title"] == "New Task"
    assert new_task["user_id"] == test_user_without_tasks.id
    assert new_task["is_active"] is True

    user_tasks = (await db_session.scalars(query)).all()
    assert len(user_tasks) == 1
    assert user_tasks[0].title == "New Task"
    assert user_tasks[0].id == new_task["id"]


async def test_update_task(
        authenticated_client_with_tasks,
        test_user_with_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    user_task = (await db_session.scalars(query)).first()
    assert user_task is not None
    assert user_task.description is None
    assert user_task.updated_at is None
    assert user_task.due_date is None
    old_status = user_task.status.value
    old_priority = user_task.priority.value

    res = await authenticated_client_with_tasks.patch(
        f"/api/tasks/{user_task.id}",
        json={
            "title": "new title",
            "description": "new description",
            "status": "completed",
            "priority": "low",
            "due_date": f"{datetime.now() + timedelta(days=10)}"
        }
    )
    assert res.status_code == 200
    updated_task = res.json()
    assert updated_task["id"] == user_task.id
    assert updated_task["updated_at"] is not None
    assert updated_task["description"] == "new description"
    assert updated_task["due_date"] is not None
    assert updated_task["status"] == "completed"
    assert updated_task["status"] != old_status
    assert updated_task["priority"] == "low"
    assert updated_task["priority"] != old_priority


async def test_update_task_not_owner(
        authenticated_client_without_tasks,
        test_user_with_tasks,
        test_user_without_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    user_task = (await db_session.scalars(query)).first()
    assert user_task is not None
    assert user_task.user_id != test_user_without_tasks.id

    res = await authenticated_client_without_tasks.patch(
        f"/api/tasks/{user_task.id}",
        json={
            "description": "new description"
        }
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Только владелец может изменить задачу"


async def test_update_task_empty_fields(
        authenticated_client_with_tasks,
        test_user_with_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    user_task = (await db_session.scalars(query)).first()
    assert user_task is not None

    res = await authenticated_client_with_tasks.patch(
        f"/api/tasks/{user_task.id}",
        json={}
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Должно быть хотя-бы одно поле для изменения"


async def test_delete_task(
        authenticated_client_with_tasks,
        test_user_with_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    user_task = (await db_session.scalars(query)).first()
    assert user_task is not None
    assert user_task.is_active is True

    res = await authenticated_client_with_tasks.delete(
        f"/api/tasks/{user_task.id}"
    )
    assert res.status_code == 204
    assert user_task.is_active is False


async def test_delete_wrong_task(
        authenticated_client_with_tasks,
        test_user_with_tasks
):

    res = await authenticated_client_with_tasks.delete(
        "/api/tasks/1000"
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Активная задача с ID: 1000 не найдена"


async def test_delete_task_not_owner(
        authenticated_client_without_tasks,
        test_user_with_tasks,
        db_session
):
    query = (
        select(Task)
        .where(Task.user_id == test_user_with_tasks.id)
    )
    user_task = (await db_session.scalars(query)).first()
    assert user_task is not None
    assert user_task.is_active is True

    res = await authenticated_client_without_tasks.delete(
        f"/api/tasks/{user_task.id}"
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Только владелец может удалить задачу"
    assert user_task.is_active is True
