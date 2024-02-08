# from fastapi import APIRouter
# # from db import client
# from posts.mongo_schemas import all_posts, one_post
# from posts.models import Post
#
# posts = APIRouter()
#
# @posts.get("/")
# async def home():
#     return all_posts(client.local.posts.find({},{'_id': 0}))
#
# @posts.post("/add_post")
# async def add_post(post: Post):
#     client.local.posts.insert_one(post.dict())
#     return post.dict()
#
