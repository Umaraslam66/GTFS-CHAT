import os
from functools import lru_cache

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load .env from backend directory for local development
# BASE_DIR is backend/app/, so PROJECT_ROOT is backend/../ (project root)
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
# Try loading .env from backend/ first, then project root
load_dotenv(BASE_DIR.parent / ".env")  # backend/.env
load_dotenv(PROJECT_ROOT / ".env", override=False)  # .env at project root (don't override)


class Settings(BaseModel):
    database_url: str = Field(..., alias="DATABASE_URL")
    
    @field_validator("database_url", mode="before")
    @classmethod
    def resolve_duckdb_path(cls, v: str) -> str:
        """Resolve relative DuckDB paths to absolute paths."""
        if isinstance(v, str) and v.startswith("duckdb:///"):
            # Extract the path part (everything after duckdb:///)
            path_part = v[10:]  # Remove "duckdb:///"
            # If it's a relative path, resolve it from project root
            if not Path(path_part).is_absolute():
                # Remove leading slash if present (duckdb:///data -> data)
                path_part = path_part.lstrip("/")
                # Resolve from project root (parent of backend/)
                abs_path = (PROJECT_ROOT / path_part).resolve()
                # Return with single slash after duckdb://
                return f"duckdb:///{abs_path}"
        return v
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

