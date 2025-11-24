from sqlalchemy.orm import Session
from app.core.exceptions import not_found, forbidden
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas import CommentCreateReq, CommentUpdateReq
from app.services.model_client import analyze_sentiment


def get_comments_controller(post_id: int, db: Session):
    """댓글 목록 조회 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found")

    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            "comment_id": comment.id,
            "user_id": comment.user_id,
            "nickname": comment.user.nickname if comment.user else "알 수 없음",
            "content": comment.content,
            "created_at": comment.created_at
        })
    return comments_data


async def create_comment_controller(post_id: int, req: CommentCreateReq, user_id: int, db: Session):
    """댓글 작성 컨트롤러"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise not_found("post_not_found")
    
    # 감성 분석 (로그용)
    sentiment_res = await analyze_sentiment(req.content)
    if sentiment_res:
        print(f"댓글 감성 분석: {sentiment_res}")

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=req.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {"comment_id": comment.id}


def update_comment_controller(post_id: int, comment_id: int, req: CommentUpdateReq, user_id: int, db: Session):
    """댓글 수정 컨트롤러"""
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise not_found("comment_not_found")
    
    if comment.user_id != user_id:
        raise forbidden()
    
    comment.content = req.content
    db.commit()
    
    return {"comment_id": comment_id}


def delete_comment_controller(post_id: int, comment_id: int, user_id: int, db: Session):
    """댓글 삭제 컨트롤러"""
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise not_found("comment_not_found")
    
    if comment.user_id != user_id:
        raise forbidden()
    
    db.delete(comment)
    db.commit()
    
    return {"comment_id": comment_id}
