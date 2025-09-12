from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import time
from app.retrieval.adapter import retrieve
from pathlib import Path
import json

router = APIRouter(prefix="/v1/advisor", tags=["advisor"])


class AdvisorResponse(BaseModel):
    summary: str
    findings: List[str]
    actions: List[str]
    insights: List[str]
    citations: List[str]
    explainability_tag: str
    trace_id: str
    source_attributions: Optional[List[dict]] = None
    guardrail_reason: Optional[str] = None


class AdvisorRequest(BaseModel):
    prompt: str
    module: str
    trace_id: str


@router.post("/answer", response_model=AdvisorResponse)
def advisor_answer(req: AdvisorRequest):
    t0 = time.perf_counter()
    # Simulate summary, findings, etc.
    summary = f"Stub summary for: {req.prompt}"
    findings = [f"Finding for {req.module}"]
    actions = ["Action 1"]
    insights = ["Insight 1"]
    citations = ["§1.1", "§2.2"]
    explainability_tag = "local-rag"
    # Retrieval
    results = retrieve(topic=req.prompt, top_k=5)
    if not results:
        source_attributions = []
        guardrail_reason = "No relevant documentation found in local KB"
    else:
        source_attributions = [
            {
                "doc": r["doc"],
                "section": r["section"],
                "anchor": r["anchor"],
                "path": r["path"],
                "score": r["score"],
            }
            for r in results
        ]
        guardrail_reason = None
    elapsed = int((time.perf_counter() - t0) * 1000)
    telemetry_line = {
        "event": "advisor_response",
        "trace_id": req.trace_id,
        "advisor_ttfa_ms": elapsed,
        "advisor_has_citations": bool(source_attributions),
        "retrieved_docs_count": len(source_attributions),
    }
    log_path = Path(__file__).parent.parent.parent / "logs/dev_telemetry.jsonl"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(telemetry_line) + "\n")
    return AdvisorResponse(
        summary=summary,
        findings=findings,
        actions=actions,
        insights=insights,
        citations=citations,
        explainability_tag=explainability_tag,
        trace_id=req.trace_id,
        source_attributions=source_attributions,
        guardrail_reason=guardrail_reason,
    )
