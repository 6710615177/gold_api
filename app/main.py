from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 เพิ่มบรรทัดนี้

from app.core.config import settings
from app.routes import dashboard, features, market, news, predict

app = FastAPI(title=settings.app_name, version="0.1.0")

# 🔥 ใส่ CORS ตรงนี้ (สำคัญมาก)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ตอน dev ใช้ * ได้เลย
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROUTES =================
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(features.router, prefix="/api/features", tags=["features"])
app.include_router(predict.router, prefix="/api/predict", tags=["predict"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "environment": settings.app_env,
        "message": "Gold trading mock API is running",
        "docs": "/docs",
    }