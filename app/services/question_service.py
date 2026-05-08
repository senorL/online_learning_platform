"""题库服务：题目CRUD、提交答案、批量导入。"""

import json
import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.question import Question
from app.models.wrong_question import WrongQuestion
from app.models.study import StudyRecord
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate, AnswerSubmit


def get_questions(
    db: Session,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """获取题目列表，支持多维度筛选和分页。

    Args:
        db: 数据库会话
        subject: 学科筛选
        chapter: 章节筛选
        question_type: 题型筛选
        difficulty: 难度筛选
        keyword: 关键词搜索
        page: 页码
        page_size: 每页数量

    Returns:
        包含题目列表和分页信息的字典
    """
    query = db.query(Question)
    if subject:
        query = query.filter(Question.subject == subject)
    if chapter:
        query = query.filter(Question.chapter == chapter)
    if question_type:
        query = query.filter(Question.type == question_type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if keyword:
        query = query.filter(Question.content.contains(keyword))

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_questions_by_subject(db: Session, subject: str) -> List[Question]:
    """按学科获取全部题目（兼容旧前端）。

    Args:
        db: 数据库会话
        subject: 学科

    Returns:
        题目列表
    """
    return db.query(Question).filter(Question.subject == subject).all()


def create_question(db: Session, question_in: QuestionCreate) -> Question:
    """创建新题目。

    Args:
        db: 数据库会话
        question_in: 题目数据

    Returns:
        新题目实例
    """
    question = Question(**question_in.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def update_question(db: Session, question_id: int, question_in: QuestionUpdate) -> Question:
    """更新题目。

    Args:
        db: 数据库会话
        question_id: 题目ID
        question_in: 更新数据

    Returns:
        更新后的题目实例
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    for key, value in question_in.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: int) -> None:
    """删除题目。

    Args:
        db: 数据库会话
        question_id: 题目ID
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(question)
    db.commit()


def submit_answer(db: Session, user: User, submission: AnswerSubmit) -> dict:
    """提交答案，自动判分并记录错题和打卡。

    Args:
        db: 数据库会话
        user: 当前用户
        submission: 提交数据

    Returns:
        判题结果字典
    """
    question = db.query(Question).filter(Question.id == submission.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    is_correct = submission.user_answer.strip() == question.answer.strip()

    if not is_correct:
        # 检查是否已有同一错题记录（未移除的）
        existing = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == user.id,
            WrongQuestion.question_id == question.id,
            WrongQuestion.removed == False,
        ).first()
        if not existing:
            db.add(WrongQuestion(
                user_id=user.id,
                question_id=question.id,
                wrong_answer=submission.user_answer,
            ))

    # 更新每日打卡记录，按学科和章节细分
    today = datetime.date.today()
    # 优先使用提交上来的学科，章节直接用题目自带的（题目上的章节标签是最准确的）
    sub = submission.subject or question.subject
    chap = question.chapter or "综合练习"

    record = db.query(StudyRecord).filter(
        StudyRecord.user_id == user.id,
        StudyRecord.date == today,
        StudyRecord.subject == sub,
        StudyRecord.chapter == chap,
    ).first()
    if record:
        record.count += 1
    else:
        db.add(StudyRecord(
            user_id=user.id,
            subject=sub,
            chapter=chap,
            count=1
        ))

    db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": question.answer,
        "explanation": question.explanation,
        "points": question.points if is_correct else 0,
    }


def batch_import_questions(db: Session, questions_data: List[dict]) -> int:
    """批量导入题目。

    Args:
        db: 数据库会话
        questions_data: 题目数据列表

    Returns:
        成功导入的题目数量
    """
    count = 0
    for q_data in questions_data:
        question = Question(
            subject=q_data.get("subject", ""),
            chapter=q_data.get("chapter"),
            type=q_data.get("type", "choice"),
            content=q_data.get("content", ""),
            options=q_data.get("options"),
            answer=q_data.get("answer", ""),
            explanation=q_data.get("explanation"),
            points=q_data.get("points", 5),
        )
        db.add(question)
        count += 1
    db.commit()
    return count
