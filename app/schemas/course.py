"""课程、章节、视频相关Pydantic模型。"""

from typing import Optional, List
from pydantic import BaseModel





class ChapterCreate(BaseModel):
    """创建章节请求。"""
    title: str
    sort_order: int = 0


class ChapterUpdate(BaseModel):
    """更新章节请求。"""
    title: Optional[str] = None
    sort_order: Optional[int] = None


class ChapterOut(BaseModel):
    """章节响应（含视频列表）。"""
    id: int
    course_id: int
    title: str
    sort_order: int
    pass

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    """创建课程请求。"""
    name: str
    subject: str
    grade: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None


class CourseUpdate(BaseModel):
    """更新课程请求。"""
    name: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None


class CourseOut(BaseModel):
    """课程响应（含章节）。"""
    id: int
    name: str
    subject: str
    grade: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    chapters: List[ChapterOut] = []

    class Config:
        from_attributes = True


class CourseListOut(BaseModel):
    """课程列表项（不含章节详情）。"""
    id: int
    name: str
    subject: str
    grade: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None

    class Config:
        from_attributes = True
