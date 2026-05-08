"""认证服务：注册、登录逻辑。"""

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, user_in: UserCreate) -> User:
    """注册新用户。

    Args:
        db: 数据库会话
        user_in: 注册请求数据

    Returns:
        新创建的用户实例

    Raises:
        HTTPException: 400 用户名已存在
    """
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        grade=user_in.grade,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, credentials: UserLogin) -> dict:
    """用户登录，验证凭据并返回token。

    Args:
        db: 数据库会话
        credentials: 登录凭据

    Returns:
        包含token和用户信息的字典

    Raises:
        HTTPException: 401 用户名或密码错误
    """
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token(
        data={"sub": user.username, "role": user.role, "id": user.id}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "grade": user.grade,
        "avatar": user.avatar,
        "user_id": user.id,
    }
