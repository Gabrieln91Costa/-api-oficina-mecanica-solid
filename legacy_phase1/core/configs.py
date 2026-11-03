from pydantic import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "API Oficina Mecânica"

    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite+aiosqlite:///./oficina.db"

    JWT_SECRET_KEY: str = "oficina-mecanica-secret-key"

    JWT_ALGORITHM: str = "HS256"

    JWT_EXPIRE_MINUTES: int = 60


settings = Settings()