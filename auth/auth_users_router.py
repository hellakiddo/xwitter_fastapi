from datetime import timedelta, datetime
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db import SessionLocal
from .auth_models import CreateUser, Token, UserPassword
from models import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

auth = APIRouter(prefix='/auth',tags=['auth'])

SECRET_KEY = '2424245454545'
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not sha256_crypt.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Данных нет. id или username.'
            )
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Такого незнаю.'
        )


@auth.post("/users", response_model=None, status_code=HTTPStatus.CREATED)
async def create_user(create_user_request: CreateUser, db: Session = Depends(get_db)):
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=sha256_crypt.hash(create_user_request.password),
        is_active=False,
    )

    db.add(create_user_model)
    db.commit()
    return JSONResponse(
        "Пользователь создан. Иди за токеном"
    )


@auth.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail='Пароль или username не тот.')
    token = create_access_token(
        user.username, user.id, 'user', timedelta(minutes=20)
    )

    return {'access_token': token, 'token_type': 'bearer'}


@auth.put("/change_password", status_code=HTTPStatus.OK)
async def change_password(
    user_password: UserPassword,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Проблемы аутентификации.'
        )
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not sha256_crypt.verify(user_password.password, user_model.hashed_password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Старый пароль неверный.'
        )
    user_model.hashed_password = sha256_crypt.hash(user_password.new_password)
    db.add(user_model)
    db.commit()
    return JSONResponse(
        "Пароль изменен."
    )
