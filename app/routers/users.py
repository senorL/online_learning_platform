"""用户个人路由：资料、热力图、活动记录。"""

import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.core.security import get_current_user, hash_password
from app.models.user import User
from app.models.study import StudyRecord
from app.schemas.user import ProfileUpdate, UserOut

router = APIRouter(prefix="/api", tags=["个人中心"])


@router.get("/my/profile")
def get_profile(current_user: User = Depends(get_current_user)) -> dict:
    """获取当前用户资料。"""
    return success_response(data=UserOut.model_validate(current_user).model_dump())


@router.put("/my/profile")
def update_profile(
    update_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """更新个人资料。"""
    if update_data.grade is not None:
        current_user.grade = update_data.grade
    if update_data.password:
        current_user.hashed_password = hash_password(update_data.password)
    if update_data.avatar is not None:
        current_user.avatar = update_data.avatar
    db.commit()
    return success_response(
        data={"username": current_user.username, "grade": current_user.grade, "avatar": current_user.avatar},
        message="资料更新成功",
    )


@router.get("/my/heatmap")
def get_heatmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取学习热力图数据（近一年）。"""
    records = db.query(StudyRecord).filter(StudyRecord.user_id == current_user.id).all()
    heatmap = {}
    for r in records:
        date_str = str(r.date)
        heatmap[date_str] = heatmap.get(date_str, 0) + r.count
    return success_response(data=heatmap)


@router.get("/my/activity")
def get_activity(
    date: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取每日做题详情。"""
    query = db.query(StudyRecord).filter(StudyRecord.user_id == current_user.id)
    if date:
        query = query.filter(StudyRecord.date == date)
        records = query.order_by(StudyRecord.subject).all()
        data = [
            {
                "subject": (r.subject.strip() if r.subject else "综合") or "综合",
                "chapter": (r.chapter.strip() if r.chapter else "综合练习") or "综合练习",
                "count": r.count
            }
            for r in records
        ]
        return success_response(data=data)
    else:
        # 如果没有指定 date，默认聚合最近30天的每日总数
        from sqlalchemy import func
        records = db.query(
            StudyRecord.date,
            func.sum(StudyRecord.count).label("total_count")
        ).filter(StudyRecord.user_id == current_user.id)\
         .group_by(StudyRecord.date)\
         .order_by(StudyRecord.date.desc())\
         .limit(30).all()
        
        data = [{"date": str(r.date), "count": r.total_count} for r in records]
        return success_response(data=data)
