from fastapi import APIRouter, HTTPException, Query

from app.schemas.response_models import FeaturesResponse
from app.services.feature_service import get_gold_features

router = APIRouter()


@router.get("/gold", response_model=FeaturesResponse)
def fetch_gold_features(
    interval: str = Query("1h", description="1m, 5m, 15m, 30m, 1h, 1d"),
    period: str = Query("7d", description="1d, 5d, 7d, 1mo, 3mo"),
):
    try:
        return get_gold_features(interval=interval, period=period)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Feature engine error: {exc}") from exc
