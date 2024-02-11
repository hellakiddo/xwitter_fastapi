import secrets
from datetime import timedelta, datetime
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from sqlalchemy.future import select

from db import get_async_session
from .auth_models import CreateUser, Token, UserPassword
from models import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from celery_worker import send_confirm_email_task

auth = APIRouter(prefix='/auth',tags=['auth'])

SECRET_KEY = '2424245454545'
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


async def authenticate_user(username: str, password: str, db: AsyncSession):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == username))
        user = result.scalars().first()

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
                status_code=HTTPStatus.UNAUTHORIZED,
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
            detail='Токен сдох кажется.'
        )


@auth.post("/users", response_model=None, status_code=HTTPStatus.CREATED)
async def create_user(create_user_request: CreateUser, db: AsyncSession = Depends(get_async_session)):
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=sha256_crypt.hash(create_user_request.password),
        is_active=False,
        activation_code=secrets.token_urlsafe(32)
    )
    try:
        async with db.begin():
            db.add(create_user_model)
            await db.commit()

        send_confirm_email_task.delay(
            create_user_request.email,
            code=create_user_model.activation_code
        )

        return JSONResponse(
            content="Пользователь создан. На почту пришло письмо активации.",
            status_code=HTTPStatus.CREATED
        )

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Пользователь с таким именем или адресом электронной почты уже существует."
        )


@auth.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Пароль или username не тот.'
        )

    token = create_access_token(
        user.username, user.id, 'feed', timedelta(minutes=20)
    )

    return {'access_token': token, 'token_type': 'bearer'}


@auth.put("/change_password", status_code=HTTPStatus.OK)
async def change_password(
        user_password: UserPassword,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Проблемы аутентификации.'
        )
    async with db.begin():
        user_model = await db.execute(
            select(User).filter(User.id == user.get('id'))
        )
        user_model = user_model.scalars().first()
        if not sha256_crypt.verify(user_password.password, user_model.hashed_password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Старый пароль неверный.'
            )
        user_model.hashed_password = sha256_crypt.hash(user_password.new_password)
        await db.commit()

    return JSONResponse(
        content="Пароль изменен.",
        status_code=HTTPStatus.OK
    )

@auth.post("/activate/{activation_code}", status_code=HTTPStatus.OK)
async def activate_user(activation_code: str, db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        user = await db.execute(select(User).filter(User.activation_code == activation_code))
        user = user.scalars().first()
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Пользователь с указанным кодом активации не найден.'
            )
        user.is_active = True
        user.activation_code = None
        await db.commit()

    return JSONResponse(
        content="Пользователь успешно активирован.",
        status_code=HTTPStatus.OK
    )
