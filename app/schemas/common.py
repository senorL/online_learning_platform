"""统一响应格式模型。"""

from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一API响应格式。"""

    code: int = 200
    data: Any = None
    message: str = "操作成功"
