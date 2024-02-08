from typing import Optional

from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str
    hashed_password: Optional[str] = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str

