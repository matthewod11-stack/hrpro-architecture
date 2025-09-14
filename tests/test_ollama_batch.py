import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")

import sys
import types


def test_ollama_rerank_batch(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "yaml",
        types.SimpleNamespace(
            safe_load=lambda f: {"ollama": {"endpoint": "http://x", "model": "m"}}
        ),
    )
    from app.retrieval import rerank as rerank_mod

    class DummyResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"responses": ["0.5", "0.25"]}

    calls = {"count": 0}

    def fake_post(url, json, timeout):
        calls["count"] += 1
        assert isinstance(json.get("passages"), list)
        return DummyResp()

    monkeypatch.setattr(rerank_mod.requests, "post", fake_post)

    query = "test"
    candidates = [
        {"section": "alpha", "snippet": "alpha snippet"},
        {"section": "beta", "snippet": "beta snippet"},
    ]

    scores = rerank_mod.ollama_rerank(query, candidates)

    assert scores == [0.5, 0.25]
    assert calls["count"] == 1
