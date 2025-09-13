from app.services import telemetry


def test_emit_and_tail(tmp_path, monkeypatch):
    monkeypatch.setattr(telemetry, "LOG_DIR", tmp_path)
    telemetry.emit("advisor", {"event": "start", "trace_id": "t1"})
    telemetry.emit(
        "advisor", {"event": "final", "trace_id": "t1", "has_citations": True}
    )
    rows = telemetry.tail("advisor", 10)
    assert len(rows) == 2
    assert rows[-1]["has_citations"] is True
