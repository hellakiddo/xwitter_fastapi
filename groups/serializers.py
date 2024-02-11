from posts.serializers import serialize_user, serialize_comment, serialize_image


def serialize_group(group):
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "author_id": group.author_id
    }

def serialize_group_posts(post):
    return {
        "id": str(post.id),
        "name": [serialize_group(name) for name in post.group],
        "text": post.text,
        "author": serialize_user(post.author),
        "comments": [serialize_comment(comment) for comment in post.comments],
        "created_at": post.created_at,
        "images": [serialize_image(image) for image in post.images],
    }