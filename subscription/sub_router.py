from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from auth.auth_router import get_current_user
from db import get_async_session
from models import Subscription, User
from .serializers import serialize_subscription, serialize_user
from .sub_models import SubscriptionCreate, AllSubscriptionResponse

subscriptions = APIRouter(tags=['subscriptions'])


@subscriptions.post("/users/{user_id}/create_subscription", response_model=SubscriptionCreate, status_code=HTTPStatus.CREATED)
async def create_subscription(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Path(...),
):
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Не аутентифицирован.'
        )

    new_subscription = Subscription(
        follower_id=user['id'],
        following_id=user_id
    )

    async with db.begin() as tx:
        db.add(new_subscription)
        await tx.commit()

    async with db.begin():
        await db.refresh(new_subscription)

    return JSONResponse('Подписка создана', status_code=HTTPStatus.CREATED)


@subscriptions.delete("/subscriptions/{subscription_id}/delete_subscription", status_code=HTTPStatus.NO_CONTENT)
async def delete_subscription(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    subscription_id: int = Path(...),
):
    subscription = await db.execute(select(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.follower_id == user['id']
    ))
    subscription = subscription.scalars().first()

    if not subscription:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Подписка не найдена или нет прав на удаление.'
        )

    await db.delete(subscription)
    await db.commit()

    return JSONResponse(content='Подписка удалена.')



@subscriptions.get("/users/{user_id}/subscriptions/")
async def get_subscriptions(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
        user_id: int = Path(...),
):
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Не аутентифицирован.'
        )

    subscriptions_query = select(Subscription).filter(
        Subscription.follower_id == user_id
    )
    subscriptions = await db.execute(subscriptions_query)
    subscriptions = subscriptions.scalars().all()
    if not subscriptions:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не подписан ни на кого.'
        )
    subscribed_users = []
    for subscription in subscriptions:
        following_user = await db.execute(
            select(User).filter(User.id == subscription.following_id)
        )
        following_user = following_user.scalar()

        if following_user:
            serialized_user = await serialize_user(following_user)
            subscribed_users.append(serialized_user)

    return subscribed_users



@subscriptions.get("/subscriptions", response_model=List[AllSubscriptionResponse])
async def current_user_subscriptions(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Не аутентифицирован.'
        )

    async with db.begin():
        subscriptions_query = select(Subscription).filter(
            Subscription.follower_id == user.get('id')
        )
        subscriptions = await db.execute(subscriptions_query)
        subscriptions = subscriptions.scalars().all()

        serialized_subscriptions = []
        for subscription in subscriptions:
            following_user = await db.execute(
                select(User).filter(User.id == subscription.following_id)
            )
            following_user = following_user.scalar()
            if following_user:
                serialized_subscription = await serialize_subscription(subscription, following_user)
                serialized_subscriptions.append(serialized_subscription)

    return serialized_subscriptions