from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated

from .crud import Task_Crud
from app.modules.users.crud import UserCrud
from app.modules.users.models import User
from .schemas import TaskIn, TaskOut, TaskUpdate
from app.core.dependencies import get_task_crud, get_user_crud
from app.core.auth import get_current_user


tasks_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@tasks_router.get("/", response_model=list[TaskOut], status_code=status.HTTP_200_OK)
async def get_user_tasks(
    task_crud: Annotated[Task_Crud, Depends(get_task_crud)],
    user_crud: Annotated[UserCrud, Depends(get_user_crud)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100
):
    '''
    Возвращает активные задачи пользователя
    '''
    db_user = await user_crud.get_user(current_user.id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активный пользователь с ID: {current_user.id} не найден"
        )
    user_tasks = await task_crud.get_user_tasks(current_user.id, skip, limit)
    return user_tasks


@tasks_router.get("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    task_crud: Annotated[Task_Crud, Depends(get_task_crud)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    '''
    Возвращает данные о задаче с указанным ID
    '''

    db_task = await task_crud.get_task(task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активная задача с ID: {task_id} не найдена"
        )
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец имеет доступ к задаче"
        )
    return db_task


@tasks_router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskIn,
    task_crud: Annotated[Task_Crud, Depends(get_task_crud)],
    user_crud: Annotated[UserCrud, Depends(get_user_crud)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    '''
    Создает новую задачу
    '''
    db_user = await user_crud.get_user(current_user.id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активный пользователь с ID: {current_user.id} не найден"
        )
    new_task = await task_crud.create_task(task, current_user.id)
    return new_task


@tasks_router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int, task_update: TaskUpdate,
    task_crud: Annotated[Task_Crud, Depends(get_task_crud)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    '''
    Обновляет указанную задачу
    '''
    db_task = await task_crud.get_task(task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активная задача с ID: {task_id} не найдена"
        )
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец может изменить задачу"
        )
    task_dict = task_update.model_dump(exclude_unset=True)
    if not task_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Должно быть хотя-бы одно поле для изменения"
        )
    updated_task = await task_crud.update_task(task_id, task_dict)
    return updated_task


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    task_crud: Annotated[Task_Crud, Depends(get_task_crud)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    '''
    Выполняет мягкое удаление указанной задачи
    '''
    db_task = await task_crud.get_task(task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активная задача с ID: {task_id} не найдена"
        )
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только владелец может удалить задачу"
        )
    await task_crud.delete_task(task_id)
