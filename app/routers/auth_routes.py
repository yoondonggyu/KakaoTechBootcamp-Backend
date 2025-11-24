from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.schemas import LoginReq, SignupReq
from app.controllers import auth_controller
from app.core.database import get_db

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login(req: LoginReq, db: Session = Depends(get_db)):
    """로그인 API"""
    data = auth_controller.login_controller(req, db)
    return {"message": "login_success", "data": data}


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(req: SignupReq, db: Session = Depends(get_db)):
    """회원가입 API"""
    data = auth_controller.signup_controller(req, db)
    return {"message": "register_success", "data": data}
