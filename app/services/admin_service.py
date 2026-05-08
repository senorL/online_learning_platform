"""管理后台服务：用户管理、章节管理、数据统计。"""

import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.question import Question
from app.models.study import StudyRecord
from app.models.course import Course, Chapter, Video


def get_users(db: Session, keyword: Optional[str] = None, role: Optional[str] = None,
              page: int = 1, page_size: int = 20) -> dict:
    """获取用户列表。"""
    query = db.query(User)
    if keyword:
        query = query.filter(User.username.contains(keyword))
    if role:
        query = query.filter(User.role == role)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def update_user_admin(db: Session, user_id: int, update_data: dict) -> User:
    """管理员修改用户信息。"""
    from fastapi import HTTPException
    from app.core.security import hash_password

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if "username" in update_data and update_data["username"]:
        existing = db.query(User).filter(User.username == update_data["username"], User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已被其他用户使用")

    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    elif "password" in update_data:
        update_data.pop("password")

    for key, value in update_data.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user_admin(db: Session, user_id: int) -> None:
    """管理员删除用户。"""
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")
    db.delete(user)
    db.commit()


def get_chapters(
    db: Session,
    keyword: Optional[str] = None,
    course_id: Optional[int] = None,
    subject: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """获取章节列表，支持搜索和筛选。

    Args:
        db: 数据库会话
        keyword: 按章节名称搜索
        course_id: 按课程ID筛选
        subject: 按学科筛选
        page: 页码
        page_size: 每页数量

    Returns:
        包含章节列表和分页信息的字典
    """
    query = db.query(Chapter).join(Course, Chapter.course_id == Course.id)

    if keyword:
        query = query.filter(Chapter.title.contains(keyword))
    if course_id:
        query = query.filter(Chapter.course_id == course_id)
    if subject:
        query = query.filter(Course.subject == subject)

    total = query.count()
    chapters = query.order_by(Chapter.course_id, Chapter.sort_order).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # 构建返回数据（包含所属课程信息）
    items = []
    for ch in chapters:
        items.append({
            "id": ch.id,
            "course_id": ch.course_id,
            "title": ch.title,
            "sort_order": ch.sort_order,
            "course_name": ch.course.name if ch.course else "",
            "course_subject": ch.course.subject if ch.course else "",
            "course_grade": ch.course.grade if ch.course else "",
            "video_count": len(ch.videos) if ch.videos else 0,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_stats(db: Session) -> dict:
    """获取平台统计数据。"""
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)

    total_students = db.query(User).filter(User.role == "student").count()
    total_questions = db.query(Question).count()
    daily_active = db.query(StudyRecord).filter(StudyRecord.date == today).count()

    # 近30天每日答题量
    daily_counts = (
        db.query(StudyRecord.date, func.sum(StudyRecord.count))
        .filter(StudyRecord.date >= thirty_days_ago)
        .group_by(StudyRecord.date)
        .order_by(StudyRecord.date)
        .all()
    )

    # 各学科题目分布
    subject_dist = (
        db.query(Question.subject, func.count(Question.id))
        .group_by(Question.subject)
        .all()
    )

    return {
        "total_students": total_students,
        "total_questions": total_questions,
        "daily_active": daily_active,
        "daily_counts": [{"date": str(d), "count": int(c)} for d, c in daily_counts],
        "subject_distribution": [{"subject": s, "count": int(c)} for s, c in subject_dist],
    }
