from fastapi import FastAPI
import models
from db import engine

# from posts.router import posts
# from user.router import users
from auth.auth_users_router import auth


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
# app.include_router(posts)
# app.include_router(users)
app.include_router(auth)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
