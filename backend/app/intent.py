import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional

from dateutil import parser


@dataclass
class ParsedIntent:
    origin: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    intent_type: str = "departures"  # departures | arrivals | routes | summary
    raw: str = ""


TIME_KEYWORDS = {
    "morning": time(6, 0),
    "noon": time(12, 0),
    "afternoon": time(14, 0),
    "evening": time(18, 0),
    "night": time(21, 0),
}


def parse_intent(message: str) -> ParsedIntent:
    """Lightweight heuristic parser to extract origin, destination, date/time, and intent type."""
    lowered = message.lower()
    origin, destination = _extract_stops(lowered)
    intent_type = _detect_intent_type(lowered)
    when_date, when_time = _extract_datetime(lowered)

    return ParsedIntent(
        origin=origin,
        destination=destination,
        date=when_date,
        time=when_time,
        intent_type=intent_type,
        raw=message,
    )


def _extract_stops(text: str) -> tuple[Optional[str], Optional[str]]:
    # Capture stop names non-greedily and stop at common time/date cues or punctuation
    pattern = (
        r"from\s+([a-zåäöøéü0-9 \-]+?)\s+to\s+"
        r"([a-zåäöøéü0-9 \-]+?)(?=\s+(after|at|by|around|tomorrow|today|tonight|this|on)\b|[?.!,]|$)"
    )
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip().title(), match.group(2).strip().title()
    return None, None


def _detect_intent_type(text: str) -> str:
    if "arriv" in text:
        return "arrivals"
    if "route" in text or "how to get" in text:
        return "routes"
    if "summary" in text or "freq" in text:
        return "summary"
    return "departures"


def _extract_datetime(text: str) -> tuple[Optional[date], Optional[time]]:
    extracted_date = None
    extracted_time = None

    # explicit times/dates
    try:
        dt = parser.parse(text, fuzzy=True, default=datetime.now())
        extracted_date = dt.date()
        extracted_time = dt.time().replace(microsecond=0)
    except (parser.ParserError, ValueError):
        pass

    # relative keywords
    now = datetime.now()
    if "tomorrow" in text:
        extracted_date = (now + timedelta(days=1)).date()
    if any(word in text for word in ("today", "tonight")):
        extracted_date = now.date()

    for keyword, mapped_time in TIME_KEYWORDS.items():
        if keyword in text:
            extracted_time = mapped_time
            break

    return extracted_date, extracted_time

