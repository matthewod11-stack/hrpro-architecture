def parse_sse(raw: str):
    events = []
    for line in raw.splitlines():
        if line.startswith("data: "):
            evt = json.loads(line.split("data: ", 1)[1])
            events.append(evt)
    return events


import json

import pytest
pytest.importorskip("yaml")
from fastapi.testclient import TestClient

from app.api.main import app
from app.services import telemetry


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(telemetry, "LOG_DIR", tmp_path / "telemetry", raising=False)
    telemetry.LOG_DIR.mkdir(parents=True, exist_ok=True)

    from app.services import retrieval
    from app.retrieval import ollama_client

    monkeypatch.setattr(
        retrieval,
        "retrieve",
        lambda q, top_k=6: [
            {
                "anchor": "§1.4.5",
                "source": "PRD_v4.0_unified_numbered.md",
                "path": "docs/PRD_v4.0_unified_numbered.md",
                "snippet_start": 0,
                "snippet": "Advisor responses include sources...",
                "score": 1.0,
            }
        ],
    )

    def fake_chat(**kw):
        yield {"response": "Hello world."}

    monkeypatch.setattr(ollama_client, "chat", lambda **kw: fake_chat())

    return TestClient(app)


def test_advisor_happy(client):
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


def test_advisor_timeout(client, monkeypatch):
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


def test_advisor_stream_chunks(client):
    resp = client.post(
        "/v1/advisor/answer", json={"query": "How do we enforce citations?"}
    )
    events = parse_sse(resp.text)
    chunk_count = sum(1 for e in events if e.get("event") == "delta")
    assert chunk_count > 0
    assert resp.headers["content-type"].startswith("text/event-stream")
