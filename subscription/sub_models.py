from typing import Optional

from pydantic import BaseModel

class SubscriptionResponse(BaseModel):
    follower_id: int
    following_id: int

class AllSubscriptionResponse(BaseModel):
    follower_id: int
    following_id: int
    following_username: str
    following_email: str

class SubscriptionCreate(BaseModel):
    pass
