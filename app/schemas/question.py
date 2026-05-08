"""题库相关Pydantic模型。"""

from typing import Optional, List
from pydantic import BaseModel


class QuestionCreate(BaseModel):
    """创建题目请求。"""
    course_id: Optional[int] = None
    subject: str
    chapter: Optional[str] = None
    type: str = "choice"  # choice/fill_blank/essay
    difficulty: str = "medium"  # easy/medium/hard
    content: str
    options: Optional[str] = None  # JSON字符串
    answer: str
    explanation: Optional[str] = None
    points: int = 5
    source: str = "manual"  # manual/ai


class QuestionUpdate(BaseModel):
    """更新题目请求。"""
    course_id: Optional[int] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    type: Optional[str] = None
    difficulty: Optional[str] = None
    content: Optional[str] = None
    options: Optional[str] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[int] = None
    source: Optional[str] = None


class QuestionOut(BaseModel):
    """题目响应。"""
    id: int
    course_id: Optional[int] = None
    subject: str
    chapter: Optional[str] = None
    type: str
    difficulty: str = "medium"
    content: str
    options: Optional[str] = None
    answer: str
    explanation: Optional[str] = None
    points: int
    source: str = "manual"

    class Config:
        from_attributes = True


class QuestionOutNoAnswer(BaseModel):
    """题目响应（不含答案，用于答题场景）。"""
    id: int
    course_id: Optional[int] = None
    subject: str
    chapter: Optional[str] = None
    type: str
    difficulty: str = "medium"
    content: str
    options: Optional[str] = None
    points: int

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    """提交答案请求。"""
    question_id: int
    user_answer: str
    subject: Optional[str] = None
    chapter: Optional[str] = None


class QuestionBatchImport(BaseModel):
    """批量导入题目请求（单题结构）。"""
    subject: str
    chapter: Optional[str] = None
    type: str = "choice"
    difficulty: str = "medium"
    content: str
    options: Optional[str] = None
    answer: str
    explanation: Optional[str] = None
    points: int = 5


class GenerateQuestionsRequest(BaseModel):
    """AI出题请求。"""
    subject: str
    chapter: str
    difficulty: str = "medium"  # easy/medium/hard
    types: List[str] = ["choice", "fill_blank"]  # 题型列表
    count: int = 10
