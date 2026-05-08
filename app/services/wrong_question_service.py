"""错题本服务：查看、移除、艾宾浩斯复习、AI讲解。"""

import datetime
from typing import List, Optional
import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.wrong_question import WrongQuestion
from app.models.question import Question
from app.models.user import User
from app.core.config import (
    EBBINGHAUS_INTERVALS,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
)


def get_wrong_questions(db: Session, user_id: int, subject: Optional[str] = None) -> List[dict]:
    """获取用户的错题列表（不含已移除的）。

    Args:
        db: 数据库会话
        user_id: 用户ID
        subject: 学科筛选

    Returns:
        错题列表，包含题目详情
    """
    query = (
        db.query(WrongQuestion, Question)
        .join(Question, WrongQuestion.question_id == Question.id)
        .filter(WrongQuestion.user_id == user_id, WrongQuestion.removed == False)
    )
    if subject:
        query = query.filter(Question.subject == subject)

    results = query.order_by(WrongQuestion.added_at.desc()).all()
    return [
        {
            "id": wq.id,
            "question_id": wq.question_id,
            "wrong_answer": wq.wrong_answer,
            "added_at": wq.added_at.isoformat() if wq.added_at else None,
            "content": q.content,
            "options": q.options,
            "answer": q.answer,
            "explanation": q.explanation,
            "subject": q.subject,
            "type": q.type,
        }
        for wq, q in results
    ]


def remove_wrong_question(db: Session, user_id: int, wrong_id: int) -> None:
    """软删除错题（标记为已移除）。

    Args:
        db: 数据库会话
        user_id: 用户ID
        wrong_id: 错题记录ID

    Raises:
        HTTPException: 404 错题不存在
    """
    wq = db.query(WrongQuestion).filter(
        WrongQuestion.id == wrong_id,
        WrongQuestion.user_id == user_id,
    ).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")
    wq.removed = True
    db.commit()


def get_ebbinghaus_review(db: Session, user_id: int) -> List[dict]:
    """获取今天应该复习的错题（基于艾宾浩斯遗忘曲线）。

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        今日应复习的错题列表
    """
    now = datetime.datetime.utcnow()
    review_list = []

    wrong_questions = (
        db.query(WrongQuestion, Question)
        .join(Question, WrongQuestion.question_id == Question.id)
        .filter(WrongQuestion.user_id == user_id, WrongQuestion.removed == False)
        .all()
    )

    for wq, q in wrong_questions:
        review_count = wq.review_count or 0
        if review_count >= len(EBBINGHAUS_INTERVALS):
            continue  # 已完成所有复习周期

        interval_days = EBBINGHAUS_INTERVALS[review_count]
        reference_time = wq.last_review_at or wq.added_at
        if reference_time is None:
            continue

        next_review = reference_time + datetime.timedelta(days=interval_days)
        if now >= next_review:
            review_list.append({
                "id": wq.id,
                "question_id": wq.question_id,
                "wrong_answer": wq.wrong_answer,
                "review_count": review_count,
                "next_interval": EBBINGHAUS_INTERVALS[review_count],
                "content": q.content,
                "options": q.options,
                "answer": q.answer,
                "explanation": q.explanation,
                "subject": q.subject,
            })

    return review_list


def mark_reviewed(db: Session, user_id: int, wrong_id: int) -> None:
    """标记错题已复习，更新复习计数和时间。

    Args:
        db: 数据库会话
        user_id: 用户ID
        wrong_id: 错题记录ID
    """
    wq = db.query(WrongQuestion).filter(
        WrongQuestion.id == wrong_id,
        WrongQuestion.user_id == user_id,
    ).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")
    wq.review_count = (wq.review_count or 0) + 1
    wq.last_review_at = datetime.datetime.utcnow()
    db.commit()


async def ai_explain(db: Session, user_id: int, wrong_id: int) -> str:
    """调用DeepSeek AI讲解错题。

    Args:
        db: 数据库会话
        user_id: 用户ID
        wrong_id: 错题记录ID

    Returns:
        AI生成的讲解文本
    """
    wq = db.query(WrongQuestion).filter(
        WrongQuestion.id == wrong_id,
        WrongQuestion.user_id == user_id,
    ).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")

    question = db.query(Question).filter(Question.id == wq.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    prompt = (
        f"你是一位耐心的初中老师，请用初中生能理解的语言讲解这道题。\n\n"
        f"题目：{question.content}\n"
    )
    if question.options:
        prompt += f"选项：{question.options}\n"
    prompt += (
        f"正确答案：{question.answer}\n"
        f"学生的错误答案：{wq.wrong_answer}\n\n"
        f"请分析学生为什么会选错，并详细讲解解题思路。"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一位专业的初中教师，擅长用通俗易懂的方式为初中生讲解题目。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI讲解服务暂时不可用：{str(e)}")
