"""错题本相关Pydantic模型。"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WrongQuestionOut(BaseModel):
    """错题响应。"""
    id: int
    question_id: int
    wrong_answer: Optional[str] = None
    added_at: Optional[datetime] = None
    # 题目信息（嵌套）
    content: Optional[str] = None
    options: Optional[str] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    subject: Optional[str] = None
    type: Optional[str] = None
