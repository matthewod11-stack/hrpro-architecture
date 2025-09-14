import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")
pytest.importorskip("yaml")

from app.retrieval.adapter import retrieve


@pytest.fixture(scope="session", autouse=True)
def setup_kb():
    import subprocess

    subprocess.run(["python", "tools/build_corpus.py"], check=True)
    subprocess.run(["python", "tools/index_corpus.py"], check=True)


def test_retrieve_nonempty():
    results = retrieve("design tokens", top_k=5)
    assert len(results) > 0
    for r in results:
        assert 0 <= r["score"] <= 1


def test_retrieve_nohit():
    results = retrieve("gibberishnotfound", top_k=3)
    assert isinstance(results, list)
    assert len(results) == 0 or all(0 <= r["score"] <= 1 for r in results)


def test_meta_alignment():
    results = retrieve("acceptance criteria", top_k=2)
    import json
    from pathlib import Path

    meta = json.load(open(Path("versions/index/meta.json")))
    for r in results:
        assert r["id"] in [m["id"] for m in meta.values() if isinstance(m, dict)]
        assert Path(r["path"]).exists()
