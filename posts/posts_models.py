from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class PostCreate(BaseModel):
    text: str

class PostResponse(BaseModel):
    id: int
    text: str
    created_at: date
    author_id: Optional[int]

    class Config:
        orm_mode = True

# ====== Comments =====

class CommentCreate(BaseModel):
    text: str
    created_at: Optional[datetime]


class CommentResponse(BaseModel):
    id: Optional[int]
    text: str
    user_id: int
    post_id: int
    created_at: Optional[date]