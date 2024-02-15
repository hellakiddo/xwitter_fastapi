from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, MetaData, Table
from sqlalchemy.orm import relationship

from db import Base

# в отдельную папку и


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
    Column("activation_code", String, unique=True, nullable=False),
)

comments = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("text", String),
    Column("created_at", Date, default=datetime.date),
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("text", String),
    Column("created_at", Date, default=datetime.date),
    Column("author_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("groups.id"), nullable=True),
    Column("image", String, nullable=True),
)
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")


class GroupSubscription(Base):
    __tablename__ = "group_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    user = relationship("User", back_populates="group_subscriptions")
    group = relationship("Group", back_populates="user_subscriptions")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))

    user_subscriptions = relationship("GroupSubscription", back_populates="group")
    posts = relationship("Post", back_populates="group")
    author = relationship("User", back_populates="groups")
    members = relationship(
        "User",
        secondary="group_subscriptions",
        back_populates="groups",
        overlaps="group_subscriptions,user_subscriptions",
        viewonly=True
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    activation_code = Column(String, unique=True, nullable=False)

    followers = relationship("Subscription", foreign_keys=[Subscription.following_id], back_populates="follower")
    following = relationship("Subscription", foreign_keys=[Subscription.follower_id], back_populates="following")
    comments = relationship("Comment", back_populates="user")
    posts = relationship("Post", back_populates="author")
    group_subscriptions = relationship("GroupSubscription", back_populates="user")
    groups = relationship(
        "Group",
        secondary="group_subscriptions",
        back_populates="members",
        overlaps="group_subscriptions,user_subscriptions",
        viewonly=True
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(Date, default=datetime.date)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    post = relationship("Post", back_populates="comments")

# все модели разделить
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(Date, default=datetime.date)
    author_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    image = Column(String, nullable=True)

    comments = relationship("Comment", back_populates="post")
    author = relationship("User", back_populates="posts")
    group = relationship("Group", back_populates="posts")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)