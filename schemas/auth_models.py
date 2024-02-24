from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserPassword(BaseModel):
    password: str
    new_password: str = Field(min_length=6)