from fastapi.testclient import TestClient

from app.main import app
from app.deps import get_db


class DummySession:
    """Placeholder session; chat endpoint short-circuits before DB when stops are missing."""
    pass


def override_get_db():
    yield DummySession()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_chat_requires_message():
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 400


def test_chat_missing_stops_prompts():
    resp = client.post("/api/chat", json={"message": "Show me departures"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["messages"][0]["warnings"] is not None

