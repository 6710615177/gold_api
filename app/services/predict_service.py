from __future__ import annotations

from datetime import datetime, timezone


MODEL_VERSION = "mock-rule-v1"


def mock_prediction(features: dict) -> dict:
    rsi = float(features["rsi"])
    macd = float(features["macd"])
    macd_signal = float(features["macd_signal"])
    news_score = float(features["news_score"])
    trend = features["trend"]

    bullish_score = 0
    bearish_score = 0

    if rsi >= 60:
        bullish_score += 1
    elif rsi <= 40:
        bearish_score += 1

    if macd > macd_signal:
        bullish_score += 1
    elif macd < macd_signal:
        bearish_score += 1

    if news_score > 0:
        bullish_score += 1
    elif news_score < 0:
        bearish_score += 1

    if trend == "bullish":
        bullish_score += 1
    else:
        bearish_score += 1

    if bullish_score - bearish_score >= 2:
        action = "BUY"
        confidence = min(0.55 + (bullish_score * 0.08), 0.92)
        reason = "Mock rule engine: bullish momentum from RSI/MACD/news/trend"
    elif bearish_score - bullish_score >= 2:
        action = "SELL"
        confidence = min(0.55 + (bearish_score * 0.08), 0.92)
        reason = "Mock rule engine: bearish momentum from RSI/MACD/news/trend"
    else:
        action = "HOLD"
        confidence = 0.58
        reason = "Mock rule engine: signals are mixed, waiting for clearer setup"

    return {
        "action": action,
        "confidence": round(confidence, 4),
        "reason": reason,
        "model_version": MODEL_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
