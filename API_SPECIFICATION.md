# 커뮤니티 백엔드 API 명세서

## 기본 정보
- Base URL: `http://localhost:8000/api`
- 인증 방식: Header에 `X-User-Id: {user_id}` 전달 (로그인 필요 API만)

---

## 1. 인증 (Auth)

### 1.1 로그인
- **Method**: `POST`
- **URL**: `/api/auth/login`
- **인증**: 불필요
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "Password123!"
}
```
- **Response** (200):
```json
{
  "message": "login_success",
  "data": {
    "user_id": 1,
    "nickname": "사용자닉네임",
    "profile_image_url": "https://cdn.example.com/profile.jpg"
  }
}
```

### 1.2 회원가입
- **Method**: `POST`
- **URL**: `/api/auth/signup`
- **인증**: 불필요
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "password_check": "Password123!",
  "nickname": "사용자닉네임",
  "profile_image_url": "https://example.com/image.jpg"
}
```
- **Response** (200):
```json
{
  "message": "register_success",
  "data": {
    "user_id": 1
  }
}
```

---

## 2. 사용자 (Users)

### 2.1 프로필 이미지 업로드
- **Method**: `POST`
- **URL**: `/api/users/profile/upload`
- **인증**: 불필요
- **Request**: `multipart/form-data`
  - `file`: 이미지 파일 (jpg, png, jpeg, 최대 5MB)
- **Response** (200):
```json
{
  "message": "upload_success",
  "data": {
    "profile_image_url": "https://cdn.example.com/uuid_filename.jpg"
  }
}
```

### 2.2 프로필(닉네임) 수정
- **Method**: `PATCH`
- **URL**: `/api/users/profile`
- **인증**: 필요 (`X-User-Id` 헤더)
- **Request Body**:
```json
{
  "nickname": "새닉네임"
}
```
- **Response** (200):
```json
{
  "message": "update_profile_success",
  "data": {
    "nickname": "새닉네임"
  }
}
```

### 2.3 회원 탈퇴
- **Method**: `DELETE`
- **URL**: `/api/users/profile`
- **인증**: 필요 (`X-User-Id` 헤더)
- **Response** (200):
```json
{
  "message": "delete_user_success",
  "data": null
}
```

### 2.4 비밀번호 변경
- **Method**: `PUT`
- **URL**: `/api/users/password`
- **인증**: 필요 (`X-User-Id` 헤더)
- **Request Body**:
```json
{
  "old_password": "OldPassword123!",
  "password": "NewPassword123!",
  "password_check": "NewPassword123!"
}
```
- **Response** (200):
```json
{
  "message": "update_password_success",
  "data": null
}
```

---

## 3. 게시글 (Posts)

### 3.1 게시글 목록 조회
- **Method**: `GET`
- **URL**: `/api/posts`
- **인증**: 선택 (`X-User-Id` 헤더 - 좋아요 여부 표시용)
- **Query Parameters**:
  - `page`: 페이지 번호 (기본값: 1, 최소: 1)
  - `limit`: 페이지당 개수 (기본값: 10, 최소: 1, 최대: 100)
- **Response** (200):
```json
{
  "message": "get_posts_success",
  "data": {
    "posts": [
      {
        "post_id": 1,
        "user_id": 1,
        "nickname": "작성자닉네임",
        "title": "게시글 제목",
        "content": "게시글 내용",
        "image_url": "https://cdn.example.com/image.jpg",
        "like_count": 5,
        "view_count": 100,
        "comment_count": 3,
        "liked": false
      }
    ],
    "total": 50,
    "page": 1,
    "limit": 10
  }
}
```

### 3.2 게시글 상세 조회
- **Method**: `GET`
- **URL**: `/api/posts/{post_id}`
- **인증**: 선택 (`X-User-Id` 헤더 - 좋아요 여부 표시용)
- **Response** (200):
```json
{
  "message": "get_post_success",
  "data": {
    "post_id": 1,
    "user_id": 1,
    "nickname": "작성자닉네임",
    "title": "게시글 제목",
    "content": "게시글 내용",
    "image_url": "https://cdn.example.com/image.jpg",
    "like_count": 5,
    "view_count": 100,
    "liked": false,
    "comments": [
      {
        "comment_id": 1,
        "user_id": 2,
        "nickname": "댓글작성자",
        "content": "댓글 내용"
      }
    ]
  }
}
```

### 3.3 게시글 작성
- **Method**: `POST`
- **URL**: `/api/posts`
- **인증**: 필요 (`X-User-Id` 헤더)
- **Request Body**:
```json
{
  "title": "게시글 제목",
  "content": "게시글 내용",
  "image_url": "https://cdn.example.com/image.jpg"
}
```
- **Response** (200):
```json
{
  "message": "create_post_success",
  "data": {
    "post_id": 1
  }
}
```

### 3.4 게시글 수정
- **Method**: `PATCH`
- **URL**: `/api/posts/{post_id}`
- **인증**: 필요 (`X-User-Id` 헤더, 작성자만 수정 가능)
- **Request Body** (모든 필드 선택):
```json
{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "image_url": "https://cdn.example.com/new_image.jpg"
}
```
- **Response** (200):
```json
{
  "message": "update_post_success",
  "data": {
    "post_id": 1
  }
}
```

### 3.5 게시글 삭제
- **Method**: `DELETE`
- **URL**: `/api/posts/{post_id}`
- **인증**: 필요 (`X-User-Id` 헤더, 작성자만 삭제 가능)
- **Response** (200):
```json
{
  "message": "delete_post_success",
  "data": {
    "post_id": 1
  }
}
```

### 3.6 좋아요 토글
- **Method**: `POST`
- **URL**: `/api/posts/{post_id}/like`
- **인증**: 필요 (`X-User-Id` 헤더)
- **Response** (200):
```json
{
  "message": "like_toggled",
  "data": {
    "post_id": 1,
    "like_count": 6,
    "liked": true
  }
}
```

### 3.7 조회수 증가
- **Method**: `PATCH`
- **URL**: `/api/posts/{post_id}/view`
- **인증**: 불필요
- **Response** (200):
```json
{
  "message": "view_incremented",
  "data": {
    "post_id": 1,
    "view_count": 101
  }
}
```

### 3.8 게시글 이미지 업로드
- **Method**: `POST`
- **URL**: `/api/posts/upload`
- **인증**: 불필요
- **Request**: `multipart/form-data`
  - `file`: 이미지 파일 (jpg, png, jpeg, 최대 5MB)
- **Response** (200):
```json
{
  "message": "upload_success",
  "data": {
    "image_url": "https://cdn.example.com/uuid_filename.jpg"
  }
}
```

---

## 4. 댓글 (Comments)

### 4.1 댓글 목록 조회
- **Method**: `GET`
- **URL**: `/api/posts/{post_id}/comments`
- **인증**: 불필요
- **Response** (200):
```json
{
  "message": "get_comments_success",
  "data": {
    "comments": [
      {
        "comment_id": 1,
        "user_id": 2,
        "nickname": "댓글작성자",
        "content": "댓글 내용"
      }
    ]
  }
}
```

### 4.2 댓글 작성
- **Method**: `POST`
- **URL**: `/api/posts/{post_id}/comments`
- **인증**: 필요 (`X-User-Id` 헤더)
- **Request Body**:
```json
{
  "content": "댓글 내용"
}
```
- **Response** (200):
```json
{
  "message": "create_comment_success",
  "data": {
    "comment_id": 1
  }
}
```

### 4.3 댓글 수정
- **Method**: `PATCH`
- **URL**: `/api/posts/{post_id}/comments/{comment_id}`
- **인증**: 필요 (`X-User-Id` 헤더, 작성자만 수정 가능)
- **Request Body**:
```json
{
  "content": "수정된 댓글 내용"
}
```
- **Response** (200):
```json
{
  "message": "update_comment_success",
  "data": {
    "comment_id": 1
  }
}
```

### 4.4 댓글 삭제
- **Method**: `DELETE`
- **URL**: `/api/posts/{post_id}/comments/{comment_id}`
- **인증**: 필요 (`X-User-Id` 헤더, 작성자만 삭제 가능)
- **Response** (200):
```json
{
  "message": "delete_comment_success",
  "data": {
    "comment_id": 1
  }
}
```

---

## 에러 응답 형식

모든 에러는 다음 형식을 따릅니다:

```json
{
  "message": "에러_메시지_코드",
  "data": null
}
```

### 주요 에러 코드

- `invalid_credentials`: 잘못된 이메일/비밀번호
- `duplicate_email`: 중복된 이메일
- `duplicate_nickname`: 중복된 닉네임
- `invalid_email_format`: 잘못된 이메일 형식
- `invalid_password_format`: 잘못된 비밀번호 형식 (8-20자, 대소문자, 숫자/특수문자 포함)
- `password_mismatch`: 비밀번호 불일치
- `nickname_required`: 닉네임 필수
- `nickname_too_long`: 닉네임이 너무 김 (최대 10자)
- `nickname_contains_space`: 닉네임에 공백 포함
- `title_too_long`: 제목이 너무 김 (최대 26자)
- `post_not_found`: 게시글을 찾을 수 없음
- `comment_not_found`: 댓글을 찾을 수 없음
- `forbidden`: 권한 없음 (작성자만 수정/삭제 가능)
- `unauthorized_user`: 인증되지 않은 사용자
- `invalid_file_type`: 잘못된 파일 형식
- `file_too_large`: 파일이 너무 큼 (최대 5MB)
- `missing_fields`: 필수 필드 누락

### HTTP 상태 코드

- `200`: 성공
- `400`: 잘못된 요청
- `401`: 인증 필요
- `403`: 권한 없음
- `404`: 리소스를 찾을 수 없음
- `409`: 충돌 (중복 등)
- `422`: 처리할 수 없는 엔티티 (검증 실패)
- `500`: 서버 내부 오류

---

## 검증 규칙

### 이메일
- 형식: `user@example.com`
- 허용 문자: 영문, 숫자, @, ., _, +, -

### 비밀번호
- 길이: 8-20자
- 대문자 포함 필수
- 소문자 포함 필수
- 숫자 또는 특수문자 포함 필수

### 닉네임
- 길이: 최대 10자
- 공백 불가

### 게시글 제목
- 길이: 최대 26자

### 파일 업로드
- 허용 형식: jpg, png, jpeg
- 최대 크기: 5MB



