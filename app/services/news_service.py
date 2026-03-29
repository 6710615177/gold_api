from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable

import feedparser
import requests

from app.core.config import settings


POSITIVE_TERMS = {"rise", "rises", "up", "gain", "gains", "support", "safe haven", "surge"}
NEGATIVE_TERMS = {"fall", "falls", "down", "drop", "drops", "hawkish", "selloff", "slump"}
DEFAULT_IMAGE = "https://via.placeholder.com/400x200?text=Gold+News"
DEFAULT_NEWS = [
    {
        "title": "Gold holds near recent highs as traders watch bond yields",
        "source": "MockWire",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "summary": "Fallback mock item used when live news is unavailable.",
        "url": "https://example.com/mock-gold-news-1",
        "sentiment": "neutral",
        "image_url": "https://via.placeholder.com/400x200?text=Gold+News"
    },
    {
        "title": "Dollar softens and keeps bullion sentiment supported",
        "source": "MockWire",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "summary": "Fallback mock item used when live news is unavailable.",
        "url": "https://example.com/mock-gold-news-2",
        "sentiment": "positive",
        "image_url": "https://via.placeholder.com/400x200?text=Gold+News"
    },
]


def _infer_sentiment(text: str) -> str:
    lowered = text.lower()
    pos = sum(1 for term in POSITIVE_TERMS if term in lowered)
    neg = sum(1 for term in NEGATIVE_TERMS if term in lowered)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def _normalize_items(items: Iterable[dict], limit: int) -> list[dict]:
    normalized = []
    for item in items:
        title = item.get("title") or "Untitled"
        summary = item.get("summary") or item.get("description") or ""
        image_url = (
    item.get("image_url")
    or _extract_image_from_summary(summary)
    or DEFAULT_IMAGE
)

        image_url = item.get("image_url") or _extract_image_from_summary(summary) or DEFAULT_IMAGE

        normalized.append(
            {
                "title": title,
                "source": item.get("source") or "Unknown",
                "published_at": item.get("published_at") or datetime.now(timezone.utc).isoformat(),
                "summary": summary,
                "url": item.get("url") or "",
                "sentiment": item.get("sentiment") or _infer_sentiment(f"{title} {summary}"),
                "image_url": image_url,   # 👈 เพิ่ม
            }
        )
        if len(normalized) >= limit:
            break
    return normalized


def _fetch_from_newsapi(limit: int) -> list[dict]:
    if not settings.news_api_key:
        raise RuntimeError("NEWS_API_KEY missing")
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": 'gold OR bullion OR XAUUSD OR "Federal Reserve" OR dollar',
            "pageSize": limit,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": settings.news_api_key,
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    articles = payload.get("articles", [])
    raw = []
    for article in articles:
        raw.append(
            {
                "title": article.get("title"),
                "source": article.get("source", {}).get("name", "NewsAPI"),
                "published_at": article.get("publishedAt"),
                "summary": article.get("description"),
                "url": article.get("url"),
                "image_url": article.get("urlToImage"),  # 👈 เพิ่มตรงนี้
            }
        )
    return _normalize_items(raw, limit)


def _fetch_from_yahoo_rss(limit: int) -> list[dict]:
    feed = feedparser.parse("https://finance.yahoo.com/rss/headline?s=GC%3DF")
    raw = []
    for entry in feed.entries[:limit]:
        published = entry.get("published") or entry.get("updated")
        published_at = datetime.now(timezone.utc).isoformat()
        if published:
            try:
                published_at = parsedate_to_datetime(published).astimezone(timezone.utc).isoformat()
            except Exception:
                pass
        raw.append(
            {
                "title": entry.get("title"),
                "source": "Yahoo Finance RSS",
                "published_at": published_at,
                "summary": entry.get("summary"),
                "url": entry.get("link"),
                "image_url": _extract_image_from_summary(entry.get("summary", "")),  # 👈 เพิ่ม
            }
        )
    if not raw:
        raise RuntimeError("Yahoo RSS returned no items")
    return _normalize_items(raw, limit)


def get_news_data(limit: int = 5) -> dict:
    try:
        if settings.use_real_news and settings.news_api_key:
            news = _fetch_from_newsapi(limit)
        else:
            news = _fetch_from_yahoo_rss(limit)
    except Exception:
        news = _normalize_items(DEFAULT_NEWS, limit)

    return {"keyword": "gold", "count": len(news), "news": news}


def compute_news_score(news_items: list[dict]) -> float:
    score = 0.0
    for item in news_items:
        sentiment = item.get("sentiment", "neutral")
        if sentiment == "positive":
            score += 1.0
        elif sentiment == "negative":
            score -= 1.0
    if not news_items:
        return 0.0
    return round(score / len(news_items), 4)

def _extract_image_from_summary(summary: str) -> str | None:
    if not summary:
        return None
    import re
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match:
        return match.group(1)
    return None