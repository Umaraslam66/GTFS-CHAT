from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import schemas
from .deps import get_db
from .adk_agent import run_agent
from .adk_runner import adk_chat

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=schemas.ChatResponse)
def chat_endpoint(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    return run_agent(payload.message, session=db)


@router.post("/chat/adk", response_model=schemas.ChatResponse)
def chat_adk_endpoint(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    return adk_chat(payload.message, session=db)

