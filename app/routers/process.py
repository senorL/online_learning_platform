"""用户学习进度相关路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.config import success_response
from app.core.security import get_current_user
from app.models.study import UserProcess
from app.models.user import User
from app.schemas.process import UserProcessCreate, UserProcessResponse
import datetime

router = APIRouter(
    prefix="/api/process",
    tags=["Process"]
)

@router.post("/record", response_model=dict)
def record_process(
    process_in: UserProcessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """保存或更新视频学习进度。"""
    # 查找是否已经存在该学科+章节的进度
    process = db.query(UserProcess).filter(
        UserProcess.user_id == current_user.id,
        UserProcess.subject == process_in.subject,
        UserProcess.chapter == process_in.chapter
    ).first()

    if process:
        process.minute = process_in.minute
        process.second = process_in.second
        process.updated_at = datetime.datetime.utcnow()
    else:
        process = UserProcess(
            user_id=current_user.id,
            subject=process_in.subject,
            chapter=process_in.chapter,
            minute=process_in.minute,
            second=process_in.second
        )
        db.add(process)

    db.commit()
    db.refresh(process)

    return success_response(data=UserProcessResponse.model_validate(process).model_dump(), message="进度保存成功")

@router.get("/latest", response_model=dict)
def get_latest_process(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户最新的学习进度。"""
    process = db.query(UserProcess).filter(
        UserProcess.user_id == current_user.id
    ).order_by(UserProcess.updated_at.desc()).first()

    if process:
        return success_response(data=UserProcessResponse.model_validate(process).model_dump(), message="获取成功")
    return success_response(data=None, message="无进度记录")
