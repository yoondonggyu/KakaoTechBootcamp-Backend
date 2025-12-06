"""
pytest configuration and fixtures for FASTAPI_Project_back

테스트 설정 및 공통 Fixture 정의
- 인메모리 SQLite 데이터베이스로 격리된 테스트 환경 제공
- 각 테스트마다 깨끗한 DB 상태 보장
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from unittest.mock import patch, MagicMock
import hashlib

# 상대 임포트를 위한 sys.path 설정
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import get_db

# ============================================================================
# 테스트 데이터베이스 설정
# ============================================================================

TestBase = declarative_base()
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Many-to-Many association table for Post and Tag
test_post_tags = Table(
    "post_tags",
    TestBase.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================================
# 테스트용 ORM 모델 (실제 모델과 동일한 구조, SQLite 호환)
# ============================================================================

class TestUser(TestBase):
    """테스트용 User 모델"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    profile_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TestPost(TestBase):
    """테스트용 Post 모델"""
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    image_class = Column(String(50), nullable=True)
    board_type = Column(String(50), default="couple")
    summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(50), nullable=True)
    like_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("TestUser", backref="posts")
    comments = relationship("TestComment", backref="post", cascade="all, delete-orphan")
    likes = relationship("TestPostLike", backref="post", cascade="all, delete-orphan")
    tags = relationship("TestTag", secondary=test_post_tags, backref="posts")


class TestPostLike(TestBase):
    """테스트용 PostLike 모델"""
    __tablename__ = "post_likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())


class TestComment(TestBase):
    """테스트용 Comment 모델"""
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sentiment_label = Column(String(20), nullable=True)
    sentiment_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TestTag(TestBase):
    """테스트용 Tag 모델"""
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# 헬퍼 함수
# ============================================================================

def override_get_db():
    """테스트용 데이터베이스 세션 의존성"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def simple_hash(password: str) -> str:
    """간단한 해시 함수 (테스트용)"""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================================
# 기본 Fixture
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    각 테스트마다 새로운 데이터베이스 생성

    Scope: function - 테스트 함수마다 새로운 DB
    Yield: 테스트 실행 후 모든 테이블 삭제
    """
    TestBase.metadata.create_all(bind=engine)
    yield
    TestBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    테스트 클라이언트 Fixture

    FastAPI TestClient를 생성하고 DB 의존성을 오버라이드
    테스트 종료 후 자동으로 정리됨
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session(test_db):
    """직접 DB 조작이 필요할 때 사용하는 세션 Fixture"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ============================================================================
# 테스트 데이터 Fixture
# ============================================================================

@pytest.fixture
def test_user_data():
    """
    테스트용 사용자 데이터

    Returns:
        dict: 회원가입에 필요한 모든 필드
    """
    return {
        "email": "test@example.com",
        "password": "Test1234!@#$",
        "password_check": "Test1234!@#$",
        "nickname": "테스트유저",
        "profile_image_url": "https://example.com/image.jpg"
    }


@pytest.fixture
def test_user_data_2():
    """두 번째 테스트 사용자 (중복 테스트용)"""
    return {
        "email": "test2@example.com",
        "password": "Test5678!@#$",
        "password_check": "Test5678!@#$",
        "nickname": "테스트유저2",
        "profile_image_url": "https://example.com/image2.jpg"
    }


@pytest.fixture
def test_post_data():
    """
    테스트용 게시글 데이터

    Returns:
        dict: 게시글 생성에 필요한 필드
    """
    return {
        "title": "테스트 게시글 제목",
        "content": "테스트 게시글 내용입니다. 충분히 긴 내용으로 작성합니다.",
        "board_type": "couple"
    }


@pytest.fixture
def test_comment_data():
    """테스트용 댓글 데이터"""
    return {
        "content": "테스트 댓글 내용입니다."
    }


# ============================================================================
# 인증 관련 Fixture
# ============================================================================

@pytest.fixture
def registered_user(client, test_user_data, db_session):
    """
    회원가입 완료된 사용자

    DB에 직접 사용자를 생성하여 테스트 환경 준비

    Returns:
        dict: {"user_data": 원본 데이터, "user_id": DB에 저장된 ID}
    """
    # 실제 서비스는 평문 비밀번호를 사용함 (해시 없음)
    user = TestUser(
        email=test_user_data["email"],
        password=test_user_data["password"],  # 평문 비밀번호
        nickname=test_user_data["nickname"],
        profile_image_url=test_user_data["profile_image_url"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return {
        "user_data": test_user_data,
        "user_id": user.id
    }


@pytest.fixture
def registered_user_2(client, test_user_data_2, db_session):
    """두 번째 등록된 사용자"""
    # 실제 서비스는 평문 비밀번호를 사용함 (해시 없음)
    user = TestUser(
        email=test_user_data_2["email"],
        password=test_user_data_2["password"],  # 평문 비밀번호
        nickname=test_user_data_2["nickname"],
        profile_image_url=test_user_data_2["profile_image_url"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return {
        "user_data": test_user_data_2,
        "user_id": user.id
    }


@pytest.fixture
def logged_in_user(client, registered_user):
    """로그인된 사용자 정보"""
    return {
        "user_id": registered_user["user_id"],
        "user_data": registered_user["user_data"]
    }


@pytest.fixture
def auth_header(logged_in_user):
    """
    인증 헤더

    X-User-Id 헤더를 포함한 dict 반환
    인증이 필요한 API 호출 시 사용
    """
    if logged_in_user and logged_in_user.get("user_id"):
        return {"X-User-Id": str(logged_in_user["user_id"])}
    return {}


@pytest.fixture
def auth_header_2(registered_user_2):
    """두 번째 사용자의 인증 헤더"""
    return {"X-User-Id": str(registered_user_2["user_id"])}


# ============================================================================
# 게시글/댓글 Fixture
# ============================================================================

@pytest.fixture
def created_post(client, auth_header, test_post_data, db_session, logged_in_user):
    """
    생성된 게시글

    테스트에서 바로 사용할 수 있는 게시글 생성
    """
    post = TestPost(
        user_id=logged_in_user["user_id"],
        title=test_post_data["title"],
        content=test_post_data["content"],
        board_type=test_post_data.get("board_type", "couple")
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    return {
        "post_id": post.id,
        "post_data": test_post_data,
        "user_id": logged_in_user["user_id"]
    }


@pytest.fixture
def created_comment(db_session, created_post, logged_in_user, test_comment_data):
    """생성된 댓글"""
    comment = TestComment(
        content=test_comment_data["content"],
        post_id=created_post["post_id"],
        user_id=logged_in_user["user_id"]
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)

    return {
        "comment_id": comment.id,
        "comment_data": test_comment_data,
        "post_id": created_post["post_id"],
        "user_id": logged_in_user["user_id"]
    }


# ============================================================================
# Mock Fixture (외부 서비스 의존성 제거)
# ============================================================================

@pytest.fixture
def mock_model_client():
    """
    모델 서비스 클라이언트 Mock

    외부 AI 모델 서비스 호출을 Mock으로 대체
    테스트가 외부 서비스 없이도 동작하도록 함
    """
    with patch('app.services.model_client.ModelClient') as mock:
        instance = MagicMock()
        instance.analyze_sentiment.return_value = {
            "label": "positive",
            "confidence": 0.95
        }
        instance.summarize.return_value = {
            "summary": "테스트 요약 내용입니다."
        }
        instance.classify_image.return_value = {
            "class": "Dog",
            "confidence": 0.85
        }
        mock.return_value = instance
        yield mock


# ============================================================================
# 유틸리티 Fixture
# ============================================================================

@pytest.fixture
def valid_png_image():
    """유효한 PNG 이미지 바이너리 (1x1 픽셀)"""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'


@pytest.fixture
def valid_jpeg_image():
    """유효한 JPEG 이미지 바이너리 (최소 헤더)"""
    return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'
