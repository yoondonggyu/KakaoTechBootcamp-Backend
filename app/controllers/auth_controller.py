from app.schemas import LoginReq, SignupReq
from app.core.validators import validate_email, validate_password_pair, validate_nickname
from app.core.exceptions import bad_request, conflict
from app.models.memory import USERS, USERS_BY_EMAIL, USERS_BY_NICK, COUNTERS, User


def login_controller(req: LoginReq):
    """로그인 컨트롤러"""
    validate_email(req.email)
    
    uid = USERS_BY_EMAIL.get(req.email)
    if not uid:
        raise bad_request("invalid_credentials")
    
    u = USERS[uid]
    if u.password != req.password:
        raise bad_request("invalid_credentials")
    
    return {
        "user_id": u.id,
        "nickname": u.nickname,
        "profile_image_url": u.profile_image_url
    }


def signup_controller(req: SignupReq):
    """회원가입 컨트롤러"""
    from app.core.exceptions import bad_request
    
    validate_email(req.email)
    validate_password_pair(req.password, req.password_check)
    validate_nickname(req.nickname)
    
    # 프로필 이미지 URL 필수 검증
    if not req.profile_image_url:
        raise bad_request("profile_image_url_required")

    if req.email in USERS_BY_EMAIL:
        raise conflict("duplicate_email")
    if req.nickname in USERS_BY_NICK:
        raise conflict("duplicate_nickname")

    uid = COUNTERS["user"]
    COUNTERS["user"] += 1
    
    user = User(
        id=uid,
        email=req.email,
        password=req.password,
        nickname=req.nickname,
        profile_image_url=str(req.profile_image_url)
    )
    
    USERS[uid] = user
    USERS_BY_EMAIL[req.email] = uid
    USERS_BY_NICK[req.nickname] = uid
    
    return {"user_id": uid}

