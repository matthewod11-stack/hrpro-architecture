import json

import pytest

pytest.importorskip("yaml")
from fastapi.testclient import TestClient

from app.api.main import app
from app.services import telemetry


def parse_sse(raw: str) -> list[dict]:
    events = []
    for line in raw.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line.split("data: ", 1)[1]))
    return events


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Test client with stubbed retrieval, model, and telemetry."""
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


def test_advisor_returns_citations(client):
    resp = client.post("/v1/advisor/answer", json={"query": "design tokens", "top_k": 1})
    assert resp.status_code == 200
    events = parse_sse(resp.text)
    final = next(e for e in events if e.get("event") == "final")["answer"]
    assert isinstance(final["citations"], list)
    assert len(final["citations"]) > 0


def test_advisor_no_citations_when_missing(client, monkeypatch):
    from app.services import retrieval

    monkeypatch.setattr(retrieval, "retrieve", lambda q, top_k=6: [])
    resp = client.post("/v1/advisor/answer", json={"query": "gibberishnotfound"})
    events = parse_sse(resp.text)
    final = next(e for e in events if e.get("event") == "final")["answer"]
    assert final["citations"] == []


def test_advisor_telemetry_fields(client, tmp_path):
    client.post("/v1/advisor/answer", json={"query": "acceptance criteria"})
    log_path = tmp_path / "telemetry" / "advisor.jsonl"
    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    final = next(l for l in lines if l.get("event") == "final")
    assert "has_citations" in final
    assert "total_ms" in final
