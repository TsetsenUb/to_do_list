from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from typing import Annotated

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .dependencies import get_user_crud
from app.modules.users.crud import UserCrud


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def create_access_token(data: dict):
    """
    Создаёт JWT с payload (sub, role, id, exp).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        user_crud: Annotated[UserCrud, Depends(get_user_crud)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    user = await user_crud.check_user_email(email)
    if not user or user.is_active is False:
        raise credentials_exception
    print("!!!", user.id, type(user.id))
    return user
