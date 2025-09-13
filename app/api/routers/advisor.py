from __future__ import annotations

import json
import uuid
from typing import Iterator, Dict, Any

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.schemas.advisor import AdvisorQuery
from app.services.advisor_orchestrator import stream_advisor_answer

router = APIRouter()


def _sse_frame(obj: Dict[str, Any]) -> bytes:
    """Encode a Python object as an SSE data frame."""
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n".encode("utf-8")


@router.post("/v1/advisor/answer")
def advisor_answer(q: AdvisorQuery) -> StreamingResponse:
    """
    SSE endpoint that streams advisor events.

    Contract: emits at least a 'start', one or more streamed events from the orchestrator,
    and a final 'ping' to encourage client flush.
    """
    trace_id = "adv_" + uuid.uuid4().hex

    def gen() -> Iterator[bytes]:
        # Surface trace_id immediately so UI can display it
        yield _sse_frame({"event": "start", "trace_id": trace_id})
        # Heartbeat delta to coax flush
        yield _sse_frame({"event": "delta", "text": "", "trace_id": trace_id})
        for evt in stream_advisor_answer(q, trace_id):
            # Each evt is expected to be a dict containing at least {"event": "...", ...}
            # Ensure the trace_id is present on every frame
            if "trace_id" not in evt:
                evt["trace_id"] = trace_id
            yield _sse_frame(evt)
        # Final heartbeat to flush last frame
        yield _sse_frame({"event": "ping", "trace_id": trace_id})

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(gen(), media_type="text/event-stream", headers=headers)
