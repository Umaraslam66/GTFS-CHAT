"""
Google ADK-inspired agent wrapper using OpenRouter via LiteLLM.
References:
- BitDoze guide on OpenRouter with ADK: https://www.bitdoze.com/google-adk-openrouter-models/
"""

import logging
from typing import List, Optional
from datetime import date, time

import litellm

from .config import get_settings
from .intent import parse_intent
from .query_planner import departures_between, search_stops
from . import schemas

settings = get_settings()
logger = logging.getLogger(__name__)

# Configure litellm for OpenRouter
litellm.api_key = settings.openrouter_api_key or None
litellm.api_base = "https://openrouter.ai/api/v1"


SYSTEM_PROMPT = """
You are a GTFS Sweden travel assistant. Always ground answers in GTFS Sweden 3 data.
If you receive a tool result table, summarize clearly and concisely.
Return succinct, user-friendly text; avoid speculation.
"""


def run_agent(message: str, session, max_rows: int = 50) -> schemas.ChatResponse:
    """
    Entry point for the chat endpoint.
    1) Parse intent heuristically.
    2) Use GTFS tools (search, departures).
    3) Let OpenRouter LLM craft the summary text when available; otherwise use deterministic text.
    """
    parsed = parse_intent(message)
    warnings: List[str] = []

    if not parsed.origin or not parsed.destination:
        return schemas.ChatResponse(
            messages=[
                schemas.ChatMessage(
                    role="assistant",
                    text="Please specify both origin and destination (e.g., 'from Stockholm C to Göteborg').",
                    warnings=["Missing origin or destination."]
                )
            ],
            metadata={}
        )

    tables = departures_between(
        session=session,
        origin_name=parsed.origin,
        destination_name=parsed.destination,
        travel_date=parsed.date,
        after_time=parsed.time,
        limit_rows=max_rows,
    )

    if not tables:
        return schemas.ChatResponse(
            messages=[
                schemas.ChatMessage(
                    role="assistant",
                    text="I could not find departures for that query. Try another time window or check stop names.",
                    warnings=["No results found."]
                )
            ],
            metadata={}
        )

    summary_text = build_summary_text(parsed, tables[0])
    return schemas.ChatResponse(
        messages=[
            schemas.ChatMessage(
                role="assistant",
                text=summary_text,
                table=tables[0],
                warnings=warnings or None,
            )
        ],
        metadata={}
    )


def build_summary_text(parsed, table: schemas.TableData) -> str:
    """Use OpenRouter LLM if configured; otherwise fallback to deterministic summary."""
    if settings.openrouter_api_key:
        try:
            prompt = f"""
{SYSTEM_PROMPT}

User asked: "{parsed.raw}"
We found {len(table.rows)} departures.
Provide a short helpful summary (one sentence) mentioning origin/destination and if filters were applied.
"""
            completion = litellm.completion(
                model=settings.openrouter_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=80,
                temperature=0.2,
            )
            return completion["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # best-effort fallback
            logger.warning("OpenRouter summary failed, using fallback: %s", exc)

    parts = [f"Departures from {parsed.origin} to {parsed.destination}"]
    if parsed.date:
        parts.append(f"on {parsed.date.isoformat()}")
    if parsed.time:
        parts.append(f"after {parsed.time.strftime('%H:%M')}")
    parts.append(f"({len(table.rows)} results).")
    return " ".join(parts)

