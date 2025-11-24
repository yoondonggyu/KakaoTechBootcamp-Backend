from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user_id
from app.controllers import user_controller
from app.schemas import NicknamePatchReq, PasswordUpdateReq
from app.core.database import get_db

router = APIRouter(tags=["users"])


@router.post("/users/profile/upload")
async def upload_profile_image(file: UploadFile = File(...)):
    """프로필 이미지 업로드 API"""
    file_data = await file.read()
    filename = file.filename or "unknown"
    data = user_controller.upload_profile_image_controller(file.content_type or "", file_data, filename)
    return {"message": "upload_success", "data": data}


@router.patch("/users/profile")
async def patch_nickname(req: NicknamePatchReq, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """프로필(닉네임) 수정 API"""
    data = user_controller.update_profile_controller(req, user_id, db)
    return {"message": "update_profile_success", "data": data}


@router.delete("/users/profile")
async def delete_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """회원 탈퇴 API"""
    user_controller.delete_user_controller(user_id, db)
    return {"message": "delete_user_success", "data": None}


@router.put("/users/password")
async def update_password(req: PasswordUpdateReq, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """비밀번호 변경 API"""
    user_controller.update_password_controller(req, user_id, db)
    return {"message": "update_password_success", "data": None}
