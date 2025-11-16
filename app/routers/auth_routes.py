from fastapi import APIRouter, status
from app.schemas import LoginReq, SignupReq
from app.controllers import auth_controller

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login(req: LoginReq):
    """로그인 API"""
    data = auth_controller.login_controller(req)
    return {"message": "login_success", "data": data}


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(req: SignupReq):
    """회원가입 API"""
    data = auth_controller.signup_controller(req)
    return {"message": "register_success", "data": data}
