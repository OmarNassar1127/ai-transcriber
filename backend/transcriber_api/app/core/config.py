from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Transcriber API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_WS_URL: str = "wss://api.openai.com/v1/realtime"

    # CORS settings (for development)
    BACKEND_CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
