from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.handlers.sha2_crypt import sha256_crypt

from auth.token_jwt import create_jwt_token
from db import client, users_collection

auth = APIRouter()

def fake_hash_password(password: str):
    return password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@auth.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = users_collection.find_one({"username": form_data.username})
    if not user_dict or not sha256_crypt.verify(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token_expires = timedelta(minutes=500)
    jwt_token = create_jwt_token({"sub": user_dict["username"]}, expires_delta=token_expires)

    return {"access_token": jwt_token, "token_type": "bearer"}

