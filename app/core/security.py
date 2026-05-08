"""安全相关：密码哈希、JWT令牌、用户认证依赖注入。"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .deps import get_db

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 令牌提取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def hash_password(password: str) -> str:
    """对明文密码进行哈希加密。

    Args:
        password: 明文密码

    Returns:
        哈希后的密码字符串
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配。

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌。

    Args:
        data: 载荷数据
        expires_delta: 过期时间偏移量

    Returns:
        编码后的JWT字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """从JWT令牌中解析当前登录用户（依赖注入）。

    Args:
        token: Bearer令牌
        db: 数据库会话

    Returns:
        当前用户模型实例

    Raises:
        HTTPException: 401 未登录或令牌无效
    """
    from app.models.user import User  # 延迟导入避免循环引用

    credentials_exception = HTTPException(
        status_code=401,
        detail="登录已过期，请重新登录",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    return user


def require_role(*roles: str):
    """构造角色权限检查依赖。

    Args:
        *roles: 允许的角色列表，如 "admin", "teacher"

    Returns:
        依赖注入函数
    """
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="没有权限执行此操作")
        return current_user
    return role_checker
