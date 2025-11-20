from app.core.exceptions import not_found, forbidden, bad_request, unauthorized
from app.models.memory import POSTS, COMMENTS, COUNTERS, USERS, Comment
from app.schemas import CommentCreateReq, CommentUpdateReq
from app.services.model_client import analyze_sentiment


async def create_comment_controller(post_id: int, req: CommentCreateReq, user_id: int):
    """댓글 작성 컨트롤러 + 감성 분석"""
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
    
    # 🎯 Model API 호출 (감성 분석) - 비동기로 처리
    sentiment_result = None
    try:
        sentiment = await analyze_sentiment(req.content, explain=False)
        if sentiment:
            label = sentiment.get("label", "unknown")
            confidence = sentiment.get("confidence", 0)
            sentiment_result = {
                "label": label,
                "confidence": confidence
            }
            print(f"✅ 댓글 감성 분석: {label} (신뢰도: {confidence:.2%}) - 댓글 ID: {cid}")
            
            # 부정적인 댓글 감지 시 로그
            if label == "negative" and confidence > 0.7:
                print(f"⚠️ 부정적인 댓글이 감지되었습니다. (댓글 ID: {cid}, 신뢰도: {confidence:.2%})")
    except Exception as e:
        # Model API 실패해도 댓글 작성은 성공 처리
        print(f"⚠️ 감성 분석 실패 (댓글 작성은 성공): {e}")
    
    result = {"comment_id": cid}
    if sentiment_result:
        result["sentiment"] = sentiment_result  # Model API 결과 포함
    
    return result


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

