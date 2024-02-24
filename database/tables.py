from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, MetaData, Table, Text, DateTime

metadata = MetaData()

subscriptions = Table(
    "subscriptions",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("follower_id", Integer, ForeignKey("users.id")),
    Column("following_id", Integer, ForeignKey("users.id")),
)

group_subscriptions = Table(
    "group_subscriptions",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("groups.id")),
)

groups = Table(
    "groups",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, unique=True, index=True),
    Column("description", String),
    Column("author_id", Integer, ForeignKey("users.id")),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("email", String, unique=True, index=True),
    Column("username", String, unique=True, index=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("hashed_password", String),
    Column("is_active", Boolean, default=True),
    Column("activation_code", String, unique=False, nullable=False),
)

comments = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("text", String),
    Column("created_at", Date, default=datetime.now),
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("text", String),
    Column("created_at", Date, default=datetime.now),
    Column("author_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("groups.id"), nullable=True),
    Column("image", String, nullable=True),
)

chat_messages_table = Table(
    "chat_messages",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, index=True),
    Column("room_id", Integer, index=True),
    Column("content", String),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

private_messages_table = Table(
    "private_messages",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("sender_id", Integer, index=True),
    Column("receiver_id", Integer, index=True),
    Column("content", String),
    Column("timestamp", DateTime, default=datetime.utcnow),
)
