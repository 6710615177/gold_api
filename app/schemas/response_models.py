from pydantic import BaseModel, Field
from typing import Literal


class MarketSnapshot(BaseModel):
    symbol: str
    interval: str
    period: str
    price: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    change: float
    change_percent: float
    timestamp: str


class NewsItem(BaseModel):
    title: str
    source: str
    published_at: str
    summary: str | None = None
    url: str
    sentiment: Literal["positive", "negative", "neutral"]
    image_url: str | None = None


class NewsResponse(BaseModel):
    keyword: str
    count: int
    news: list[NewsItem]


class FeatureSet(BaseModel):
    close: float
    sma_20: float
    ema_20: float
    rsi: float
    macd: float
    macd_signal: float
    atr: float
    news_score: float
    trend: str


class FeaturesResponse(BaseModel):
    symbol: str
    interval: str
    period: str
    features: FeatureSet
    generated_at: str


class PredictionResponse(BaseModel):
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=1)
    reason: str
    model_version: str
    generated_at: str


class DashboardResponse(BaseModel):
    market: MarketSnapshot
    features: FeatureSet
    prediction: PredictionResponse
    news: list[NewsItem]
