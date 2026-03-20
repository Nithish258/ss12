from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_EXPIRY_DAYS: int = 7
    CORS_ORIGIN: str = "http://localhost:3000"
    PORT: int = 3001

    class Config:
        env_file = ".env"

settings = Settings()
