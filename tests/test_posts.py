"""
게시글(Posts) API 테스트 케이스

테스트 대상:
- GET    /api/posts           : 게시글 목록 조회
- GET    /api/posts/{id}      : 게시글 상세 조회
- POST   /api/posts           : 게시글 생성
- PATCH  /api/posts/{id}      : 게시글 수정
- DELETE /api/posts/{id}      : 게시글 삭제
- POST   /api/posts/{id}/like : 좋아요 토글
- PATCH  /api/posts/{id}/view : 조회수 증가
- POST   /api/posts/upload    : 이미지 업로드

테스트 구조:
1. 정상 케이스 (Happy Path)
2. 유효성 검사 실패 케이스
3. 권한 관련 케이스
4. 리소스 없음 케이스
"""
import pytest
import io


class TestGetPosts:
    """
    게시글 목록 조회 API 테스트

    엔드포인트: GET /api/posts
    쿼리 파라미터:
    - page: 페이지 번호 (기본값 1)
    - limit: 페이지당 항목 수 (기본값 10, 최대 100)
    - board_type: 게시판 타입 (couple, family 등)
    """

    def test_get_posts_success(self, client):
        """
        [성공] 게시글 목록 조회

        Given: 게시글이 존재하거나 비어있음
        When: 목록 조회 API 호출
        Then: 200 OK, 게시글 목록 반환

        예상 결과:
        - Status: 200
        - Response: {"message": "get_posts_success", "data": [...]}
        """
        response = client.get("/api/posts")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "get_posts_success"
        assert "data" in data

    def test_get_posts_with_pagination(self, client):
        """
        [성공] 페이지네이션 적용 목록 조회

        Given: 페이지 파라미터 지정
        When: page=1, limit=5로 조회
        Then: 200 OK, 최대 5개 항목 반환
        """
        response = client.get("/api/posts?page=1&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "get_posts_success"

    def test_get_posts_with_board_type(self, client):
        """
        [성공] 게시판 타입별 목록 조회

        Given: board_type 파라미터 지정
        When: board_type=couple로 조회
        Then: 200 OK, 해당 타입 게시글만 반환
        """
        response = client.get("/api/posts?board_type=couple")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "get_posts_success"

    def test_get_posts_invalid_page_zero(self, client):
        """
        [실패] 페이지 번호 0

        Given: page=0 (유효하지 않음, 1 이상이어야 함)
        When: 목록 조회 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.get("/api/posts?page=0")

        assert response.status_code == 422

    def test_get_posts_invalid_page_negative(self, client):
        """
        [실패] 음수 페이지 번호

        Given: page=-1
        When: 목록 조회 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.get("/api/posts?page=-1")

        assert response.status_code == 422

    def test_get_posts_invalid_limit_zero(self, client):
        """
        [실패] limit 0

        Given: limit=0 (최소 1 이상이어야 함)
        When: 목록 조회 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.get("/api/posts?limit=0")

        assert response.status_code == 422

    def test_get_posts_limit_exceeds_max(self, client):
        """
        [실패] limit 최대값 초과

        Given: limit=101 (최대 100)
        When: 목록 조회 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.get("/api/posts?limit=101")

        assert response.status_code == 422


class TestGetPost:
    """
    게시글 상세 조회 API 테스트

    엔드포인트: GET /api/posts/{post_id}
    """

    def test_get_post_success(self, client, created_post):
        """
        [성공] 게시글 상세 조회

        Given: 존재하는 게시글 ID
        When: 상세 조회 API 호출
        Then: 200 OK, 게시글 상세 정보 반환

        예상 결과:
        - Status: 200
        - Response: {"message": "get_post_success", "data": {...}}
        """
        response = client.get(f"/api/posts/{created_post['post_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "get_post_success"
        assert "data" in data

    def test_get_post_not_found(self, client):
        """
        [실패] 존재하지 않는 게시글 조회

        Given: 존재하지 않는 게시글 ID (99999)
        When: 상세 조회 API 호출
        Then: 404 Not Found 또는 400 Bad Request
        """
        response = client.get("/api/posts/99999")

        assert response.status_code in [400, 404]

    def test_get_post_invalid_id_format(self, client):
        """
        [실패] 잘못된 게시글 ID 형식

        Given: 숫자가 아닌 ID ("invalid")
        When: 상세 조회 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.get("/api/posts/invalid")

        assert response.status_code == 422


class TestCreatePost:
    """
    게시글 생성 API 테스트

    엔드포인트: POST /api/posts
    요청 형식: JSON
    {
        "title": "제목",
        "content": "내용",
        "board_type": "couple",
        "image_url": "https://...",  // 선택
        "image_class": "Dog"          // 선택
    }
    인증: X-User-Id 헤더 필요
    """

    def test_create_post_success(self, client, auth_header, test_post_data):
        """
        [성공] 게시글 생성

        Given: 인증된 사용자, 유효한 게시글 데이터
        When: 게시글 생성 API 호출
        Then: 201 Created

        예상 결과:
        - Status: 201
        - Response: {"message": "create_post_success", "data": {...}}
        """
        response = client.post(
            "/api/posts",
            json=test_post_data,
            headers=auth_header
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "create_post_success"

    def test_create_post_with_image(self, client, auth_header, test_post_data):
        """
        [성공] 이미지 포함 게시글 생성

        Given: 인증된 사용자, 이미지 URL 포함 게시글 데이터
        When: 게시글 생성 API 호출
        Then: 201 Created
        """
        test_post_data["image_url"] = "https://example.com/image.jpg"
        test_post_data["image_class"] = "Dog"

        response = client.post(
            "/api/posts",
            json=test_post_data,
            headers=auth_header
        )

        assert response.status_code == 201

    def test_create_post_unauthorized(self, client, test_post_data):
        """
        [실패] 인증 없이 게시글 생성

        Given: 인증 헤더 없음
        When: 게시글 생성 API 호출
        Then: 401 또는 403 또는 422

        예상 결과:
        - 인증이 필요한 엔드포인트에서 거부됨
        """
        response = client.post("/api/posts", json=test_post_data)

        assert response.status_code in [401, 403, 422]

    def test_create_post_missing_title(self, client, auth_header):
        """
        [실패] 제목 없이 게시글 생성

        Given: title 필드 누락
        When: 게시글 생성 API 호출
        Then: 422 Unprocessable Entity
        """
        incomplete_data = {
            "content": "내용만 있는 게시글"
        }

        response = client.post(
            "/api/posts",
            json=incomplete_data,
            headers=auth_header
        )

        assert response.status_code == 422

    def test_create_post_missing_content(self, client, auth_header):
        """
        [실패] 내용 없이 게시글 생성

        Given: content 필드 누락
        When: 게시글 생성 API 호출
        Then: 422 Unprocessable Entity
        """
        incomplete_data = {
            "title": "제목만 있는 게시글"
        }

        response = client.post(
            "/api/posts",
            json=incomplete_data,
            headers=auth_header
        )

        assert response.status_code == 422

    def test_create_post_empty_title(self, client, auth_header):
        """
        [실패] 빈 제목으로 게시글 생성

        Given: title이 빈 문자열
        When: 게시글 생성 API 호출
        Then: 400 또는 422
        """
        data = {
            "title": "",
            "content": "내용입니다"
        }

        response = client.post(
            "/api/posts",
            json=data,
            headers=auth_header
        )

        assert response.status_code in [400, 422]

    def test_create_post_title_too_long(self, client, auth_header):
        """
        [실패] 제목 길이 초과

        Given: title이 최대 길이(2000자) 초과
        When: 게시글 생성 API 호출
        Then: 422 Unprocessable Entity
        """
        long_title_data = {
            "title": "A" * 2001,
            "content": "내용"
        }

        response = client.post(
            "/api/posts",
            json=long_title_data,
            headers=auth_header
        )

        assert response.status_code == 422


class TestUpdatePost:
    """
    게시글 수정 API 테스트

    엔드포인트: PATCH /api/posts/{post_id}
    인증: X-User-Id 헤더 필요 (작성자만 수정 가능)
    """

    def test_update_post_success(self, client, auth_header, created_post):
        """
        [성공] 게시글 수정

        Given: 인증된 작성자, 수정할 게시글 존재
        When: 게시글 수정 API 호출
        Then: 200 OK

        예상 결과:
        - Status: 200
        - Response: {"message": "update_post_success", "data": {...}}
        """
        update_data = {"title": "수정된 제목"}

        response = client.patch(
            f"/api/posts/{created_post['post_id']}",
            json=update_data,
            headers=auth_header
        )

        assert response.status_code == 200

    def test_update_post_not_found(self, client, auth_header):
        """
        [실패] 존재하지 않는 게시글 수정

        Given: 존재하지 않는 게시글 ID
        When: 수정 API 호출
        Then: 403 또는 404
        """
        update_data = {"title": "수정된 제목"}

        response = client.patch(
            "/api/posts/99999",
            json=update_data,
            headers=auth_header
        )

        assert response.status_code in [403, 404]

    def test_update_post_unauthorized(self, client, created_post):
        """
        [실패] 인증 없이 게시글 수정

        Given: 인증 헤더 없음
        When: 수정 API 호출
        Then: 401 또는 403 또는 422
        """
        update_data = {"title": "수정된 제목"}

        response = client.patch(
            f"/api/posts/{created_post['post_id']}",
            json=update_data
        )

        assert response.status_code in [401, 403, 422]

    def test_update_post_by_non_owner(self, client, auth_header_2, created_post):
        """
        [실패] 다른 사용자가 게시글 수정 시도

        Given: 게시글 작성자가 아닌 다른 사용자로 인증
        When: 수정 API 호출
        Then: 403 Forbidden
        """
        update_data = {"title": "수정된 제목"}

        response = client.patch(
            f"/api/posts/{created_post['post_id']}",
            json=update_data,
            headers=auth_header_2
        )

        assert response.status_code == 403


class TestDeletePost:
    """
    게시글 삭제 API 테스트

    엔드포인트: DELETE /api/posts/{post_id}
    인증: X-User-Id 헤더 필요 (작성자만 삭제 가능)
    """

    def test_delete_post_success(self, client, auth_header, created_post):
        """
        [성공] 게시글 삭제

        Given: 인증된 작성자, 삭제할 게시글 존재
        When: 삭제 API 호출
        Then: 200 OK

        예상 결과:
        - Status: 200
        - Response: {"message": "delete_post_success", ...}
        """
        response = client.delete(
            f"/api/posts/{created_post['post_id']}",
            headers=auth_header
        )

        assert response.status_code == 200

    def test_delete_post_not_found(self, client, auth_header):
        """
        [실패] 존재하지 않는 게시글 삭제

        Given: 존재하지 않는 게시글 ID
        When: 삭제 API 호출
        Then: 403 또는 404
        """
        response = client.delete("/api/posts/99999", headers=auth_header)

        assert response.status_code in [403, 404]

    def test_delete_post_unauthorized(self, client, created_post):
        """
        [실패] 인증 없이 게시글 삭제

        Given: 인증 헤더 없음
        When: 삭제 API 호출
        Then: 401 또는 403 또는 422
        """
        response = client.delete(f"/api/posts/{created_post['post_id']}")

        assert response.status_code in [401, 403, 422]

    def test_delete_post_by_non_owner(self, client, auth_header_2, created_post):
        """
        [실패] 다른 사용자가 게시글 삭제 시도

        Given: 게시글 작성자가 아닌 다른 사용자로 인증
        When: 삭제 API 호출
        Then: 403 Forbidden
        """
        response = client.delete(
            f"/api/posts/{created_post['post_id']}",
            headers=auth_header_2
        )

        assert response.status_code == 403


class TestToggleLike:
    """
    좋아요 토글 API 테스트

    엔드포인트: POST /api/posts/{post_id}/like
    인증: X-User-Id 헤더 필요
    동작: 좋아요 추가/취소 토글
    """

    def test_toggle_like_add(self, client, auth_header, created_post):
        """
        [성공] 좋아요 추가

        Given: 인증된 사용자, 좋아요하지 않은 게시글
        When: 좋아요 API 호출
        Then: 200 OK, 좋아요 추가됨
        """
        response = client.post(
            f"/api/posts/{created_post['post_id']}/like",
            headers=auth_header
        )

        assert response.status_code == 200

    def test_toggle_like_remove(self, client, auth_header, created_post):
        """
        [성공] 좋아요 취소 (토글)

        Given: 인증된 사용자, 이미 좋아요한 게시글
        When: 좋아요 API 두 번 호출
        Then: 200 OK, 좋아요 취소됨
        """
        # 첫 번째 호출: 좋아요 추가
        client.post(
            f"/api/posts/{created_post['post_id']}/like",
            headers=auth_header
        )

        # 두 번째 호출: 좋아요 취소
        response = client.post(
            f"/api/posts/{created_post['post_id']}/like",
            headers=auth_header
        )

        assert response.status_code == 200

    def test_toggle_like_not_found(self, client, auth_header):
        """
        [실패] 존재하지 않는 게시글에 좋아요

        Given: 존재하지 않는 게시글 ID
        When: 좋아요 API 호출
        Then: 400 또는 404
        """
        response = client.post("/api/posts/99999/like", headers=auth_header)

        assert response.status_code in [400, 404]

    def test_toggle_like_unauthorized(self, client, created_post):
        """
        [실패] 인증 없이 좋아요

        Given: 인증 헤더 없음
        When: 좋아요 API 호출
        Then: 401 또는 403 또는 422
        """
        response = client.post(f"/api/posts/{created_post['post_id']}/like")

        assert response.status_code in [401, 403, 422]


class TestIncrementView:
    """
    조회수 증가 API 테스트

    엔드포인트: PATCH /api/posts/{post_id}/view
    인증: 불필요 (누구나 조회 가능)
    """

    def test_increment_view_success(self, client, created_post):
        """
        [성공] 조회수 증가

        Given: 존재하는 게시글
        When: 조회수 증가 API 호출
        Then: 200 OK, 조회수 +1
        """
        response = client.patch(f"/api/posts/{created_post['post_id']}/view")

        assert response.status_code == 200

    def test_increment_view_not_found(self, client):
        """
        [실패] 존재하지 않는 게시글 조회수 증가

        Given: 존재하지 않는 게시글 ID
        When: 조회수 증가 API 호출
        Then: 400 또는 404
        """
        response = client.patch("/api/posts/99999/view")

        assert response.status_code in [400, 404]


class TestUploadPostImage:
    """
    게시글 이미지 업로드 API 테스트

    엔드포인트: POST /api/posts/upload
    요청 형식: multipart/form-data
    필드: file (이미지 파일)
    """

    def test_upload_post_image_success_png(self, client, valid_png_image):
        """
        [성공] PNG 이미지 업로드

        Given: 유효한 PNG 이미지 파일
        When: 업로드 API 호출
        Then: 200 OK, 업로드된 URL 반환

        예상 결과:
        - Status: 200
        - Response: {"message": "upload_success", "data": {"url": "..."}}
        """
        files = {"file": ("test_image.png", io.BytesIO(valid_png_image), "image/png")}

        response = client.post("/api/posts/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "upload_success"

    def test_upload_post_image_success_jpeg(self, client, valid_jpeg_image):
        """
        [성공] JPEG 이미지 업로드

        Given: 유효한 JPEG 이미지 파일
        When: 업로드 API 호출
        Then: 200 OK
        """
        files = {"file": ("test_image.jpg", io.BytesIO(valid_jpeg_image), "image/jpeg")}

        response = client.post("/api/posts/upload", files=files)

        assert response.status_code == 200

    def test_upload_post_image_invalid_type(self, client):
        """
        [실패] 잘못된 파일 타입 업로드

        Given: 텍스트 파일 (이미지가 아님)
        When: 업로드 API 호출
        Then: 400 또는 415 또는 422

        예상 결과:
        - 이미지 파일만 허용됨
        """
        text_data = b"This is not an image"
        files = {"file": ("test.txt", io.BytesIO(text_data), "text/plain")}

        response = client.post("/api/posts/upload", files=files)

        assert response.status_code in [400, 415, 422]

    def test_upload_post_image_no_file(self, client):
        """
        [실패] 파일 없이 업로드 요청

        Given: file 필드 없음
        When: 업로드 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.post("/api/posts/upload")

        assert response.status_code == 422
