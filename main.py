from fastapi import FastAPI

from posts.posts_router import posts
from subscription.sub_router import subscriptions
from auth.auth_router import auth
from groups.groups_router import groups_router


app = FastAPI()
app.include_router(posts)
app.include_router(subscriptions)
app.include_router(auth)
app.include_router(groups_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
