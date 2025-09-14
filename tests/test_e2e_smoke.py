import json

from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def client(monkeypatch, tmp_path):
    from app.services import telemetry

    monkeypatch.setattr(telemetry, "LOG_DIR", tmp_path / "telemetry", raising=False)
    telemetry.LOG_DIR.mkdir(parents=True, exist_ok=True)
    from app.services import retrieval

    monkeypatch.setattr(
        retrieval,
        "retrieve",
        lambda q, top_k=6: [
            {
                "anchor": "§1.4.5",
                "source": "PRD_v4.0_unified_numbered.md",
                "path": "docs/PRD/PRD_v4.0_unified_numbered.md",
                "snippet_start": 0,
                "snippet": "Advisor responses include sources...",
                "score": 1.0,
            }
        ],
    )
    from app.services import ollama_client

    def fake_chat(**kw):
        yield {"text": "Hello "}
        yield {"text": "world."}

    monkeypatch.setattr(ollama_client, "chat", lambda **kw: fake_chat())
    from app.api.main import app

    return TestClient(app)


def test_e2e_smoke_happy_path(client, tmp_path):
    r = client.post(
        "/v1/advisor/answer", json={"query": "x", "persona": "cpo", "top_k": 1}
    )
    assert r.status_code == 200
    evts = [
        json.loads(line.split("data: ")[1])
        for line in r.text.splitlines()
        if line.startswith("data: ")
    ]
    final = next(e for e in evts if e.get("event") == "final")["answer"]
    assert final["citations"]
    trace = next(e for e in evts if "trace_id" in e)["trace_id"]
    tdir = tmp_path / "telemetry"
    adv = (tdir / "advisor.jsonl").read_text().splitlines()
    assert any(trace in x for x in adv)
