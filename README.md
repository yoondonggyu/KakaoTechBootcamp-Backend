# 🚀 아무 말 대잔치 - Backend API

> FastAPI 기반 커뮤니티 게시판 REST API 서버

## 📋 프로젝트 소개

**아무 말 대잔치** 커뮤니티의 백엔드 API 서버입니다.  
FastAPI 프레임워크를 사용하여 빠르고 안정적인 REST API를 제공합니다.

## 🔗 관련 저장소

| 저장소 | 설명 | 링크 |
|--------|------|------|
| **Frontend** | Vanilla JS 기반 웹 UI | [KakaoTechBootcamp-Frontend](https://github.com/yoondonggyu/KakaoTechBootcamp-Frontend) |
| **Backend** | FastAPI 기반 REST API | [현재 저장소](https://github.com/yoondonggyu/KakaoTechBootcamp-Backend) |
| **Model** | AI 모델 서빙 API | [KakaoTechBootcamp-Model](https://github.com/yoondonggyu/KakaoTechBootcamp-Model) |

## ✨ 주요 기능

### 🔐 인증 (Auth)
- 회원가입 (이메일, 비밀번호, 닉네임, 프로필 이미지)
- 로그인 (세션 기반)
- 비밀번호 검증 (8자 이상, 대소문자/숫자/특수문자 포함)

### 👤 사용자 (User)
- 프로필 이미지 업로드
- 닉네임 수정
- 비밀번호 변경

### 📝 게시글 (Post)
- 게시글 CRUD
- 이미지 업로드 + AI 분류 연동
- 좋아요 토글
- 조회수 카운트
- 페이지네이션

### 💬 댓글 (Comment)
- 댓글 CRUD
- 게시글별 댓글 목록

### 🤖 AI 연동
- Model API와 연동하여 이미지 분류
- 자동 태깅, 요약, 감정 분석

## 🛠 기술 스택

| 분류 | 기술 |
|------|------|
| **Framework** | FastAPI |
| **Language** | Python 3.10+ |
| **Database** | MySQL 8.0 |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic |
| **Server** | Uvicorn |

## 📁 프로젝트 구조

```
FASTAPI_Project_back/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── core/
│   │   ├── database.py      # DB 연결 설정
│   │   ├── security.py      # 인증 관련
│   │   ├── validators.py    # 입력값 검증
│   │   ├── exceptions.py    # 커스텀 예외
│   │   └── formatter.py     # 응답 포맷
│   ├── models/              # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── post.py
│   │   └── comment.py
│   ├── controllers/         # 비즈니스 로직
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── post_controller.py
│   │   └── comment_controller.py
│   ├── routers/             # API 라우터
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   ├── post_routes.py
│   │   └── comment_routes.py
│   ├── services/            # 외부 서비스 연동
│   │   └── model_client.py  # Model API 클라이언트
│   └── schemas.py           # Pydantic 스키마
├── uploads/                 # 업로드된 이미지
├── .env.example             # 환경 변수 예제
└── requirements.txt
```

## 🚀 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yoondonggyu/KakaoTechBootcamp-Backend.git
cd KakaoTechBootcamp-Backend
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 DATABASE_URL 설정
```

### 5. 데이터베이스 생성
```sql
CREATE DATABASE FASTAPI_Project_DB;
```

### 6. 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```

### 7. API 문서 확인
```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

## 📚 API 명세

### 인증 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/signup` | 회원가입 |
| POST | `/api/auth/login` | 로그인 |

### 사용자 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/users/profile/upload` | 프로필 이미지 업로드 |
| PATCH | `/api/users/profile` | 닉네임 수정 |
| PUT | `/api/users/password` | 비밀번호 변경 |

### 게시글 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/posts` | 게시글 목록 |
| GET | `/api/posts/{id}` | 게시글 상세 |
| POST | `/api/posts` | 게시글 작성 |
| PATCH | `/api/posts/{id}` | 게시글 수정 |
| DELETE | `/api/posts/{id}` | 게시글 삭제 |
| POST | `/api/posts/upload` | 이미지 업로드 |
| POST | `/api/posts/{id}/like` | 좋아요 토글 |
| PATCH | `/api/posts/{id}/view` | 조회수 증가 |

### 댓글 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/posts/{id}/comments` | 댓글 목록 |
| POST | `/api/posts/{id}/comments` | 댓글 작성 |
| PATCH | `/api/comments/{id}` | 댓글 수정 |
| DELETE | `/api/comments/{id}` | 댓글 삭제 |

## 🔒 환경 변수

```env
# .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/FASTAPI_Project_DB
MODEL_API_URL=http://localhost:8001/api
```

## 👨‍💻 개발자

- **윤동규** - [GitHub](https://github.com/yoondonggyu)

## 📝 라이선스

This project is licensed under the MIT License.
