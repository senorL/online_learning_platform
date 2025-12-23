from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    password: str
    grade: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    grade: Optional[str] = None
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str

class SystemStats(BaseModel):
    total_students: int
    total_questions: int
    daily_active: int