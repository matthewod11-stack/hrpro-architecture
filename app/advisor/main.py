"""FastAPI application entrypoint for the Advisor service."""

import json
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.routers import advisor, charts

app = FastAPI(title="HRPro Advisor API")

# include routers after app creation
app.include_router(advisor.router)
app.include_router(charts.router)

ADVISOR_SHAPE = {
    "summary": "",
    "findings": [],
    "actions": [],
    "insights": [],
    "citations": [],
    "explainability_tag": "",
    "trace_id": "",
}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/v1/advisor/answer")
async def advisor_answer(req: Request):
    body = await req.json()
    stream = bool(body.get("stream", False))
    trace_id = str(uuid.uuid4())

    if not stream:
        payload = {
            **ADVISOR_SHAPE,
            "summary": "Hello from stub — backend reached successfully.",
            "citations": ["Local KB"],
            "explainability_tag": "demo",
            "trace_id": trace_id,
        }
        return JSONResponse(payload)

    def gen():
        # simulate token stream
        yield f"data: {json.dumps({'delta':'Hello '})}\n\n"
        time.sleep(0.2)
        yield f"data: {json.dumps({'delta':'from '})}\n\n"
        time.sleep(0.2)
        yield f"data: {json.dumps({'delta':'SSE stub'})}\n\n"
        time.sleep(0.2)
        final = {
            **ADVISOR_SHAPE,
            "summary": "Hello from SSE stub (final)",
            "citations": ["Local KB"],
            "explainability_tag": "demo",
            "trace_id": trace_id,
        }
        yield f"data: {json.dumps({'final': final})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
