from fastapi import APIRouter, Query

from app.schemas.response_models import NewsResponse
from app.services.news_service import get_news_data

router = APIRouter()


@router.get("/gold", response_model=NewsResponse)
def fetch_gold_news(limit: int = Query(5, ge=1, le=20)):
    return get_news_data(limit=limit)
 