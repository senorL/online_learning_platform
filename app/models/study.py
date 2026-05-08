"""学习记录模型：打卡记录 + 视频播放进度。"""

import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class StudyRecord(Base):
    """每日学习打卡记录（用于热力图）。"""

    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=datetime.date.today, nullable=False)
    subject = Column(String(20), nullable=True)
    chapter = Column(String(100), nullable=True)
    count = Column(Integer, default=0)  # 当日做题量

    # 关联关系
    user = relationship("User", back_populates="study_records")


class UserProcess(Base):
    """用户学习进度记录。"""

    __tablename__ = "user_processes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(50), nullable=False)
    chapter = Column(String(200), nullable=False)
    minute = Column(Integer, default=0)
    second = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="user_processes")
