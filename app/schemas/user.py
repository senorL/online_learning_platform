"""用户相关Pydantic模型。"""

from typing import Optional
from pydantic import BaseModel, field_validator
from app.core.config import MIN_PASSWORD_LENGTH, MIN_USERNAME_LENGTH


class UserCreate(BaseModel):
    """用户注册请求。"""

    username: str
    password: str
    grade: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < MIN_USERNAME_LENGTH:
            raise ValueError(f"用户名至少{MIN_USERNAME_LENGTH}个字符")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"密码至少{MIN_PASSWORD_LENGTH}位")
        return v


class UserLogin(BaseModel):
    """用户登录请求。"""

    username: str
    password: str


class UserOut(BaseModel):
    """用户信息响应。"""

    id: int
    username: str
    role: str
    grade: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """个人资料更新请求。"""

    grade: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"密码至少{MIN_PASSWORD_LENGTH}位")
        return v


class UserAdminUpdate(BaseModel):
    """管理员修改用户信息请求。"""

    role: Optional[str] = None
    is_active: Optional[bool] = None
    grade: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"密码至少{MIN_PASSWORD_LENGTH}位")
        return v

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < MIN_USERNAME_LENGTH:
            raise ValueError(f"用户名至少{MIN_USERNAME_LENGTH}个字符")
        return v
