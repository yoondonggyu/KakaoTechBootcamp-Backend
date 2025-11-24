from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class User:
    id: int
    email: str
    password: str
    nickname: str
    profile_image_url: str

@dataclass
class Post:
    id: int
    user_id: int
    title: str
    content: str
    image_url: str | None
    board_type: str = "couple"  # couple, planner, private
    tags: list[str] = field(default_factory=list)
    summary: str | None = None
    sentiment_score: float | None = None
    sentiment_label: str | None = None
    like_count: int = 0
    view_count: int = 0

@dataclass
class Comment:
    id: int
    post_id: int
    user_id: int
    content: str

USERS: Dict[int, User] = {}
USERS_BY_EMAIL: Dict[str, int] = {}
USERS_BY_NICK: Dict[str, int] = {}

POSTS: Dict[int, Post] = {}
COMMENTS: Dict[int, Comment] = {}
LIKES: Dict[int, Set[int]] = {}  # post_id -> set(user_id)

COUNTERS = {"user": 1, "post": 1, "comment": 1}
