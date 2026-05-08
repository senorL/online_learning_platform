"""错题本路由：查看、移除、复习、AI讲解。"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.core.security import get_current_user
from app.models.user import User
from app.services import wrong_question_service

router = APIRouter(prefix="/api", tags=["错题本"])


@router.get("/my/mistakes")
def get_mistakes(
    subject: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取我的错题本（不含已移除的）。"""
    data = wrong_question_service.get_wrong_questions(db, current_user.id, subject=subject)
    return success_response(data=data)


@router.delete("/my/mistakes/{wrong_id}")
def remove_mistake(
    wrong_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """移除错题（软删除）。"""
    wrong_question_service.remove_wrong_question(db, current_user.id, wrong_id)
    return success_response(message="错题已移除")


@router.get("/my/review")
def get_review(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取今日艾宾浩斯复习推荐。"""
    data = wrong_question_service.get_ebbinghaus_review(db, current_user.id)
    return success_response(data=data)


@router.post("/my/review/{wrong_id}")
def mark_reviewed(
    wrong_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """标记错题已复习。"""
    wrong_question_service.mark_reviewed(db, current_user.id, wrong_id)
    return success_response(message="已标记为已复习")


@router.post("/my/mistakes/{wrong_id}/ai-explain")
async def ai_explain(
    wrong_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """AI讲解错题。"""
    explanation = await wrong_question_service.ai_explain(db, current_user.id, wrong_id)
    return success_response(data={"explanation": explanation})
