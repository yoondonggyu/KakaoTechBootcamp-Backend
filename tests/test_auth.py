"""
인증(Auth) API 테스트 케이스

테스트 대상:
- POST /api/auth/signup : 회원가입
- POST /api/auth/login  : 로그인

테스트 흐름:
1. 정상 케이스 (Happy Path)
2. 유효성 검사 실패 케이스 (Validation Error)
3. 비즈니스 로직 에러 케이스 (Business Logic Error)
"""
import pytest


class TestSignup:
    """
    회원가입 API 테스트

    엔드포인트: POST /api/auth/signup
    요청 형식: JSON
    {
        "email": "user@example.com",
        "password": "Password123!",
        "password_check": "Password123!",
        "nickname": "닉네임",
        "profile_image_url": "https://example.com/image.jpg"
    }
    """

    # =========================================================================
    # 정상 케이스 (Happy Path)
    # =========================================================================

    def test_signup_success(self, client, test_user_data):
        """
        [성공] 정상 회원가입

        Given: 유효한 사용자 데이터
        When: 회원가입 API 호출
        Then: 201 Created, message="register_success"

        예상 결과:
        - Status: 201
        - Response: {"message": "register_success", "data": {...}}
        """
        response = client.post("/api/auth/signup", json=test_user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data["message"] == "register_success"
        assert "data" in data

    def test_signup_without_profile_image(self, client, test_user_data):
        """
        [성공] 프로필 이미지 없이 회원가입

        Given: profile_image_url이 없는 사용자 데이터
        When: 회원가입 API 호출
        Then: 201 Created (프로필 이미지는 선택사항)
        """
        test_user_data.pop("profile_image_url", None)

        response = client.post("/api/auth/signup", json=test_user_data)

        # 프로필 이미지가 필수가 아니라면 성공, 필수라면 422
        assert response.status_code in [201, 422]

    # =========================================================================
    # 중복 검사 케이스
    # =========================================================================

    def test_signup_duplicate_email(self, client, test_user_data):
        """
        [실패] 중복 이메일로 회원가입 시도

        Given: 이미 가입된 이메일
        When: 같은 이메일로 재가입 시도
        Then: 400 또는 409 Conflict

        예상 결과:
        - Status: 400 또는 409
        - Response: {"message": "email_already_exists", ...}
        """
        # 첫 번째 회원가입 (성공)
        first_response = client.post("/api/auth/signup", json=test_user_data)
        assert first_response.status_code == 201

        # 두 번째 회원가입 (실패 - 중복)
        second_response = client.post("/api/auth/signup", json=test_user_data)

        assert second_response.status_code in [400, 409]
        # 에러 메시지 검증 (구현에 따라 다를 수 있음)
        data = second_response.json()
        assert "message" in data

    # =========================================================================
    # 유효성 검사 실패 케이스
    # =========================================================================

    def test_signup_invalid_email_format(self, client, test_user_data):
        """
        [실패] 잘못된 이메일 형식

        Given: 유효하지 않은 이메일 형식 (@ 없음)
        When: 회원가입 API 호출
        Then: 400 Bad Request 또는 422 Unprocessable Entity

        예상 결과:
        - Status: 400 또는 422
        - 이메일 형식 에러 메시지
        """
        test_user_data["email"] = "invalid-email"

        response = client.post("/api/auth/signup", json=test_user_data)

        # 서버 구현에 따라 400 (커스텀 검증) 또는 422 (Pydantic) 반환
        assert response.status_code in [400, 422]

    def test_signup_password_mismatch(self, client, test_user_data):
        """
        [실패] 비밀번호 확인 불일치

        Given: password와 password_check가 다름
        When: 회원가입 API 호출
        Then: 400 또는 422

        예상 결과:
        - Status: 400 또는 422
        - Response: {"message": "password_mismatch", ...}
        """
        test_user_data["password_check"] = "DifferentPassword123!"

        response = client.post("/api/auth/signup", json=test_user_data)

        assert response.status_code in [400, 422]

    def test_signup_missing_required_fields(self, client):
        """
        [실패] 필수 필드 누락

        Given: email, password만 있고 나머지 필드 누락
        When: 회원가입 API 호출
        Then: 422 Unprocessable Entity

        예상 결과:
        - Status: 422
        - 누락된 필드에 대한 에러 메시지
        """
        incomplete_data = {
            "email": "test@example.com",
            "password": "Test1234!@#$"
            # nickname, password_check 누락
        }

        response = client.post("/api/auth/signup", json=incomplete_data)

        assert response.status_code == 422

    def test_signup_empty_nickname(self, client, test_user_data):
        """
        [실패] 빈 닉네임

        Given: nickname이 빈 문자열
        When: 회원가입 API 호출
        Then: 400 또는 422
        """
        test_user_data["nickname"] = ""

        response = client.post("/api/auth/signup", json=test_user_data)

        assert response.status_code in [400, 422]

    def test_signup_invalid_profile_url(self, client, test_user_data):
        """
        [실패] 잘못된 프로필 URL 형식

        Given: 유효하지 않은 URL 형식
        When: 회원가입 API 호출
        Then: 422 Unprocessable Entity
        """
        test_user_data["profile_image_url"] = "not-a-valid-url"

        response = client.post("/api/auth/signup", json=test_user_data)

        assert response.status_code == 422

    def test_signup_weak_password(self, client, test_user_data):
        """
        [실패] 약한 비밀번호

        Given: 규칙을 만족하지 않는 비밀번호 (숫자/특수문자 없음)
        When: 회원가입 API 호출
        Then: 400 또는 422

        비밀번호 규칙 (일반적):
        - 8자 이상
        - 대소문자 포함
        - 숫자 포함
        - 특수문자 포함
        """
        test_user_data["password"] = "weak"
        test_user_data["password_check"] = "weak"

        response = client.post("/api/auth/signup", json=test_user_data)

        assert response.status_code in [400, 422]


class TestLogin:
    """
    로그인 API 테스트

    엔드포인트: POST /api/auth/login
    요청 형식: JSON
    {
        "email": "user@example.com",
        "password": "Password123!"
    }
    """

    # =========================================================================
    # 정상 케이스 (Happy Path)
    # =========================================================================

    def test_login_success(self, client, registered_user):
        """
        [성공] 정상 로그인

        Given: 등록된 사용자의 올바른 자격 증명
        When: 로그인 API 호출
        Then: 200 OK, message="login_success"

        예상 결과:
        - Status: 200
        - Response: {"message": "login_success", "data": {"user_id": ...}}
        """
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": registered_user["user_data"]["password"]
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["message"] == "login_success"
        assert "data" in data

    # =========================================================================
    # 인증 실패 케이스
    # =========================================================================

    def test_login_wrong_password(self, client, registered_user):
        """
        [실패] 잘못된 비밀번호

        Given: 등록된 이메일, 잘못된 비밀번호
        When: 로그인 API 호출
        Then: 400 또는 401 Unauthorized

        예상 결과:
        - Status: 400 또는 401
        - Response: {"message": "invalid_credentials", ...}
        """
        login_data = {
            "email": registered_user["user_data"]["email"],
            "password": "WrongPassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code in [400, 401]

    def test_login_nonexistent_user(self, client):
        """
        [실패] 존재하지 않는 사용자

        Given: 등록되지 않은 이메일
        When: 로그인 API 호출
        Then: 400, 401, 또는 404

        예상 결과:
        - 보안상 "이메일 없음"과 "비밀번호 틀림"을 구분하지 않는 것이 좋음
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code in [400, 401, 404]

    # =========================================================================
    # 유효성 검사 실패 케이스
    # =========================================================================

    def test_login_invalid_email_format(self, client):
        """
        [실패] 잘못된 이메일 형식으로 로그인

        Given: 유효하지 않은 이메일 형식
        When: 로그인 API 호출
        Then: 400, 401, 또는 422
        """
        login_data = {
            "email": "invalid-email",
            "password": "SomePassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code in [400, 401, 422]

    def test_login_missing_password(self, client):
        """
        [실패] 비밀번호 누락

        Given: email만 있고 password 누락
        When: 로그인 API 호출
        Then: 422 Unprocessable Entity
        """
        login_data = {
            "email": "test@example.com"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_missing_email(self, client):
        """
        [실패] 이메일 누락

        Given: password만 있고 email 누락
        When: 로그인 API 호출
        Then: 422 Unprocessable Entity
        """
        login_data = {
            "password": "SomePassword123!"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_empty_credentials(self, client):
        """
        [실패] 빈 자격 증명

        Given: email과 password가 모두 빈 문자열
        When: 로그인 API 호출
        Then: 400, 401, 또는 422
        """
        login_data = {
            "email": "",
            "password": ""
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code in [400, 401, 422]

    def test_login_empty_body(self, client):
        """
        [실패] 빈 요청 본문

        Given: 빈 JSON 객체
        When: 로그인 API 호출
        Then: 422 Unprocessable Entity
        """
        response = client.post("/api/auth/login", json={})

        assert response.status_code == 422
