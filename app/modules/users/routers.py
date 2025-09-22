from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from .crud import UserCrud
from .schemas import UserIn, UserOut
from app.core.dependencies import get_user_crud
from app.core.security import verify_password
from app.core.auth import create_access_token


users_router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@users_router.get('/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, user_crud: Annotated[UserCrud, Depends(get_user_crud)]):
    '''
    Получение данных о пользователе
    '''
    db_user = await user_crud.get_user(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активный пользователь с ID: {user_id} не найден"
        )
    return db_user


@users_router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn, user_crud: Annotated[UserCrud, Depends(get_user_crud)]):
    '''
    Создание нового пользователя с проверкой на уникальность почты
    '''
    if await user_crud.check_user_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {user.email} уже зарегистрирован"
        )

    new_user = await user_crud.create_user(user)
    return new_user


@users_router.post("/token")
async def login(
    user_crud: Annotated[UserCrud, Depends(get_user_crud)],
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Аутентифицирует пользователя и возвращает JWT с email и id.
    """
    user = await user_crud.check_user_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный адрес электронной почты или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.patch('/restore/{user_id}', response_model=UserOut, status_code=status.HTTP_200_OK)
async def restore_user(user_id: int, user_crud: Annotated[UserCrud, Depends(get_user_crud)]):
    '''
    Восстановление удаленного пользователя
    '''
    db_user = await user_crud.get_user(user_id, active=False)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Удаленный пользователь с ID: {user_id} не найден"
        )
    restored_user = await user_crud.restore_user(user_id)
    return restored_user


@users_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user_crud: Annotated[UserCrud, Depends(get_user_crud)]):
    '''
    Мягкое удаление пользователя с указанным ID
    '''
    db_user = await user_crud.get_user(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID: {user_id} не найден"
        )
    await user_crud.delete_user(user_id)
