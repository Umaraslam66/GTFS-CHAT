from app.response_formatter import build_chat_response


def test_response_formatter_wraps_table():
    table = None
    resp = build_chat_response("hello", tables=[table] if table else None)
    assert resp.messages[0].text == "hello"
    assert resp.messages[0].table is None

