from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    text: str

class Post(BaseModel):
    id: int
    text: str
    created_at: Optional[datetime]
    author_id: Optional[int]

    class Config:
        orm_mode = True