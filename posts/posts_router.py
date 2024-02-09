import datetime
from http import HTTPStatus

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from auth.auth_router import get_current_user
from db import SessionLocal
from models import Post
from .posts_models import PostCreate

posts = APIRouter(tags=['posts'])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@posts.post("/create_post", response_model=PostCreate,status_code=HTTPStatus.CREATED)
async def create_post(
    post: PostCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = user.get('id')
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Authentication failed.'
        )
    new_post = Post(
        text=post.text,
        author_id=user_id,
        created_at=datetime.datetime.now()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return JSONResponse('Пост создан.')


@posts.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts