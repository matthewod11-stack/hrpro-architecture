import json
import pytest

pytest.importorskip("yaml")


def test_eval_harness_smoke(monkeypatch, tmp_path):
    from app.services import advisor_orchestrator as ao

    def fake_stream(q, trace):
        yield {"event": "final", "answer": {"citations": [{"anchor": "§1.4.5"}]}}

    monkeypatch.setattr(ao, "stream_advisor_answer", fake_stream)
    gold = tmp_path / "g.jsonl"
    gold.write_text('{"qid":"G1","query":"x","must_anchor":"§1.4.5"}\n')
    import sys

    from evals.run_advisor_eval import main as run_main

    sys.argv = ["x", "--goldens", str(gold), "--out", str(tmp_path / "out.jsonl")]
    code = run_main()
    assert code == 0
    out = (tmp_path / "out.jsonl").read_text().splitlines()
    assert json.loads(out[0])["ok"] is True
