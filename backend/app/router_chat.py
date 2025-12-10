from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import schemas
from .deps import get_db
from .adk_handler import run_adk_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat/adk", response_model=schemas.ChatResponse)
async def chat_adk_endpoint(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    """Chat endpoint using Google ADK agent with OpenRouter."""
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    
    return await run_adk_agent(
        message=payload.message,
        session=db,
        session_id=payload.session_id,
        model=payload.model,
    )

