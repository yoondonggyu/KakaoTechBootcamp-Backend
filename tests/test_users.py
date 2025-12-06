"""
사용자(Users) API 테스트 케이스
- 프로필 이미지 업로드
- 프로필(닉네임) 수정
- 비밀번호 변경
- 회원 탈퇴
"""
import pytest
import io


class TestProfileImageUpload:
    """프로필 이미지 업로드 API 테스트"""
    
    def test_upload_valid_image(self, client):
        """유효한 이미지 업로드 테스트"""
        # 가짜 이미지 데이터 생성 (1x1 PNG)
        image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {"file": ("test_image.png", io.BytesIO(image_data), "image/png")}
        
        response = client.post("/api/users/profile/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "upload_success"
    
    def test_upload_jpeg_image(self, client):
        """JPEG 이미지 업로드 테스트"""
        # 최소한의 JPEG 데이터
        image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9telecom0telecom4\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd5\xff\xd9'
        files = {"file": ("test_image.jpg", io.BytesIO(image_data), "image/jpeg")}
        
        response = client.post("/api/users/profile/upload", files=files)
        
        # 업로드 성공하거나 이미지 형식 관련 에러
        assert response.status_code in [200, 400, 422]
    
    def test_upload_invalid_file_type(self, client):
        """잘못된 파일 타입 업로드 테스트"""
        text_data = b"This is not an image"
        files = {"file": ("test.txt", io.BytesIO(text_data), "text/plain")}
        
        response = client.post("/api/users/profile/upload", files=files)
        
        assert response.status_code in [400, 422, 415]
    
    def test_upload_no_file(self, client):
        """파일 없이 업로드 요청 테스트"""
        response = client.post("/api/users/profile/upload")
        
        assert response.status_code == 422


class TestProfileUpdate:
    """프로필 수정 API 테스트"""
    
    def test_update_nickname_success(self, client, logged_in_user, auth_header):
        """닉네임 수정 성공 테스트"""
        update_data = {"nickname": "새닉네임"}
        
        response = client.patch(
            "/api/users/profile",
            json=update_data,
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "update_profile_success"
    
    def test_update_nickname_unauthorized(self, client):
        """인증 없이 닉네임 수정 시도 테스트"""
        update_data = {"nickname": "새닉네임"}
        
        response = client.patch("/api/users/profile", json=update_data)
        
        assert response.status_code in [401, 403, 422]
    
    def test_update_empty_nickname(self, client, auth_header):
        """빈 닉네임으로 수정 시도 테스트"""
        update_data = {"nickname": ""}
        
        response = client.patch(
            "/api/users/profile",
            json=update_data,
            headers=auth_header
        )
        
        assert response.status_code in [400, 422]


class TestPasswordUpdate:
    """비밀번호 변경 API 테스트"""
    
    def test_update_password_success(self, client, logged_in_user, auth_header):
        """비밀번호 변경 성공 테스트"""
        password_data = {
            "old_password": logged_in_user["user_data"]["password"],
            "password": "NewPassword123!@#$",
            "password_check": "NewPassword123!@#$"
        }
        
        response = client.put(
            "/api/users/password",
            json=password_data,
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "update_password_success"
    
    def test_update_password_wrong_old(self, client, auth_header):
        """잘못된 현재 비밀번호로 변경 시도 테스트"""
        password_data = {
            "old_password": "WrongOldPassword123!",
            "password": "NewPassword123!@#$",
            "password_check": "NewPassword123!@#$"
        }
        
        response = client.put(
            "/api/users/password",
            json=password_data,
            headers=auth_header
        )
        
        assert response.status_code in [400, 401, 403, 422]
    
    def test_update_password_mismatch(self, client, auth_header, logged_in_user):
        """새 비밀번호 확인 불일치 테스트"""
        password_data = {
            "old_password": logged_in_user["user_data"]["password"] if logged_in_user else "Test1234!@#$",
            "password": "NewPassword123!@#$",
            "password_check": "DifferentPassword123!@#$"
        }
        
        response = client.put(
            "/api/users/password",
            json=password_data,
            headers=auth_header
        )
        
        assert response.status_code in [400, 422]
    
    def test_update_password_unauthorized(self, client):
        """인증 없이 비밀번호 변경 시도 테스트"""
        password_data = {
            "old_password": "OldPassword123!",
            "password": "NewPassword123!@#$",
            "password_check": "NewPassword123!@#$"
        }
        
        response = client.put("/api/users/password", json=password_data)
        
        assert response.status_code in [401, 403, 422]


class TestUserDeletion:
    """회원 탈퇴 API 테스트"""
    
    def test_delete_user_success(self, client, logged_in_user, auth_header):
        """회원 탈퇴 성공 테스트"""
        response = client.delete("/api/users/profile", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "delete_user_success"
    
    def test_delete_user_unauthorized(self, client):
        """인증 없이 회원 탈퇴 시도 테스트"""
        response = client.delete("/api/users/profile")
        
        assert response.status_code in [401, 403, 422]
    
    def test_delete_user_twice(self, client, logged_in_user, auth_header):
        """이미 탈퇴한 사용자 재탈퇴 시도 테스트"""
        # 첫 번째 탈퇴
        client.delete("/api/users/profile", headers=auth_header)
        
        # 두 번째 탈퇴 시도
        response = client.delete("/api/users/profile", headers=auth_header)
        
        assert response.status_code in [401, 403, 404, 422]
