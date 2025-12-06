from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth_routes, user_routes, post_routes, comment_routes
from app.core.exceptions import APIError
from app.core.formatter import create_json_response
import os

# uploads 폴더 생성
UPLOAD_DIR = os.path.abspath("./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Community API")

# 업로드 폴더를 static으로 서빙
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://[::]:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 루트 경로
@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Community API",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api"
    }

# 라우터 등록
app.include_router(auth_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(post_routes.router, prefix="/api")
app.include_router(comment_routes.router, prefix="/api")

# 전역 예외 처리
@app.exception_handler(APIError)
async def handle_api_error(_: Request, exc: APIError):
    """커스텀 API 에러 처리"""
    return create_json_response(exc.status_code, exc.message, exc.data)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError):
    """Pydantic 검증 에러 처리"""
    errors = exc.errors()
    if errors:
        # 첫 번째 에러 메시지 사용
        error = errors[0]
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "invalid_request")
        
        # 필드별 에러 메시지 매핑
        error_messages = {
            "email": "invalid_email_format",
            "password": "invalid_password_format",
            "nickname": "invalid_request",
            "title": "invalid_request",
            "content": "invalid_request",
        }
        
        # 필드명에서 에러 타입 추출
        for key, error_msg in error_messages.items():
            if key in field.lower():
                return create_json_response(422, error_msg, None)
        
        return create_json_response(422, "invalid_request", None)
    
    return create_json_response(422, "invalid_request", None)

@app.exception_handler(Exception)
async def handle_unexpected(_: Request, exc: Exception):
    """예상치 못한 서버 내부 오류 처리"""
    return create_json_response(500, "internal_server_error", None)

# Admin Page Setup
from app.core.admin import setup_admin
setup_admin(app)
