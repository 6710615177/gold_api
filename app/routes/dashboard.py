from fastapi import APIRouter, HTTPException, Query

from app.schemas.response_models import DashboardResponse
from app.services.feature_service import get_gold_features
from app.services.market_service import get_market_data
from app.services.news_service import get_news_data
from app.services.predict_service import mock_prediction

router = APIRouter()


@router.get("/gold", response_model=DashboardResponse)
def get_dashboard(
    interval: str = Query("1h", description="1m, 5m, 15m, 30m, 1h, 1d"),
    period: str = Query("7d", description="1d, 5d, 7d, 1mo, 3mo"),
    news_limit: int = Query(5, ge=1, le=20),
):
    try:
        market = get_market_data(interval=interval, period=period)
        news = get_news_data(limit=news_limit)
        features_payload = get_gold_features(interval=interval, period=period)
        prediction = mock_prediction(features_payload["features"])
        return {
            "market": market,
            "features": features_payload["features"],
            "prediction": prediction,
            "news": news["news"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Dashboard engine error: {exc}") from exc
