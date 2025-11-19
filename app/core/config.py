from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Clothing Store API"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    SQLALCHEMY_DATABASE_URI: str = (
        "mysql+pymysql://user:password@localhost:3306/ai_clothing_store"
    )
    PAYPAL_CLIENT_ID: str = "PAYPAL_CLIENT_ID"
    PAYPAL_CLIENT_SECRET: str = "PAYPAL_CLIENT_SECRET"
    PAYPAL_BASE_URL: str = "https://api.sandbox.paypal.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
