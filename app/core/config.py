"""应用配置常量和统一响应格式。"""

import os
from typing import Any, Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ---- JWT 配置 ----
SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key-for-project")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# ---- DeepSeek AI 配置 ----
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ---- 业务常量 ----
MIN_PASSWORD_LENGTH = 6
MIN_USERNAME_LENGTH = 2

VALID_GRADES = ["七年级", "八年级", "九年级"]
VALID_SUBJECTS = ["数学", "语文", "英语", "物理", "化学", "生物", "地理", "道法"]
VALID_ROLES = ["student", "teacher", "admin"]
VALID_QUESTION_TYPES = ["choice", "fill_blank", "essay"]
VALID_DIFFICULTIES = ["easy", "medium", "hard"]

# AI出题配置
AI_GENERATE_BATCH_SIZE = 10  # 每次AI生成题目数量
MIN_QUESTIONS_THRESHOLD = 5  # 数据库中少于此数量时触发AI补充

# 艾宾浩斯复习间隔（天）
EBBINGHAUS_INTERVALS = [1, 2, 4, 7, 15]

# 分页默认值
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# ---- 统一响应格式 ----
def success_response(
    data: Any = None,
    message: str = "操作成功",
) -> dict:
    """构造统一成功响应。

    Args:
        data: 返回数据
        message: 提示消息

    Returns:
        统一格式的响应字典
    """
    return {"code": 200, "data": data, "message": message}


def error_response(
    code: int = 500,
    message: str = "服务器内部错误",
    data: Any = None,
) -> dict:
    """构造统一错误响应。

    Args:
        code: 错误码 (401/403/404/422/500)
        message: 错误描述
        data: 附加数据

    Returns:
        统一格式的响应字典
    """
    return {"code": code, "data": data, "message": message}
