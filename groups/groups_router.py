import uuid
from datetime import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from auth.auth_router import get_current_user
from db import get_async_session
from posts.posts_models import PostResponse
from posts.posts_router import save_image_async
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


@groups_router.get("/group/{group_id}", status_code=HTTPStatus.OK)
async def get_group_posts(group_id: int, db: AsyncSession = Depends(get_async_session)):
    group = await db.execute(select(Group).filter(Group.id == group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Группы нет, удалили.")
    posts = await db.execute(select(Post).filter(Post.group_id == group_id))
    group_posts = posts.unique().scalars().all()

    return group_posts


@groups_router.post("/group/{group_id}/create_post", response_model=PostResponse, status_code=HTTPStatus.CREATED)
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
        created_at=datetime.now(),
        image=image.filename
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



@groups_router.post("/group/{group_id}/subscribe", status_code=HTTPStatus.NO_CONTENT)
async def subscribe_to_group(
        group_id: int,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    try:
        async with db.begin():
            is_subscribed = await db.execute(
                select(exists().where((GroupSubscription.group_id == group_id) & (GroupSubscription.user_id == user_id)))
            )
            if is_subscribed.scalar():
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail="Вы уже подписаны на эту группу."
                )
            new_subscription = GroupSubscription(user_id=user_id, group_id=group_id)
            db.add(new_subscription)
            await db.commit()

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Вы уже подписаны на эту группу."
        )

    return JSONResponse(content="Вы подписались на группу")


@groups_router.delete("/group/{group_id}/unsubscribe", status_code=HTTPStatus.NO_CONTENT)
async def unsubscribe_from_group(
        group_id: int,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    user_id = user.get('id')
    try:
        async with db.begin():
            subscription = await db.execute(
                select(GroupSubscription).filter(
                    (GroupSubscription.group_id == group_id) & (GroupSubscription.user_id == user_id)
                ).options(selectinload(GroupSubscription.group))
            )
            subscription = subscription.scalars().first()

            if not subscription:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Вы не подписаны на эту группу."
                )
            await db.delete(subscription)
            await db.commit()

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Вы не подписаны на эту группу."
        )

    return JSONResponse(content="Вы отписались от группы")