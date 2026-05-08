"""用户学习进度 Schema"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserProcessCreate(BaseModel):
    subject: str
    chapter: str
    minute: int
    second: int

class UserProcessResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    chapter: str
    minute: int
    second: int
    updated_at: datetime

    class Config:
        from_attributes = True


