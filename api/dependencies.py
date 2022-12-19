from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from jose import jwt, JWTError

from api.controller.user import UserController
from api.database import connection
from api.model.shared import TokenData
from api.model.user import User
from api.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/users/login")


def get_cursor():
    with connection.cursor() as cursor:
        yield cursor


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_user_controller(cursor=Depends(get_cursor), settings: Settings = Depends(get_settings)) -> UserController:
    return UserController(cursor, settings)


def get_current_user(token: str = Depends(oauth2_scheme), user_controller: UserController = Depends(get_user_controller), settings: Settings = Depends(get_settings)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_email_address = payload.get("sub")
        if user_email_address is None:
            raise credentials_exception
        token_data = TokenData(email_address=user_email_address)
    except JWTError:
        raise credentials_exception
    user = user_controller.get_user_by_email(token_data.email_address)
    if user is None or user.is_active is False:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user
