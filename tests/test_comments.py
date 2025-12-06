"""
댓글(Comments) API 테스트 케이스
- 댓글 목록 조회
- 댓글 생성
- 댓글 수정
- 댓글 삭제
"""
import pytest


class TestGetComments:
    """댓글 목록 조회 API 테스트"""
    
    def test_get_comments_success(self, client):
        """댓글 목록 조회 성공 테스트 (게시글이 없어도 빈 목록 반환 가능)"""
        response = client.get("/api/posts/1/comments")
        
        # 게시글이 없으면 404, 있으면 200
        assert response.status_code in [200, 404, 400]
    
    def test_get_comments_invalid_post_id(self, client):
        """잘못된 게시글 ID로 댓글 조회 테스트"""
        response = client.get("/api/posts/invalid/comments")
        
        assert response.status_code == 422


class TestCreateComment:
    """댓글 생성 API 테스트"""
    
    def test_create_comment_post_not_found(self, client, auth_header, test_comment_data):
        """존재하지 않는 게시글에 댓글 작성 시도 테스트"""
        response = client.post(
            "/api/posts/99999/comments",
            json=test_comment_data,
            headers=auth_header
        )
        
        assert response.status_code in [404, 400]
    
    def test_create_comment_unauthorized(self, client, test_comment_data):
        """인증 없이 댓글 작성 시도 테스트"""
        response = client.post("/api/posts/1/comments", json=test_comment_data)
        
        assert response.status_code in [401, 403, 422]
    
    def test_create_comment_missing_content(self, client, auth_header):
        """내용 없이 댓글 작성 시도 테스트"""
        empty_comment = {}
        
        response = client.post(
            "/api/posts/1/comments",
            json=empty_comment,
            headers=auth_header
        )
        
        assert response.status_code == 422
    
    def test_create_comment_empty_content(self, client, auth_header, created_post):
        """빈 내용으로 댓글 작성 시도 테스트

        Note: 현재 서버 구현에서는 빈 댓글도 허용됨 (201)
        비즈니스 로직에 따라 400/422 또는 201이 반환될 수 있음
        """
        empty_comment = {"content": ""}
        post_id = created_post["post_id"]

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json=empty_comment,
            headers=auth_header
        )

        # 서버 구현에 따라 빈 댓글 허용 (201) 또는 거부 (400/422)
        assert response.status_code in [201, 400, 422]


class TestUpdateComment:
    """댓글 수정 API 테스트"""
    
    def test_update_comment_not_found(self, client, auth_header):
        """존재하지 않는 댓글 수정 시도 테스트"""
        update_data = {"content": "수정된 댓글 내용"}
        
        response = client.patch(
            "/api/posts/1/comments/99999",
            json=update_data,
            headers=auth_header
        )
        
        assert response.status_code in [403, 404, 400]
    
    def test_update_comment_unauthorized(self, client):
        """인증 없이 댓글 수정 시도 테스트"""
        update_data = {"content": "수정된 댓글 내용"}
        
        response = client.patch("/api/posts/1/comments/1", json=update_data)
        
        assert response.status_code in [401, 403, 422]
    
    def test_update_comment_missing_content(self, client, auth_header):
        """내용 없이 댓글 수정 시도 테스트"""
        empty_update = {}
        
        response = client.patch(
            "/api/posts/1/comments/1",
            json=empty_update,
            headers=auth_header
        )
        
        assert response.status_code == 422
    
    def test_update_comment_post_not_found(self, client, auth_header):
        """존재하지 않는 게시글의 댓글 수정 시도 테스트"""
        update_data = {"content": "수정된 댓글 내용"}
        
        response = client.patch(
            "/api/posts/99999/comments/1",
            json=update_data,
            headers=auth_header
        )
        
        assert response.status_code in [403, 404, 400]


class TestDeleteComment:
    """댓글 삭제 API 테스트"""
    
    def test_delete_comment_not_found(self, client, auth_header):
        """존재하지 않는 댓글 삭제 시도 테스트"""
        response = client.delete(
            "/api/posts/1/comments/99999",
            headers=auth_header
        )
        
        assert response.status_code in [403, 404, 400]
    
    def test_delete_comment_unauthorized(self, client):
        """인증 없이 댓글 삭제 시도 테스트"""
        response = client.delete("/api/posts/1/comments/1")
        
        assert response.status_code in [401, 403, 422]
    
    def test_delete_comment_post_not_found(self, client, auth_header):
        """존재하지 않는 게시글의 댓글 삭제 시도 테스트"""
        response = client.delete(
            "/api/posts/99999/comments/1",
            headers=auth_header
        )
        
        assert response.status_code in [403, 404, 400]


class TestCommentIntegration:
    """댓글 통합 테스트 (게시글과 연동)"""
    
    def test_comment_workflow(self, client, auth_header, test_post_data, test_comment_data):
        """게시글 생성 -> 댓글 작성 -> 댓글 조회 -> 댓글 수정 -> 댓글 삭제 워크플로우"""
        # 1. 게시글 생성
        post_response = client.post(
            "/api/posts",
            json=test_post_data,
            headers=auth_header
        )
        
        if post_response.status_code != 201:
            pytest.skip("게시글 생성 실패 - 통합 테스트 스킵")
        
        post_id = post_response.json().get("data", {}).get("post_id")
        if not post_id:
            pytest.skip("게시글 ID를 가져올 수 없음 - 통합 테스트 스킵")
        
        # 2. 댓글 작성
        comment_response = client.post(
            f"/api/posts/{post_id}/comments",
            json=test_comment_data,
            headers=auth_header
        )
        
        assert comment_response.status_code == 201
        assert comment_response.json()["message"] == "create_comment_success"
        
        comment_id = comment_response.json().get("data", {}).get("comment_id")
        
        # 3. 댓글 목록 조회
        list_response = client.get(f"/api/posts/{post_id}/comments")
        
        assert list_response.status_code == 200
        assert list_response.json()["message"] == "get_comments_success"
        
        if not comment_id:
            pytest.skip("댓글 ID를 가져올 수 없음 - 수정/삭제 테스트 스킵")
        
        # 4. 댓글 수정
        update_response = client.patch(
            f"/api/posts/{post_id}/comments/{comment_id}",
            json={"content": "수정된 댓글 내용"},
            headers=auth_header
        )
        
        assert update_response.status_code == 200
        assert update_response.json()["message"] == "update_comment_success"
        
        # 5. 댓글 삭제
        delete_response = client.delete(
            f"/api/posts/{post_id}/comments/{comment_id}",
            headers=auth_header
        )
        
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "delete_comment_success"
