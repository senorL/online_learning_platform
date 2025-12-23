from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student") # student 或 admin [cite: 16]
    grade = Column(String, nullable=True)
    avatar = Column(String, nullable=True)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    subject = Column(String)
    video_url = Column(String)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String)
    content = Column(Text)
    options = Column(String) # 存储选项的JSON字符串 [cite: 14]
    answer = Column(String)

class WrongQuestion(Base):
    __tablename__ = "wrong_questions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    created_at = Column(Date, default=datetime.date.today) # [cite: 11]

class StudyRecord(Base):
    __tablename__ = "study_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.date.today)
    count = Column(Integer, default=0) # 当日做题量 [cite: 12]