from pydantic import BaseModel, HttpUrl, Field

# Auth
class LoginReq(BaseModel):
    email: str
    password: str

class LoginRes(BaseModel):
    message: str = "login_success"
    data: dict

class SignupReq(BaseModel):
    email: str
    password: str
    password_check: str
    nickname: str
    profile_image_url: HttpUrl

# Users
class NicknamePatchReq(BaseModel):
    nickname: str

class PasswordUpdateReq(BaseModel):
    old_password: str
    password: str
    password_check: str

# Posts
class PostCreateReq(BaseModel):
    title: str = Field(..., max_length=2000)
    content: str
    image_url: HttpUrl | None = None
    image_class: str | None = None  # 이미지 분류 결과 (Dog/Cat)
    board_type: str = "couple"

class PostUpdateReq(BaseModel):
    title: str | None = None
    content: str | None = None
    image_url: HttpUrl | None = None
    image_class: str | None = None

# Comments
class CommentCreateReq(BaseModel):
    content: str

class CommentUpdateReq(BaseModel):
    content: str
