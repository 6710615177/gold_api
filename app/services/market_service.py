from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yfinance as yf

from app.core.config import settings


ALLOWED_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d"}
ALLOWED_PERIODS = {"1d", "5d", "7d", "1mo", "3mo"}


def _to_iso(ts: Any) -> str:
    if hasattr(ts, "to_pydatetime"):
        ts = ts.to_pydatetime()
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def get_market_data(interval: str | None = None, period: str | None = None) -> dict:
    interval = interval or settings.default_interval
    period = period or settings.default_period

    if interval not in ALLOWED_INTERVALS:
        raise ValueError(f"Unsupported interval: {interval}")
    if period not in ALLOWED_PERIODS:
        raise ValueError(f"Unsupported period: {period}")

    ticker = yf.Ticker(settings.market_symbol)
    df = ticker.history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        raise RuntimeError("No market data returned from provider")

    last = df.iloc[-1]
    prev_close = float(df.iloc[-2]["Close"]) if len(df) > 1 else float(last["Open"])
    close = float(last["Close"])
    change = close - prev_close
    change_percent = (change / prev_close * 100) if prev_close else 0.0

    return {
        "symbol": settings.market_symbol,
        "interval": interval,
        "period": period,
        "price": close,
        "open": float(last["Open"]),
        "high": float(last["High"]),
        "low": float(last["Low"]),
        "close": close,
        "volume": float(last.get("Volume", 0.0)),
        "change": round(change, 4),
        "change_percent": round(change_percent, 4),
        "timestamp": _to_iso(df.index[-1]),
    }


def get_price_history(interval: str | None = None, period: str | None = None):
    interval = interval or settings.default_interval
    period = period or settings.default_period
    ticker = yf.Ticker(settings.market_symbol)
    df = ticker.history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        raise RuntimeError("No market data returned from provider")
    return df
