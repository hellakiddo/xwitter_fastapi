# from fastapi import APIRouter
# from passlib.handlers.sha2_crypt import sha256_crypt
# from pydantic import BaseModel, EmailStr
# from starlette.responses import JSONResponse
#
# from .models import UserIn, UserInDB, UserOut
# # from db import client
#
# users = APIRouter()
#
#
#
# @users.post("/users", response_model=UserOut)
# async def create_user(form_data: UserIn):
#     hashed_password = sha256_crypt.hash(form_data.password)
#     form_data.hashed_password = hashed_password
#     client.local.users.insert_one(form_data.dict())
#     return UserOut(**form_data.dict())