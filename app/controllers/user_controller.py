import os
import uuid
from sqlalchemy.orm import Session
from app.core.validators import validate_nickname
from app.core.exceptions import bad_request, conflict, unauthorized
from app.models.user import User
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
    
    # TODO: Replace with actual CDN or static file serving URL
    url = f"http://localhost:8000/uploads/{name}"
    return {"profile_image_url": url}


def update_profile_controller(req: NicknamePatchReq, user_id: int, db: Session):
    """프로필(닉네임) 수정 컨트롤러"""
    
    # validation_failed 형식으로 검증
    validate_nickname(req.nickname, raise_validation_failed=True)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized()
    
    # 중복 검사 (본인 닉네임은 허용)
    existing = db.query(User).filter(User.nickname == req.nickname).first()
    if existing and existing.id != user_id:
        raise conflict("duplicate_nickname")
    
    user.nickname = req.nickname
    db.commit()
    db.refresh(user)
    
    return {"nickname": user.nickname}


def delete_user_controller(user_id: int, db: Session):
    """회원 탈퇴 컨트롤러"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized()
    
    # Cascade delete handles related data
    db.delete(user)
    db.commit()
    
    return None


def update_password_controller(req: PasswordUpdateReq, user_id: int, db: Session):
    """비밀번호 변경 컨트롤러"""
    from app.core.validators import validate_password_pair
    
    # password_validation_failed 형식으로 검증
    validate_password_pair(req.password, req.password_check, raise_validation_failed=True)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized()
    
    if user.password != req.old_password:
        raise bad_request("invalid_credentials")
    
    user.password = req.password
    db.commit()
    return None
