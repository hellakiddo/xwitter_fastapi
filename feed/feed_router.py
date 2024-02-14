from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from auth.auth_router import get_current_user
from db import get_async_session
from models import Subscription, GroupSubscription, Post
from posts.posts_models import PostWithCommentsResponse

feed_router = APIRouter(tags=['feed'])

@feed_router.get("/feed", response_model=List[PostWithCommentsResponse])
async def get_feed_posts(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    user_id = current_user.get('id')

    async with db.begin():
        following_user_ids = await get_following_user_ids(db, user_id)
        following_group_ids = await get_following_group_ids(db, user_id)
        user_posts = await get_posts(db, Post.author_id.in_(following_user_ids), db)
        group_posts = await get_posts(db, Post.group_id.in_(following_group_ids), db)
        return user_posts + group_posts

async def get_posts(db: AsyncSession, condition, transaction: AsyncSession):
    posts = await transaction.execute(
        select(Post).filter(condition).options(joinedload(Post.comments), joinedload(Post.author))
    )
    return posts.unique().scalars().all()

async def get_following_user_ids(db: AsyncSession, user_id: int):
    subscriptions = await db.execute(
        select(Subscription.following_id).filter(Subscription.follower_id == user_id)
    )
    return [sub.following_id for sub in subscriptions]

async def get_following_group_ids(db: AsyncSession, user_id: int):
    group_subscriptions = await db.execute(
        select(GroupSubscription.group_id).filter(GroupSubscription.user_id == user_id)
    )
    return [group_sub.group_id for group_sub in group_subscriptions]
