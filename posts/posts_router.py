import datetime
import os
import uuid
from http import HTTPStatus
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Path, Form, UploadFile
from sqlalchemy.orm import joinedload
from starlette.responses import JSONResponse
from sqlalchemy.future import select

from auth.auth_router import get_current_user
from database.db import get_async_session
from database.models import Post, Comment
from .posts_models import CommentCreate, CommentResponse, PostResponse, PostWithCommentsResponse

posts = APIRouter(tags=['posts'])


@posts.post("/create_post", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_post(
        text: str = Form(...),
        image: UploadFile = Form(...),
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    image_data = await image.read()
    image_filename = f"{uuid.uuid4()}.jpg"
    user_id = user.get('id')
    new_post = Post(
        text=text,
        author_id=user_id,
        created_at=datetime.datetime.now(),
        image=f'/uploaded_images/{image_filename}'
    )
    async with db.begin() as tx:
        db.add(new_post)
        await tx.commit()

    async with db.begin():
        await db.refresh(new_post)

    if image_data:
        image_url = await save_image_async(image_data, image_filename)
        new_post.image = image_url

    return new_post


async def save_image_async(image_data, image_filename):
    upload_folder = "uploaded_images"
    os.makedirs(upload_folder, exist_ok=True)
    image_path = os.path.join(upload_folder, image_filename)
    with open(image_path, "wb") as img_file:
        img_file.write(image_data)
    return f"/uploaded_images/{image_filename}"


@posts.delete("/posts/{post_id}/delete_post", status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
        post_id: int = Path(...),
        user: dict = Depends(get_current_user, ),
        db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    post = await db.execute(select(Post).filter(Post.author_id == user_id, Post.id == post_id))
    post_found = post.scalars().first()
    if not post_found:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Нет прав на удаление или пост не найден.'
        )

    if not db.is_active:
        async with db.begin():
            await db.delete(post_found)
            await db.commit()
    else:
        await db.delete(post_found)
        await db.commit()

    return JSONResponse(content='Пост удален.')


@posts.post("/posts/{post_id}/create_comment", response_model=CommentResponse, status_code=HTTPStatus.CREATED)
async def create_comment(
        comment: CommentCreate,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
        post_id: int = Path(...),
):
    new_comment = Comment(
        text=comment.text,
        user_id=user["id"],
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
        post_id=post_id,
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


@posts.get("/", response_model=List[PostWithCommentsResponse])
async def get_all_posts(db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        all_posts = await db.execute(select(Post).options(joinedload(Post.comments)))
        posts = all_posts.unique().scalars().all()
    return posts
