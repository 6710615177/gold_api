# Gold Trading Mock API

โปรเจคนี้เป็น FastAPI สำหรับงานเดโม่/วางโครงก่อนที่โมเดลจริงจะเสร็จ

## สิ่งที่มีในโปรเจค
- ดึงข้อมูลราคาทองจาก `yfinance` (`GC=F`)
- ดึงข่าวจาก Yahoo Finance RSS เป็นค่าเริ่มต้น
- ถ้ามี `NEWS_API_KEY` และเปิด `USE_REAL_NEWS=true` จะใช้ NewsAPI แทน
- คำนวณฟีเจอร์เบื้องต้น: SMA20, EMA20, RSI, MACD, ATR, news_score
- ทำนายแบบ mock rule engine เพื่อให้ UI ใช้งานรอโมเดลจริงได้

## Endpoints
- `GET /api/market/gold`
- `GET /api/news/gold`
- `GET /api/features/gold`
- `GET /api/predict/gold`
- `GET /api/dashboard/gold`

## วิธีรัน
```bash
python -m venv .venv
source .venv/bin/activate   # Windows ใช้ .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

แล้วเปิด
- `http://127.0.0.1:8000/docs`

## ตัวอย่างเรียกใช้งาน
```bash
curl "http://127.0.0.1:8000/api/dashboard/gold?interval=1h&period=7d&news_limit=5"
```

## โครงสร้างข้อมูลที่ UI จะใช้
`/api/dashboard/gold` จะตอบข้อมูลครบชุด
```json
{
  "market": {
    "symbol": "GC=F",
    "interval": "1h",
    "period": "7d",
    "price": 3052.4,
    "open": 3049.8,
    "high": 3055.3,
    "low": 3048.5,
    "close": 3052.4,
    "volume": 1234.0,
    "change": 6.2,
    "change_percent": 0.20,
    "timestamp": "2026-03-28T10:00:00+00:00"
  },
  "features": {
    "close": 3052.4,
    "sma_20": 3042.2,
    "ema_20": 3045.1,
    "rsi": 61.2,
    "macd": 1.42,
    "macd_signal": 1.10,
    "atr": 12.0,
    "news_score": 0.2,
    "trend": "bullish"
  },
  "prediction": {
    "action": "BUY",
    "confidence": 0.79,
    "reason": "Mock rule engine: bullish momentum from RSI/MACD/news/trend",
    "model_version": "mock-rule-v1",
    "generated_at": "2026-03-28T10:00:01+00:00"
  },
  "news": [
    {
      "title": "Gold rises on softer dollar",
      "source": "Yahoo Finance RSS",
      "published_at": "2026-03-28T09:20:00+00:00",
      "summary": "...",
      "url": "https://...",
      "sentiment": "positive"
    }
  ]
}
```

## พอโมเดลจริงเสร็จ ต้องแก้ตรงไหน
หลัก ๆ แก้แค่ 2 จุด

### 1) `app/services/predict_service.py`
ตอนนี้ใช้ฟังก์ชัน `mock_prediction(features)`
ในอนาคตให้เปลี่ยนเป็นโหลดโมเดลจริง เช่น `joblib`, `pickle`, `onnxruntime`, `torch`

แนวคิดตัวอย่าง:
```python
# pseudocode
model = joblib.load("artifacts/gold_model.pkl")
scaler = joblib.load("artifacts/scaler.pkl")

def real_prediction(features: dict) -> dict:
    x = [[
        features["close"],
        features["sma_20"],
        features["ema_20"],
        features["rsi"],
        features["macd"],
        features["macd_signal"],
        features["atr"],
        features["news_score"],
    ]]
    x_scaled = scaler.transform(x)
    pred = model.predict(x_scaled)[0]
    prob = float(model.predict_proba(x_scaled).max())
    return {
        "action": pred,
        "confidence": prob,
        "reason": "Prediction from trained model",
        "model_version": "ml-model-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
```

### 2) `app/routes/predict.py` และ `app/routes/dashboard.py`
ตอนนี้เรียก `mock_prediction(...)`
พอมีโมเดลจริง ให้เปลี่ยนเป็น `real_prediction(...)`

ตัวอย่าง:
```python
# เดิม
prediction = mock_prediction(features_payload["features"])

# ใหม่
prediction = real_prediction(features_payload["features"])
```

## สิ่งที่ควรเตรียมจากฝั่งโมเดล
ก่อนเสียบโมเดลจริง ควรตกลงกันให้ชัดว่า
- ใช้ฟีเจอร์อะไรบ้าง และลำดับไหน
- ต้องมี scaler / encoder หรือไม่
- output เป็น `BUY/SELL/HOLD` หรือเป็น class id
- confidence มาจากอะไร เช่น probability หรือ score
- model version จะส่งกลับอย่างไร

## แนวทาง production ต่อจากนี้
- เพิ่ม caching สำหรับ market/news
- เพิ่ม logging
- เพิ่ม retry / timeout
- เพิ่ม auth ถ้าจะเปิดให้ UI ภายนอกเรียก
- แยก model service ออกมา ถ้าทีม model ใหญ่ขึ้น
