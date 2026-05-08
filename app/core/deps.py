"""公共依赖注入函数。"""

from app.database import SessionLocal


def get_db():
    """获取数据库会话（依赖注入）。

    Yields:
        SQLAlchemy Session 实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
