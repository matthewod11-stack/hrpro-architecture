import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


def get_telemetry_lines():
    log_path = Path(__file__).parent.parent / "logs/dev_telemetry.jsonl"
    if not log_path.exists():
        return []
    return [json.loads(line) for line in open(log_path)]


client = TestClient(app)


def test_advisor_returns_attributions():
    resp = client.post(
        "/v1/advisor/answer",
        json={"prompt": "design tokens", "module": "dashboard", "trace_id": "t1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["source_attributions"], list)
    assert len(data["source_attributions"]) > 0
    assert data["guardrail_reason"] is None


def test_advisor_returns_guardrail_reason():
    resp = client.post(
        "/v1/advisor/answer",
        json={"prompt": "gibberishnotfound", "module": "dashboard", "trace_id": "t2"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_attributions"] == []
    assert data["guardrail_reason"] is not None


def test_advisor_telemetry_fields():
    # Call once to ensure log
    client.post(
        "/v1/advisor/answer",
        json={"prompt": "acceptance criteria", "module": "dashboard", "trace_id": "t3"},
    )
    lines = get_telemetry_lines()
    found = False
    for line in lines:
        if line.get("event") == "advisor_response":
            assert "advisor_ttfa_ms" in line
            assert "advisor_has_citations" in line
            assert "retrieved_docs_count" in line
            found = True
    assert found
