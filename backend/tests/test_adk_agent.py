import types

from app.adk_agent import build_summary_text, run_agent
from app.schemas import TableColumn, TableData, ChatResponse


class DummyParsed:
    def __init__(self, raw: str, origin: str, destination: str, date=None, time=None):
        self.raw = raw
        self.origin = origin
        self.destination = destination
        self.date = date
        self.time = time


class DummySession:
    """Session placeholder; not used directly in these tests."""
    pass


def test_summary_fallback_without_openrouter(monkeypatch):
    parsed = DummyParsed("from A to B", "A", "B")
    table = TableData(columns=[TableColumn(id="c1", label="C1")], rows=[{"c1": "v"}])

    monkeypatch.setattr("app.adk_agent.settings", types.SimpleNamespace(openrouter_api_key=""))
    result = build_summary_text(parsed, table)
    assert "Departures from A to B" in result


def test_run_agent_missing_stops():
    resp: ChatResponse = run_agent("Show me departures", session=DummySession())
    assert resp.messages[0].warnings is not None


def test_run_agent_no_results(monkeypatch):
    # Force departures_between to return empty
    monkeypatch.setattr("app.adk_agent.departures_between", lambda *args, **kwargs: [])
    resp: ChatResponse = run_agent("from A to B", session=DummySession())
    assert resp.messages[0].warnings is not None

