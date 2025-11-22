# API 명세서

## 인증 (Authentication)

### 로그인
- **Method**: `POST`
- **Endpoint**: `/api/auth/login`
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "Test@1234"
}
```
- **Request 필수 필드**:
  - `email`: String - 사용자 이메일
  - `password`: String - 사용자 비밀번호
- **Description**: 사용자가 로그인 폼에서 이메일과 비밀번호를 입력하면, 서버는 입력값 검증 후 로그인 절차를 수행합니다.
- **Success Response (200)**:
```json
{
  "message": "login_success",
  "data": {
    "user_id": 1,
    "nickname": "estar",
    "profile_image_url": "https://image.kr/img.jpg"
  }
}
```
- **Error Responses**:
  - `400`: `{ "message": "email_required", "data": null }` - 이메일을 입력해주세요
  - `400`: `{ "message": "invalid_email_format", "data": null }` - 올바른 이메일 주소 형식을 입력해주세요(예 : example@example.com)
  - `400`: `{ "message": "password_required", "data": null }` - 비밀번호를 입력해주세요
  - `401`: `{ "message": "invalid_credentials", "data": null }` - 아이디 또는 비밀번호를 확인 해주세요
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 회원 가입
- **Method**: `POST`
- **Endpoint**: `/api/auth/signup`
- **Request Body**:
```json
{
  "email": "test@startupcode.kr",
  "password": "Test@1234",
  "password_check": "Test@1234",
  "nickname": "startup",
  "profile_image_url": "https://cdn.example.com/profile.jpg"
}
```
- **Description**: 회원 정보(이메일, 비밀번호, 닉네임, 프로필 URL)를 서버로 전송해 신규 계정을 생성한다.  
※ 프로필 이미지는 사전 업로드 API를 통해 URL을 획득 후 포함한다.
- **Success Response (201)**:
```json
{
  "message": "register_success",
  "data": {
    "user_id": 1
  }
}
```
- **Error Responses**:
  - `400`: `{ "message": "email_required", "data": null }` - 이메일을 입력해주세요
  - `400`: `{ "message": "invalid_email_format", "data": null }` - 올바른 이메일 주소 형식을 입력해주세요 (예 : example@example.com)
  - `400`: `{ "message": "invalid_email_character", "data": { "allowed": "영문, @, ." } }` - 이메일은 영문과 @, .만 사용이 가능합니다.
  - `409`: `{ "message": "duplicate_email", "data": null }` - 중복된 이메일입니다.
  - `400`: `{ "message": "password_required", "data": null }` - 비밀번호를 입력해주세요
  - `400`: `{ "message": "invalid_password_format", "data": null }` - 비밀번호는 8자 이상, 20자 이하이며 대문자, 소문자, 특수문자를 각각 1개 포함해야 합니다.
  - `400`: `{ "message": "password_check_required", "data": null }` - 비밀번호를 한번 더 입력해주세요
  - `422`: `{ "message": "password_mismatch", "data": null }` - 비밀번호가 다릅니다.
  - `400`: `{ "message": "nickname_required", "data": null }` - 닉네임을 입력해주세요
  - `400`: `{ "message": "nickname_contains_space", "data": null }` - 띄어쓰기 없애주세요
  - `400`: `{ "message": "nickname_too_long", "data": { "max_length": 10 } }` - 닉네임은 최대 10자까지 작성 가능합니다.
  - `409`: `{ "message": "duplicate_nickname", "data": null }` - 중복된 닉네임입니다.
  - `400`: `{ "message": "profile_image_url_required", "data": null }` - 프로필 사진을 추가해주세요
  - `500`: `{ "message": "internal_server_error", "data": null }` - 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.

---

## 사용자 (User)

### 프로필 이미지 업로드
- **Method**: `POST`
- **Endpoint**: `/api/users/profile/upload`
- **Request**: Multipart Form-data: `{ "file": [이미지 파일] }`
- **Description**: 업로드 성공 및 이미지 URL 반환. 게시글 작성/수정 시 이미지 파일 업로드용 API. 업로드 후 반환된 URL을 본문 image_url 필드에 포함시켜 사용.
- **Success Response (200)**:
```json
{
  "message": "upload_success",
  "data": {
    "profile_image_url": "https://cdn.example.com/profile.jpg"
  }
}
```
- **Error Responses**:
  - `400`: `{ "message": "file_required", "data": null }` - 프로필 사진을 추가해주세요
  - `400`: `{ "message": "invalid_file_type", "data": { "allowed": ["jpg","png","jpeg"] } }` - jpg, png, jpeg 파일만 업로드 가능합니다.
  - `413`: `{ "message": "file_too_large", "data": { "max_size": "5MB" } }` - 파일 크기가 너무 큽니다. (최대 5MB)
  - `500`: `{ "message": "internal_server_error", "data": null }` - 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.

---

### 닉네임 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/users/profile`
- **Request Body**:
```json
{
  "nickname": "새닉네임"
}
```
- **Description**: "수정하기" 클릭 시 호출. 서버가 빈값/길이/띄어쓰기/중복을 모두 검증하고 결과를 반환한다. 200 응답을 받으면 프론트는 "수정 완료" 토스트를 띄운다.
- **Success Response (200)**:
```json
{
  "message": "update_profile_success",
  "data": {
    "nickname": "스타트업코드"
  }
}
```
- **Error Responses**:
  - `400`: `{ "message": "invalid_request", "data": null }`
  - `401`: `{ "message": "unauthorized_user", "data": null }`
  - `409`: `{ "message": "duplicate_nickname", "data": null }` - 중복된 닉네임 입니다.
  - `422`: `{ "message": "validation_failed", "data": { "field": "nickname", "reason": "nickname_too_long" } }`
    - `nickname_blank` → "닉네임을 입력해주세요"
    - `nickname_too_long` → "닉네임은 최대 10자까지 작성 가능합니다."
    - `nickname_has_space` → "띄어쓰기를 없애주세요"
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 회원 탈퇴
- **Method**: `DELETE`
- **Endpoint**: `/api/users/profile`
- **Description**: 서버는 사용자의 게시글/댓글 삭제 → 계정 삭제를 트랜잭션으로 처리. 성공 시 로그아웃 처리 후 로그인 페이지로 이동.
- **Success Response (200)**:
```json
{
  "message": "delete_user_success",
  "data": null
}
```
- **Note**: 세션/토큰 폐기 → 로그인 페이지로 이동
- **Error Responses**:
  - `401`: `{ "message": "unauthorized_user", "data": null }` - 로그인 만료 등
  - `500`: `{ "message": "internal_server_error", "data": null }` - 에러 토스트

---

### 비밀번호 수정
- **Method**: `PUT`
- **Endpoint**: `/api/users/password`
- **Request Body**:
```json
{
  "old_password": "현재비밀번호",
  "password": "새비밀번호",
  "password_check": "새비밀번호"
}
```
- **Description**: "비밀번호 수정" 페이지에서 수정하기 버튼 클릭 시 호출. 입력값이 비어 있거나 유효성 검사를 통과하지 못하면 서버에서 에러 메시지를 반환한다. 모든 검증을 통과하면 비밀번호를 갱신하고 "수정 완료" 토스트 메시지를 표시한다.
- **Success Response (200)**:
```json
{
  "message": "update_password_success",
  "data": null
}
```
- **Note**: 토스트 "수정 완료" 표시
- **Error Responses**:
  - `400`: `{ "message": "invalid_request", "data": null }` - 입력값 형식 오류
  - `401`: `{ "message": "unauthorized_user", "data": null }` - 로그인 세션 만료 시 재로그인 유도
  - `422`: `{ "message": "password_validation_failed", "data": { "reason": "password_too_short" } }`
    - `password_blank` → "비밀번호를 입력해주세요"
    - `password_check_blank` → "비밀번호를 한번 더 입력해주세요"
    - `password_mismatch` → "비밀번호가 다릅니다."
    - `password_too_short` → "비밀번호는 8자 이상, 20자 이하이며 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."
    - `password_invalid_format` → (동일 메시지)
  - `500`: `{ "message": "internal_server_error", "data": null }` - 에러 토스트 표시

---

## 게시글 (Post)

### 게시글 목록 조회
- **Method**: `GET`
- **Endpoint**: `/api/posts`
- **Query Parameters**:
  - `page`: int (기본값: 1, 최소: 1) - 페이지 번호
  - `limit`: int (기본값: 10, 최소: 1, 최대: 100) - 페이지당 게시글 수
- **Headers** (선택):
  - `X-User-Id`: int - 로그인한 사용자 ID (좋아요 상태 확인용)
- **Description**: 게시글 목록을 페이지네이션으로 조회합니다. 최신순(ID 역순)으로 정렬됩니다.
- **Success Response (200)**:
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
- **Error Responses**: 없음 (항상 성공)

---

### 게시글 상세 조회
- **Method**: `GET`
- **Endpoint**: `/api/posts/{post_id}`
- **Path Parameters**:
  - `post_id`: int - 게시글 ID
- **Headers** (선택):
  - `X-User-Id`: int - 로그인한 사용자 ID (좋아요 상태 확인용)
- **Description**: 특정 게시글의 상세 정보와 댓글 목록을 조회합니다.
- **Success Response (200)**:
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
- **Error Responses**:
  - `404`: `{ "message": "post_not_found", "data": null }` - 게시글을 찾을 수 없습니다.

---

### 게시글 등록
- **Method**: `POST`
- **Endpoint**: `/api/posts`
- **Request Body**:
```json
{
  "title": "게시글 제목",
  "content": "게시글 내용",
  "image_url": "https://cdn.example.com/sample.jpg"
}
```
- **Description**: "게시글 작성 완료" 버튼 클릭 시 서버에 새 게시글 등록 요청을 보낸다. 이미지는 `/api/posts/upload` 에서 업로드 후 반환된 URL을 image_url 필드로 전달한다. 제목 최대 26자까지 작성 가능하며, 본문은 LONGTEXT 타입으로 저장된다.
- **Success Response (201)**:
```json
{
  "message": "create_post_success",
  "data": {
    "post_id": 1
  }
}
```
- **Error Responses**:
  - `400`: `{ "message": "invalid_request", "data": null }`
  - `401`: `{ "message": "unauthorized_user", "data": null }`
  - `422`: `{ "message": "title_too_long", "data": { "max_length": 26 } }`
  - `422`: `{ "message": "missing_fields", "data": { "required": ["title", "content"] } }`
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 게시글 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/posts/{post_id}`
- **Request Body**:
```json
{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "image_url": "https://cdn.example.com/edited.jpg"
}
```
- **Description**: 게시글 수정 버튼 클릭 시 수정 페이지로 이동 후, 사용자가 변경한 내용을 서버에 반영한다. 새 이미지는 `/api/posts/upload` 로 미리 업로드 후 URL만 전달한다.
- **Success Response (200)**:
```json
{
  "message": "update_post_success",
  "data": {
    "post_id": 1
  }
}
```
- **Error Responses**:
  - `400`: `{ "message": "invalid_request", "data": null }`
  - `403`: `{ "message": "forbidden", "data": null }`
  - `404`: `{ "message": "post_not_found", "data": null }`
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 게시글 삭제
- **Method**: `DELETE`
- **Endpoint**: `/api/posts/{post_id}`
- **Description**: 삭제 버튼 클릭 시 확인 모달을 띄우고, "확인" 클릭 시 해당 게시글을 삭제한다.
- **Success Response (200)**:
```json
{
  "message": "delete_post_success",
  "data": {
    "post_id": 1
  }
}
```
- **Error Responses**:
  - `403`: `{ "message": "forbidden", "data": null }`
  - `404`: `{ "message": "post_not_found", "data": null }`
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 좋아요
- **Method**: `POST`
- **Endpoint**: `/api/posts/{post_id}/like`
- **Description**: 좋아요 버튼 클릭 시 호출. 비활성화(D9D9D9) 상태일 때 → 활성화(ACA0EB)로 변경되고 +1, 활성화 상태일 때 → 비활성화로 변경되고 -1. 누적 좋아요 수와 상태를 함께 반환한다.
- **Success Response (200)**:
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
- **Error Responses**:
  - `401`: `{ "message": "unauthorized_user", "data": null }`
  - `404`: `{ "message": "post_not_found", "data": null }`
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 이미지 업로드 API (게시글 등록 / 수정 공용)
- **Method**: `POST`
- **Endpoint**: `/api/posts/upload`
- **Request**: Multipart Form-data: `{ "file": [이미지 파일] }`
- **Description**: 이미지 업로드 버튼 클릭 시 파일을 업로드하고, 성공 시 이미지 URL을 반환한다.  
**※ Model API 연동**: 이미지 업로드 시 자동으로 이미지 분류(강아지/고양이)가 실행되며, 분류 결과가 응답에 포함됩니다. Model API 서버가 응답하지 않거나 오류가 발생해도 이미지 업로드는 성공 처리됩니다.
- **Success Response (200)**:
```json
{
  "message": "upload_success",
  "data": {
    "image_url": "https://cdn.example.com/sample.jpg",
    "prediction": {
      "class_name": "Dog",
      "confidence_score": 0.9999850988388062
    }
  }
}
```
또는 (Model API 실패 시):
```json
{
  "message": "upload_success",
  "data": {
    "image_url": "https://cdn.example.com/sample.jpg",
    "prediction_error": "Model API가 None을 반환했습니다. Model API 서버(포트 8002)가 실행 중인지 확인하세요."
  }
}
```
- **Note**: 
  - `prediction` 필드는 Model API가 정상 작동할 때만 포함됩니다.
  - Model API 서버가 응답하지 않거나 오류가 발생하면 `prediction_error` 필드가 포함됩니다.
  - Model API 실패 시에도 이미지 업로드는 성공 처리되므로 `image_url`은 항상 포함됩니다.
- **Error Responses**:
  - `400`: `{ "message": "invalid_file_type", "data": { "allowed": ["jpg","png","jpeg"] } }` - jpg, png, jpeg 파일만 업로드 가능합니다.
  - `413`: `{ "message": "file_too_large", "data": { "max_size": "5MB" } }` - 파일 크기가 너무 큽니다. (최대 5MB)
  - `500`: `{ "message": "internal_server_error", "data": null }` - 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.

---

### 조회 수 증가
- **Method**: `PATCH`
- **Endpoint**: `/api/posts/{post_id}/view`
- **Success Response (200)**:
```json
{
  "message": "view_incremented",
  "data": {
    "post_id": 1,
    "view_count": 151
  }
}
```

---

## 댓글 (Comment)

### 댓글 목록 조회
- **Method**: `GET`
- **Endpoint**: `/api/posts/{post_id}/comments`
- **Path Parameters**:
  - `post_id`: int - 게시글 ID
- **Description**: 특정 게시글의 댓글 목록을 조회합니다.
- **Success Response (200)**:
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
- **Error Responses**:
  - `404`: `{ "message": "post_not_found", "data": null }` - 게시글을 찾을 수 없습니다.

---

### 댓글 등록
- **Method**: `POST`
- **Endpoint**: `/api/posts/{post_id}/comments`
- **Request Body**:
```json
{
  "content": "댓글 내용"
}
```
- **Description**: 댓글 입력 시 버튼이 활성화(ACA0EB → 7F6AEE). 입력 후 등록 버튼 클릭 시 서버로 댓글 등록 요청.  
**※ Model API 연동**: 댓글 작성 시 자동으로 감성 분석(positive/negative)이 실행되며, 분석 결과가 응답에 포함됩니다. Model API 서버가 응답하지 않거나 오류가 발생해도 댓글 작성은 성공 처리됩니다.
- **Success Response (201)**:
```json
{
  "message": "create_comment_success",
  "data": {
    "comment_id": 1,
    "sentiment": {
      "label": "positive",
      "confidence": 0.85
    }
  }
}
```
또는 (Model API 실패 시):
```json
{
  "message": "create_comment_success",
  "data": {
    "comment_id": 1
  }
}
```
- **Note**: 
  - `sentiment` 필드는 Model API가 정상 작동할 때만 포함됩니다.
  - Model API 서버가 응답하지 않거나 오류가 발생하면 `sentiment` 필드는 포함되지 않지만, 댓글 작성은 성공 처리됩니다.
- **Error Responses**:
  - `400`: `{ "message": "invalid_request", "data": null }` - 잘못된 요청입니다.
  - `401`: `{ "message": "unauthorized_user", "data": null }` - 로그인이 필요합니다.
  - `404`: `{ "message": "post_not_found", "data": null }` - 게시글을 찾을 수 없습니다.
  - `500`: `{ "message": "internal_server_error", "data": null }` - 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.

---

### 댓글 수정
- **Method**: `PATCH`
- **Endpoint**: `/api/posts/{post_id}/comments/{comment_id}`
- **Request Body**:
```json
{
  "content": "수정된 댓글 내용"
}
```
- **Description**: 수정 버튼 클릭 시 기존 내용이 입력창에 표시되고, 등록 버튼이 "댓글 수정" 버튼으로 변경됨. 수정 완료 시 내용 갱신.
- **Success Response (200)**:
```json
{
  "message": "update_comment_success",
  "data": {
    "comment_id": 1
  }
}
```
- **Error Responses**:
  - `403`: `{ "message": "forbidden", "data": null }`
  - `404`: `{ "message": "comment_not_found", "data": null }`
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

### 댓글 삭제
- **Method**: `DELETE`
- **Endpoint**: `/api/posts/{post_id}/comments/{comment_id}`
- **Description**: 댓글 삭제 버튼 클릭 시 확인 모달 띄우고, "확인" 클릭 시 댓글 삭제. 모달 시: 백그라운드 불투명도 50%, 스크롤 및 클릭 차단.
- **Success Response (200)**:
```json
{
  "message": "delete_comment_success",
  "data": {
    "comment_id": 1
  }
}
```
- **Error Responses**:
  - `403`: `{ "message": "forbidden", "data": null }`
  - `404`: `{ "message": "comment_not_found", "data": null }`
  - `500`: `{ "message": "internal_server_error", "data": null }`

---

## Model API 연동 정보

### 포트 자동 감지
- Backend는 실행 중인 Model API 서버의 포트를 자동으로 감지합니다.
- 우선순위: 8002 → 8001 → 8003 → 8082 → 8502 → 8000
- 환경변수 `MODEL_API_URL` 또는 `MODEL_API_PORT`로 수동 설정 가능합니다.

### 이미지 분류 (Image Classification)
- **엔드포인트**: Model API `/api/predict`
- **트리거**: 게시글 이미지 업로드 시 자동 실행
- **결과**: `prediction` 객체에 `class_name` (Dog/Cat)과 `confidence_score` 포함

### 감성 분석 (Sentiment Analysis)
- **엔드포인트**: Model API `/api/sentiment`
- **트리거**: 댓글 작성 시 자동 실행
- **결과**: `sentiment` 객체에 `label` (positive/negative)과 `confidence` 포함

---

## 공통 에러 코드

- `400`: 잘못된 요청 (Bad Request)
- `401`: 인증 필요 (Unauthorized)
- `403`: 권한 없음 (Forbidden)
- `404`: 리소스 없음 (Not Found)
- `409`: 충돌 (Conflict - 중복 등)
- `413`: 페이로드 너무 큼 (Payload Too Large)
- `422`: 유효성 검사 실패 (Unprocessable Entity)
- `500`: 서버 내부 오류 (Internal Server Error)
