from typing import Optional
from pydantic import BaseModel

class GroupResponse(BaseModel):
    name: str
    description: Optional[str]
    id: Optional[int]
    author_id: Optional[int]

class GroupCreate(GroupResponse):
    pass

class Group(GroupResponse):
    id: int

    class Config:
        orm_mode = True
