from fastapi import APIRouter, HTTPException, Query

from app.schemas.response_models import PredictionResponse
from app.services.feature_service import get_gold_features
from app.services.predict_service import mock_prediction

router = APIRouter()


@router.get("/gold", response_model=PredictionResponse)
def predict_gold(
    interval: str = Query("1h", description="1m, 5m, 15m, 30m, 1h, 1d"),
    period: str = Query("7d", description="1d, 5d, 7d, 1mo, 3mo"),
):
    try:
        features_payload = get_gold_features(interval=interval, period=period)
        return mock_prediction(features_payload["features"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Prediction engine error: {exc}") from exc
