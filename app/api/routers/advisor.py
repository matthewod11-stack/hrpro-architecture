from __future__ import annotations

import json
import uuid

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.schemas.advisor import AdvisorQuery
from app.services.advisor_orchestrator import stream_advisor_answer

router = APIRouter()


def _sse_frame(obj: dict) -> bytes:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n".encode()


@router.post("/v1/advisor/answer")
def advisor_answer(q: AdvisorQuery):
    trace_id = "adv_" + uuid.uuid4().hex

    def gen():
        # surface trace_id immediately so UI can display it
        yield _sse_frame({"event": "start", "trace_id": trace_id})
        # heartbeat delta to coax flush
        yield _sse_frame({"event": "delta", "text": "", "trace_id": trace_id})
        for evt in stream_advisor_answer(q, trace_id):
            yield _sse_frame(evt)
        # final heartbeat to flush last frame
        yield _sse_frame({"event": "ping", "trace_id": trace_id})

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)
