from models import Post, Comment, User

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

def serialize_post(post: Post) -> dict:
    return {
        "id": post.id,
        "text": post.text,
        "created_at": post.created_at,
        "author": serialize_user(post.author),
        "comments": [serialize_comment(comment) for comment in post.comments],
    }
