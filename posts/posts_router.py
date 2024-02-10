import datetime
from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette.responses import JSONResponse
from sqlalchemy.future import select

from auth.auth_router import get_current_user
from db import get_async_session
from models import Post, Comment
from .posts_models import PostCreate, CommentCreate, CommentResponse, PostResponse
from .serializers import serialize_post

posts = APIRouter(tags=['posts'])


@posts.post("/create_post", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
    post: PostCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Не аутентифицирован.'
        )

    new_post = Post(
        text=post.text,
        author_id=user_id,
        created_at=datetime.datetime.now()
    )

    async with db.begin() as tx:
        db.add(new_post)
        await tx.commit()

    async with db.begin():
        await db.refresh(new_post)

    return new_post

@posts.delete("/posts/{post_id}/delete_post", status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    post = await db.execute(select(Post).filter(Post.author_id == user_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Нет прав на его удаление.'
        )
    if not db.is_active:
        async with db.begin():
            await db.delete(post)
            await db.commit()
    else:
        await db.delete(post)
        await db.commit()

    return JSONResponse(content='Пост удален.')

@posts.post("/posts/{post_id}/create_comment", response_model=CommentResponse, status_code=HTTPStatus.CREATED)
async def create_comment(
    comment: CommentCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    post_id: int = Path(...),
):
    user_id = user.get('id')
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Не аутентифицирован.'
        )

    new_comment = Comment(
        text=comment.text,
        user_id=user_id,
        post_id=post_id,
        created_at=datetime.datetime.now()
    )

    async with db.begin():
        db.add(new_comment)
        await db.commit()

    async with db.begin():
        await db.refresh(new_comment)

    comment_response = CommentResponse(
        id=new_comment.id,
        text=new_comment.text,
        user_id=new_comment.user_id,
        post_id=new_comment.post_id,
        created_at=new_comment.created_at
    )

    return comment_response


@posts.delete("/posts/{post_id}/delete_comment/{comment_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_comment(
        comment_id: int,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    comment = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = comment.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Нет такого коммента."
        )
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Вы его не создали. Удалить нельзя"
        )

    await db.delete(comment)
    await db.commit()

    return JSONResponse(content="Удален коммент")

@posts.get("/")
async def get_posts(db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        all_posts = await db.execute(
            select(Post).options(joinedload(Post.comments), joinedload(Post.author))
        )
        serialized_posts = [serialize_post(post) for post in all_posts.unique().scalars().all()]
        return serialized_posts

