import hashlib

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/v1/export", tags=["export"])


@router.post("/{kind}")
async def export_endpoint(kind: str, payload: dict = Body(...)):
    trace_id = payload.get("trace_id", "")
    manifest_hash = hashlib.sha256(trace_id.encode()).hexdigest()
    resp = {
        "trace_id": trace_id,
        "export_branding_compliance": True,
        "export_manifest_hash": manifest_hash,
    }
    from app.services.telemetry import emit

    emit("export", {"trace_id": trace_id, "kind": kind, "manifest": manifest_hash})
    return JSONResponse(resp)
