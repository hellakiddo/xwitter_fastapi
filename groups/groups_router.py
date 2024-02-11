import base64
from datetime import datetime
from http import HTTPStatus
from typing import List

from bson import Binary
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from auth.auth_router import get_current_user
from db import get_async_session, images_collection
from posts.posts_models import PostResponse, PostCreate
from .groups_models import GroupResponse, GroupCreate
from models import Group, Post, GroupSubscription
from .serializers import serialize_group, serialize_group_posts

groups_router = APIRouter(tags=["groups"])


@groups_router.post("/create_group", response_model=GroupResponse, status_code=HTTPStatus.CREATED)
async def create_group(
        group: GroupCreate,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    group_data = group.dict()
    group_data["author_id"] = user["id"]
    new_group = Group(**group_data)

    try:
        async with db.begin():
            db.add(new_group)
            await db.commit()

        async with db.begin():
            await db.refresh(new_group)

        return serialize_group(new_group)

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Группа с таким именем или описанием уже существует."
        )



@groups_router.delete("/delete_group/{group_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_group(
        group_id: int,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    group = await db.execute(select(Group).filter(Group.id == group_id))
    group = group.scalars().first()
    if not group:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Группы нет, удалили."
        )
    if group.author_id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Вы не создали эту группу. Удалить нельзя."
        )

    await db.delete(group)
    await db.commit()

    return JSONResponse(content="Группа удалена")


@groups_router.get("/group/{group_id}", response_model=List[GroupResponse], status_code=HTTPStatus.OK)
async def get_group_posts(group_id: int, db: AsyncSession = Depends(get_async_session)):
    group = await db.execute(select(Group).filter(Group.id == group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Группы нет, удалили.")
    posts = await db.execute(select(Post).filter(Post.group_id == group_id))
    group_posts = posts.unique().scalars().all()

    return [serialize_group_posts(post) for post in group_posts]


@groups_router.post("/group/{group_id}/create_post", response_model=PostResponse, status_code=HTTPStatus.CREATED)
async def create_group_post(
    post: PostCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    group_id: int = Path(...),
):
    image_data = None
    if post.image:
        image_data = base64.b64decode(post.image)
    user_id = user.get('id')
    is_member = await db.execute(
        select(exists().where((GroupSubscription.group_id == group_id) & (GroupSubscription.user_id == user_id)))
    )
    if not is_member.scalar():
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Вы не являетесь участником этой группы."
        )

    new_post = Post(
        text=post.text,
        author_id=user_id,
        group_id=group_id,
        created_at=datetime.now(),
    )

    async with db.begin():
        db.add(new_post)
        await db.flush()

    if image_data:
        image_document = {
            "post_id": str(new_post.id),
            "image_data": Binary(image_data),
            "created_at": datetime.now()
        }
        images_collection.insert_one(image_document)

    return new_post
