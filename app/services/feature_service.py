from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from app.core.config import settings
from app.services.market_service import get_price_history
from app.services.news_service import compute_news_score, get_news_data


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def get_gold_features(interval: str | None = None, period: str | None = None) -> dict:
    interval = interval or settings.default_interval
    period = period or settings.default_period
    df = get_price_history(interval=interval, period=period).copy()

    df["sma_20"] = df["Close"].rolling(20).mean()
    df["ema_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["rsi"] = _rsi(df["Close"])
    df["macd"], df["macd_signal"] = _macd(df["Close"])
    df["atr"] = _atr(df)

    latest = df.iloc[-1]
    news_payload = get_news_data(limit=5)
    news_score = compute_news_score(news_payload["news"])
    trend = "bullish" if float(latest["Close"]) >= float(latest["ema_20"]) else "bearish"

    features = {
        "close": round(float(latest["Close"]), 4),
        "sma_20": round(float(latest["sma_20"]), 4),
        "ema_20": round(float(latest["ema_20"]), 4),
        "rsi": round(float(latest["rsi"]), 4) if pd.notna(latest["rsi"]) else 50.0,
        "macd": round(float(latest["macd"]), 4),
        "macd_signal": round(float(latest["macd_signal"]), 4),
        "atr": round(float(latest["atr"]), 4) if pd.notna(latest["atr"]) else 0.0,
        "news_score": news_score,
        "trend": trend,
    }

    return {
        "symbol": settings.market_symbol,
        "interval": interval,
        "period": period,
        "features": features,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
