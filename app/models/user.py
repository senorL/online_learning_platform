"""用户模型。"""

from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户表，支持学生、教师和管理员三种角色。"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False)  # student/teacher/admin
    grade = Column(String(20), nullable=True)  # 七年级/八年级/九年级
    avatar = Column(Text(4294967295), nullable=True)  # Base64头像
    is_active = Column(Boolean, default=True, nullable=False)  # 是否启用

    # 关联关系
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    wrong_questions = relationship("WrongQuestion", back_populates="user", cascade="all, delete-orphan")
    study_records = relationship("StudyRecord", back_populates="user", cascade="all, delete-orphan")
    study_progresses = relationship("StudyProgress", back_populates="user", cascade="all, delete-orphan")
