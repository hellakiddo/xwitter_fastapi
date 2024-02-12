from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from auth.auth_router import get_current_user
from db import get_async_session
from models import Subscription, GroupSubscription, Post
from posts.posts_router import get_images_from_mongodb
from posts.serializers import serialize_post


feed_router = APIRouter(tags=['feed'])

@feed_router.get("/feed")
async def get_feed_posts(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    user_id = current_user.get('id')

    async with db.begin():
        following_user_ids = await get_following_user_ids(db, user_id)
        following_group_ids = await get_following_group_ids(db, user_id)
        user_posts = await get_user_posts(db, following_user_ids, db)
        group_posts = await get_group_posts(db, following_group_ids, db)
        all_posts = user_posts + group_posts
        for post in all_posts:
            post_id = str(post.id)
            images = await get_images_from_mongodb(post_id)
            post.images = images

        serialized_posts = [serialize_post(post) for post in all_posts]
        return serialized_posts


async def get_user_posts(db: AsyncSession, following_user_ids: List[int], transaction: AsyncSession):
    user_posts = await transaction.execute(
        select(Post).filter(Post.author_id.in_(following_user_ids))
        .options(joinedload(Post.comments), joinedload(Post.author))
    )
    return user_posts.unique().scalars().all()


async def get_group_posts(db: AsyncSession, following_group_ids: List[int], transaction: AsyncSession):
    group_posts = await transaction.execute(
        select(Post).filter(Post.group_id.in_(following_group_ids))
        .options(joinedload(Post.comments), joinedload(Post.author))
    )
    return group_posts.unique().scalars().all()


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
