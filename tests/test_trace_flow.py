import secrets
import pytest
from fastapi.testclient import TestClient
from app.api.main import app


@pytest.mark.parametrize("module", ["pip", "306090"])
@pytest.mark.parametrize("kind", ["pdf", "xlsx", "csv"])
def test_trace_flow(module, kind):
    client = TestClient(app)
    trace_id = "it-" + secrets.token_hex(8)
    payload = {
        "content": {"dummy": True},
        "module": module,
        "client": "DemoCo",
        "trace_id": trace_id,
    }
    resp = client.post(f"/v1/export/{kind}", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["trace_id"] == trace_id
    assert data["export_branding_compliance"] is True
    assert isinstance(data["export_manifest_hash"], str)
    assert len(data["export_manifest_hash"]) == 64
    assert all(c in "0123456789abcdef" for c in data["export_manifest_hash"])
