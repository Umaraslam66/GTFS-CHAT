"""
Minimal ADK runner wrapper that reuses our existing chat flow but exposes a callable
that can be plugged into ADK. This keeps FastAPI as the serving layer while ADK/LiteLLM
handles reasoning. We rely on OPENROUTER_API_KEY and OPENROUTER_MODEL from env.
"""
import os
import logging
from typing import Any, Dict

import litellm

from .config import get_settings
from .intent import parse_intent
from .query_planner import departures_between
from .schemas import ChatResponse, ChatMessage

settings = get_settings()
logger = logging.getLogger(__name__)

litellm.api_key = settings.openrouter_api_key or None
litellm.api_base = "https://openrouter.ai/api/v1"


def adk_chat(message: str, session) -> ChatResponse:
    parsed = parse_intent(message)
    if not parsed.origin or not parsed.destination:
        return ChatResponse(
            messages=[
                ChatMessage(
                    role="assistant",
                    text="Please provide both origin and destination (e.g., 'from Stockholm C to Göteborg').",
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
    )

    if not tables:
        return ChatResponse(
            messages=[
                ChatMessage(
                    role="assistant",
                    text="No rail departures found. Try another time window or check stop names.",
                    warnings=["No results found."]
                )
            ],
            metadata={}
        )

    summary = _llm_summary(parsed, tables[0])
    return ChatResponse(
        messages=[
            ChatMessage(
                role="assistant",
                text=summary,
                table=tables[0],
                warnings=None,
            )
        ],
        metadata={}
    )


def _llm_summary(parsed, table) -> str:
    if not settings.openrouter_api_key:
        return _fallback_summary(parsed, table)
    prompt = f"""
You are a concise GTFS Sweden rail assistant.
User asked: "{parsed.raw}"
Rows: {len(table.rows)}
Summarize in one sentence, mentioning origin, destination, and if time/date filters apply.
"""
    try:
        completion = litellm.completion(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": "Be concise and factual based on provided results."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=80,
            temperature=0.2,
        )
        return completion["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning("OpenRouter summary failed, fallback used: %s", exc)
        return _fallback_summary(parsed, table)


def _fallback_summary(parsed, table) -> str:
    parts = [f"Rail departures from {parsed.origin} to {parsed.destination}"]
    if parsed.date:
        parts.append(f"on {parsed.date.isoformat()}")
    if parsed.time:
        parts.append(f"after {parsed.time.strftime('%H:%M')}")
    parts.append(f"({len(table.rows)} results).")
    return " ".join(parts)

