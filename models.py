from datetime import datetime

from DateTime import DateTime
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from db import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    followers = relationship("Subscription", foreign_keys=[Subscription.following_id], back_populates="follower")
    following = relationship("Subscription", foreign_keys=[Subscription.follower_id], back_populates="following")
    comments = relationship("Comment", back_populates="user")
    posts = relationship("Post", back_populates="author")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(Date, default=datetime.date)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    post = relationship("Post", back_populates="comments")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(Date, default=datetime.date)
    author_id = Column(Integer, ForeignKey("users.id"))

    comments = relationship("Comment", back_populates="post")
    author = relationship("User", back_populates="posts")