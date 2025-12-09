from app.intent import parse_intent


def test_parse_basic_departure_intent():
    msg = "Which trains go from Uppsala to Stockholm tomorrow after 14:00?"
    parsed = parse_intent(msg)
    assert parsed.origin == "Uppsala"
    assert parsed.destination == "Stockholm"
    assert parsed.intent_type == "departures"
    assert parsed.date is not None
    assert parsed.time is not None


def test_parse_missing_stops():
    parsed = parse_intent("Show me departures")
    assert parsed.origin is None
    assert parsed.destination is None

