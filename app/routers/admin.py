"""管理后台路由：用户管理、章节管理、数据统计。"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.core.security import require_role
from app.models.user import User
from app.models.course import Chapter, Video
from app.schemas.user import UserAdminUpdate, UserOut
from app.schemas.course import ChapterOut, ChapterUpdate, VideoCreate, VideoOut
from app.services import admin_service
from app.services import course_service

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


@router.get("/users")
def list_users(
    keyword: Optional[str] = None,
    role: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """获取用户列表。"""
    result = admin_service.get_users(db, keyword=keyword, role=role, page=page, page_size=page_size)
    result["items"] = [UserOut.model_validate(u).model_dump() for u in result["items"]]
    return success_response(data=result)


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    update_data: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """修改用户状态或角色。"""
    user = admin_service.update_user_admin(db, user_id, update_data.model_dump(exclude_unset=True))
    return success_response(data=UserOut.model_validate(user).model_dump(), message="用户信息已更新")


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """删除用户。"""
    admin_service.delete_user_admin(db, user_id)
    return success_response(message="用户已删除")


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """获取平台数据统计。"""
    data = admin_service.get_stats(db)
    return success_response(data=data)


# ---- 章节管理 ----
@router.get("/chapters")
def list_chapters(
    keyword: Optional[str] = None,
    course_id: Optional[int] = None,
    subject: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """获取章节列表（支持搜索和筛选）。"""
    result = admin_service.get_chapters(
        db, keyword=keyword, course_id=course_id, subject=subject,
        page=page, page_size=page_size,
    )
    return success_response(data=result)


@router.get("/chapters/{chapter_id}")
def get_chapter_detail(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """获取章节详情（含视频列表）。"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return success_response(data=ChapterOut.model_validate(chapter).model_dump())


@router.put("/chapters/{chapter_id}")
def update_chapter(
    chapter_id: int,
    chapter_in: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """更新章节信息。"""
    chapter = course_service.update_chapter(db, chapter_id, chapter_in)
    return success_response(data=ChapterOut.model_validate(chapter).model_dump(), message="章节已更新")


@router.delete("/chapters/{chapter_id}")
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """删除章节。"""
    course_service.delete_chapter(db, chapter_id)
    return success_response(message="章节已删除")


@router.post("/chapters/{chapter_id}/videos")
def add_video_to_chapter(
    chapter_id: int,
    video_in: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "teacher")),
) -> dict:
    """为章节添加视频。"""
    video = course_service.create_video(db, chapter_id, video_in)
    return success_response(data=VideoOut.model_validate(video).model_dump(), message="视频已添加")
