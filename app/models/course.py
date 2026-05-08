"""课程、章节、视频模型。"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Course(Base):
    """课程表。"""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(20), nullable=False, index=True)  # 学科
    grade = Column(String(20), nullable=True, index=True)  # 年级
    description = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)  # 保留兼容旧数据

    # 关联关系
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan",
                            order_by="Chapter.sort_order")
    questions = relationship("Question", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Chapter(Base):
    """章节表，一个课程有多个章节。"""

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)

    # 关联关系
    course = relationship("Course", back_populates="chapters")
    videos = relationship("Video", back_populates="chapter", cascade="all, delete-orphan",
                          order_by="Video.sort_order")


class Video(Base):
    """视频表，一个章节有多个视频。"""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    duration = Column(Integer, default=0)  # 时长（秒）
    sort_order = Column(Integer, default=0)

    # 关联关系
    chapter = relationship("Chapter", back_populates="videos")
    study_progresses = relationship("StudyProgress", back_populates="video")
