import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env if present for local development
load_dotenv()


class Settings(BaseModel):
    database_url: str = Field(..., alias="DATABASE_URL")
    trafiklab_api_key: str = Field(..., alias="TRAFIKLAB_API_KEY")
    model_provider: str = Field("ollama", alias="MODEL_PROVIDER")
    model_name: str = Field("llama3.2", alias="MODEL_NAME")
    log_level: str = Field("INFO", alias="LOG_LEVEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(**os.environ)

