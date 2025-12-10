import os
from functools import lru_cache

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env from backend directory for local development
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")


class Settings(BaseModel):
    database_url: str = Field(..., alias="DATABASE_URL")
    trafiklab_api_key: str = Field(..., alias="TRAFIKLAB_API_KEY")
    model_provider: str = Field("ollama", alias="MODEL_PROVIDER")
    model_name: str = Field("llama3.2", alias="MODEL_NAME")
    openrouter_api_key: str = Field("", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field("openrouter/quasar-alpha", alias="OPENROUTER_MODEL")
    log_level: str = Field("INFO", alias="LOG_LEVEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(**os.environ)

