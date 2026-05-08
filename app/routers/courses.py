"""课程路由：课程、章节、视频CRUD。"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseOut, CourseListOut,
    ChapterCreate, ChapterUpdate, ChapterOut,
    VideoCreate, VideoUpdate, VideoOut,
)
from app.services import course_service

router = APIRouter(prefix="/api", tags=["课程管理"])


@router.get("/courses")
def list_courses(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """获取课程列表，支持学科和年级筛选。"""
    courses = course_service.get_courses(db, subject=subject, grade=grade)
    data = [CourseListOut.model_validate(c).model_dump() for c in courses]
    return success_response(data=data)


@router.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)) -> dict:
    """获取课程详情（含章节和视频）。"""
    course = course_service.get_course_detail(db, course_id)
    return success_response(data=CourseOut.model_validate(course).model_dump())


@router.post("/courses")
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """创建课程（需要教师或管理员权限）。"""
    course = course_service.create_course(db, course_in)
    return success_response(data=CourseListOut.model_validate(course).model_dump(), message="课程创建成功")


@router.put("/courses/{course_id}")
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """更新课程。"""
    course = course_service.update_course(db, course_id, course_in)
    return success_response(data=CourseListOut.model_validate(course).model_dump(), message="课程更新成功")


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """删除课程。"""
    course_service.delete_course(db, course_id)
    return success_response(message="课程已删除")


# ---- 章节 ----
@router.post("/courses/{course_id}/chapters")
def create_chapter(
    course_id: int, chapter_in: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """为课程创建章节。"""
    chapter = course_service.create_chapter(db, course_id, chapter_in)
    return success_response(data=ChapterOut.model_validate(chapter).model_dump())


@router.put("/chapters/{chapter_id}")
def update_chapter(
    chapter_id: int, chapter_in: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """更新章节。"""
    chapter = course_service.update_chapter(db, chapter_id, chapter_in)
    return success_response(data=ChapterOut.model_validate(chapter).model_dump())


@router.delete("/chapters/{chapter_id}")
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """删除章节。"""
    course_service.delete_chapter(db, chapter_id)
    return success_response(message="章节已删除")


# ---- 视频 ----
@router.post("/chapters/{chapter_id}/videos")
def create_video(
    chapter_id: int, video_in: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """为章节创建视频。"""
    video = course_service.create_video(db, chapter_id, video_in)
    return success_response(data=VideoOut.model_validate(video).model_dump())


@router.put("/videos/{video_id}")
def update_video(
    video_id: int, video_in: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """更新视频。"""
    video = course_service.update_video(db, video_id, video_in)
    return success_response(data=VideoOut.model_validate(video).model_dump())


@router.delete("/videos/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """删除视频。"""
    course_service.delete_video(db, video_id)
    return success_response(message="视频已删除")
