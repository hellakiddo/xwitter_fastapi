from fastapi import FastAPI
import models
from db import engine

from posts.posts_router import posts
# from feed.router import users
from auth.auth_router import auth


app = FastAPI()
app.include_router(posts)
# app.include_router(users)
app.include_router(auth)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
