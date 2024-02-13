from fastapi import UploadFile
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict


class PostCreate(BaseModel):
    text: str
    image: Optional[UploadFile]
    group_id: Optional[int]


class PostResponse(BaseModel):
    id: int
    text: str
    created_at: date
    author_id: Optional[int]
    image: Optional[str]

    class Config:
        orm_mode = True



# ====== Comments =====

class CommentCreate(BaseModel):
    text: str
    created_at: Optional[date]


class CommentResponse(BaseModel):
    id: int
    text: str
    user_id: int
    post_id: int
    created_at: date

class PostWithCommentsResponse(BaseModel):
    id: int
    text: str
    created_at: date
    author_id: Optional[int]
    image: Optional[str]
    comments: List

    class Config:
        orm_mode = True