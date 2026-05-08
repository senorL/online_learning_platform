"""Pydantic模型包。"""

from app.schemas.common import ApiResponse
from app.schemas.user import UserCreate, UserLogin, UserOut, ProfileUpdate, UserAdminUpdate
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseOut,
    ChapterCreate, ChapterUpdate, ChapterOut,
)
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionOut, QuestionOutNoAnswer,
    AnswerSubmit, QuestionBatchImport, GenerateQuestionsRequest,
)
from app.schemas.wrong_question import WrongQuestionOut

__all__ = [
    "ApiResponse",
    "UserCreate", "UserLogin", "UserOut", "ProfileUpdate", "UserAdminUpdate",
    "CourseCreate", "CourseUpdate", "CourseOut",
    "ChapterCreate", "ChapterUpdate", "ChapterOut",
    "QuestionCreate", "QuestionUpdate", "QuestionOut", "QuestionOutNoAnswer",
    "AnswerSubmit", "QuestionBatchImport", "GenerateQuestionsRequest",
    "WrongQuestionOut",
]
