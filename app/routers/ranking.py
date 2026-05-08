"""排行榜路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import success_response
from app.services import ranking_service

router = APIRouter(prefix="/api", tags=["排行榜"])


@router.get("/ranking")
def get_ranking(
    period: str = "all",
    dimension: str = "count",
    limit: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    """获取排行榜。

    Args:
        period: week/month/all
        dimension: count/streak
        limit: 返回条数
    """
    data = ranking_service.get_ranking(db, period=period, dimension=dimension, limit=limit)
    return success_response(data=data)
