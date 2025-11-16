# main_routes_only.py
# 2-1 단계: Route만 이용해서 요청에 응답하는 백엔드
from fastapi import FastAPI, UploadFile, File, Path, Header, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, HttpUrl
import os
import uuid
import re

app = FastAPI(title="Routes Only - Community API")

# ========== 루트 경로 ==========
@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Community API (Routes Only)",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api"
    }

# ========== 데이터 저장소 (Route 내에서 직접 관리) ==========
USERS = {}
USERS_BY_EMAIL = {}
USERS_BY_NICK = {}
POSTS = {}
COMMENTS = {}
LIKES = {}  # post_id -> set(user_id)
COUNTERS = {"user": 1, "post": 1, "comment": 1}

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== Pydantic 스키마 ==========
class LoginReq(BaseModel):
    email: str
    password: str

class SignupReq(BaseModel):
    email: str
    password: str
    password_check: str
    nickname: str
    profile_image_url: HttpUrl

class NicknamePatchReq(BaseModel):
    nickname: str

class PasswordUpdateReq(BaseModel):
    old_password: str
    password: str
    password_check: str

class PostCreateReq(BaseModel):
    title: str
    content: str
    image_url: Optional[HttpUrl] = None

class PostUpdateReq(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class CommentCreateReq(BaseModel):
    content: str

class CommentUpdateReq(BaseModel):
    content: str

# ========== 헬퍼 함수 (Route 내에서 사용) ==========
def get_current_user_id(x_user_id: Optional[int] = Header(None)):
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    return x_user_id

# ========== 인증 API ==========
@app.post("/api/auth/login")
async def login(req: LoginReq):
    """로그인 - Route에서 직접 처리"""
    # 이메일 검증
    if not req.email:
        return JSONResponse(status_code=400, content={"message": "email_required", "data": None})
    
    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    if not email_pattern.match(req.email):
        return JSONResponse(status_code=400, content={"message": "invalid_email_format", "data": None})
    
    # 로그인 처리
    user_id = USERS_BY_EMAIL.get(req.email)
    if not user_id or user_id not in USERS:
        return JSONResponse(status_code=401, content={"message": "invalid_credentials", "data": None})
    
    user = USERS[user_id]
    if user["password"] != req.password:
        return JSONResponse(status_code=401, content={"message": "invalid_credentials", "data": None})
    
    return {
        "message": "login_success",
        "data": {
            "user_id": user["id"],
            "nickname": user["nickname"],
            "profile_image_url": user["profile_image_url"]
        }
    }

@app.post("/api/auth/signup", status_code=201)
async def signup(req: SignupReq):
    """회원가입 - Route에서 직접 처리"""
    # 이메일 검증
    if not req.email:
        return JSONResponse(status_code=400, content={"message": "email_required", "data": None})
    
    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    if not email_pattern.match(req.email):
        return JSONResponse(status_code=400, content={"message": "invalid_email_format", "data": None})
    
    if req.email in USERS_BY_EMAIL:
        return JSONResponse(status_code=409, content={"message": "duplicate_email", "data": None})
    
    # 비밀번호 검증
    if not req.password or len(req.password) < 8 or len(req.password) > 20:
        return JSONResponse(status_code=400, content={"message": "invalid_password_format", "data": None})
    
    if req.password != req.password_check:
        return JSONResponse(status_code=422, content={"message": "password_mismatch", "data": None})
    
    # 닉네임 검증
    if not req.nickname:
        return JSONResponse(status_code=400, content={"message": "nickname_required", "data": None})
    if " " in req.nickname:
        return JSONResponse(status_code=400, content={"message": "nickname_contains_space", "data": None})
    if len(req.nickname) > 10:
        return JSONResponse(status_code=400, content={"message": "nickname_too_long", "data": {"max_length": 10}})
    
    if req.nickname in USERS_BY_NICK:
        return JSONResponse(status_code=409, content={"message": "duplicate_nickname", "data": None})
    
    # 사용자 생성
    user_id = COUNTERS["user"]
    COUNTERS["user"] += 1
    
    user = {
        "id": user_id,
        "email": req.email,
        "password": req.password,
        "nickname": req.nickname,
        "profile_image_url": str(req.profile_image_url)
    }
    
    USERS[user_id] = user
    USERS_BY_EMAIL[req.email] = user_id
    USERS_BY_NICK[req.nickname] = user_id
    
    return {"message": "register_success", "data": {"user_id": user_id}}

# ========== 사용자 API ==========
@app.post("/api/users/profile/upload")
async def upload_profile_image(file: UploadFile = File(...)):
    """프로필 이미지 업로드 - Route에서 직접 처리"""
    if not file:
        return JSONResponse(status_code=400, content={"message": "file_required", "data": None})
    
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        return JSONResponse(status_code=400, content={"message": "invalid_file_type", "data": {"allowed": ["jpg", "png", "jpeg"]}})
    
    file_data = await file.read()
    if len(file_data) > 5 * 1024 * 1024:
        return JSONResponse(status_code=413, content={"message": "file_too_large", "data": {"max_size": "5MB"}})
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    url = f"https://cdn.example.com/{filename}"
    return {"message": "upload_success", "data": {"profile_image_url": url}}

@app.patch("/api/users/profile")
async def patch_nickname(req: NicknamePatchReq, x_user_id: Optional[int] = Header(None)):
    """닉네임 수정 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if x_user_id not in USERS:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    # 닉네임 검증
    if not req.nickname:
        return JSONResponse(status_code=422, content={"message": "validation_failed", "data": {"field": "nickname", "reason": "nickname_blank"}})
    if " " in req.nickname:
        return JSONResponse(status_code=422, content={"message": "validation_failed", "data": {"field": "nickname", "reason": "nickname_has_space"}})
    if len(req.nickname) > 10:
        return JSONResponse(status_code=422, content={"message": "validation_failed", "data": {"field": "nickname", "reason": "nickname_too_long"}})
    
    # 중복 검사
    if req.nickname in USERS_BY_NICK and USERS_BY_NICK[req.nickname] != x_user_id:
        return JSONResponse(status_code=409, content={"message": "duplicate_nickname", "data": None})
    
    # 닉네임 업데이트
    old_nickname = USERS[x_user_id]["nickname"]
    if old_nickname != req.nickname:
        USERS_BY_NICK.pop(old_nickname, None)
        USERS_BY_NICK[req.nickname] = x_user_id
        USERS[x_user_id]["nickname"] = req.nickname
    
    return {"message": "update_profile_success", "data": {"nickname": req.nickname}}

@app.delete("/api/users/profile")
async def delete_user(x_user_id: Optional[int] = Header(None)):
    """회원 탈퇴 - Route에서 직접 처리"""
    if not x_user_id or x_user_id not in USERS:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    user = USERS[x_user_id]
    USERS_BY_EMAIL.pop(user["email"], None)
    USERS_BY_NICK.pop(user["nickname"], None)
    USERS.pop(x_user_id, None)
    
    return {"message": "delete_user_success", "data": None}

@app.put("/api/users/password")
async def update_password(req: PasswordUpdateReq, x_user_id: Optional[int] = Header(None)):
    """비밀번호 변경 - Route에서 직접 처리"""
    if not x_user_id or x_user_id not in USERS:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    user = USERS[x_user_id]
    if user["password"] != req.old_password:
        return JSONResponse(status_code=400, content={"message": "invalid_credentials", "data": None})
    
    # 비밀번호 검증
    if not req.password:
        return JSONResponse(status_code=422, content={"message": "password_validation_failed", "data": {"reason": "password_blank"}})
    if not req.password_check:
        return JSONResponse(status_code=422, content={"message": "password_validation_failed", "data": {"reason": "password_check_blank"}})
    if len(req.password) < 8 or len(req.password) > 20:
        return JSONResponse(status_code=422, content={"message": "password_validation_failed", "data": {"reason": "password_too_short"}})
    if req.password != req.password_check:
        return JSONResponse(status_code=422, content={"message": "password_validation_failed", "data": {"reason": "password_mismatch"}})
    
    user["password"] = req.password
    return {"message": "update_password_success", "data": None}

# ========== 게시글 API ==========
@app.get("/api/posts")
async def get_posts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), x_user_id: Optional[int] = Header(None)):
    """게시글 목록 조회 - Route에서 직접 처리"""
    all_posts = list(POSTS.values())
    sorted_posts = sorted(all_posts, key=lambda x: x["id"], reverse=True)
    
    start = (page - 1) * limit
    end = start + limit
    paginated_posts = sorted_posts[start:end]
    
    posts_data = []
    for post in paginated_posts:
        user = USERS.get(post["user_id"], {})
        comment_count = len([c for c in COMMENTS.values() if c["post_id"] == post["id"]])
        liked = False
        if x_user_id and post["id"] in LIKES:
            liked = x_user_id in LIKES[post["id"]]
        
        posts_data.append({
            "post_id": post["id"],
            "user_id": post["user_id"],
            "nickname": user.get("nickname", "알 수 없음"),
            "title": post["title"],
            "content": post["content"],
            "image_url": post["image_url"],
            "like_count": post["like_count"],
            "view_count": post["view_count"],
            "comment_count": comment_count,
            "liked": liked
        })
    
    return {
        "message": "get_posts_success",
        "data": {
            "posts": posts_data,
            "total": len(all_posts),
            "page": page,
            "limit": limit
        }
    }

@app.get("/api/posts/{post_id}")
async def get_post(post_id: int, x_user_id: Optional[int] = Header(None)):
    """게시글 상세 조회 - Route에서 직접 처리"""
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    post = POSTS[post_id]
    user = USERS.get(post["user_id"], {})
    comments = [c for c in COMMENTS.values() if c["post_id"] == post_id]
    
    comments_data = []
    for comment in comments:
        comment_user = USERS.get(comment["user_id"], {})
        comments_data.append({
            "comment_id": comment["id"],
            "user_id": comment["user_id"],
            "nickname": comment_user.get("nickname", "알 수 없음"),
            "content": comment["content"]
        })
    
    liked = False
    if x_user_id and post_id in LIKES:
        liked = x_user_id in LIKES[post_id]
    
    return {
        "message": "get_post_success",
        "data": {
            "post_id": post["id"],
            "user_id": post["user_id"],
            "nickname": user.get("nickname", "알 수 없음"),
            "title": post["title"],
            "content": post["content"],
            "image_url": post["image_url"],
            "like_count": post["like_count"],
            "view_count": post["view_count"],
            "liked": liked,
            "comments": comments_data
        }
    }

@app.post("/api/posts", status_code=201)
async def create_post(req: PostCreateReq, x_user_id: Optional[int] = Header(None)):
    """게시글 작성 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if not req.title or not req.content:
        return JSONResponse(status_code=422, content={"message": "missing_fields", "data": {"required": ["title", "content"]}})
    
    if len(req.title) > 26:
        return JSONResponse(status_code=422, content={"message": "title_too_long", "data": {"max_length": 26}})
    
    post_id = COUNTERS["post"]
    COUNTERS["post"] += 1
    
    post = {
        "id": post_id,
        "user_id": x_user_id,
        "title": req.title,
        "content": req.content,
        "image_url": str(req.image_url) if req.image_url else None,
        "like_count": 0,
        "view_count": 0
    }
    
    POSTS[post_id] = post
    return {"message": "create_post_success", "data": {"post_id": post_id}}

@app.patch("/api/posts/{post_id}")
async def update_post(post_id: int, req: PostUpdateReq, x_user_id: Optional[int] = Header(None)):
    """게시글 수정 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    post = POSTS[post_id]
    if post["user_id"] != x_user_id:
        return JSONResponse(status_code=403, content={"message": "forbidden", "data": None})
    
    if req.title is not None:
        if len(req.title) > 26:
            return JSONResponse(status_code=422, content={"message": "title_too_long", "data": {"max_length": 26}})
        post["title"] = req.title
    
    if req.content is not None:
        post["content"] = req.content
    
    if req.image_url is not None:
        post["image_url"] = str(req.image_url)
    
    return {"message": "update_post_success", "data": {"post_id": post_id}}

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int, x_user_id: Optional[int] = Header(None)):
    """게시글 삭제 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    post = POSTS[post_id]
    if post["user_id"] != x_user_id:
        return JSONResponse(status_code=403, content={"message": "forbidden", "data": None})
    
    # 관련 댓글 삭제
    comments_to_delete = [cid for cid, c in COMMENTS.items() if c["post_id"] == post_id]
    for cid in comments_to_delete:
        COMMENTS.pop(cid, None)
    
    LIKES.pop(post_id, None)
    POSTS.pop(post_id, None)
    
    return {"message": "delete_post_success", "data": {"post_id": post_id}}

@app.post("/api/posts/{post_id}/like")
async def toggle_like(post_id: int, x_user_id: Optional[int] = Header(None)):
    """좋아요 토글 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    if post_id not in LIKES:
        LIKES[post_id] = set()
    
    if x_user_id in LIKES[post_id]:
        LIKES[post_id].remove(x_user_id)
        liked = False
    else:
        LIKES[post_id].add(x_user_id)
        liked = True
    
    POSTS[post_id]["like_count"] = len(LIKES[post_id])
    
    return {
        "message": "like_toggled",
        "data": {
            "post_id": post_id,
            "like_count": POSTS[post_id]["like_count"],
            "liked": liked
        }
    }

@app.patch("/api/posts/{post_id}/view")
async def inc_view(post_id: int):
    """조회수 증가 - Route에서 직접 처리"""
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    POSTS[post_id]["view_count"] += 1
    return {
        "message": "view_incremented",
        "data": {
            "post_id": post_id,
            "view_count": POSTS[post_id]["view_count"]
        }
    }

@app.post("/api/posts/upload")
async def upload_post_image(file: UploadFile = File(...)):
    """게시글 이미지 업로드 - Route에서 직접 처리"""
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        return JSONResponse(status_code=400, content={"message": "invalid_file_type", "data": {"allowed": ["jpg", "png", "jpeg"]}})
    
    file_data = await file.read()
    if len(file_data) > 5 * 1024 * 1024:
        return JSONResponse(status_code=413, content={"message": "file_too_large", "data": {"max_size": "5MB"}})
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    url = f"https://cdn.example.com/{filename}"
    return {"message": "upload_success", "data": {"image_url": url}}

# ========== 댓글 API ==========
@app.get("/api/posts/{post_id}/comments")
async def get_comments(post_id: int):
    """댓글 목록 조회 - Route에서 직접 처리"""
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    post_comments = [c for c in COMMENTS.values() if c["post_id"] == post_id]
    
    comments_data = []
    for comment in post_comments:
        user = USERS.get(comment["user_id"], {})
        comments_data.append({
            "comment_id": comment["id"],
            "user_id": comment["user_id"],
            "nickname": user.get("nickname", "알 수 없음"),
            "content": comment["content"]
        })
    
    return {"message": "get_comments_success", "data": {"comments": comments_data}}

@app.post("/api/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: int, req: CommentCreateReq, x_user_id: Optional[int] = Header(None)):
    """댓글 작성 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    if not req.content or not req.content.strip():
        return JSONResponse(status_code=400, content={"message": "invalid_request", "data": None})
    
    comment_id = COUNTERS["comment"]
    COUNTERS["comment"] += 1
    
    comment = {
        "id": comment_id,
        "post_id": post_id,
        "user_id": x_user_id,
        "content": req.content
    }
    
    COMMENTS[comment_id] = comment
    return {"message": "create_comment_success", "data": {"comment_id": comment_id}}

@app.patch("/api/posts/{post_id}/comments/{comment_id}")
async def update_comment(post_id: int, comment_id: int, req: CommentUpdateReq, x_user_id: Optional[int] = Header(None)):
    """댓글 수정 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    if comment_id not in COMMENTS:
        return JSONResponse(status_code=404, content={"message": "comment_not_found", "data": None})
    
    comment = COMMENTS[comment_id]
    if comment["post_id"] != post_id:
        return JSONResponse(status_code=404, content={"message": "comment_not_found", "data": None})
    
    if comment["user_id"] != x_user_id:
        return JSONResponse(status_code=403, content={"message": "forbidden", "data": None})
    
    comment["content"] = req.content
    return {"message": "update_comment_success", "data": {"comment_id": comment_id}}

@app.delete("/api/posts/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: int, comment_id: int, x_user_id: Optional[int] = Header(None)):
    """댓글 삭제 - Route에서 직접 처리"""
    if not x_user_id:
        return JSONResponse(status_code=401, content={"message": "unauthorized_user", "data": None})
    
    if post_id not in POSTS:
        return JSONResponse(status_code=404, content={"message": "post_not_found", "data": None})
    
    if comment_id not in COMMENTS:
        return JSONResponse(status_code=404, content={"message": "comment_not_found", "data": None})
    
    comment = COMMENTS[comment_id]
    if comment["post_id"] != post_id:
        return JSONResponse(status_code=404, content={"message": "comment_not_found", "data": None})
    
    if comment["user_id"] != x_user_id:
        return JSONResponse(status_code=403, content={"message": "forbidden", "data": None})
    
    COMMENTS.pop(comment_id, None)
    return {"message": "delete_comment_success", "data": {"comment_id": comment_id}}

# ========== 예외 처리 ==========
@app.exception_handler(Exception)
async def all_errors(_, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "internal_server_error", "data": None})
