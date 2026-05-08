"""选课（学生-课程多对多关联）模型。"""

import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Enrollment(Base):
    """选课表：学生与课程的多对多关联。"""

    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
