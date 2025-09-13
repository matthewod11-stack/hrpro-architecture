def parse_sse(raw: str):
    events = []
    for line in raw.splitlines():
        if line.startswith("data: "):
            evt = json.loads(line.split("data: ", 1)[1])
            events.append(evt)
    return events


import json

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_advisor_happy():
    resp = client.post(
        "/v1/advisor/answer", json={"query": "How do we enforce citations?"}
    )
    events = parse_sse(resp.text)
    # Assert first frame is start
    assert events[0]["event"] == "start"
    assert "trace_id" in events[0]
    # Assert at least one delta frame (may be empty text)
    delta_events = [e for e in events if e.get("event") == "delta"]
    assert len(delta_events) >= 1
    # Assert exactly one final frame
    final_events = [e for e in events if e.get("event") == "final"]
    assert len(final_events) == 1
    answer = final_events[0]["answer"]
    assert answer["trace_id"].startswith("adv_")
    for k in [
        "summary",
        "findings",
        "actions",
        "insights",
        "citations",
        "explainability_tag",
        "trace_id",
    ]:
        assert k in answer


def test_advisor_timeout(monkeypatch):
    def raise_timeout(*a, **kw):
        raise TimeoutError("ollama timeout")

    monkeypatch.setattr("app.retrieval.ollama_client.chat", raise_timeout)
    resp = client.post("/v1/advisor/answer", json={"query": "timeout test"})
    events = parse_sse(resp.text)
    # Allow start first, then error
    error_events = [e for e in events if e.get("event") == "error"]
    assert len(error_events) >= 1
    err = error_events[0]
    assert "timeout" in err["message"]
    assert "trace_id" in err


def test_advisor_stream_chunks():
    resp = client.post(
        "/v1/advisor/answer", json={"query": "How do we enforce citations?"}
    )
    events = parse_sse(resp.text)
    chunk_count = sum(1 for e in events if e.get("event") == "delta")
    assert chunk_count > 0
    assert resp.headers["content-type"].startswith("text/event-stream")
