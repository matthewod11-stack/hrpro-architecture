import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")

import sys
import types

import requests

from app.services import telemetry


def test_ollama_rerank_fallback(monkeypatch, tmp_path):
    """When Ollama is unreachable, heuristic scores are returned and logged."""

    monkeypatch.setitem(
        sys.modules,
        "yaml",
        types.SimpleNamespace(
            safe_load=lambda f: {"ollama": {"endpoint": "http://x", "model": "m"}}
        ),
    )
    from app.retrieval import rerank as rerank_mod

    def boom(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(rerank_mod.requests, "post", boom)
    monkeypatch.setattr(telemetry, "LOG_DIR", tmp_path, raising=False)
    telemetry.LOG_DIR.mkdir(parents=True, exist_ok=True)

    query = "test"
    candidates = [
        {"section": "alpha", "snippet": "alpha snippet"},
        {"section": "beta", "snippet": "beta snippet"},
    ]

    expected = rerank_mod.heuristic_rerank(query, candidates)
    scores = rerank_mod.ollama_rerank(query, candidates)

    assert scores == expected

    log_file = tmp_path / "retrieval.jsonl"
    lines = log_file.read_text().splitlines()
    assert any("ollama_rerank_fallback" in line for line in lines)

