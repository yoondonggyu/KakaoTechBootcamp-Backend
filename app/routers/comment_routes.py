from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user_id
from app.controllers import comment_controller
from app.schemas import CommentCreateReq, CommentUpdateReq
from app.core.database import get_db

router = APIRouter(tags=["comments"])


@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: int, db: Session = Depends(get_db)):
    """댓글 목록 조회 API"""
    data = comment_controller.get_comments_controller(post_id, db)
    return {"message": "get_comments_success", "data": data}


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    req: CommentCreateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """댓글 작성 API (감성 분석 포함)"""
    data = await comment_controller.create_comment_controller(post_id, req, user_id, db)
    return {"message": "create_comment_success", "data": data}


@router.patch("/posts/{post_id}/comments/{comment_id}")
async def update_comment(
    post_id: int,
    comment_id: int,
    req: CommentUpdateReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """댓글 수정 API"""
    data = comment_controller.update_comment_controller(post_id, comment_id, req, user_id, db)
    return {"message": "update_comment_success", "data": data}


@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(
    post_id: int,
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """댓글 삭제 API"""
    data = comment_controller.delete_comment_controller(post_id, comment_id, user_id, db)
    return {"message": "delete_comment_success", "data": data}
