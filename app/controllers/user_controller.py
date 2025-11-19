import os
import uuid
from app.core.validators import validate_nickname
from app.core.exceptions import bad_request, conflict, unauthorized
from app.models.memory import USERS, USERS_BY_NICK, USERS_BY_EMAIL, POSTS, COMMENTS, LIKES
from app.schemas import NicknamePatchReq, PasswordUpdateReq

UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_profile_image_controller(file_content_type: str, file_data: bytes, filename: str):
    """프로필 이미지 업로드 컨트롤러"""
    from app.core.exceptions import payload_too_large
    
    if not file_data:
        raise bad_request("file_required")
    
    if file_content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise bad_request("invalid_file_type", {"allowed": ["jpg", "png", "jpeg"]})
    
    if len(file_data) > 5 * 1024 * 1024:
        raise payload_too_large("file_too_large", {"max_size": "5MB"})
    
    name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, name)
    
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    url = f"https://cdn.example.com/{name}"
    return {"profile_image_url": url}


def update_profile_controller(req: NicknamePatchReq, user_id: int):
    """프로필(닉네임) 수정 컨트롤러"""
    from app.core.validators import validate_nickname
    
    # validation_failed 형식으로 검증
    validate_nickname(req.nickname, raise_validation_failed=True)
    
    u = USERS.get(user_id)
    if not u:
        raise unauthorized()
    
    # 중복 검사 (본인 닉네임은 허용)
    if req.nickname in USERS_BY_NICK and USERS_BY_NICK[req.nickname] != user_id:
        raise conflict("duplicate_nickname")
    
    # 인덱스 갱신
    if u.nickname != req.nickname:
        USERS_BY_NICK.pop(u.nickname, None)
        USERS_BY_NICK[req.nickname] = user_id
        u.nickname = req.nickname
    
    return {"nickname": u.nickname}


def delete_user_controller(user_id: int):
    """회원 탈퇴 컨트롤러"""
    u = USERS.get(user_id)
    if not u:
        raise unauthorized()
    
    # 관련 게시글 삭제 및 정리
    posts_to_delete = [pid for pid, post in POSTS.items() if post.user_id == user_id]
    for pid in posts_to_delete:
        comment_ids = [cid for cid, c in COMMENTS.items() if c.post_id == pid]
        for cid in comment_ids:
            COMMENTS.pop(cid, None)
        LIKES.pop(pid, None)
        POSTS.pop(pid, None)

    # 사용자가 남긴 댓글 제거
    for cid, comment in list(COMMENTS.items()):
        if comment.user_id == user_id:
            COMMENTS.pop(cid, None)

    # 사용자가 누른 좋아요 제거
    for pid, user_set in LIKES.items():
        if user_id in user_set:
            user_set.remove(user_id)
            post = POSTS.get(pid)
            if post:
                post.like_count = len(user_set)

    # 사용자 인덱스 정리
    USERS_BY_EMAIL.pop(u.email, None)
    USERS_BY_NICK.pop(u.nickname, None)
    USERS.pop(user_id, None)
    
    return None


def update_password_controller(req: PasswordUpdateReq, user_id: int):
    """비밀번호 변경 컨트롤러"""
    from app.core.validators import validate_password_pair
    
    # password_validation_failed 형식으로 검증
    validate_password_pair(req.password, req.password_check, raise_validation_failed=True)
    
    u = USERS.get(user_id)
    if not u:
        raise unauthorized()
    
    if u.password != req.old_password:
        raise bad_request("invalid_credentials")
    
    u.password = req.password
    return None

