import base64

from models import Post, Comment, User, Group
from posts.posts_models import CommentResponse


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

def serialize_comment(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "text": comment.text,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "created_at": comment.created_at
    }

def serialize_group(group: Group) -> dict:
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
    }
def serialize_image(image):
    return {
        "post_id": image.get("post_id", ""),
        "image_data": base64.b64encode(image.get("image_data", b"")).decode("utf-8"),
        "created_at": image.get("created_at", ""),
    }

def serialize_post(post):
    return {
        "id": str(post.id),
        "text": post.text,
        "author": serialize_user(post.author),
        "comments": [serialize_comment(comment) for comment in post.comments],
        "created_at": post.created_at,
        "images": post.image,
    }


def serialize_post_with_comments(post: Post):
    serialized_post = serialize_post(post)
    serialized_post["comments"] = [serialize_comment(comment) for comment in post.comments]
    return serialized_post

