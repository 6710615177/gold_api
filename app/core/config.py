from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gold Trading Mock API"
    app_env: str = "dev"
    use_real_news: bool = False
    news_api_key: str | None = None
    market_symbol: str = "GC=F"
    default_interval: str = "1h"
    default_period: str = "7d"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
