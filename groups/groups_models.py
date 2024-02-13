from datetime import date
from typing import Optional, List
from pydantic import BaseModel

class GroupResponse(BaseModel):
    pass

class GroupCreate(GroupResponse):
    pass

class Group(GroupResponse):
    id: int

    class Config:
        orm_mode = True

class GroupPostResponse(BaseModel):
    id: int
    text: str
    created_at: date
    author_id: Optional[int]
    image: Optional[str]
    group_id: int

    class Config:
        orm_mode = True