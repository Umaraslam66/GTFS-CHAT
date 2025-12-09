from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import schemas
from .intent import parse_intent
from .query_planner import departures_between
from .response_formatter import build_chat_response
from .deps import get_db

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=schemas.ChatResponse)
def chat_endpoint(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    parsed = parse_intent(payload.message)
    warnings = []

    if not parsed.origin or not parsed.destination:
        return build_chat_response(
            "Please specify both origin and destination stops (e.g., 'from Stockholm C to Göteborg').",
            warnings=["Missing origin or destination."],
        )

    travel_date: Optional[date] = parsed.date
    tables = departures_between(
        session=db,
        origin_name=parsed.origin,
        destination_name=parsed.destination,
        travel_date=travel_date,
        after_time=parsed.time,
    )

    if not tables:
        return build_chat_response(
            "I could not find departures for that query. Try adjusting the time or stop names.",
            warnings=["No results found."],
        )

    summary = f"Departures from {parsed.origin} to {parsed.destination}"
    if parsed.date:
        summary += f" on {parsed.date.isoformat()}"
    if parsed.time:
        summary += f" after {parsed.time.strftime('%H:%M')}"

    return build_chat_response(summary, tables=tables, warnings=warnings)

