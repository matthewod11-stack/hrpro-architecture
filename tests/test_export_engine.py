from pathlib import Path

from app.services import export_engine


def test_pdf_export_manifest_and_branding(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    req = {
        "trace_id": "adv_123",
        "client": "acme",
        "module": "advisor",
        "title": "Advisor Summary",
        "content": "Hello world",
        "branding": {"client_name": "ACME", "logo_path": ""},
    }
    path, ok, mh = export_engine.render_pdf(req)
    assert ok is True
    assert Path(path).exists()
    mh2 = export_engine._manifest_hash(req, Path(path))
    assert mh == mh2


def test_branding_noncompliance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    req = {
        "trace_id": "adv_123",
        "client": "acme",
        "module": "advisor",
        "title": "Advisor Summary",
        "content": "x",
        "branding": {"client_name": ""},
    }
    path, ok, mh = export_engine.render_csv(req)
    assert Path(path).exists()
    assert ok is False
    assert len(mh) == 64
