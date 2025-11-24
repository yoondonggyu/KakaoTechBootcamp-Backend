from sqlalchemy.orm import Session
from app.schemas import LoginReq, SignupReq
from app.core.validators import validate_email, validate_password_pair, validate_nickname
from app.core.exceptions import bad_request, conflict
from app.models.user import User


def login_controller(req: LoginReq, db: Session):
    """로그인 컨트롤러"""
    validate_email(req.email)
    
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise bad_request("invalid_credentials")
    
    if user.password != req.password:
        raise bad_request("invalid_credentials")
    
    return {
        "user_id": user.id,
        "nickname": user.nickname,
        "profile_image_url": user.profile_image_url
    }


def signup_controller(req: SignupReq, db: Session):
    """회원가입 컨트롤러"""
    validate_email(req.email)
    validate_password_pair(req.password, req.password_check)
    validate_nickname(req.nickname)
    
    # 프로필 이미지 URL 필수 검증
    if not req.profile_image_url:
        raise bad_request("profile_image_url_required")

    if db.query(User).filter(User.email == req.email).first():
        raise conflict("duplicate_email")
    if db.query(User).filter(User.nickname == req.nickname).first():
        raise conflict("duplicate_nickname")

    user = User(
        email=req.email,
        password=req.password,
        nickname=req.nickname,
        profile_image_url=str(req.profile_image_url)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"user_id": user.id}
