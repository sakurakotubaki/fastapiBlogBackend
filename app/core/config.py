from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://bloguser:blogpass@localhost:5432/blogdb"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SUPERUSER_EMAIL: str = "admin@co.jp"
    SUPERUSER_PASSWORD: str = 'admin[1234;"'

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
