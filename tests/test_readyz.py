import sys
import types

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
import pytest

# Provide minimal yaml stub to satisfy imports when PyYAML is missing
yaml_stub = types.ModuleType("yaml")
yaml_stub.safe_load = lambda *a, **kw: {}
yaml_stub.dump = lambda *a, **kw: None
sys.modules.setdefault("yaml", yaml_stub)

from app.api.main import app
from app.retrieval import adapter, ollama_client


@pytest.mark.asyncio
async def test_readyz_success(tmp_path, monkeypatch):
    # Create required index files
    files = {
        "meta.json",
        "matrix.npz",
        "tfidf.joblib",
        "nn.joblib",
    }
    for name in files:
        (tmp_path / name).write_text("x")

    monkeypatch.setattr(adapter, "META_PATH", tmp_path / "meta.json")
    monkeypatch.setattr(adapter, "MATRIX_PATH", tmp_path / "matrix.npz")
    monkeypatch.setattr(adapter, "VEC_PATH", tmp_path / "tfidf.joblib")
    monkeypatch.setattr(adapter, "NN_PATH", tmp_path / "nn.joblib")
    monkeypatch.setattr(ollama_client, "health_ok", lambda: True)

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            resp = await ac.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_readyz_ollama_failure(tmp_path, monkeypatch):
    for name in ["meta.json", "matrix.npz", "tfidf.joblib", "nn.joblib"]:
        (tmp_path / name).write_text("x")
    monkeypatch.setattr(adapter, "META_PATH", tmp_path / "meta.json")
    monkeypatch.setattr(adapter, "MATRIX_PATH", tmp_path / "matrix.npz")
    monkeypatch.setattr(adapter, "VEC_PATH", tmp_path / "tfidf.joblib")
    monkeypatch.setattr(adapter, "NN_PATH", tmp_path / "nn.joblib")
    monkeypatch.setattr(ollama_client, "health_ok", lambda: False)

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            resp = await ac.get("/readyz")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "not ready"
    assert any("ollama" in e for e in body["errors"])


@pytest.mark.asyncio
async def test_readyz_missing_index(monkeypatch, tmp_path):
    # don't create index files to trigger missing
    monkeypatch.setattr(adapter, "META_PATH", tmp_path / "meta.json")
    monkeypatch.setattr(adapter, "MATRIX_PATH", tmp_path / "matrix.npz")
    monkeypatch.setattr(adapter, "VEC_PATH", tmp_path / "tfidf.joblib")
    monkeypatch.setattr(adapter, "NN_PATH", tmp_path / "nn.joblib")
    monkeypatch.setattr(ollama_client, "health_ok", lambda: True)

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            resp = await ac.get("/readyz")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "not ready"
    assert any("missing index files" in e for e in body["errors"])
