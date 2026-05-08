"""题库模型。"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Question(Base):
    """题目表，支持选择题、填空题、解答题。"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    subject = Column(String(20), nullable=False, index=True)
    chapter = Column(String(100), nullable=True)  # 章节名称
    type = Column(String(20), default="choice", nullable=False)  # choice/fill_blank/essay
    difficulty = Column(String(10), default="medium", nullable=False, index=True)  # easy/medium/hard
    content = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON字符串，选择题选项
    answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)  # 解析
    points = Column(Integer, default=5)  # 分值
    source = Column(String(20), default="manual")  # manual/ai 题目来源

    # 关联关系
    course = relationship("Course", back_populates="questions")
    wrong_questions = relationship("WrongQuestion", back_populates="question")
