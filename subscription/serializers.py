from models import User, Subscription

async def serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

async def serialize_subscription(subscription: Subscription, user: User):
    return {
        "follower_id": subscription.follower_id,
        "following_id": subscription.following_id,
        "following_username": user.username,
        "following_email": user.email,
    }