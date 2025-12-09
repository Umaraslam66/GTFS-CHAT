import logging

from fastapi import FastAPI

from .config import get_settings
from .router_chat import router as chat_router
from .router_health import router as health_router

settings = get_settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="GTFS Sweden Chat Backend", version="0.1.0")

app.include_router(health_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "GTFS Sweden chat backend is running"}

