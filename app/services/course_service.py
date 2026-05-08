"""课程服务：课程、章节、视频CRUD。"""

from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.course import Course, Chapter
from app.schemas.course import CourseCreate, CourseUpdate, ChapterCreate, ChapterUpdate


def get_courses(
    db: Session,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[Course]:
    """获取课程列表，支持学科和年级筛选。

    Args:
        db: 数据库会话
        subject: 学科筛选
        grade: 年级筛选
        skip: 偏移量
        limit: 每页数量

    Returns:
        课程列表
    """
    query = db.query(Course)
    if subject:
        query = query.filter(Course.subject == subject)
    if grade:
        query = query.filter((Course.grade == grade) | (Course.grade.is_(None)))
    return query.offset(skip).limit(limit).all()


def get_course_detail(db: Session, course_id: int) -> Course:
    """获取课程详情（含章节和视频）。

    Args:
        db: 数据库会话
        course_id: 课程ID

    Returns:
        课程实例

    Raises:
        HTTPException: 404 课程不存在
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course


def create_course(db: Session, course_in: CourseCreate) -> Course:
    """创建新课程。

    Args:
        db: 数据库会话
        course_in: 课程创建数据

    Returns:
        新课程实例
    """
    course = Course(**course_in.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course_id: int, course_in: CourseUpdate) -> Course:
    """更新课程信息。

    Args:
        db: 数据库会话
        course_id: 课程ID
        course_in: 更新数据

    Returns:
        更新后的课程实例
    """
    course = get_course_detail(db, course_id)
    update_data = course_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> None:
    """删除课程。

    Args:
        db: 数据库会话
        course_id: 课程ID
    """
    course = get_course_detail(db, course_id)
    db.delete(course)
    db.commit()


# ---- 章节 ----
def create_chapter(db: Session, course_id: int, chapter_in: ChapterCreate) -> Chapter:
    """为课程创建章节。"""
    get_course_detail(db, course_id)  # 确保课程存在
    chapter = Chapter(course_id=course_id, **chapter_in.model_dump())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def update_chapter(db: Session, chapter_id: int, chapter_in: ChapterUpdate) -> Chapter:
    """更新章节。"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    for key, value in chapter_in.model_dump(exclude_unset=True).items():
        setattr(chapter, key, value)
    db.commit()
    db.refresh(chapter)
    return chapter


def delete_chapter(db: Session, chapter_id: int) -> None:
    """删除章节。"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    db.delete(chapter)
    db.commit()



