"""排行榜服务：做题数量、连续打卡排名。"""

import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.study import StudyRecord
from app.models.user import User


def get_ranking(db: Session, period: str = "all", dimension: str = "count", limit: int = 20) -> list:
    """获取排行榜。"""
    today = datetime.date.today()
    if period == "week":
        start_date = today - datetime.timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    else:
        start_date = None

    if dimension == "streak":
        return _rank_by_streak(db, limit)
    return _rank_by_count(db, start_date, limit)


def _rank_by_count(db: Session, start_date, limit: int) -> list:
    query = (
        db.query(User.id, User.username, User.grade, User.avatar,
                 func.coalesce(func.sum(StudyRecord.count), 0).label("total_count"))
        .outerjoin(StudyRecord, User.id == StudyRecord.user_id)
        .filter(User.role == "student", User.is_active == True)
    )
    if start_date:
        query = query.filter(StudyRecord.date >= start_date)
    results = query.group_by(User.id).order_by(func.coalesce(func.sum(StudyRecord.count), 0).desc()).limit(limit).all()
    return [{"rank": i+1, "user_id": r.id, "username": r.username, "grade": r.grade,
             "avatar": r.avatar, "total_count": int(r.total_count)} for i, r in enumerate(results)]


def _rank_by_streak(db: Session, limit: int) -> list:
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    streaks = []
    for s in students:
        dates = [r.date for r in db.query(StudyRecord.date).filter(
            StudyRecord.user_id == s.id).order_by(StudyRecord.date.desc()).all()]
        streak = _calc_streak(dates)
        streaks.append({"user_id": s.id, "username": s.username, "grade": s.grade,
                        "avatar": s.avatar, "streak_days": streak})
    streaks.sort(key=lambda x: x["streak_days"], reverse=True)
    for i, item in enumerate(streaks[:limit]):
        item["rank"] = i + 1
    return streaks[:limit]


def _calc_streak(dates: list) -> int:
    if not dates:
        return 0
    today = datetime.date.today()
    streak, expected = 0, today
    for d in dates:
        if d == expected:
            streak += 1
            expected -= datetime.timedelta(days=1)
        elif d < expected:
            break
    return streak
