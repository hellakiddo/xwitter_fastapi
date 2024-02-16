from datetime import timedelta, datetime
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.db import get_async_session
from database.models import User
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

auth = APIRouter(prefix='/auth',tags=['auth'])

SECRET_KEY = '2424245454545'
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


async def authenticate_user(username: str, password: str, db: AsyncSession):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == username))
        user = result.scalars().first()

    if not user.is_active:
        return None
    if not user or not sha256_crypt.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer), db: AsyncSession = Depends(get_async_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Данных нет. id или username.'
            )
        async with db.begin():
            user = await db.execute(select(User).filter(User.id == user_id, User.username == username))
            user = user.scalars().first()

        if not user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Пользователь не найден.'
            )

        if not user.is_active:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Пользователь не активирован.'
            )
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Токен сдох кажется. Не авторизован'
        )