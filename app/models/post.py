from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, BigInteger, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Many-to-Many association table for Post and Tag
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    image_class = Column(String(50), nullable=True)  # 이미지 분류 결과 (Dog/Cat)
    board_type = Column(String(50), default="couple")
    summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(50), nullable=True)
    like_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="posts")
    comments = relationship("Comment", backref="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", backref="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=post_tags, backref="posts")

class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
