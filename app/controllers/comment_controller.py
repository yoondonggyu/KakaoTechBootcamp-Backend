from app.core.exceptions import not_found, forbidden, bad_request, unauthorized
from app.models.memory import POSTS, COMMENTS, COUNTERS, USERS, Comment
from app.schemas import CommentCreateReq, CommentUpdateReq


def create_comment_controller(post_id: int, req: CommentCreateReq, user_id: int):
    """댓글 작성 컨트롤러"""
    if user_id not in USERS:
        raise unauthorized()

    if post_id not in POSTS:
        raise not_found("post_not_found")
    
    if not req.content or not req.content.strip():
        raise bad_request("invalid_request", {"message": "댓글 내용을 입력해주세요."})
    
    cid = COUNTERS["comment"]
    COUNTERS["comment"] += 1
    
    comment = Comment(
        id=cid,
        post_id=post_id,
        user_id=user_id,
        content=req.content
    )
    
    COMMENTS[cid] = comment
    return {"comment_id": cid}


def get_comments_controller(post_id: int):
    """댓글 목록 조회 컨트롤러"""
    if post_id not in POSTS:
        raise not_found("post_not_found")
    
    post_comments = [c for c in COMMENTS.values() if c.post_id == post_id]
    
    comments_data = []
    for comment in post_comments:
        user = USERS.get(comment.user_id)
        comments_data.append({
            "comment_id": comment.id,
            "user_id": comment.user_id,
            "nickname": user.nickname if user else "알 수 없음",
            "content": comment.content
        })
    
    return {"comments": comments_data}


def update_comment_controller(post_id: int, comment_id: int, req: CommentUpdateReq, user_id: int):
    """댓글 수정 컨트롤러"""
    if post_id not in POSTS:
        raise not_found("post_not_found")
    
    comment = COMMENTS.get(comment_id)
    if not comment or comment.post_id != post_id:
        raise not_found("comment_not_found")
    
    if comment.user_id != user_id:
        raise forbidden()
    
    if not req.content or not req.content.strip():
        raise bad_request("invalid_request", {"message": "댓글 내용을 입력해주세요."})
    
    comment.content = req.content
    return {"comment_id": comment_id}


def delete_comment_controller(post_id: int, comment_id: int, user_id: int):
    """댓글 삭제 컨트롤러"""
    if post_id not in POSTS:
        raise not_found("post_not_found")
    
    comment = COMMENTS.get(comment_id)
    if not comment or comment.post_id != post_id:
        raise not_found("comment_not_found")
    
    if comment.user_id != user_id:
        raise forbidden()
    
    COMMENTS.pop(comment_id, None)
    return {"comment_id": comment_id}

