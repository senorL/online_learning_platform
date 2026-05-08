"""题库路由：题目CRUD、提交答案、批量导入、AI出题。"""

import json
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionOut,
    QuestionOutNoAnswer, AnswerSubmit, GenerateQuestionsRequest,
)
from app.services import question_service
from app.services import deepseek_service

router = APIRouter(prefix="/api", tags=["题库"])


@router.get("/questions")
def list_questions(
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    """获取题目列表（支持筛选和分页）。"""
    result = question_service.get_questions(
        db, subject=subject, chapter=chapter, question_type=type,
        difficulty=difficulty, keyword=keyword, page=page, page_size=page_size,
    )
    result["items"] = [QuestionOut.model_validate(q).model_dump() for q in result["items"]]
    return success_response(data=result)


@router.get("/questions/by-subject/{subject}")
def get_by_subject(subject: str, db: Session = Depends(get_db)) -> dict:
    """按学科获取全部题目（兼容旧前端）。"""
    questions = question_service.get_questions_by_subject(db, subject)
    data = [QuestionOut.model_validate(q).model_dump() for q in questions]
    return success_response(data=data)


@router.post("/questions/submit")
def submit_answer(
    submission: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """提交答案，自动判分。"""
    result = question_service.submit_answer(db, current_user, submission)
    return success_response(data=result)


@router.post("/questions/generate")
def generate_questions(
    req: GenerateQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """AI智能出题：优先从数据库抽题，不够则调用DeepSeek补充生成。

    请求体:
        subject: 学科
        chapter: 章节名称
        difficulty: 难度 easy/medium/hard
        types: 题型列表 ["choice", "fill_blank"]
        count: 需要的题目数量（默认10）
    """
    try:
        questions = deepseek_service.get_or_generate_questions(
            db,
            subject=req.subject,
            chapter=req.chapter,
            difficulty=req.difficulty,
            question_types=req.types,
            count=req.count,
        )
        data = [QuestionOutNoAnswer.model_validate(q).model_dump() for q in questions]
        return success_response(data=data, message=f"成功获取{len(data)}道题目")
    except ValueError as e:
        return {"code": 500, "data": None, "message": str(e)}
    except Exception as e:
        return {"code": 500, "data": None, "message": f"出题失败: {str(e)}"}


@router.post("/questions")
def create_question(
    question_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """新增题目。"""
    q = question_service.create_question(db, question_in)
    return success_response(data=QuestionOut.model_validate(q).model_dump(), message="题目创建成功")


@router.put("/questions/{question_id}")
def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """编辑题目。"""
    q = question_service.update_question(db, question_id, question_in)
    return success_response(data=QuestionOut.model_validate(q).model_dump(), message="题目更新成功")


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """删除题目。"""
    question_service.delete_question(db, question_id)
    return success_response(message="题目已删除")


@router.post("/questions/import")
def import_questions(
    questions: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """批量导入题目。"""
    count = question_service.batch_import_questions(db, questions)
    return success_response(data={"imported_count": count}, message=f"成功导入{count}道题目")
