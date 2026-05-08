"""认证路由：注册、登录。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/api", tags=["用户认证"])


@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> dict:
    """用户注册。"""
    user = register_user(db, user_in)
    return success_response(
        data=UserOut.model_validate(user).model_dump(),
        message="注册成功",
    )


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> dict:
    """用户登录，返回JWT令牌。"""
    result = login_user(db, credentials)
    return success_response(data=result, message="登录成功")
