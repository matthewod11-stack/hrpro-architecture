import pytest

pytest.importorskip("sklearn")
pytest.importorskip("scipy")

from app.retrieval.adapter import retrieve, _load


def test_faiss_index_loads():
    _load()
    # Should not raise
    assert True


def test_retrieve_design_tokens():
    results = retrieve("design tokens", top_k=3)
    assert isinstance(results, list)
    assert len(results) > 0
    for r in results:
        assert 0 <= r["score"] <= 1


def test_eval_runner():
    import subprocess
    import os

    subprocess.run(["python", "tools/eval_retrieval.py"], check=True)
    assert os.path.exists("evals/retrieval_eval_report.csv")
