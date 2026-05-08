"""错题本模型。"""

import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class WrongQuestion(Base):
    """错题表：记录学生的错题及复习状态。"""

    __tablename__ = "wrong_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    wrong_answer = Column(Text, nullable=True)  # 学生的错误答案
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    removed = Column(Boolean, default=False, nullable=False)  # 软删除标记
    last_review_at = Column(DateTime, nullable=True)  # 上次复习时间（艾宾浩斯）
    review_count = Column(Integer, default=0)  # 复习次数

    # 关联关系
    user = relationship("User", back_populates="wrong_questions")
    question = relationship("Question", back_populates="wrong_questions")
